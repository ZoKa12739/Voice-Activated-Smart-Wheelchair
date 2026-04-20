/* USER CODE BEGIN Header */
/**
  ******************************************************************************
  * @file           : main.c
  * @brief          : Main program body
  ******************************************************************************
  * @attention
  *
  * Copyright (c) 2025 STMicroelectronics.
  * All rights reserved.
  *
  * This software is licensed under terms that can be found in the LICENSE file
  * in the root directory of this software component.
  * If no LICENSE file comes with this software, it is provided AS-IS.
  *
  ******************************************************************************
  */
/* USER CODE END Header */
/* Includes ------------------------------------------------------------------*/
#include "main.h"
#include "adc.h"
#include "dac.h"
#include "dma.h"
#include "usart.h"
#include "gpio.h"

/* Private includes ----------------------------------------------------------*/
/* USER CODE BEGIN Includes */
#include <stdio.h>  // 用于 sprintf
#include <string.h> // 用于 strlen
#include "ir_avoidance.h"
/* USER CODE END Includes */

/* Private typedef -----------------------------------------------------------*/
/* USER CODE BEGIN PTD */

/* USER CODE END PTD */

/* Private define ------------------------------------------------------------*/
/* USER CODE BEGIN PD */

/* USER CODE END PD */

/* Private macro -------------------------------------------------------------*/
/* USER CODE BEGIN PM */

/* USER CODE END PM */

/* Private variables ---------------------------------------------------------*/

/* USER CODE BEGIN PV */

// 1. ADC 数据存储 (DMA 自动搬运)
volatile uint16_t adc_values[4];

// 2. 调试打印缓冲区
char uart_buf[100];

// 3. 树莓派命令接收相关
uint8_t rx_buffer[1];
volatile char pi_command = 'S'; // 默认停止

// 4. 速度控制相关
uint8_t current_gear = 3;       // 当前档位 (默认3档)
float speed_ratio = 1.0f;       // 速度系数

// 5. 核心阈值定义 (适配 3.3V 全量程)
#define JOY_CENTER  2048        // 1.65V 对应 4095 的一半
#define DEADZONE    300         // 死区

// 6. 最大偏移量定义 (0-2048 之间)
// 从 2000 减少到 1200：使前进输出 Y≈848(0.69V) 而非 48(0.039V)，电机驱动更稳定
#define MAX_DEV     1200 

// 7. DAC 安全输出边界 (12-bit: 0-4095)
// 避免打到上下电源轨，降低外部模拟链路出现极值误判的风险
#define DAC_SAFE_MIN 1
#define DAC_SAFE_MAX 4094

/* USER CODE END PV */

/* Private function prototypes -----------------------------------------------*/
void SystemClock_Config(void);
/* USER CODE BEGIN PFP */
void MX_USART1_UART_Init(void);
void MX_USART2_UART_Init(void);

/* USER CODE END PFP */

/* Private user code ---------------------------------------------------------*/
/* USER CODE BEGIN 0 */

static inline uint16_t clamp_u12_safe(uint16_t v)
{
  if (v < DAC_SAFE_MIN) {
    return DAC_SAFE_MIN;
  }
  if (v > DAC_SAFE_MAX) {
    return DAC_SAFE_MAX;
  }
  return v;
}

/* USER CODE END 0 */

/**
  * @brief  The application entry point.
  * @retval int
  */
