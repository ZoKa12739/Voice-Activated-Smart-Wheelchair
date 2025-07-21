#ifndef _ml_ultrasonic_h
#define _ml_ultrasonic_h
#include "headfile.h"

//-------------------------------------------------------------------------------------------------------------------
// @brief		超声波模块初始化
// @param		trig_gpio	选择触发信号的GPIO引脚
// @param		trig_pin	选择触发信号的引脚号
// @param		echo_gpio	选择回波信号的GPIO引脚
// @param		echo_pin	选择回波信号的引脚号
// @return		void
// Sample usage:		ultrasonic_init(GPIO_A, Pin_1, GPIO_A, Pin_2);  // 初始化PA1为触发信号，PA2为回波信号
//-------------------------------------------------------------------------------------------------------------------
void ultrasonic_init(GPIOn_enum trig_gpio, Pinx_enum trig_pin, 
                     GPIOn_enum echo_gpio, Pinx_enum echo_pin);

//-------------------------------------------------------------------------------------------------------------------
// @brief		获取超声波测距结果
// @param		trig_gpio	选择触发信号的GPIO引脚
// @param		trig_pin	选择触发信号的引脚号
// @param		echo_gpio	选择回波信号的GPIO引脚
// @param		echo_pin	选择回波信号的引脚号
// @return		float       返回测量距离，单位为厘米(cm)，如果测量超时返回-1
// Sample usage:		distance = ultrasonic_get_distance(GPIO_A, Pin_1, GPIO_A, Pin_2);
//-------------------------------------------------------------------------------------------------------------------
float ultrasonic_get_distance(GPIOn_enum trig_gpio, Pinx_enum trig_pin, 
                              GPIOn_enum echo_gpio, Pinx_enum echo_pin);

#endif