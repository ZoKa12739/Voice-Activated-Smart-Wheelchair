#ifndef _ml_buzzer_h
#define _ml_buzzer_h
#include "headfile.h"

// 蜂鸣器类型枚举
typedef enum {
    BUZZER_ACTIVE,    // 有源蜂鸣器（只需GPIO控制）
    BUZZER_PASSIVE,   // 无源蜂鸣器（需要PWM控制）
} BUZZER_TYPE_enum;

// 蜂鸣器触发方式
typedef enum {
    BUZZER_HIGH_ACTIVE,  // 高电平有效
    BUZZER_LOW_ACTIVE,   // 低电平有效
} BUZZER_ACTIVE_enum;

// ===== 有源蜂鸣器函数 =====

//-------------------------------------------------------------------------------------------------------------------
// @brief		初始化有源蜂鸣器
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		active_mode	选择触发方式（高电平有效或低电平有效）
// @return		void
// Sample usage:		buzzer_active_init(GPIO_A, Pin_4, BUZZER_LOW_ACTIVE);  // 初始化PA4为低电平有效蜂鸣器
//-------------------------------------------------------------------------------------------------------------------
void buzzer_active_init(GPIOn_enum gpio, Pinx_enum pin, BUZZER_ACTIVE_enum active_mode);

//-------------------------------------------------------------------------------------------------------------------
// @brief		控制有源蜂鸣器
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		state		控制状态：1为鸣响，0为停止
// @param		active_mode	选择触发方式（高电平有效或低电平有效）
// @return		void
// Sample usage:		buzzer_active_control(GPIO_A, Pin_4, 1, BUZZER_LOW_ACTIVE);  // 使蜂鸣器鸣响
//-------------------------------------------------------------------------------------------------------------------
void buzzer_active_control(GPIOn_enum gpio, Pinx_enum pin, uint8_t state, BUZZER_ACTIVE_enum active_mode);

//-------------------------------------------------------------------------------------------------------------------
// @brief		有源蜂鸣器短鸣一次
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		time_ms		鸣响持续时间(ms)
// @param		active_mode	选择触发方式（高电平有效或低电平有效）
// @return		void
// Sample usage:		buzzer_active_beep_once(GPIO_A, Pin_4, 200, BUZZER_LOW_ACTIVE);  // 蜂鸣器鸣响200ms
//-------------------------------------------------------------------------------------------------------------------
void buzzer_active_beep_once(GPIOn_enum gpio, Pinx_enum pin, uint16_t time_ms, BUZZER_ACTIVE_enum active_mode);

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
void buzzer_active_beep_times(GPIOn_enum gpio, Pinx_enum pin, uint16_t on_time, uint16_t off_time, uint8_t times, BUZZER_ACTIVE_enum active_mode);

//-------------------------------------------------------------------------------------------------------------------
// @brief		有源蜂鸣器发出SOS紧急信号（3短-3长-3短）
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		active_mode	选择触发方式（高电平有效或低电平有效）
// @return		void
// Sample usage:		buzzer_active_sos(GPIO_A, Pin_4, BUZZER_LOW_ACTIVE);  // 蜂鸣器发出SOS紧急信号
//-------------------------------------------------------------------------------------------------------------------
void buzzer_active_sos(GPIOn_enum gpio, Pinx_enum pin, BUZZER_ACTIVE_enum active_mode);

// ===== 无源蜂鸣器函数 =====

//-------------------------------------------------------------------------------------------------------------------
// @brief		初始化无源蜂鸣器
// @param		tim		    选择定时器
// @param		tim_ch		选择定时器通道
// @return		void
// Sample usage:		buzzer_passive_init(TIM_2, TIM2_CH1);  // 初始化TIM2的CH1通道为无源蜂鸣器
//-------------------------------------------------------------------------------------------------------------------
void buzzer_passive_init(TIMn_enum tim, TIMn_CHn_enum tim_ch);

//-------------------------------------------------------------------------------------------------------------------
// @brief		控制无源蜂鸣器频率
// @param		tim		    选择定时器
// @param		tim_ch		选择定时器通道
// @param		freq		设置频率(Hz)
// @param		duty		设置占空比(0~50000)
// @return		void
// Sample usage:		buzzer_passive_control(TIM_2, TIM2_CH1, 1000, 25000);  // 设置频率为1KHz，50%占空比
//-------------------------------------------------------------------------------------------------------------------
void buzzer_passive_control(TIMn_enum tim, TIMn_CHn_enum tim_ch, uint16_t freq, uint16_t duty);

//-------------------------------------------------------------------------------------------------------------------
// @brief		蜂鸣器发声一段时间后停止
// @param		tim		    选择定时器
// @param		tim_ch		选择定时器通道
// @param		freq		设置频率(Hz)
// @param		duty		设置占空比(0~50000)
// @param		time_ms		持续时间(ms)
// @return		void
// Sample usage:		buzzer_beep(TIM_2, TIM2_CH1, 1000, 25000, 200);  // 1KHz频率发声200ms
//-------------------------------------------------------------------------------------------------------------------
void buzzer_beep(TIMn_enum tim, TIMn_CHn_enum tim_ch, uint16_t freq, uint16_t duty, uint16_t time_ms);

// 音符定义
#define NOTE_C4  262
#define NOTE_CS4 277
// ... 其他音符定义保持不变
#define NOTE_C6  1047

//-------------------------------------------------------------------------------------------------------------------
// @brief		简单音乐播放
// @param		tim		    选择定时器
// @param		tim_ch		选择定时器通道
// @param		melody		音符数组指针
// @param		durations	时值数组指针
// @param		length		音符数量
// @return		void
// Sample usage:		buzzer_play_melody(TIM_2, TIM2_CH1, melody, durations, sizeof(melody)/sizeof(melody[0]));
//-------------------------------------------------------------------------------------------------------------------
void buzzer_play_melody(TIMn_enum tim, TIMn_CHn_enum tim_ch, const uint16_t *melody, const uint8_t *durations, uint8_t length);

//-------------------------------------------------------------------------------------------------------------------
// @brief		播放生日快乐歌
// @param		tim		    选择定时器
// @param		tim_ch		选择定时器通道
// @return		void
// Sample usage:		buzzer_play_happy_birthday(TIM_2, TIM2_CH1);  // 播放生日快乐歌
//-------------------------------------------------------------------------------------------------------------------
void buzzer_play_happy_birthday(TIMn_enum tim, TIMn_CHn_enum tim_ch);

#endif