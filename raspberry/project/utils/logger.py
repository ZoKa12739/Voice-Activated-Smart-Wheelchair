#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
日志工具模块
"""

import logging
import os
from config import LOG_LEVEL, LOG_FILE


def get_logger(name):
    """获取日志记录器"""
    logger = logging.getLogger(name)
    logger.setLevel(getattr(logging, LOG_LEVEL))

    # 确保日志目录存在
    log_dir = os.path.dirname(LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)

    # 创建文件处理器
    file_handler = logging.FileHandler(LOG_FILE)
    file_handler.setLevel(getattr(logging, LOG_LEVEL))

    # 创建控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(getattr(logging, LOG_LEVEL))

    # 设置格式化器
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)

    # 添加处理器
    if not logger.handlers:
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)

    return logger


# 全局日志记录器
logger = get_logger(__name__)
