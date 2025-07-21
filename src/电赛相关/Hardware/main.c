#include "headfile.h"

extern void example_demo(void);

int main(void)
{
    SystemInit();
    example_demo();
    
    while(1) {
        // 保持循环或进入低功耗模式
    }
}