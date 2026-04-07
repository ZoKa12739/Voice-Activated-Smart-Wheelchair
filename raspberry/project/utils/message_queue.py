#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
消息队列模块
"""

import queue
import threading
from enum import Enum


class MessageType(Enum):
    """消息类型"""
    CONTROL_COMMAND = "control_command"  # 控制指令
    HEARTBEAT_DATA = "heartbeat_data"    # 心跳数据
    SYSTEM_STATUS = "system_status"      # 系统状态


class Message:
    """消息类"""
    def __init__(self, msg_type, data):
        self.msg_type = msg_type
        self.data = data


class MessageQueue:
    """消息队列类"""
    def __init__(self, maxsize=100):
        self.queue = queue.Queue(maxsize=maxsize)
        self.lock = threading.Lock()

    def put(self, msg_type, data):
        """放入消息"""
        msg = Message(msg_type, data)
        with self.lock:
            try:
                self.queue.put(msg, block=False)
                return True
            except queue.Full:
                return False

    def get(self, block=True, timeout=None):
        """获取消息"""
        with self.lock:
            try:
                return self.queue.get(block=block, timeout=timeout)
            except queue.Empty:
                return None

    def qsize(self):
        """获取队列大小"""
        with self.lock:
            return self.queue.qsize()

    def empty(self):
        """检查队列是否为空"""
        with self.lock:
            return self.queue.empty()


# 全局消息队列实例
msg_queue = MessageQueue()
