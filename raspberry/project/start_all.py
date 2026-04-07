#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
启动所有模块
"""

import sys
import os
import time

# 添加当前目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from serial_controller import SerialController
from heartbeat_sensor import HeartbeatSensor
from integrated_control import IntegratedControl
from onenet_control import OneNetControl
from utils.logger import get_logger

logger = get_logger(__name__)


def main():
    """主函数"""
    logger.info("开始启动所有模块")
    
    # 创建模块实例
    serial_controller = SerialController()
    heartbeat_sensor = HeartbeatSensor()
    integrated_control = IntegratedControl()
    onenet_control = OneNetControl()
    
    # 启动模块（顺序很重要）
    logger.info("启动串口控制模块")
    serial_controller.start()
    time.sleep(2)
    
    logger.info("启动心跳检测模块")
    heartbeat_sensor.start()
    time.sleep(2)
    
    logger.info("启动集成控制模块")
    integrated_control.start()
    time.sleep(2)
    
    logger.info("启动OneNet控制模块")
    onenet_control.start()
    time.sleep(2)
    
    logger.info("所有模块启动完成")
    logger.info("系统已就绪，按 Ctrl+C 退出")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("收到中断信号，正在停止所有模块...")
        
        # 停止模块（顺序相反）
        onenet_control.stop()
        integrated_control.stop()
        heartbeat_sensor.stop()
        serial_controller.stop()
        
        logger.info("所有模块已停止")


if __name__ == "__main__":
    main()
