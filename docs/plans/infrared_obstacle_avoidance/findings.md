# Infrared Obstacle Avoidance Integration - Findings

## Hardware Requirements
- **Sensors**: 2x Infrared Distance Sensors (Analog output recommended).
- **Placement**: One on the left side, one on the right side of the wheelchair.

## STM32 Pin Mapping (Finalized)
- **Left IR Sensor**: PA6 (ADC1_IN6)
- **Right IR Sensor**: PA7 (ADC1_IN7)
- *Rationale*: Allows proportional distance detection for deceleration logic.

## Integration Principles
- **Hard Safety (Highest Priority)**: Resides entirely on STM32. Raspberry Pi integration is forbidden for this safety loop to prevent OS-level lag or crashes from affecting braking.
- **Behavior 1: Immediate Hard Stop**: If obstacle distance < StopThreshold, force DAC output to 2048 (Center/Stop) immediately.
- **Behavior 2: Distant Deceleration**: If StopThreshold < distance < WarningThreshold, scale down `speed_ratio` proportionally.
