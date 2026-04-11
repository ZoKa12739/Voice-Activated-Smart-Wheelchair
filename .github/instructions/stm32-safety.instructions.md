---
description: "Use when editing STM32 firmware, UART command handling, motor control, braking logic, or joystick override logic in this wheelchair project. Enforces safety-first embedded coding and verification rules."
name: "STM32 Safety-First Firmware Rules"
applyTo: "stm32/WheelchairControl/**/*.c, stm32/WheelchairControl/**/*.h"
---
# STM32 Safety-First Firmware Rules

- Treat safety logic as highest priority: manual joystick override should preempt remote or AI commands.
- Preserve stop behavior quality. Parsing failures, timeouts, or unknown UART commands should fall back to safe stop behavior.
- Keep compatibility for existing control characters (`F`, `B`, `L`, `R`, `S`, `A`, `D`). New commands may be added, but should remain backward-compatible.
- For movement-related code changes, keep bounded speed levels and avoid unbounded acceleration paths.
- Prefer non-blocking control flow in real-time paths; avoid long delays inside loops that affect control responsiveness.
- Keep ISR work minimal. Move heavy logic outside interrupts and protect shared state safely.
- When changing thresholds or gains, document rationale and expected effects in concise comments near constants.
- Avoid mixing unrelated refactors with safety-critical edits.
- Add or update verification notes in PR/commit context: happy path, invalid command input, and emergency stop behavior.

## Change Checklist

- Confirm manual override still interrupts autonomous/remote motion immediately.
- Confirm `S` (stop) command behavior is unchanged or intentionally improved.
- Confirm unknown/garbled UART input does not produce motion.
- Confirm no new blocking delay harms control loop timing.
