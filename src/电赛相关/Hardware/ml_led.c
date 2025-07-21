#include "ml_led.h"

//-------------------------------------------------------------------------------------------------------------------
// @brief		LED初始化
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		connection	选择LED连接方式（低电平点亮或高电平点亮）
// @return		void
// Sample usage:		led_init(GPIO_A, Pin_3, LED_LOW_ON);  // 初始化PA3为低电平点亮的LED
//-------------------------------------------------------------------------------------------------------------------
void led_init(GPIOn_enum gpio, Pinx_enum pin, LED_CONNECTION_enum connection)
{
    gpio_init(gpio, pin, OUT_PP);  // LED配置为推挽输出
    
    // 设置初始状态为熄灭
    if (connection == LED_LOW_ON)
        gpio_set(gpio, pin, 1);  // 低电平点亮，初始设为高电平
    else
        gpio_set(gpio, pin, 0);  // 高电平点亮，初始设为低电平
}

//-------------------------------------------------------------------------------------------------------------------
// @brief		设置LED状态
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		state		设置LED状态：LED_ON(点亮) 或 LED_OFF(熄灭)
// @param		connection	选择LED连接方式（低电平点亮或高电平点亮）
// @return		void
// Sample usage:		led_set(GPIO_A, Pin_3, LED_ON, LED_LOW_ON);  // 点亮LED
//-------------------------------------------------------------------------------------------------------------------
void led_set(GPIOn_enum gpio, Pinx_enum pin, LED_STATE_enum state, LED_CONNECTION_enum connection)
{
    if (connection == LED_LOW_ON)
        gpio_set(gpio, pin, !state);  // 低电平点亮，取反状态值
    else
        gpio_set(gpio, pin, state);   // 高电平点亮，直接使用状态值
}

//-------------------------------------------------------------------------------------------------------------------
// @brief		LED翻转（点亮变熄灭，熄灭变点亮）
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		connection	选择LED连接方式（低电平点亮或高电平点亮）
// @return		void
// Sample usage:		led_toggle(GPIO_A, Pin_3, LED_LOW_ON);  // 翻转LED状态
//-------------------------------------------------------------------------------------------------------------------
void led_toggle(GPIOn_enum gpio, Pinx_enum pin, LED_CONNECTION_enum connection)
{
    uint8_t current_state = gpio_get(gpio, pin);
    gpio_set(gpio, pin, !current_state);  // 当前状态取反
}

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
void led_blink(GPIOn_enum gpio, Pinx_enum pin, LED_CONNECTION_enum connection, uint16_t ms, uint8_t times)
{
    for (uint8_t i = 0; i < times; i++)
    {
        led_set(gpio, pin, LED_ON, connection);  // 点亮
        delay_ms(ms);
        led_set(gpio, pin, LED_OFF, connection); // 熄灭
        delay_ms(ms);
    }
}