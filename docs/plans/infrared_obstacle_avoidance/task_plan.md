# Infrared Obstacle Avoidance - Task Plan

## Phase 1: Hardware & Signal Calibration
- [ ] Configure PA6 and PA7 as ADC channels in `MX_ADC1_Init()`.
- [ ] Measure sensor output voltage vs distance to calibrate `StopThreshold` and `WarningThreshold`.
- [ ] Implement DMA multi-channel sampling for PA0, PA1 (Joystick) and PA6, PA7 (IR).

## Phase 2: Core Safety Driver
- [ ] Implement a safe-stop macro that resets DAC outputs to 2048 regardless of Pi/User input.
- [ ] Add IR distance filtering (e.g., Moving Average) to prevent jitter from sunlight or reflections.

## Phase 3: Control Logic Integration
- [ ] Update movement logic: Check IR status BEFORE applying `pi_command` or `adc_values`.
- [ ] Implement proportional speed reduction: `speed_ratio = map(distance, Warning, Stop, 1.0, 0.0)`.
- [ ] ENSURE manual override can still move backward if a forward obstacle is detected (Directional safety).

## Phase 4: Verification (Hardware Stress Test)
- [ ] Verify hard stop happens < 20ms upon sudden obstacle entry.
- [ ] Verify wheelchair slows down smoothly when approaching a wall.
- [ ] Confirm Pi UART commands are effectively ignored during hard-stop trigger.
