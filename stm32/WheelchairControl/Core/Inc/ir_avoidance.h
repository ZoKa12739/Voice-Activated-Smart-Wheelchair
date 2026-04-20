/**
  ******************************************************************************
  * @file           : ir_avoidance.h
  * @brief          : Header for infrared obstacle avoidance module.
  ******************************************************************************
  */
#ifndef __IR_AVOIDANCE_H
#define __IR_AVOIDANCE_H

#include "main.h"

typedef enum {
  IR_STATE_NORMAL = 0,
  IR_STATE_BLOCKED_REVERSE,
  IR_STATE_FAULT_BYPASS,
} IR_State_t;

typedef enum {
  IR_SIDE_NONE = 0,
  IR_SIDE_LEFT,
  IR_SIDE_RIGHT,
  IR_SIDE_BOTH,
} IR_Side_t;

/*
 * 阈值定义 (ADC 采样值 0-4095)
 * 基于当前实测：障碍靠近时 ADC 变小（约 1000），无遮挡时更大（约 2900-3900）。
 */
// 左右传感器独立阈值：左侧当前实测偏高，适当上调进入阈值以保证触发一致性
#define IR_STOP_ENTER_THRESHOLD_LEFT  1400 // 左侧进入强制后退阈值
#define IR_STOP_ENTER_THRESHOLD_RIGHT 1200  // 右侧进入强制后退阈值
#define IR_STOP_EXIT_THRESHOLD_LEFT   1520  // 左侧退出阈值(含滞回)
#define IR_STOP_EXIT_THRESHOLD_RIGHT  1400  // 右侧退出阈值(含滞回)
// 兼容减速线性映射，取更严格一侧作为全局下界
#define IR_STOP_ENTER_THRESHOLD       IR_STOP_ENTER_THRESHOLD_RIGHT
#define IR_STOP_EXIT_THRESHOLD        IR_STOP_EXIT_THRESHOLD_RIGHT
#define IR_WARNING_THRESHOLD    2600  // 开始减速阈值(进入预警区)
#define IR_MIN_CRAWL_RATIO      0.2f  // 预警区最低爬行速度
#define IR_ENTER_DEBOUNCE_TICKS 2     // 进入阻塞需连续命中次数(50ms循环下约100ms)
#define IR_RELEASE_DEBOUNCE_TICKS 3    // 连续清障样本数(50ms循环下约150ms)
#define IR_REVERSE_DURATION_TICKS 40   // 反向持续时长(50ms循环下约2s)
#define IR_BLOCK_FAULT_TIMEOUT_TICKS 60 // 阻塞持续过久视为故障(50ms循环下约3s)
#define IR_FAULT_SUPPRESS_TICKS 100    // 故障后暂时屏蔽红外(50ms循环下约5s)

/* 红外触发后的安全动作：后退 2s，然后恢复正常控制 */
#define IR_OVERRIDE_X_VALUE      2048  // X 归中，保持直线
#define IR_OVERRIDE_Y_VALUE      3048   // Y 后退到安全值，避免直接拉到 0 引发溢出
#define IR_OVERRIDE_X_BIAS       260    // 根据障碍侧向反向偏置，帮助避让

/* 接口函数 */
void IR_Avoidance_Init(void);
float IR_Avoidance_Process(uint16_t left_raw, uint16_t right_raw);
void IR_Apply_Safety_Override(uint16_t *dac_val_x, uint16_t *dac_val_y);
IR_State_t IR_GetState(void);
IR_Side_t IR_GetBlockedSide(void);
const char* IR_GetStateString(void);

#endif /* __IR_AVOIDANCE_H */
