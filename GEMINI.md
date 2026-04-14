# Gemini Project Context: Raspberry Smart Wheelchair

This project is a Multi-modal Smart Voice-Controlled Wheelchair System designed for individuals with mobility impairments. It follows a "Sense-Cloud-Control" tri-layer architecture, splitting high-level AI tasks and low-level real-time control between a Raspberry Pi and an STM32 microcontroller.

## 🏗️ System Architecture

### 1. Perception & Intelligence Layer (Raspberry Pi 4B)
- **Voice Control (`vosk_v2.py`)**: Uses the `Vosk` offline engine for speech-to-text. Implements a fuzzy matching algorithm using `pypinyin`.
- **Vision Control (`Pi_opencv/`)**: A C++/Qt application running `YOLOv11n` for head pose detection.
- **Safety & Health Monitoring**: 暂定目标MKB0908连接到树莓派上提供数据，并可通过小程序查看.
- **Cloud Integration (`onenet_mqtt_final.py`)**: China Mobile OneNET via MQTT.

### 2. Execution & Control Layer (STM32F407)
- **Motor Drive**: Located in `stm32/WheelchairControl/`. DAC-emulated joystick control.
- **Manual Override**: Physical joystick monitoring via ADC. Highest priority.
- **Hard-Safety Logic**: Independent STM32 braking and proportional slowdown logic.
- **Symmetric Control**: Standardized 0~3.3V range with `JOY_CENTER` at 2048 and `MAX_DEV` at 2000.

### 3. User Interaction Layer (uni-app)
- **WeChat Mini-Program (`weixin_app/`)**: Remote control, speed adjustment, and health status.

---

## ⚠️ STM32CubeMX & AI Interaction Rules (DECOUPLING MANDATE)

To prevent code loss and maintain architectural elegance, ALL development MUST follow these rules:

1. **Hardware Configuration (Manual GUI)**: 
   - Pin mapping, clock trees, and peripheral initialization (UART, DMA, I2C, etc.) MUST be adjusted manually by the user in the CubeMX GUI. 
   - AI acts as an **advisor**, providing parameters (Baud rates, modes, interrupt priorities).
2. **Business Logic (AI Decoupling)**: 
   - Data parsing, filtering algorithms, and control logic are the AI's responsibility.
   - **Modular Drivers**: AI MUST create independent `.c` and `.h` files for new features (e.g., `mkb0908_driver.c`, `ir_avoidance.c`) rather than bloating `main.c`.
   - **Main.c as Scheduler**: `main.c` should only include headers in `USER CODE BEGIN Includes` and call processing functions in `USER CODE BEGIN While`.
3. **The "USER CODE" Boundary**: Any logic inside CubeMX-generated files MUST stay within `/* USER CODE BEGIN ... */` and `/* USER CODE END ... */`.

### 📋 Division of Labor

| Task Category | Primary Operator | AI's Role |
|:---|:---|:---|
| **Peripheral Config** (UART/DMA/ADC) | **User** (CubeMX GUI) | Suggest configuration parameters and init sequences. |
| **Interrupt Handlers** | **AI** (USER CODE) | Implement efficient ring-buffer or DMA callback logic. |
| **Logic/Algorithms** | **AI** (Modular Files) | Build the "Soul": PID, filtering, and safety arbitration. |
| **System Scheduling** | **AI** (main.c blocks) | Orchestrate function calls and timing in the main loop. |

---

## 📂 Key Directory Structure

- `/raspberry`: Intelligence modules (Voice, MQTT, Vision).
- `/stm32/WheelchairControl`: STM32CubeMX + Keil project.
- `/docs`: Documentation and Manus-style plans.

---

## 🌐 Communication & Planning Conventions (Manus-style)

1. **Block-Style Bilingual Requirement**: All clarifying questions, status updates, and critical warnings **MUST** be presented in both Chinese and English using a **Block-Style**. 
   - **Chinese Block First**: Provide the complete Chinese explanation first.
   - **English Block Second**: Follow immediately with the full English translation.
   - **Avoid Interleaving**: Do not mix languages line-by-line.
2. **Mandatory Reading**: Any sections the user is required to read or verify must follow this block-style bilingual format.

## 💡 General Development Conventions
- **Safety First**: Bottom-layer manual override always takes precedence.
- **AI/Hardware Separation**: High-compute on Pi, deterministic hardware on STM32.
- **Fuzzy Mapping**: Update `command_config` in `vosk_v2.py` for new voice commands.
