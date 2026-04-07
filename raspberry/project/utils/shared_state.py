#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
共享状态模块
"""

import threading

# 系统激活状态
SYSTEM_ACTIVE = False
system_active_lock = threading.Lock()

# 模式切换相关
MODE_VOICE = "voice"
MODE_HEAD = "head"
current_mode = MODE_VOICE          # 默认语音模式
mode_lock = threading.Lock()
