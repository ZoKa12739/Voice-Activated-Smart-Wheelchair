#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
集成控制模块
将语音控制和头部姿态控制合并到一个模块中，确保状态同步
"""

import os
import time
import threading
import cv2
import numpy as np
import json
import pyaudio
from dataclasses import dataclass
from typing import List, Tuple, Optional
from vosk import Model, KaldiRecognizer
from config import VOICE_MODEL_PATH, YOLO_MODEL_PATH, CAMERA_ID, AUDIO_DIR
from utils.message_queue import msg_queue, MessageType
from utils.logger import get_logger

logger = get_logger(__name__)

# 系统激活状态
SYSTEM_ACTIVE = False
system_active_lock = threading.Lock()

# 模式切换相关
MODE_VOICE = "voice"
MODE_HEAD = "head"
current_mode = MODE_VOICE          # 默认语音模式
mode_lock = threading.Lock()

# 头部姿态检测常量
MODEL_INPUT_SIZE = 128
CLASSES = ["front", "left", "up", "right", "down"]
MODEL_SCORE_THRESHOLD = 0.45
MODEL_NMS_THRESHOLD = 0.50
LETTERBOX_FOR_SQUARE = True

# 语音识别常量
RMS_THRESHOLD_HIGH = 120
RMS_THRESHOLD_LOW = 60
CONFIRM_FRAMES = 2
SILENCE_FRAMES = 3

# 指令配置
command_config = {
    "前进": {
        "code": 'F',
        "voice": "前进",
        "pinyin": ["qian jin", "xiang qian", "wang qian"],
        "pinyin_no_tone": ["qian jin", "xiang qian", "wang qian"],
        "aliases": ["前进", "向前", "往前", "前近", "钱进"],
        "keywords": ["前", "进", "向", "往", "走"],
        "min_length": 2,
        "require_full": False
    },
    "后退": {
        "code": 'B',
        "voice": "后退",
        "pinyin": ["hou tui", "xiang hou", "wang hou"],
        "pinyin_no_tone": ["hou tui", "xiang hou", "wang hou"],
        "aliases": ["后退", "向后", "往后", "后推", "厚退"],
        "keywords": ["后", "退", "倒", "撤", "向"],
        "min_length": 2,
        "require_full": False
    },
    "向左": {
        "code": 'L',
        "voice": "左转",
        "pinyin": ["xiang zuo", "wang zuo", "zuo"],
        "pinyin_no_tone": ["xiang zuo", "wang zuo", "zuo"],
        "aliases": ["向左", "往左", "左转", "左"],
        "keywords": ["左", "向", "往", "转"],
        "min_length": 1,
        "require_full": False
    },
    "向右": {
        "code": 'R',
        "voice": "右转",
        "pinyin": ["xiang you", "wang you"],
        "pinyin_no_tone": ["xiang you", "wang you"],
        "aliases": ["向右", "往右", "右转", "右"],
        "keywords": ["右", "向", "往", "转"],
        "min_length": 1,
        "require_full": False
    },
    "停止": {
        "code": 'S',
        "voice": "停止",
        "pinyin": ["ting zhi", "ting", "zhan zhu"],
        "pinyin_no_tone": ["ting zhi", "ting", "zhan zhu"],
        "aliases": ["停止", "停", "站住", "停住"],
        "keywords": ["停", "止", "站"],
        "min_length": 1,
        "require_full": False
    },
    "加速": {
        "code": 'A',
        "voice": "加速",
        "pinyin": ["jia su", "kuai dian"],
        "pinyin_no_tone": ["jia su", "kuai dian"],
        "aliases": ["加速", "快点", "加速前进", "加速行驶"],
        "keywords": ["加", "速", "快"],
        "min_length": 2,
        "require_full": False
    },
    "减速": {
        "code": 'D',
        "voice": "减速",
        "pinyin": ["jian su", "man dian"],
        "pinyin_no_tone": ["jian su", "man dian"],
        "aliases": ["减速", "慢点", "减速行驶", "减速前进"],
        "keywords": ["减", "速", "慢"],
        "min_length": 2,
        "require_full": False
    },
    "关机": {
        "code": 'X',
        "voice": "关机",
        "pinyin": ["guan ji", "shutdown", "guan dian"],
        "pinyin_no_tone": ["guan ji", "shutdown", "guan dian"],
        "aliases": ["关机", "关闭", "关", "关机了", "关闭系统"],
        "keywords": ["关", "机", "闭"],
        "min_length": 1,
        "require_full": False
    },
    "开始": {
        "code": 'START',
        "voice": "启动",
        "pinyin": ["kai shi", "qi dong", "kai qi"],
        "pinyin_no_tone": ["kai shi", "qi dong", "kai qi"],
        "aliases": ["开始", "启动", "开启", "开", "还是", "海誓", "凯时", "开时", "开始系统"],
        "keywords": ["开", "始", "启", "动"],
        "min_length": 1,
        "require_full": False
    },
    "语音模式": {
        "code": "MODE_VOICE",
        "voice": "语音模式",
        "pinyin": ["yu yin mo shi", "yu yin"],
        "pinyin_no_tone": ["yu yin mo shi", "yu yin"],
        "aliases": ["语音模式", "语音", "声音模式", "声控模式"],
        "keywords": ["语", "音", "模式"],
        "min_length": 2,
        "require_full": False
    },
    "头部模式": {
        "code": "MODE_HEAD",
        "voice": "头部模式",
        "pinyin": ["tou bu mo shi", "tou bu"],
        "pinyin_no_tone": ["tou bu mo shi", "tou bu"],
        "aliases": ["头部模式", "头部", "头控模式", "头部控制"],
        "keywords": ["头", "部", "模式"],
        "min_length": 2,
        "require_full": False
    }
}

class VoiceFeedback:
    """语音反馈"""
    def __init__(self, audio_dir):
        self.audio_dir = audio_dir
        try:
            import pygame
            pygame.mixer.init()
            self.pygame = pygame
            self.enabled = True
            logger.info("语音反馈系统初始化成功")
        except Exception as e:
            logger.warning(f"语音反馈系统初始化失败: {e}")
            self.enabled = False
    def play_command_voice(self, command, code):
        """播放命令语音"""
        if not self.enabled:
            return
        try:
            if code == "MODE_VOICE":
                filename = os.path.join(self.audio_dir, "语音模式.mp3")
            elif code == "MODE_HEAD":
                filename = os.path.join(self.audio_dir, "头部模式.mp3")
            else:
                filename = os.path.join(self.audio_dir, f"{command}.mp3")
            if os.path.exists(filename):
                self.pygame.mixer.music.load(filename)
                self.pygame.mixer.music.play()
                logger.info(f"播放语音: {command}")
            else:
                logger.warning(f"语音文件缺失: {filename}")
        except Exception as e:
            logger.error(f"播放语音失败: {e}")
    def play_startup(self):
        """播放启动语音"""
        self.play_command_voice("启动", "START")
    def play_switch_mode(self, mode):
        """播放模式切换语音"""
        if mode == MODE_VOICE:
            self.play_command_voice("语音模式", "MODE_VOICE")
        elif mode == MODE_HEAD:
            self.play_command_voice("头部模式", "MODE_HEAD")

class AudioEnergyFilter:
    """音频能量过滤器"""
    def __init__(self):
        self.energy_history = []
        self.max_history = 10
        self.avg_energy = 0
    def update(self, audio_data):
        """更新音频能量"""
        energy = np.sqrt(np.mean(np.square(audio_data)))
        self.energy_history.append(energy)
        if len(self.energy_history) > self.max_history:
            self.energy_history.pop(0)
        self.avg_energy = np.mean(self.energy_history)
        return energy
    @property
    def triggered(self):
        """是否触发"""
        return self.avg_energy > RMS_THRESHOLD_HIGH

class CommandManager:
    """命令管理器"""
    def __init__(self):
        self.last_command = None
        self.last_command_time = 0
        self.last_command_text = ""
        self.command_count = 0
        self.GLOBAL_COOLDOWN = 1.0
        self.SAME_TEXT_THRESHOLD = 0.8
    def should_send(self, command_code, text="", is_same_speech_segment=False):
        """判断是否应该发送命令"""
        current_time = time.time()
        if is_same_speech_segment:
            return False, "同一语音段内已触发"
        if self.last_command == command_code:
            time_diff = current_time - self.last_command_time
            if time_diff < self.GLOBAL_COOLDOWN:
                return False, f"冷却中({time_diff:.2f}s)"
        if text and self.last_command_text:
            similarity = self.text_similarity(text, self.last_command_text)
            if similarity > self.SAME_TEXT_THRESHOLD:
                return False, f"文本相似({similarity:.2f})"
        return True, "可以发送"
    def text_similarity(self, text1, text2):
        """计算文本相似度"""
        if not text1 or not text2:
            return 0
        set1 = set(text1)
        set2 = set(text2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))
        return intersection / union if union > 0 else 0
    def record_sent(self, command_code, text=""):
        """记录已发送的命令"""
        self.last_command = command_code
        self.last_command_time = time.time()
        self.last_command_text = text
        self.command_count += 1

# 模式切换函数
def switch_mode(new_mode, voice_feedback=None):
    """切换模式"""
    global current_mode
    with mode_lock:
        if new_mode == current_mode:
            return
        # 发送停止指令
        msg_queue.put(MessageType.CONTROL_COMMAND, 'S')
        current_mode = new_mode
        logger.info(f"=== 切换到 {new_mode} 模式 ===")
        # 播放模式切换语音反馈
        if voice_feedback:
            voice_feedback.play_switch_mode(new_mode)

# 智能匹配函数
def smart_match(text, is_partial=False):
    """智能匹配指令"""
    if not text:
        return None, None, 0
    import re
    chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
    chinese_matches = chinese_pattern.findall(text)
    if not chinese_matches:
        return None, None, 0
    chinese_text = ''.join(chinese_matches)
    if len(chinese_text) < 1:
        return None, None, 0

    # 直接匹配别名
    for command, config in command_config.items():
        if len(chinese_text) < config.get("min_length", 1):
            continue
        if command in chinese_text:
            return command, config["code"], 1.0
        for alias in config["aliases"]:
            if alias in chinese_text:
                score = min(0.95, len(alias) / len(chinese_text) * 0.95)
                return command, config["code"], score

    # 关键词匹配
    best_match, best_code, best_score = None, None, 0
    for command, config in command_config.items():
        if len(chinese_text) < config.get("min_length", 1):
            continue
        keyword_score = 0
        for keyword in config["keywords"]:
            if keyword in chinese_text:
                keyword_score += 0.1
        if keyword_score > 0:
            match_score = min(0.8, keyword_score)
            if match_score > best_score:
                best_score = match_score
                best_match = command
                best_code = config["code"]

    return best_match, best_code, best_score

@dataclass
class Detection:
    """检测结果类"""
    class_id: int
    class_name: str
    confidence: float
    box: Tuple[int, int, int, int]  # x,y,w,h

def sigmoid(x: np.ndarray) -> np.ndarray:
    """sigmoid函数"""
    return 1.0 / (1.0 + np.exp(-x))

def format_to_square(img_bgr: np.ndarray) -> np.ndarray:
    """将图像填充为正方形（右下补黑）"""
    h, w = img_bgr.shape[:2]
    m = max(h, w)
    out = np.zeros((m, m, 3), dtype=img_bgr.dtype)
    out[0:h, 0:w] = img_bgr
    return out

class HeadPoseYoloOpenCV:
    """YOLOv11n 头部姿态检测（ONNX），支持方向死区调整"""
    def __init__(self, onnx_path: str, front_bias_threshold: float = 0.1):
        """
        :param front_bias_threshold: 当检测为左/右且与前方置信度差小于此值时，强制判为前方
        """
        self.net = cv2.dnn.readNetFromONNX(onnx_path)
        self.net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
        self.net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)
        try:
            cv2.setNumThreads(1)
        except Exception:
            pass
        self.front_bias_threshold = front_bias_threshold

    def infer(self, frame_bgr: np.ndarray) -> List[Detection]:
        """执行推理"""
        t0 = time.time()
        if frame_bgr is None or frame_bgr.size == 0:
            return []

        model_input = frame_bgr
        if LETTERBOX_FOR_SQUARE:
            model_input = format_to_square(model_input)

        blob = cv2.dnn.blobFromImage(
            model_input,
            scalefactor=1.0 / 255.0,
            size=(MODEL_INPUT_SIZE, MODEL_INPUT_SIZE),
            mean=(0, 0, 0),
            swapRB=True,
            crop=False
        )
        self.net.setInput(blob)
        out_names = self.net.getUnconnectedOutLayersNames()
        outs = self.net.forward(out_names)
        out0 = outs[0]

        if out0.ndim != 3 or out0.shape[0] != 1:
            raise RuntimeError(f"Unexpected output shape: {out0.shape}")

        rows = out0.shape[1]
        dims = out0.shape[2]
        if dims > rows:
            out2d = out0[0].T.astype(np.float32, copy=False)  # (336,9)
            rows, dims = out2d.shape
        else:
            out2d = out0[0].astype(np.float32, copy=False)

        x_factor = model_input.shape[1] / float(MODEL_INPUT_SIZE)
        y_factor = model_input.shape[0] / float(MODEL_INPUT_SIZE)

        boxes: List[List[int]] = []
        scores: List[float] = []
        class_ids: List[int] = []

        for i in range(rows):
            data = out2d[i]
            cls_logits = data[4:4 + len(CLASSES)]
            cls_scores = sigmoid(cls_logits)
            cid = int(np.argmax(cls_scores))
            max_score = float(cls_scores[cid])

            if max_score > MODEL_SCORE_THRESHOLD:
                # 增加方向死区容忍度
                # 如果最高分类是左或右，且与前方分数差小于阈值，则重新判为前方
                if CLASSES[cid] in ("left", "right"):
                    front_idx = CLASSES.index("front")
                    front_score = float(cls_scores[front_idx])
                    if front_score > 0 and (max_score - front_score) < self.front_bias_threshold:
                        cid = front_idx
                        max_score = front_score

                x, y, w, h = map(float, data[0:4])
                left = int((x - 0.5 * w) * x_factor)
                top = int((y - 0.5 * h) * y_factor)
                width = int(w * x_factor)
                height = int(h * y_factor)
                boxes.append([left, top, width, height])
                class_ids.append(cid)
                scores.append(max_score)

        idxs = cv2.dnn.NMSBoxes(
            bboxes=boxes,
            scores=scores,
            score_threshold=MODEL_SCORE_THRESHOLD,
            nms_threshold=MODEL_NMS_THRESHOLD
        )

        dets: List[Detection] = []
        if len(idxs) > 0:
            for idx in np.array(idxs).flatten().tolist():
                x, y, w, h = boxes[idx]
                cid = class_ids[idx]
                dets.append(Detection(
                    class_id=cid,
                    class_name=CLASSES[cid] if 0 <= cid < len(CLASSES) else "unknown",
                    confidence=float(scores[idx]),
                    box=(x, y, w, h)
                ))
        dt_ms = int((time.time() - t0) * 1000)
        logger.debug(f"YOLO推理耗时: {dt_ms} ms")
        return dets

def pick_best_detection(dets: List[Detection]) -> Optional[Detection]:
    """选择最佳检测结果"""
    return max(dets, key=lambda d: d.confidence) if dets else None

def pose_to_char(pose: str) -> str:
    """将姿态转换为控制字符"""
    if pose == "up":
        return "S"
    if pose == "down":
        return "B"
    if pose == "left":
        return "L"
    if pose == "right":
        return "R"
    if pose == "front":
        return "F"
    return "S"

class IntegratedControl:
    """集成控制"""
    def __init__(self):
        self.running = False
        self.voice_thread = None
        self.head_thread = None
        self.voice_feedback = VoiceFeedback(AUDIO_DIR)
        self.head_infer = None
        self.head_cap = None
    def voice_recognition_thread(self):
        """语音识别线程"""
        global SYSTEM_ACTIVE

        # 验证模型路径
        if not os.path.exists(VOICE_MODEL_PATH):
            logger.error(f"语音模型路径 '{VOICE_MODEL_PATH}' 不存在")
            return

        # 初始化 Vosk
        try:
            model = Model(VOICE_MODEL_PATH)
            logger.info("语音模型加载成功")
        except Exception as e:
            logger.error(f"模型加载失败: {e}")
            return

        recognizer = KaldiRecognizer(model, 16000)

        # 初始化 PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000,
                        input=True, frames_per_buffer=2048)
        stream.start_stream()

        # 状态变量
        local_system_active = False
        LAST_ACTIVE_TIME = 0
        ACTIVE_TIMEOUT = 60

        energy_filter = AudioEnergyFilter()
        CURRENT_SPEECH_SEGMENT = {
            "is_active": False,
            "has_triggered": False,
            "latest_text": "",
            "last_update_time": 0,
            "silence_threshold": 0.4
        }
        cmd_manager = CommandManager()
        recent_texts = []   # 用于防重复

        # 新增：记录最后一次部分结果触发指令的时间（用于去重）
        last_trigger_time = 0
        TRIGGER_COOLDOWN = 1.5 # 秒
        
        # 新增：记录特殊指令的最后触发时间
        last_special_command = {"command": None, "time": 0}
        SPECIAL_COMMAND_COOLDOWN = 1.5  # 特殊指令冷却时间1.5秒
        
        # 新增：语音检测时间限制
        MAX_DETECTION_TIME = 1.0  # 最大检测时间（秒）

        logger.info("语音识别线程已启动，等待语音指令...")

        try:
            while self.running:
                # 读取音频
                data = stream.read(2048, exception_on_overflow=False)
                if len(data) == 0:
                    continue

                audio_data = np.frombuffer(data, dtype=np.int16)
                energy_filter.update(audio_data)

                # 完整结果
                if recognizer.AcceptWaveform(data):
                    result = json.loads(recognizer.Result())
                    text = result.get('text', '').strip()
                    if text:
                        current_time = time.time()
                        logger.info(f"语音完整结果: '{text}'")

                        # 处理完整结果前，不重置标志，而是先判断是否需要忽略（避免与部分结果重复）
                        command, command_code, score = smart_match(text, is_partial=False)
                        if command and score > 0.5:
                            # 检查是否刚在部分结果中触发过指令（去重）
                            if current_time - last_trigger_time < TRIGGER_COOLDOWN:
                                logger.debug(f"完整结果在部分结果后 {current_time - last_trigger_time:.2f}s 内，忽略")
                            else:
                                # 特殊指令检查：检查是否在冷却时间内
                                is_special_command = command in ["关机", "开始"]
                                if is_special_command:
                                    if (command == last_special_command["command"] and 
                                        current_time - last_special_command["time"] < SPECIAL_COMMAND_COOLDOWN):
                                        logger.debug(f"特殊指令'{command}'冷却中，忽略")
                                        continue
                                    # 更新特殊指令触发时间
                                    last_special_command = {"command": command, "time": current_time}
                                
                                # 处理切换指令
                                if command_code == "MODE_VOICE":
                                    switch_mode(MODE_VOICE, self.voice_feedback)
                                elif command_code == "MODE_HEAD":
                                    switch_mode(MODE_HEAD, self.voice_feedback)
                                # 唤醒词
                                elif command == "开始":
                                    self.voice_feedback.play_startup()
                                    local_system_active = True
                                    LAST_ACTIVE_TIME = time.time()
                                    # 同步到全局
                                    with system_active_lock:
                                        SYSTEM_ACTIVE = True
                                    logger.info("系统已唤醒")
                                elif command == "关机":
                                    # 发送关机指令
                                    msg_queue.put(MessageType.CONTROL_COMMAND, 'X')
                                    # 播放关机语音
                                    self.voice_feedback.play_command_voice("关机", command_code)
                                    local_system_active = False
                                    # 同步到全局
                                    with system_active_lock:
                                        SYSTEM_ACTIVE = False
                                    logger.info("系统关闭")
                                elif local_system_active and command_code and current_mode == MODE_VOICE:
                                    # 普通控制指令（仅在语音模式下发送）
                                    msg_queue.put(MessageType.CONTROL_COMMAND, command_code)
                                    self.voice_feedback.play_command_voice(command, command_code)
                                    LAST_ACTIVE_TIME = time.time()

                # 部分结果（用于快速响应）
                else:
                    partial = json.loads(recognizer.PartialResult())
                    partial_text = partial.get('partial', '').strip()
                    if partial_text:
                        current_time = time.time()
                        
                        # 检查语音检测时间
                        if current_time - CURRENT_SPEECH_SEGMENT["last_update_time"] > MAX_DETECTION_TIME:
                            logger.debug("语音检测时间超过1秒，清空缓冲区")
                            # 重置状态
                            CURRENT_SPEECH_SEGMENT = {
                                "is_active": False,
                                "has_triggered": False,
                                "latest_text": "",
                                "last_update_time": current_time,
                                "silence_threshold": 0.4
                            }

                        CURRENT_SPEECH_SEGMENT["latest_text"] = partial_text
                        CURRENT_SPEECH_SEGMENT["last_update_time"] = current_time

                        # 智能匹配（针对部分结果）
                        command, command_code, score = smart_match(partial_text, is_partial=True)
                        if command and score > 0.7 and not CURRENT_SPEECH_SEGMENT["has_triggered"]:
                            # 特殊指令检查：检查是否在冷却时间内
                            is_special_command = command in ["关机", "开始"]
                            if is_special_command:
                                if (command == last_special_command["command"] and 
                                    current_time - last_special_command["time"] < SPECIAL_COMMAND_COOLDOWN):
                                    logger.debug(f"特殊指令'{command}'冷却中，忽略")
                                    continue
                                # 更新特殊指令触发时间
                                last_special_command = {"command": command, "time": current_time}
                            
                            # 处理切换指令
                            if command_code == "MODE_VOICE":
                                switch_mode(MODE_VOICE, self.voice_feedback)
                            elif command_code == "MODE_HEAD":
                                switch_mode(MODE_HEAD, self.voice_feedback)
                            # 唤醒词
                            elif command == "开始":
                                self.voice_feedback.play_startup()
                                local_system_active = True
                                LAST_ACTIVE_TIME = time.time()
                                # 同步到全局
                                with system_active_lock:
                                    SYSTEM_ACTIVE = True
                                logger.info("系统唤醒（部分结果）")
                                CURRENT_SPEECH_SEGMENT["has_triggered"] = True
                                last_trigger_time = current_time
                            # 关机指令
                            elif command == "关机":
                                # 发送关机指令
                                msg_queue.put(MessageType.CONTROL_COMMAND, 'X')
                                # 播放关机语音
                                self.voice_feedback.play_command_voice("关机", command_code)
                                local_system_active = False
                                # 同步到全局
                                with system_active_lock:
                                    SYSTEM_ACTIVE = False
                                logger.info("快速关机")
                                CURRENT_SPEECH_SEGMENT["has_triggered"] = True
                                last_trigger_time = current_time
                            # 普通控制指令（仅在语音模式下发送）
                            elif local_system_active and command_code and current_mode == MODE_VOICE:
                                # 检查命令是否应该发送
                                should_send, reason = cmd_manager.should_send(
                                    command_code, 
                                    partial_text, 
                                    is_same_speech_segment=CURRENT_SPEECH_SEGMENT["is_active"]
                                )
                                if should_send:
                                    # 快速发送指令
                                    msg_queue.put(MessageType.CONTROL_COMMAND, command_code)
                                    self.voice_feedback.play_command_voice(command, command_code)
                                    LAST_ACTIVE_TIME = time.time()
                                    cmd_manager.record_sent(command_code, partial_text)
                                    CURRENT_SPEECH_SEGMENT["has_triggered"] = True
                                    last_trigger_time = current_time
                                    logger.info(f"快速发送: {command_code}")

        except KeyboardInterrupt:
            logger.info("收到中断信号，正在退出...")
        except Exception as e:
            logger.error(f"语音识别错误: {e}")
        finally:
            stream.stop_stream()
            stream.close()
            p.terminate()
            logger.info("语音线程已退出")
    def head_pose_thread(self):
        """头部姿态检测线程"""
        self.running = True
        logger.info("头部姿态控制启动")

        # 初始化头部检测模型
        try:
            self.head_infer = HeadPoseYoloOpenCV(YOLO_MODEL_PATH, front_bias_threshold=0.1)
            logger.info("头部姿态模型加载成功")
        except Exception as e:
            logger.error(f"头部姿态模型加载失败: {e}")
            self.running = False
            return

        self.head_cap = None
        frame_counter = 0
        # 记录上一次的头部姿态，避免连续重复发送相同指令
        last_head_pose = None
        last_head_pose_time = 0
        HEAD_POSE_DEBOUNCE = 0.5  # 0.5秒内不重复发送相同姿态的指令
        
        logger.info("头部姿态控制就绪")

        try:
            while self.running:
                # 打开摄像头（如果未打开）
                if not self.head_cap or not self.head_cap.isOpened():
                    logger.info("尝试打开摄像头")
                    self.head_cap = cv2.VideoCapture(CAMERA_ID, cv2.CAP_V4L2)
                    if self.head_cap.isOpened():
                        self.head_cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
                        self.head_cap.set(cv2.CAP_PROP_FRAME_WIDTH, MODEL_INPUT_SIZE)
                        self.head_cap.set(cv2.CAP_PROP_FRAME_HEIGHT, int(MODEL_INPUT_SIZE * 3 / 4))
                        self.head_cap.set(cv2.CAP_PROP_FPS, 10)
                        self.head_cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
                        logger.info("摄像头打开成功")
                    else:
                        logger.warning("无法打开摄像头，将在3秒后重试")
                        time.sleep(3)
                        continue

                # 获取当前模式下的帧计数（每次循环都增加计数器）
                frame_counter += 1

                if frame_counter % 20 == 0:  # 每20帧检测一次
                    try:
                        # 检测帧：清空缓冲区，获取最新帧
                        # 连续 grab 两次，丢弃可能积压的旧帧（最多一帧）
                        self.head_cap.grab()   # 丢弃可能的旧帧
                        self.head_cap.grab()   # 再丢弃一帧，确保最新帧（若缓冲区空，第二次grab会等待新帧）
                        ok, frame = self.head_cap.retrieve()   # 获取最后一次 grab 的帧
                        if not ok:
                            # 如果 retrieve 失败，回退到直接 read
                            ok, frame = self.head_cap.read()
                        if ok:
                            # 执行头部检测
                            dets = self.head_infer.infer(frame)
                            best = pick_best_detection(dets)
                            # 检查当前模式和系统激活状态
                            with mode_lock:
                                mode = current_mode
                            with system_active_lock:
                                active = SYSTEM_ACTIVE
                            
                            if best is not None:
                                if mode == MODE_HEAD and active:
                                    current_time = time.time()
                                    cmd = pose_to_char(best.class_name)

                                    # 发送控制指令（防抖）
                                    if cmd != last_head_pose or (current_time - last_head_pose_time) > HEAD_POSE_DEBOUNCE:
                                        msg_queue.put(MessageType.CONTROL_COMMAND, cmd)
                                        last_head_pose = cmd
                                        last_head_pose_time = current_time
                                        logger.info(f"头部姿态发送: {cmd} ({best.class_name})")
                                else:
                                    # 系统未激活或不在头部模式，重置上一次姿态记录
                                    last_head_pose = None
                            else:
                                last_head_pose = None
                        else:
                            logger.warning("无法获取帧")
                    except Exception as e:
                        logger.error(f"读取摄像头失败: {e}")
                        # 关闭摄像头，下次循环会重新打开
                        if self.head_cap:
                            self.head_cap.release()
                            self.head_cap = None
                else:
                    try:
                        # 非检测帧：只跳过一帧，保持摄像头流更新，不做推理
                        self.head_cap.grab()
                    except Exception as e:
                        logger.error(f"摄像头 grab 失败: {e}")
                        # 关闭摄像头，下次循环会重新打开
                        if self.head_cap:
                            self.head_cap.release()
                            self.head_cap = None

                time.sleep(0.01)

        except KeyboardInterrupt:
            logger.info("收到中断信号，正在退出...")
        except Exception as e:
            logger.error(f"头部姿态控制错误: {e}")
        finally:
            # 清理
            if self.head_cap:
                self.head_cap.release()
                logger.info("摄像头已关闭")
            cv2.destroyAllWindows()
            logger.info("头部姿态控制已停止")
    def start(self):
        """启动集成控制"""
        self.running = True
        # 启动语音识别线程
        self.voice_thread = threading.Thread(target=self.voice_recognition_thread, daemon=True)
        self.voice_thread.start()
        # 启动头部姿态检测线程
        self.head_thread = threading.Thread(target=self.head_pose_thread, daemon=True)
        self.head_thread.start()
        logger.info("集成控制已启动")
    def stop(self):
        """停止集成控制"""
        self.running = False
        if self.voice_thread:
            self.voice_thread.join(timeout=5)
        if self.head_thread:
            self.head_thread.join(timeout=5)
        logger.info("集成控制已停止")


if __name__ == "__main__":
    integrated_control = IntegratedControl()
    integrated_control.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        integrated_control.stop()
