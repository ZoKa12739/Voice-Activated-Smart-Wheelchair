# Infrared Obstacle Avoidance Integration - Findings

## Hardware Requirements
- **Sensors**: 2x Infrared Distance Sensors (Analog output).
- **Placement**: One on the left side, one on the right side of the wheelchair.

## STM32 Pin Mapping (Finalized)
- **Joystick X/Y**: PA0, PA1 (ADC1_IN0, ADC1_IN1)
- **Left IR Sensor**: PA6 (ADC1_IN6)
- **Right IR Sensor**: PA7 (ADC1_IN7)
- *Note*: Rank order: IN0 -> IN1 -> IN6 -> IN7.

## Integration Principles
- **Hard Safety**: Logic resides on STM32. No Raspberry Pi integration for the core braking loop.
- **Immediate Hard Stop**: Priority 0. If distance < StopThreshold, force DAC to 2048.
- **Proportional Slowdown**: Priority 1. If StopThreshold < distance < WarningThreshold, scale `speed_ratio`.
