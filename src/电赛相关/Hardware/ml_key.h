#ifndef _ml_key_h
#define _ml_key_h
#include "headfile.h"

// 按键模式枚举
typedef enum {
    KEY_PULL_UP,   // 上拉输入，按下为低电平
    KEY_PULL_DOWN, // 下拉输入，按下为高电平
} KEY_MODE_enum;

// 按键状态枚举
typedef enum {
    KEY_RELEASE,   // 按键释放
    KEY_PRESS,     // 按键按下
} KEY_STATE_enum;

//-------------------------------------------------------------------------------------------------------------------
// @brief		按键初始化
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		mode		选择按键模式（上拉或下拉）
// @return		void
// Sample usage:		key_init(GPIO_A, Pin_0, KEY_PULL_UP);  // 初始化PA0为上拉输入按键
//-------------------------------------------------------------------------------------------------------------------
void key_init(GPIOn_enum gpio, Pinx_enum pin, KEY_MODE_enum mode);

//-------------------------------------------------------------------------------------------------------------------
// @brief		读取按键状态（带消抖）
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		mode		选择按键模式（上拉或下拉）
// @return		KEY_STATE_enum  返回按键状态：KEY_PRESS(按下) 或 KEY_RELEASE(释放)
// Sample usage:		if(key_read(GPIO_A, Pin_0, KEY_PULL_UP) == KEY_PRESS) { ... }
//-------------------------------------------------------------------------------------------------------------------
KEY_STATE_enum key_read(GPIOn_enum gpio, Pinx_enum pin, KEY_MODE_enum mode);

//-------------------------------------------------------------------------------------------------------------------
// @brief		按键扫描函数（单次按下有效，避免重复触发）
// @param		gpio		选择GPIO引脚
// @param		pin		    选择引脚号
// @param		mode		选择按键模式（上拉或下拉）
// @return		KEY_STATE_enum  返回按键状态：KEY_PRESS(按下) 或 KEY_RELEASE(释放)
// Sample usage:		if(key_scan(GPIO_A, Pin_0, KEY_PULL_UP) == KEY_PRESS) { ... } // 按键按下后执行一次
//-------------------------------------------------------------------------------------------------------------------
KEY_STATE_enum key_scan(GPIOn_enum gpio, Pinx_enum pin, KEY_MODE_enum mode);

#endif