int main(void)
{

  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();

  /* USER CODE BEGIN Init */

  /* USER CODE END Init */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN SysInit */

  /* USER CODE END SysInit */

  /* Initialize all configured peripherals */
  MX_GPIO_Init();
  MX_DMA_Init();
  MX_ADC1_Init();
  MX_DAC_Init();
  MX_USART2_UART_Init();
  MX_USART1_UART_Init();
  /* USER CODE BEGIN 2 */

  // 启动 ADC1 并开启 DMA 模式，数据存入 adc_values 数组 (扩展为 4 通道)
  HAL_ADC_Start_DMA(&hadc1, (uint32_t*)adc_values, 4);
  // // 启动 DAC 通道 1 (PA4)
  HAL_DAC_Start(&hdac, DAC_CHANNEL_1);
  // // 启动 DAC 通道 2 (PA5)
  HAL_DAC_Start(&hdac, DAC_CHANNEL_2);

  IR_Avoidance_Init();

  HAL_UART_Receive_IT(&huart2, rx_buffer, 1);

  /* USER CODE END 2 */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    /*
    * 此时，DMA 正在后台自动、连续地：
    * 1. 转换 PA0 (X轴) -> 存入 adc_values[0]
    * 2. 转换 PA1 (Y轴) -> 存入 adc_values[1]
    * 3. 转换 PA6 (左红外) -> 存入 adc_values[2]
    * 4. 转换 PA7 (右红外) -> 存入 adc_values[3]
    */

    // 1. 获取当前传感器原始数据
    uint16_t x_raw = adc_values[0];
    uint16_t y_raw = adc_values[1];
    uint16_t ir_left = adc_values[2];
    uint16_t ir_right = adc_values[3];

    // 2. 红外避障处理：获取动态速度系数
    float ir_speed_limit = IR_Avoidance_Process(ir_left, ir_right);

    // 3. 准备 DAC 输出变量
    uint16_t dac_x = JOY_CENTER;
    uint16_t dac_y = JOY_CENTER;
    uint8_t manual_override = ((x_raw > JOY_CENTER + DEADZONE || x_raw < JOY_CENTER - DEADZONE) ||
                   (y_raw > JOY_CENTER + DEADZONE || y_raw < JOY_CENTER - DEADZONE));
    uint8_t ir_blocked = (IR_GetState() == IR_STATE_BLOCKED_REVERSE);

    // 4. 安全仲裁逻辑
    if (ir_blocked)
    {
      // 【状态 A：红外强制接管】危险距离时优先后退，禁止摇杆继续前进
      IR_Apply_Safety_Override(&dac_x, &dac_y);
    }
    else if (manual_override)
    {
        // 【状态 A：人工接管】直接透传原生 ADC 值到 DAC
        dac_x = x_raw;
        dac_y = y_raw;
    }
    else
    {
        // 【状态 B：语音控制】基于 (档位系数 * 避障限速系数) 线性缩放
        uint16_t current_dev = (uint16_t)(MAX_DEV * speed_ratio * ir_speed_limit);
        if (current_dev > MAX_DEV) {
          current_dev = MAX_DEV;
        }
        if (current_dev > (JOY_CENTER - 1U)) {
          current_dev = (JOY_CENTER - 1U);
        }

        switch (pi_command)
        {
            case 'F': // 前进
                dac_x = JOY_CENTER; 
                dac_y = JOY_CENTER - current_dev; 
                break;

            case 'B': // 后退
                dac_x = JOY_CENTER; 
                dac_y = JOY_CENTER + current_dev; 
                break;

            case 'L': // 左转
                dac_x = JOY_CENTER - current_dev; 
                dac_y = JOY_CENTER; 
                break;

            case 'R': // 右转
                dac_x = JOY_CENTER + current_dev; 
                dac_y = JOY_CENTER; 
                break;

            case 'S': // 停止
            default:
                dac_x = JOY_CENTER; 
                dac_y = JOY_CENTER; 
                break;
        }
    }

      // 统一输出钳位，确保最终写入 DAC 的值始终落在安全边界内
      dac_x = clamp_u12_safe(dac_x);
      dac_y = clamp_u12_safe(dac_y);

    // 执行 DAC 输出
    HAL_DAC_SetValue(&hdac, DAC_CHANNEL_1, DAC_ALIGN_12B_R, dac_x);
    HAL_DAC_SetValue(&hdac, DAC_CHANNEL_2, DAC_ALIGN_12B_R, dac_y);

    // --- 修改调试打印 ---
    if (HAL_UART_GetState(&huart1) == HAL_UART_STATE_READY)
    {
      int len = sprintf(uart_buf, "G:%u IR:%d%% IRS:%s | CMD:%c | ADC(X:%u, Y:%u, L:%u, R:%u) | DAC(X:%u, Y:%u)\r\n", 
        current_gear, (int)(ir_speed_limit * 100), IR_GetStateString(), pi_command, x_raw, y_raw, ir_left, ir_right, dac_x, dac_y);
        HAL_UART_Transmit(&huart1, (uint8_t*)uart_buf, len, 10);
    }

    HAL_Delay(50);

  }
  /* USER CODE END 3 */
}

/**
  * @brief System Clock Configuration
  * @retval None
  */
