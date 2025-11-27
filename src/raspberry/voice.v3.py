import os
import json
import re
import time
from pypinyin import lazy_pinyin, Style
from vosk import Model, KaldiRecognizer
import pyaudio

# 尝试导入 serial，如果失败则使用模拟模式
try:
    import serial

    SERIAL_AVAILABLE = True
    print("串口库加载成功，将使用真实串口通信")
except ImportError:
    SERIAL_AVAILABLE = False
    print("未找到 pyserial 库，使用模拟串口模式")

# 语音模型路径
model_path = "E:/vosk-model-small-cn-0.22"

# 串口配置
SERIAL_PORT = "COM3"  # 根据实际情况修改串口号
BAUD_RATE =115200

# 验证模型路径
if not os.path.exists(model_path):
    print(f"错误: 路径 '{model_path}' 不存在")
    exit(1)

# 尝试加载模型
try:
    model = Model(model_path)
    print("模型加载成功!")
except Exception as e:
    print(f"模型加载失败: {e}")
    exit(1)

# 初始化串口
ser = None
if SERIAL_AVAILABLE:
    try:
        ser = serial.Serial(SERIAL_PORT, BAUD_RATE, timeout=1)
        time.sleep(2)  # 等待串口初始化
        print(f"串口 {SERIAL_PORT} 打开成功")
    except Exception as e:
        print(f"串口打开失败: {e}")
        ser = None
else:
    print("模拟串口模式：指令将在控制台显示，不会实际发送")

# 系统状态
SYSTEM_ACTIVE = False  # 系统是否被唤醒
LAST_ACTIVE_TIME = 0  # 最后活跃时间
ACTIVE_TIMEOUT = 60  # 1分钟超时

# 指令映射配置
command_config = {
    "前进": {
        "code": 'F',
        "pinyin": ["qian jin", "xiang qian", "wang qian"],
        "pinyin_no_tone": ["qian jin", "xiang qian", "wang qian"],
        "aliases": [
            "前进", "向前", "往前", "前近", "钱进",
            "向前走", "往前走", "前进走", "钱进走", "前行走",
            "想前", "象前", "向钱", "想钱", "象钱", "往前冲",
            "向前进", "往前进", "前前进", "钱前进", "前进前进",
            "往前", "网前", "望前", "王前", "忘前", "往前开",
            "往前跑", "往前行", "往前移动", "往前驾驶", "往前行驶"
        ],
        "keywords": ["前", "进", "向", "往", "走", "冲", "开", "跑", "行", "移动", "驾驶", "行驶"]
    },
    "后退": {
        "code": 'B',
        "pinyin": ["hou tui", "xiang hou", "wang hou"],
        "pinyin_no_tone": ["hou tui", "xiang hou", "wang hou"],
        "aliases": [
            "后退", "向后", "往后", "后推", "厚退", "候退", "逅退",
            "向后退", "往后退", "后退退", "厚退退", "候退退",
            "想后", "象后", "向后走", "往后走", "后退走",
            "向后退", "往后退", "后后退", "厚后退", "候后退",
            "往后", "网后", "望后", "王后", "忘后", "往后倒",
            "往后撤", "往后移", "往后移动", "往后驾驶", "往后行驶",
            "倒车", "后倒", "退后", "撤退", "后撤"
        ],
        "keywords": ["后", "退", "倒", "撤", "移", "向", "往", "走", "移动", "驾驶", "行驶"]
    },
    "向左": {
        "code": 'L',
        "pinyin": ["xiang zuo", "wang zuo"],
        "pinyin_no_tone": ["xiang zuo", "wang zuo"],
        "aliases": [
            "向左", "往左", "左转", "想左", "象左", "像左", "响左",
            "享左", "向佐", "想佐", "向左转", "往左转", "左转弯",
            "网左", "望左", "往左走", "向左走", "左走", "左转走",
            "往左拐", "向左拐", "左拐", "左转弯", "往左转", "向左转"
        ],
        "keywords": ["左", "向", "往", "转", "拐", "弯", "走"]
    },
    "向右": {
        "code": 'R',
        "pinyin": ["xiang you", "wang you"],
        "pinyin_no_tone": ["xiang you", "wang you"],
        "aliases": [
            "向右", "往右", "右转", "想右", "象右", "像右", "响右",
            "享右", "向佑", "想佑", "向右转", "往右转", "右转弯",
            "网右", "望右", "往右走", "向右走", "右走", "右转走",
            "往右拐", "向右拐", "右拐", "右转弯", "往右转", "向右转"
        ],
        "keywords": ["右", "向", "往", "转", "拐", "弯", "走"]
    },
    "停止": {
        "code": 'S',
        "pinyin": ["ting zhi", "ting"],
        "pinyin_no_tone": ["ting zhi", "ting"],
        "aliases": [
            "停止", "停下", "停", "停至", "亭止", "仃止", "停址",
            "停止运动", "停下来", "停一下", "暂停", "停车", "停住",
            "定止", "廷止", "停止前进", "停止移动", "停止运行"
        ],
        "keywords": ["停", "止", "下", "住", "车", "暂", "定"]
    },
    "加速": {
        "code": 'A',
        "pinyin": ["jia su"],
        "pinyin_no_tone": ["jia su"],
        "aliases": ["加速", "快点", "加快", "家速", "加素", "加速前进", "快一点", "加快速度"],
        "keywords": ["加", "速", "快", "点", "速", "度"]
    },
    "减速": {
        "code": 'D',
        "pinyin": ["jian su"],
        "pinyin_no_tone": ["jian su"],
        "aliases": ["减速", "慢点", "减慢", "减素", "减速前进", "慢一点", "降低速度"],
        "keywords": ["减", "速", "慢", "点", "降", "低"]
    },
    "开始": {
        "code": None,  # 唤醒词，不发送字符
        "pinyin": ["kai shi"],
        "pinyin_no_tone": ["kai shi"],
        "aliases": [
            "开始", "启动", "开", "开使", "凯始", "开式",
            "开始运动", "开始前进", "启动前进", "出发", "起步", "开车",
            "开启", "开动", "启动运行", "开始运行"
        ],
        "keywords": ["开", "始", "启", "动", "发", "步", "车"]
    }
}

