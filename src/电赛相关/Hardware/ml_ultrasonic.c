#include "ml_ultrasonic.h"

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
                     GPIOn_enum echo_gpio, Pinx_enum echo_pin)
{
    gpio_init(trig_gpio, trig_pin, OUT_PP);  // 触发信号为输出
    gpio_init(echo_gpio, echo_pin, IU);      // 回声信号为输入
    
    gpio_set(trig_gpio, trig_pin, 0);        // 初始化触发信号为低电平
}

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
                              GPIOn_enum echo_gpio, Pinx_enum echo_pin)
{
    uint32_t time_us = 0;
    float distance = 0;
    
    // 发送触发信号（至少10us高电平）
    gpio_set(trig_gpio, trig_pin, 1);        // 设置为高电平
    delay_us(15);                            // 延时15us
    gpio_set(trig_gpio, trig_pin, 0);        // 设置为低电平
    
    // 等待回波信号
    while(gpio_get(echo_gpio, echo_pin) == 0); // 等待回波信号变为高电平
    
    // 测量高电平持续时间
    time_us = 0;
    while(gpio_get(echo_gpio, echo_pin) == 1)
    {
        delay_us(1);     // 延时1us
        time_us++;       // 计数
        
        if(time_us > 30000)  // 超时检测（约5m距离限制）
            return -1;    // 返回错误距离
    }
    
    // 计算距离：声速340m/s，来回路程，单位换算为cm
    // 距离 = 时间 * 声速 / 2
    // 距离(cm) = 时间(us) * 0.034 / 2 = 时间(us) * 0.017
    distance = time_us * 0.017f;
    
    return distance;
}