void SystemClock_Config(void)
{
  RCC_OscInitTypeDef RCC_OscInitStruct = {0};
  RCC_ClkInitTypeDef RCC_ClkInitStruct = {0};

  /** Configure the main internal regulator output voltage
  */
  __HAL_RCC_PWR_CLK_ENABLE();
  __HAL_PWR_VOLTAGESCALING_CONFIG(PWR_REGULATOR_VOLTAGE_SCALE1);

  /** Initializes the RCC Oscillators according to the specified parameters
  * in the RCC_OscInitTypeDef structure.
  */
  RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSE;
  RCC_OscInitStruct.HSEState = RCC_HSE_ON;
  RCC_OscInitStruct.PLL.PLLState = RCC_PLL_ON;
  RCC_OscInitStruct.PLL.PLLSource = RCC_PLLSOURCE_HSE;
  RCC_OscInitStruct.PLL.PLLM = 4;
  RCC_OscInitStruct.PLL.PLLN = 168;
  RCC_OscInitStruct.PLL.PLLP = RCC_PLLP_DIV2;
  RCC_OscInitStruct.PLL.PLLQ = 4;
  if (HAL_RCC_OscConfig(&RCC_OscInitStruct) != HAL_OK)
  {
    Error_Handler();
  }

  /** Initializes the CPU, AHB and APB buses clocks
  */
  RCC_ClkInitStruct.ClockType = RCC_CLOCKTYPE_HCLK|RCC_CLOCKTYPE_SYSCLK
                              |RCC_CLOCKTYPE_PCLK1|RCC_CLOCKTYPE_PCLK2;
  RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_PLLCLK;
  RCC_ClkInitStruct.AHBCLKDivider = RCC_SYSCLK_DIV1;
  RCC_ClkInitStruct.APB1CLKDivider = RCC_HCLK_DIV4;
  RCC_ClkInitStruct.APB2CLKDivider = RCC_HCLK_DIV2;

  if (HAL_RCC_ClockConfig(&RCC_ClkInitStruct, FLASH_LATENCY_5) != HAL_OK)
  {
    Error_Handler();
  }
}

/* USER CODE BEGIN 4 */

// UART 接收完成回调函数
void HAL_UART_RxCpltCallback(UART_HandleTypeDef *huart)
{
    if (huart->Instance == USART2)
    {
        char cmd = rx_buffer[0];

        // --- 【加减速逻辑】 ---
        if (cmd == 'D') // Decelerate (减速/降档)
        {
            if (current_gear > 1) {
                current_gear--; // 降一档
            }
            // 如果已经是 1档，就不动了
        }
        else if (cmd == 'A') // Accelerate (加速/升档)
        {
            if (current_gear < 3) {
                current_gear++; // 升一档
            }
            // 如果已经是 3档，就不动了
        }
        
        // --- 【运动指令逻辑】 ---
        // 只有 F, B, L, R, S 才会改变运动状态
        else if (cmd == 'F' || cmd == 'B' || cmd == 'L' || cmd == 'R' || cmd == 'S') 
        {
            pi_command = cmd;
        }

        // --- 【统一更新速度系数】 ---
        // 根据当前的档位，刷新 speed_ratio
        switch (current_gear)
        {
            case 1: speed_ratio = 0.3f; break; // 1档: 30%
            case 2: speed_ratio = 0.6f; break; // 2档: 60%
            case 3: speed_ratio = 1.0f; break; // 3档: 100%
        }

        // 重新开启中断
        HAL_UART_Receive_IT(&huart2, rx_buffer, 1);
    }
}

/* USER CODE END 4 */

/**
  * @brief  This function is executed in case of error occurrence.
  * @retval None
  */
void Error_Handler(void)
{
  /* USER CODE BEGIN Error_Handler_Debug */
  /* User can add his own implementation to report the HAL error return state */
  __disable_irq();
  while (1)
  {
  }
  /* USER CODE END Error_Handler_Debug */
}
#ifdef USE_FULL_ASSERT
/**
  * @brief  Reports the name of the source file and the source line number
  *         where the assert_param error has occurred.
  * @param  file: pointer to the source file name
  * @param  line: assert_param error line source number
  * @retval None
  */
void assert_failed(uint8_t *file, uint32_t line)
{
  /* USER CODE BEGIN 6 */
  /* User can add his own implementation to report the file name and line number,
     ex: printf("Wrong parameters value: file %s on line %d\r\n", file, line) */
  /* USER CODE END 6 */
}
#endif /* USE_FULL_ASSERT */
