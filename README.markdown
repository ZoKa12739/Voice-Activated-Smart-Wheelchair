# Voice-Activated Smart Wheelchair / 基于语音识别的智能轮椅

## Project Overview / 项目概况
This project develops a voice-activated smart wheelchair to enhance mobility for the elderly and disabled. It integrates optimized voice recognition, noise reduction, and dialect support to enable safe, autonomous travel, improving users' independence and social engagement.

本项目研发一款基于语音识别的智能轮椅，旨在提升老年人和残障人士的出行能力。项目集成了优化的语音识别、降噪和方言支持技术，实现安全、自主的出行，提升用户独立性和社会参与度。

## Features / 功能
- **Voice Control**: Supports simple commands like "go," "stop," "left," "right" with feedback.  
  **语音控制**：支持“走”、“停”、“左”、“右”等简单指令，并提供语音反馈。
- **Noise Reduction**: Enhances recognition in noisy environments.  
  **降噪技术**：提升嘈杂环境下的语音识别准确率。
- **Obstacle Detection**: Uses ultrasonic sensors for safe navigation.  
  **障碍检测**：使用超声波传感器确保安全导航。
- **Dual Control**: Seamlessly switches between voice and manual control.  
  **双重控制**：语音与手动控制无缝切换。
- **Local Processing**: Lightweight voice recognition model runs offline.  
  **本地处理**：轻量化语音识别模型支持离线运行。

## Installation / 安装
1. Clone the repository: `git clone [repo-url](https://github.com/ZoKa12739/Voice-Activated-Smart-Wheelchair.git)`  
   克隆仓库：`git clone [仓库地址](https://github.com/ZoKa12739/Voice-Activated-Smart-Wheelchair.git)`
2. Install dependencies: Python 3.8+, TensorFlow, Arduino IDE.  
   安装依赖：Python 3.8+、TensorFlow、Arduino IDE。
3. Upload motor control code to Arduino Mega2560.  
   将电机控制代码上传至 Arduino Mega2560。
4. Run the voice recognition module on Raspberry Pi or PC.  
   在树莓派或PC上运行语音识别模块。

## Usage / 使用
1. Power on the wheelchair and connect the voice module.  
   启动轮椅并连接语音模块。
2. Issue voice commands (e.g., "go forward" / “前进”).  
   发出语音指令（如“前进”）。
3. Switch to manual control if needed via joystick.  
   如需手动控制，可通过摇杆切换。
4. Monitor feedback for successful command execution.  
   监控语音反馈以确认指令执行。

## Project Structure / 项目结构
- `/src/voice_recognition`: Voice processing and recognition code.  
  `/src/voice_recognition`：语音处理与识别代码。
- `/src/motor_control`: Arduino code for motor control.  
  `/src/motor_control`：Arduino电机控制代码。
- `/src/communication`: Serial and wireless communication modules.  
  `/src/communication`：串口与无线通信模块。
- `/docs`: Project documentation and test reports.  
  `/docs`：项目文档与测试报告。

## Hardware Requirements / 硬件要求
- Arduino Mega2560  
- Raspberry Pi (for voice processing)  
- Ultrasonic sensors  
- Microphone array  
- Motors and power module  
- 树莓派（用于语音处理）  
- 超声波传感器  
- 麦克风阵列  
- 电机与电源模块  

## Future Work / 未来工作
- Enhance dialect and natural language support.  
  增强方言和自然语言支持。
- Integrate IoT for remote monitoring.  
  集成物联网实现远程监控。
- Optimize power efficiency and system stability.  
  优化能耗与系统稳定性。

## Team / 团队
- Wenjie Liu (Development & Testing / 开发与测试)  
- Ziyuan Bao (Embedded Systems / 嵌入式系统开发)  
- Kunyang Zhai (Algorithm Programming / 算法编程)  
- Zhihao Sun (Project Leader / 项目负责人)  
- Mingyang Wang (Hardware Platform / 硬件平台)  

## License / 许可证
MIT License