# 预编译正则表达式
chinese_pattern = re.compile(r'[\u4e00-\u9fff]+')
tone_pattern = re.compile(r'\d')

# 预计算所有指令的拼音变体，加快匹配速度
for cmd, config in command_config.items():
    # 预先计算所有拼音变体
    config["pinyin_compact"] = [p.replace(' ', '') for p in config["pinyin_no_tone"]]
    config["pinyin_keywords"] = [p.replace(' ', '') for p in config["pinyin_no_tone"]]

# 初始化识别器
recognizer = KaldiRecognizer(model, 16000)

# 设置音频输入
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=8192)
stream.start_stream()

print("语音识别已启动，请先说'开始'唤醒系统...")
print(f"支持的指令: {list(command_config.keys())}")
print("指令映射:")
for cmd, config in command_config.items():
    if config["code"] is not None:  # 只显示有代码的指令
        print(f"  {cmd} -> 发送字符: '{config['code']}'")

# 添加状态变量
last_command = None
last_command_time = 0
COMMAND_COOLDOWN = 1.0  # 指令冷却时间，避免重复发送

# 缓存最近处理的文本，避免重复处理
recent_texts = []
MAX_RECENT_TEXTS = 5


def text_to_pinyin_fast(text):
    """快速将文本转换为无音调拼音字符串"""
    pinyin_list = lazy_pinyin(text, style=Style.TONE3)
    pinyin_str = ' '.join(pinyin_list)
    return tone_pattern.sub('', pinyin_str)


def remove_tone_fast(pinyin_str):
    """快速去除拼音中的声调数字"""
    return tone_pattern.sub('', pinyin_str)


def levenshtein_distance_fast(s1, s2):
    """快速计算两个字符串的编辑距离（优化版）"""
    if len(s1) < len(s2):
        return levenshtein_distance_fast(s2, s1)
    if len(s2) == 0:
        return len(s1)

    # 使用列表推导式优化
    previous_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def send_serial_command(command_code):
    """向串口发送指令"""
    global last_command, last_command_time

    current_time = time.time()

    # 检查冷却时间，避免重复发送相同指令
    if (last_command == command_code and
            current_time - last_command_time < COMMAND_COOLDOWN):
        return

    if ser and ser.is_open:
        try:
            # 发送单个字符命令
            command_str = command_code
            ser.write(command_str.encode('ascii'))
            print(f"向STM32发送指令: '{command_str}'")
            last_command = command_code
            last_command_time = current_time
        except Exception as e:
            print(f"串口发送失败: {e}")
    else:
        print(f"模拟发送指令: '{command_code}'")


def keyword_based_match_fast(text, command_config):
    """快速基于关键词的匹配方法"""
    best_match = None
    best_score = 0

    for command, config in command_config.items():
        score = 0
        keywords = config.get("keywords", [])

        # 使用生成器表达式优化
        score = sum(1 for keyword in keywords if keyword in text)

        # 根据关键词匹配数量计算分数
        if keywords:
            keyword_score = score / len(keywords)
            if keyword_score > best_score:
                best_score = keyword_score
                best_match = command

    return best_match, best_score


