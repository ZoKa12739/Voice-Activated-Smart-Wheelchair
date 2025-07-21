#include "ml_buzzer.h"

//-------------------------------------------------------------------------------------------------------------------
// @brief		初始化有源蜂鸣器
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		active_mode	选择触发方式（高电平有效或低电平有效）
// @return		void
// Sample usage:		buzzer_active_init(GPIO_A, Pin_4, BUZZER_LOW_ACTIVE);  // 初始化PA4为低电平有效蜂鸣器
//-------------------------------------------------------------------------------------------------------------------
void buzzer_active_init(GPIOn_enum gpio, Pinx_enum pin, BUZZER_ACTIVE_enum active_mode)
{
    gpio_init(gpio, pin, OUT_PP);  // 配置GPIO为推挽输出
    
    // 根据触发方式设置初始状态为不鸣响
    if (active_mode == BUZZER_HIGH_ACTIVE)
        gpio_set(gpio, pin, 0);    // 高电平有效，初始设为低电平
    else
        gpio_set(gpio, pin, 1);    // 低电平有效，初始设为高电平
}

//-------------------------------------------------------------------------------------------------------------------
// @brief		控制有源蜂鸣器
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		state		控制状态：1为鸣响，0为停止
// @param		active_mode	选择触发方式（高电平有效或低电平有效）
// @return		void
// Sample usage:		buzzer_active_control(GPIO_A, Pin_4, 1, BUZZER_LOW_ACTIVE);  // 使蜂鸣器鸣响
//-------------------------------------------------------------------------------------------------------------------
void buzzer_active_control(GPIOn_enum gpio, Pinx_enum pin, uint8_t state, BUZZER_ACTIVE_enum active_mode)
{
    if (active_mode == BUZZER_HIGH_ACTIVE)
        gpio_set(gpio, pin, state);          // 高电平有效，直接设置
    else
        gpio_set(gpio, pin, !state);         // 低电平有效，需要取反
}

//-------------------------------------------------------------------------------------------------------------------
// @brief		有源蜂鸣器短鸣一次
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		time_ms		鸣响持续时间(ms)
// @param		active_mode	选择触发方式（高电平有效或低电平有效）
// @return		void
// Sample usage:		buzzer_active_beep_once(GPIO_A, Pin_4, 200, BUZZER_LOW_ACTIVE);  // 蜂鸣器鸣响200ms
//-------------------------------------------------------------------------------------------------------------------
void buzzer_active_beep_once(GPIOn_enum gpio, Pinx_enum pin, uint16_t time_ms, BUZZER_ACTIVE_enum active_mode)
{
    buzzer_active_control(gpio, pin, 1, active_mode);  // 打开蜂鸣器
    delay_ms(time_ms);                                // 持续指定时间
    buzzer_active_control(gpio, pin, 0, active_mode);  // 关闭蜂鸣器
}

//-------------------------------------------------------------------------------------------------------------------
// @brief		有源蜂鸣器间歇鸣响
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		on_time		单次鸣响持续时间(ms)
// @param		off_time	鸣响间隔时间(ms)
// @param		times		鸣响次数
// @param		active_mode	选择触发方式（高电平有效或低电平有效）
// @return		void
// Sample usage:		buzzer_active_beep_times(GPIO_A, Pin_4, 100, 100, 3, BUZZER_LOW_ACTIVE);  // 蜂鸣器鸣响3次，每次100ms，间隔100ms
//-------------------------------------------------------------------------------------------------------------------
void buzzer_active_beep_times(GPIOn_enum gpio, Pinx_enum pin, uint16_t on_time, uint16_t off_time, uint8_t times, BUZZER_ACTIVE_enum active_mode)
{
    for (uint8_t i = 0; i < times; i++)
    {
        buzzer_active_control(gpio, pin, 1, active_mode);  // 打开蜂鸣器
        delay_ms(on_time);                                // 持续on_time时间
        buzzer_active_control(gpio, pin, 0, active_mode);  // 关闭蜂鸣器
        
        if (i < times - 1)  // 如果不是最后一次
            delay_ms(off_time);             // 等待off_time时间
    }
}

//-------------------------------------------------------------------------------------------------------------------
// @brief		有源蜂鸣器发出SOS紧急信号（3短-3长-3短）
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		active_mode	选择触发方式（高电平有效或低电平有效）
// @return		void
// Sample usage:		buzzer_active_sos(GPIO_A, Pin_4, BUZZER_LOW_ACTIVE);  // 蜂鸣器发出SOS紧急信号
//-------------------------------------------------------------------------------------------------------------------
void buzzer_active_sos(GPIOn_enum gpio, Pinx_enum pin, BUZZER_ACTIVE_enum active_mode)
{
    // 3短声
    for (uint8_t i = 0; i < 3; i++) {
        buzzer_active_control(gpio, pin, 1, active_mode);
        delay_ms(200);
        buzzer_active_control(gpio, pin, 0, active_mode);
        delay_ms(200);
    }
    
    delay_ms(300);  // 短暂停顿
    
    // 3长声
    for (uint8_t i = 0; i < 3; i++) {
        buzzer_active_control(gpio, pin, 1, active_mode);
        delay_ms(500);
        buzzer_active_control(gpio, pin, 0, active_mode);
        delay_ms(200);
    }
    
    delay_ms(300);  // 短暂停顿
    
    // 3短声
    for (uint8_t i = 0; i < 3; i++) {
        buzzer_active_control(gpio, pin, 1, active_mode);
        delay_ms(200);
        buzzer_active_control(gpio, pin, 0, active_mode);
        delay_ms(200);
    }
}