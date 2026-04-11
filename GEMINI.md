# Gemini Project Context: Raspberry Smart Wheelchair

This project is a Multi-modal Smart Voice-Controlled Wheelchair System designed for individuals with mobility impairments. It follows a "Sense-Cloud-Control" tri-layer architecture, splitting high-level AI tasks and low-level real-time control between a Raspberry Pi and an STM32 microcontroller.

## 🏗️ System Architecture

### 1. Perception & Intelligence Layer (Raspberry Pi 4B)
- **Voice Control (`vosk_v2.py`)**: Uses the `Vosk` offline engine for speech-to-text. Implements a fuzzy matching algorithm using `pypinyin` to handle accents and dialects (e.g., mapping "钱进" to "前进").
- **Vision Control (`Pi_opencv/`)**: A C++/Qt application running `YOLOv11n` for head pose detection (`up`, `down`, `left`, `right`, `front`). It translates poses into movement commands.
- **Safety & Health Monitoring**: Integration of the MKB0908 Physiological Module (UART) and Dual Infrared Obstacle Avoidance (Analog) for real-time heart rate monitoring, hand-off detection, and proximity braking.
- **Cloud Integration (`onenet_mqtt_final.py`)**: Connects to the China Mobile OneNET platform via MQTT for remote monitoring and control.

### 2. Execution & Control Layer (STM32F407)
- **Motor Drive**: Located in `stm32/WheelchairControl/`. It receives UART commands (`F`, `B`, `L`, `R`, `S`, `A`, `D`) and outputs analog voltages via DAC to emulate a physical joystick.
- **Manual Override**: The STM32 continuously monitors the physical joystick via ADC. If manual movement is detected, it overrides AI/Voice commands for safety.
- **Hard-Safety Logic**:
    - **Infrared Braking**: Independent STM32-level logic that forces a hard stop (DAC to 2048) if obstacles are too close, and reduces speed proportionally for distant obstacles.
    - **Symmetric Control**: Standardized 0~3.3V range with `JOY_CENTER` at 2048 and `MAX_DEV` at 2000 for symmetric motor control.
- **Safety Features**: Includes speed gear management (3 levels) and logic for safe braking.

### 3. User Interaction Layer (uni-app)
- **WeChat Mini-Program (`weixin_app/`)**: Developed with `uni-app`, providing a remote control interface, speed adjustment, and real-time status viewing (Health data, Direction).

---

## ⚠️ STM32CubeMX & AI Interaction Rules (CRITICAL)

To prevent code loss during STM32CubeMX regeneration, **ALL AI-generated code MUST strictly follow these hardware-software decoupling constraints**:

1. **The "USER CODE" Boundary**: Any AI-generated logic injected into CubeMX-generated files (e.g., `main.c`, `stm32f4xx_it.c`, `usart.c`) **MUST** be placed exclusively between `/* USER CODE BEGIN ... */` and `/* USER CODE END ... */` tags. Modifications outside these blocks are strictly forbidden.
2. **Hardware Configuration**: AI must NOT modify hardware initialization parameters (e.g., `MX_GPIO_Init`, clock trees). If a hardware configuration change is required (e.g., enabling a new UART or DMA channel), AI must instruct the user to perform the configuration via the STM32CubeMX GUI.
3. **Modular Driver Design**: For complex algorithms or new peripheral parsing (such as the MKB0908 sensor), AI must create independent driver files (e.g., `mkb0908_driver.c` and `mkb0908_driver.h`) rather than piling logic into `main.c`. `main.c` should only serve as a high-level logic scheduler and function caller.

---

## 📂 Key Directory Structure

- `/raspberry`: Core intelligence modules.
    - `vosk_v2.py`: Main voice recognition script.
    - `onenet_mqtt_final.py`: IoT cloud communication.
    - `Pi_opencv/`: C++/Qt vision project (requires OpenCV & ONNX Runtime).
    - `weixin_app/`: Source code for the WeChat Mini-program.
- `/stm32/WheelchairControl`: STM32CubeMX + Keil project for the motor controller.
- `/docs`: Documentation, including the `Defense_Guide.md` with technical insights.

---

## 🛠️ Development & Deployment

### Raspberry Pi (Python)
- **Environment**: Python 3.9+
- **Dependencies**: `vosk`, `pypinyin`, `paho-mqtt`, `pyserial`, `pyaudio`.
- **Run**: 
  ```bash
  python3 raspberry/vosk_v2.py
  python3 raspberry/onenet_mqtt_final.py
  ```

### Raspberry Pi (C++/Qt Vision)
- **Environment**: Qt 5.15+, OpenCV 4.8.0.
- **Build**: 
  ```bash
  cd raspberry/Pi_opencv
  qmake Pi_opencv.pro
  make
  sudo ./OpenCV_CameraMonitor
  ```

### STM32 (C)
- **Environment**: Keil uVision5 or STM32CubeIDE.
- **UART Config**: 115200 baud, 8N1. Connected to Raspberry Pi via `USART2`.

---

## 📡 Communication Protocol (UART)

| Character | Command | Description |
|-----------|---------|-------------|
| `F`       | Forward | Move forward |
| `B`       | Backward| Move backward |
| `L`       | Left    | Turn left |
| `R`       | Right   | Turn right |
| `S`       | Stop    | Stop all movement |
| `A`       | Accel   | Increase speed gear |
| `D`       | Decel   | Decrease speed gear |

---

## 🌐 Communication & Planning Conventions (Manus-style)

To ensure clarity and documentation quality, the following rules apply when executing multi-step tasks or critical safety updates:
1. **Block-Style Bilingual Requirement**: All clarifying questions, status updates, and critical warnings **MUST** be presented in both Chinese and English using a **Block-Style**. 
   - **Chinese Block First**: Provide the complete Chinese explanation first to ensure a smooth reading experience.
   - **English Block Second**: Follow immediately with the full English translation for technical verification and term cross-referencing.
   - **Avoid Interleaving**: Do not mix languages line-by-line.
2. **Mandatory Reading**: Any sections the user is required to read or verify (e.g., Plan summaries, Hardware safety checks) must follow this block-style bilingual format.

## 💡 General Development Conventions
- **Safety First**: Bottom-layer (STM32) manual override always takes precedence over top-layer (Pi) commands.
- **AI/Hardware Separation**: Keep high-compute AI logic (Python/C++) on the Pi and time-critical, deterministic hardware control on the STM32.
- **Fuzzy Mapping**: When adding new voice commands, update the `command_config` dictionary in `vosk_v2.py` with pypinyin aliases.
