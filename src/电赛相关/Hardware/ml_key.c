#include "ml_key.h"

//-------------------------------------------------------------------------------------------------------------------
// @brief		按键初始化
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		mode		选择按键模式（上拉或下拉）
// @return		void
// Sample usage:		key_init(GPIO_A, Pin_0, KEY_PULL_UP);  // 初始化PA0为上拉输入按键
//-------------------------------------------------------------------------------------------------------------------
void key_init(GPIOn_enum gpio, Pinx_enum pin, KEY_MODE_enum mode)
{
    if (mode == KEY_PULL_UP)
        gpio_init(gpio, pin, IU);  // 上拉输入
    else
        gpio_init(gpio, pin, ID);  // 下拉输入
}

//-------------------------------------------------------------------------------------------------------------------
// @brief		读取按键状态（带消抖）
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		mode		选择按键模式（上拉或下拉）
// @return		KEY_STATE_enum  返回按键状态：KEY_PRESS(按下) 或 KEY_RELEASE(释放)
// Sample usage:		if(key_read(GPIO_A, Pin_0, KEY_PULL_UP) == KEY_PRESS) { ... }
//-------------------------------------------------------------------------------------------------------------------
KEY_STATE_enum key_read(GPIOn_enum gpio, Pinx_enum pin, KEY_MODE_enum mode)
{
    KEY_STATE_enum key_state;
    
    if (mode == KEY_PULL_UP)
    {
        if (gpio_get(gpio, pin) == 0)  // 按下按键为低电平
            key_state = KEY_PRESS;
        else
            key_state = KEY_RELEASE;
    }
    else
    {
        if (gpio_get(gpio, pin) == 1)  // 按下按键为高电平
            key_state = KEY_PRESS;
        else
            key_state = KEY_RELEASE;
    }
    
    // 消抖
    if (key_state == KEY_PRESS)
    {
        delay_ms(10);  // 延时消抖
        
        if (mode == KEY_PULL_UP)
        {
            if (gpio_get(gpio, pin) == 0)  // 再次确认为低电平
                return KEY_PRESS;
            else
                return KEY_RELEASE;
        }
        else
        {
            if (gpio_get(gpio, pin) == 1)  // 再次确认为高电平
                return KEY_PRESS;
            else
                return KEY_RELEASE;
        }
    }
    
    return key_state;
}

//-------------------------------------------------------------------------------------------------------------------
// @brief		按键扫描函数（单次按下有效，避免重复触发）
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		mode		选择按键模式（上拉或下拉）
// @return		KEY_STATE_enum  返回按键状态：KEY_PRESS(按下) 或 KEY_RELEASE(释放)
// Sample usage:		if(key_scan(GPIO_A, Pin_0, KEY_PULL_UP) == KEY_PRESS) { ... } // 按键按下后执行一次
//-------------------------------------------------------------------------------------------------------------------
KEY_STATE_enum key_scan(GPIOn_enum gpio, Pinx_enum pin, KEY_MODE_enum mode)
{
    static uint8_t key_up = 1;  // 按键松开标志
    
    if (key_read(gpio, pin, mode) == KEY_PRESS)
    {
        if (key_up)  // 之前是松开状态
        {
            key_up = 0;
            return KEY_PRESS;
        }
    }
    else
    {
        key_up = 1;  // 标记按键松开
    }
    
    return KEY_RELEASE;
}