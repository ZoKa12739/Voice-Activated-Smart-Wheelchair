/**
  ******************************************************************************
  * @file           : ir_avoidance.c
  * @brief          : Infrared obstacle avoidance logic implementation.
  ******************************************************************************
  */
#include "ir_avoidance.h"

static uint8_t is_blocked = 0; // 0: 正常, 1: 强制停机
static uint8_t block_enter_ticks = 0;
static uint8_t release_clear_ticks = 0;
static uint8_t reverse_ticks = 0;
static uint8_t blocked_hold_ticks = 0;
static uint8_t fault_suppress_ticks = 0;
static IR_Side_t blocked_side = IR_SIDE_NONE;

/**
  * @brief 初始化避障模块
  */
void IR_Avoidance_Init(void) {
  is_blocked = 0;
  block_enter_ticks = 0;
  release_clear_ticks = 0;
  reverse_ticks = 0;
  blocked_hold_ticks = 0;
  fault_suppress_ticks = 0;
  blocked_side = IR_SIDE_NONE;
}

/**
  * @brief 处理红外数据，返回推荐的速度系数 (0.0 - 1.0)
  * @param left_raw 左侧红外 ADC 原始值
  * @param right_raw 右侧红外 ADC 原始值
  */
float IR_Avoidance_Process(uint16_t left_raw, uint16_t right_raw) {
  uint16_t nearest_val = (left_raw < right_raw) ? left_raw : right_raw;
  float ratio = 1.0f;
  uint8_t left_enter = (left_raw <= IR_STOP_ENTER_THRESHOLD_LEFT);
  uint8_t right_enter = (right_raw <= IR_STOP_ENTER_THRESHOLD_RIGHT);

  if (fault_suppress_ticks > 0) {
    fault_suppress_ticks--;
    return 1.0f;
  }

  if (reverse_ticks > 0) {
    reverse_ticks--;
    blocked_hold_ticks++;
    if (blocked_hold_ticks >= IR_BLOCK_FAULT_TIMEOUT_TICKS) {
      is_blocked = 0;
      block_enter_ticks = 0;
      release_clear_ticks = 0;
      reverse_ticks = 0;
      blocked_hold_ticks = 0;
      fault_suppress_ticks = IR_FAULT_SUPPRESS_TICKS;
      blocked_side = IR_SIDE_NONE;
      return 1.0f;
    }
    return 0.0f;
  }

  // 1. 阻塞结束后的恢复判定：清障连续稳定后才允许重新进入正常控制。
  if (is_blocked) {
    uint8_t still_blocked_by_sensor;

    if (blocked_side == IR_SIDE_LEFT) {
      still_blocked_by_sensor = (left_raw <= IR_STOP_EXIT_THRESHOLD_LEFT);
    } else if (blocked_side == IR_SIDE_RIGHT) {
      still_blocked_by_sensor = (right_raw <= IR_STOP_EXIT_THRESHOLD_RIGHT);
    } else {
      still_blocked_by_sensor = ((left_raw <= IR_STOP_EXIT_THRESHOLD_LEFT) ||
                                 (right_raw <= IR_STOP_EXIT_THRESHOLD_RIGHT));
    }

    blocked_hold_ticks++;
    if (blocked_hold_ticks >= IR_BLOCK_FAULT_TIMEOUT_TICKS) {
      is_blocked = 0;
      block_enter_ticks = 0;
      release_clear_ticks = 0;
      blocked_hold_ticks = 0;
      fault_suppress_ticks = IR_FAULT_SUPPRESS_TICKS;
      blocked_side = IR_SIDE_NONE;
      return 1.0f;
    }

    if (still_blocked_by_sensor) {
      release_clear_ticks = 0;
      return 0.0f;
    }

    release_clear_ticks++;
    if (release_clear_ticks < IR_RELEASE_DEBOUNCE_TICKS) {
      return 0.0f;
    }

    is_blocked = 0;
    block_enter_ticks = 0;
    release_clear_ticks = 0;
    blocked_hold_ticks = 0;
      blocked_side = IR_SIDE_NONE;
  }

  // 2. 强制后退判断 (距离极近，连续命中后才进入阻塞)
  if (left_enter || right_enter) {
    if (block_enter_ticks < 255) {
      block_enter_ticks++;
    }

    if (block_enter_ticks >= IR_ENTER_DEBOUNCE_TICKS) {
      if (left_enter && right_enter) {
        blocked_side = IR_SIDE_BOTH;
      } else if (left_enter) {
        blocked_side = IR_SIDE_LEFT;
      } else {
        blocked_side = IR_SIDE_RIGHT;
      }

      is_blocked = 1;
      block_enter_ticks = 0;
      release_clear_ticks = 0;
      reverse_ticks = IR_REVERSE_DURATION_TICKS;
      blocked_hold_ticks = 0;
    }

    return 0.0f;
  }

  block_enter_ticks = 0;

  // 3. 减速判断 (进入预警区)
  if (nearest_val < IR_WARNING_THRESHOLD) {
    // 线性映射：WARNING(1.0) -> STOP_ENTER(0.0)
    ratio = (float)(nearest_val - IR_STOP_ENTER_THRESHOLD) /
        (IR_WARNING_THRESHOLD - IR_STOP_ENTER_THRESHOLD);
    if (ratio < IR_MIN_CRAWL_RATIO) ratio = IR_MIN_CRAWL_RATIO;
    }

    return ratio;
}

/**
  * @brief 执行硬安全覆盖，直接修改 DAC 目标值
  */
void IR_Apply_Safety_Override(uint16_t *dac_val_x, uint16_t *dac_val_y) {
  if (is_blocked) {
    if (blocked_side == IR_SIDE_LEFT) {
      *dac_val_x = IR_OVERRIDE_X_VALUE + IR_OVERRIDE_X_BIAS;
    } else if (blocked_side == IR_SIDE_RIGHT) {
      *dac_val_x = IR_OVERRIDE_X_VALUE - IR_OVERRIDE_X_BIAS;
    } else {
      *dac_val_x = IR_OVERRIDE_X_VALUE;
    }
    *dac_val_y = IR_OVERRIDE_Y_VALUE;
    return;
  }
}

IR_State_t IR_GetState(void) {
  if (is_blocked) {
    return IR_STATE_BLOCKED_REVERSE;
  }

  if (fault_suppress_ticks > 0) {
    return IR_STATE_FAULT_BYPASS;
  }

  return IR_STATE_NORMAL;
}

IR_Side_t IR_GetBlockedSide(void) {
  return blocked_side;
}

const char* IR_GetStateString(void) {
  switch (IR_GetState()) {
    case IR_STATE_BLOCKED_REVERSE:
      switch (IR_GetBlockedSide()) {
        case IR_SIDE_LEFT:
          return "LREV";
        case IR_SIDE_RIGHT:
          return "RREV";
        case IR_SIDE_BOTH:
          return "BREV";
        case IR_SIDE_NONE:
        default:
          return "REV";
      }
    case IR_STATE_FAULT_BYPASS:
      return "FLT";
    case IR_STATE_NORMAL:
    default:
      return "NRM";
  }
}
