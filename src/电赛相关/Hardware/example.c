#include "headfile.h"
#include "ml_key.h"
#include "ml_ultrasonic.h"
#include "ml_buzzer.h"
#include "ml_led.h"

// 示例函数，避免与main.c中的main函数冲突
void example_demo(void)
{
    // 初始化系统时钟
    SystemInit();
    
    // 初始化按键 (PA0)
    key_init(GPIO_A, Pin_0, KEY_PULL_UP);
    
    // 初始化超声波 (Trig-PA1, Echo-PA2)
    ultrasonic_init(GPIO_A, Pin_1, GPIO_A, Pin_2);
    
    // 初始化有源蜂鸣器 (PA4)，设置为低电平有效
    buzzer_active_init(GPIO_A, Pin_4, BUZZER_LOW_ACTIVE);
    
    // 初始化LED (PA3, 低电平点亮)
    led_init(GPIO_A, Pin_3, LED_LOW_ON);
    
    // 初始化OLED显示
    OLED_Init();
    OLED_Clear();
    OLED_ShowString(1, 1, "STM32 Test");
    
    float distance = 0;
    
    while (1)
    {
        // 检测按键按下
        if (key_scan(GPIO_A, Pin_0, KEY_PULL_UP) == KEY_PRESS)
        {
            // 按键按下，蜂鸣器短暂鸣响作为反馈
            OLED_ShowString(2, 1, "Beep...     ");
            buzzer_active_control(GPIO_A, Pin_4, 1, BUZZER_LOW_ACTIVE);  // 打开蜂鸣器
            delay_ms(200);                                              // 持续200ms
            buzzer_active_control(GPIO_A, Pin_4, 0, BUZZER_LOW_ACTIVE);  // 关闭蜂鸣器
            OLED_ShowString(2, 1, "Beep End!   ");
        }
        
        // 测量距离
        distance = ultrasonic_get_distance(GPIO_A, Pin_1, GPIO_A, Pin_2);
        
        // 显示距离
        OLED_ShowString(3, 1, "Distance:");
        if (distance >= 0)
        {
            OLED_ShowFloat(3, 10, distance, 2, 1);
            OLED_ShowString(3, 14, "cm");
        }
        else
        {
            OLED_ShowString(3, 10, "Error");
        }
        
        // 距离小于10cm，LED闪烁，蜂鸣器报警
        if (distance >= 0 && distance < 10)
        {
            led_blink(GPIO_A, Pin_3, LED_LOW_ON, 100, 1);
            
            // 有源蜂鸣器间歇鸣响
            buzzer_active_beep_once(GPIO_A, Pin_4, 100, BUZZER_LOW_ACTIVE);
        }
        else
        {
            led_set(GPIO_A, Pin_3, LED_OFF, LED_LOW_ON);
        }
        
        delay_ms(200);
    }
}