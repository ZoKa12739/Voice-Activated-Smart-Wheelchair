# Infrared Obstacle Avoidance - Task Plan

## Phase 1: Hardware & Signal Calibration
- [x] Configure PA6 and PA7 as ADC channels in `MX_ADC1_Init()`.
- [x] Implement DMA multi-channel sampling for PA0, PA1 (Joystick) and PA6, PA7 (IR).
- [ ] Measure sensor output voltage vs distance to calibrate `StopThreshold` and `WarningThreshold`.

## Phase 2: Core Safety Driver
- [x] Implement a safe-stop macro that resets DAC outputs to 2048 regardless of Pi/User input.
- [x] Add IR distance filtering (Implemented as raw-value processing in `ir_avoidance.c`).

## Phase 3: Control Logic Integration
- [x] Update movement logic: Check IR status BEFORE applying `pi_command` or `adc_values`.
- [x] Implement proportional speed reduction: `speed_ratio` combined with `ir_speed_limit`.
- [x] ENSURE manual override still takes precedence (Handled via X/Y raw ADC priority).

## Phase 4: Verification (Hardware Stress Test)
- [ ] Verify hard stop happens < 20ms upon sudden obstacle entry.
- [ ] Verify wheelchair slows down smoothly when approaching a wall.
- [ ] Confirm Pi UART commands are effectively ignored during hard-stop trigger.
