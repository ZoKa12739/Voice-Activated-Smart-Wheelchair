#ifndef _ml_led_h
#define _ml_led_h
#include "headfile.h"

// LED状态枚举
typedef enum {
    LED_OFF = 0,
    LED_ON = 1,
} LED_STATE_enum;

// LED连接方式枚举
typedef enum {
    LED_LOW_ON,    // 低电平点亮（接地）
    LED_HIGH_ON,   // 高电平点亮（接电源）
} LED_CONNECTION_enum;

//-------------------------------------------------------------------------------------------------------------------
// @brief		LED初始化
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		connection	选择LED连接方式（低电平点亮或高电平点亮）
// @return		void
// Sample usage:		led_init(GPIO_A, Pin_3, LED_LOW_ON);  // 初始化PA3为低电平点亮的LED
//-------------------------------------------------------------------------------------------------------------------
void led_init(GPIOn_enum gpio, Pinx_enum pin, LED_CONNECTION_enum connection);

//-------------------------------------------------------------------------------------------------------------------
// @brief		设置LED状态
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		state		设置LED状态：LED_ON(点亮) 或 LED_OFF(熄灭)
// @param		connection	选择LED连接方式（低电平点亮或高电平点亮）
// @return		void
// Sample usage:		led_set(GPIO_A, Pin_3, LED_ON, LED_LOW_ON);  // 点亮LED
//-------------------------------------------------------------------------------------------------------------------
void led_set(GPIOn_enum gpio, Pinx_enum pin, LED_STATE_enum state, LED_CONNECTION_enum connection);

//-------------------------------------------------------------------------------------------------------------------
// @brief		LED翻转（点亮变熄灭，熄灭变点亮）
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		connection	选择LED连接方式（低电平点亮或高电平点亮）
// @return		void
// Sample usage:		led_toggle(GPIO_A, Pin_3, LED_LOW_ON);  // 翻转LED状态
//-------------------------------------------------------------------------------------------------------------------
void led_toggle(GPIOn_enum gpio, Pinx_enum pin, LED_CONNECTION_enum connection);

//-------------------------------------------------------------------------------------------------------------------
// @brief		LED闪烁
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		connection	选择LED连接方式（低电平点亮或高电平点亮）
// @param		ms		    闪烁间隔时间(ms)
// @param		times		闪烁次数
// @return		void
// Sample usage:		led_blink(GPIO_A, Pin_3, LED_LOW_ON, 100, 3);  // LED闪烁3次，每次间隔100ms
//-------------------------------------------------------------------------------------------------------------------
void led_blink(GPIOn_enum gpio, Pinx_enum pin, LED_CONNECTION_enum connection, uint16_t ms, uint8_t times);

#endif