def fuzzy_match_command_fast(text):
    """快速模糊匹配指令，返回最可能的指令及匹配分数"""
    if not text:
        return None, 0, 0

    # 使用预编译的正则表达式提取中文文本
    chinese_matches = chinese_pattern.findall(text)
    if not chinese_matches:
        return None, 0, 0

    chinese_text = ''.join(chinese_matches)

    # 检查是否是最近处理过的文本
    if chinese_text in recent_texts:
        return None, 0, 0

    # 添加到最近文本列表
    recent_texts.append(chinese_text)
    if len(recent_texts) > MAX_RECENT_TEXTS:
        recent_texts.pop(0)

    # 转换为拼音（无音调）
    text_pinyin = text_to_pinyin_fast(chinese_text)

    best_match = None
    highest_score = 0
    best_command_code = None

    # 第一轮：直接文本匹配（最高优先级）
    for command, config in command_config.items():
        # 检查是否直接包含指令
        if command in chinese_text:
            return command, config["code"], 1.0

        # 检查是否包含别名
        for alias in config["aliases"]:
            if alias in chinese_text:
                return command, config["code"], 0.95

    # 第二轮：关键词匹配
    keyword_match, keyword_score = keyword_based_match_fast(chinese_text, command_config)
    if keyword_match and keyword_score > 0.5:
        command_code = command_config[keyword_match]["code"]
        return keyword_match, command_code, 0.8

    # 第三轮：拼音模糊匹配 - 使用预计算的拼音
    text_pinyin_compact = text_pinyin.replace(' ', '')
    for command, config in command_config.items():
        # 对每个拼音配置进行匹配
        for pinyin_variant in config["pinyin_no_tone"]:
            command_pinyin = pinyin_variant
            distance = levenshtein_distance_fast(text_pinyin, command_pinyin)
            max_len = max(len(text_pinyin), len(command_pinyin))
            score = 1 - (distance / max_len) if max_len > 0 else 0

            # 如果拼音匹配度高，更新最佳匹配
            if score > highest_score:
                highest_score = score
                best_match = command
                best_command_code = config["code"]

    # 第四轮：部分匹配增强 - 使用预计算的紧凑拼音
    if highest_score < 0.7:
        for command, config in command_config.items():
            # 检查拼音是否包含关键部分
            for pinyin_compact in config["pinyin_compact"]:
                if (pinyin_compact in text_pinyin_compact or
                        text_pinyin_compact in pinyin_compact):
                    score = 0.7  # 部分匹配给予基础分数
                    if score > highest_score:
                        highest_score = score
                        best_match = command
                        best_command_code = config["code"]
                        break  # 找到一个匹配就退出内层循环

    return best_match, best_command_code, highest_score


def preprocess_text_fast(text):
    """快速预处理文本，提高识别准确率"""
    # 移除常见干扰词
    noise_words = ['请', '帮', '我', '要', '想', '一下', '一点', '进行', '那个', '这个']
    for word in noise_words:
        text = text.replace(word, '')

    # 标准化指令表达 - 特别加强"往前"和"往后"的处理
    replacements = {
        '往前走': '前进',
        '向前走': '前进',
        '向后退': '后退',
        '往后退': '后退',
        '向左转': '向左',
        '往左转': '向左',
        '向右转': '向右',
        '往右转': '向右',
        '往前开': '前进',
        '往前跑': '前进',
        '往前行': '前进',
        '往前移动': '前进',
        '往后倒': '后退',
        '往后撤': '后退',
        '往后移': '后退',
        '往后移动': '后退',
        '倒车': '后退',
        '后倒': '后退',
        '退后': '后退',
        '后撤': '后退'
    }

    for old, new in replacements.items():
        if old in text:
            text = text.replace(old, new)

    return text.strip()


def check_timeout():
    """检查系统是否超时"""
    global SYSTEM_ACTIVE, LAST_ACTIVE_TIME
    current_time = time.time()

    if SYSTEM_ACTIVE and (current_time - LAST_ACTIVE_TIME > ACTIVE_TIMEOUT):
        SYSTEM_ACTIVE = False
        print("\n系统已超时，请说'开始'重新唤醒")
        return True
    return False


def update_active_time():
    """更新最后活跃时间"""
    global LAST_ACTIVE_TIME
    LAST_ACTIVE_TIME = time.time()


# 性能监控
last_process_time = time.time()
process_count = 0

try:
    while True:
        # 检查超时
        check_timeout()

        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get('text', '').strip()

            if text:
                # 性能监控
                current_time = time.time()
                process_count += 1

                if current_time - last_process_time >= 5:
                    print(f"\n处理速度: {process_count / 5:.1f} 次/秒")
                    last_process_time = current_time
                    process_count = 0

                # 快速预处理文本
                processed_text = preprocess_text_fast(text)

                # 快速匹配
                command, command_code, score = fuzzy_match_command_fast(processed_text)

                if command and score > 0.5:
                    print(f"\n识别到指令: {command} (匹配度: {score:.2f})")

                    # 处理唤醒词
                    if command == "开始":
                        SYSTEM_ACTIVE = True
                        update_active_time()
                        print("系统已唤醒，请在1分钟内发出指令")
                        continue

                    # 处理其他指令
                    if SYSTEM_ACTIVE:
                        if command_code is not None:  # 确保不是唤醒词
                            print(f"执行指令: {command} -> 发送字符: '{command_code}'")
                            # 发送串口指令
                            send_serial_command(command_code)
                            # 更新活跃时间
                            update_active_time()
                    else:
                        print("系统未唤醒，请先说'开始'")

except KeyboardInterrupt:
    print("\n程序被用户中断")
finally:
    # 清理资源
    if ser and ser.is_open:
        ser.close()
    stream.stop_stream()
    stream.close()
    p.terminate()
    print("程序已退出")