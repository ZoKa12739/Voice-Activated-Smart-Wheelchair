import os
import json
import re
import jieba
import jieba.posseg as pseg
from pypinyin import lazy_pinyin, Style
from vosk import Model, KaldiRecognizer
import pyaudio

# 使用正确的路径
model_path = "E:/vosk-model-small-cn-0.22"

# 验证路径
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

# 定义目标指令及其可能的谐音/近似音（拼音形式）
command_config = {
    "向左": {
        "pinyin": ["xiang zuo"],
        "aliases": ["想左", "象左", "像左", "响左", "享左", "向佐", "想佐"],
        "direction": "left"
    },
    "向右": {
        "pinyin": ["xiang you"],
        "aliases": ["想右", "象右", "像右", "响右", "享右", "向佑", "想佑"],
        "direction": "right"
    },
    "前进": {
        "pinyin": ["qian jin"],
        "aliases": ["前近", "钱进", "前进", " Qian Jin"],
        "action": "forward"
    },
    "向前": {
        "pinyin": ["xiang qian"],
        "aliases": ["想钱", "像钱", "向钱", "镶嵌"],
        "action": "forward"
    },
    "后退": {
        "pinyin": ["hou tui"],
        "aliases": ["后推", "厚退", "候退", "逅退"],
        "action": "backward"
    },
    "停止": {
        "pinyin": ["ting zhi"],
        "aliases": ["停至", "亭止", "仃止", "停址"],
        "action": "stop"
    },
    "开始": {
        "pinyin": ["kai shi"],
        "aliases": ["开使", "凯始", "开式", "开是"],
        "action": "start"
    }
}

# 语义理解关键词配置（增强版，添加拼音和别名）
semantic_keywords = {
    # 方向关键词（增强拼音和别名支持）
    "direction": {
        "左": {
            "words": ["左", "左边", "左侧", "左转", "左拐", "左方向", "往左"],
            "pinyin": ["zuo", "zuo bian", "zuo ce", "zuo zhuan", "zuo guai", "zuo fang xiang", "wang zuo"],
            "aliases": ["佐", "坐", "做", "唑", "昨"]
        },
        "右": {
            "words": ["右", "右边", "右侧", "右转", "右拐", "右方向", "往右"],
            "pinyin": ["you", "you bian", "you ce", "you zhuan", "you guai", "you fang xiang", "wang you"],
            "aliases": ["佑", "又", "有", "幼", "诱"]
        },
        "前": {
            "words": ["前", "前面", "前方", "前进", "向前", "往前"],
            "pinyin": ["qian", "qian mian", "qian fang", "qian jin", "xiang qian", "wang qian"],
            "aliases": ["钱", "浅", "千", "牵", "签"]
        },
        "后": {
            "words": ["后", "后面", "后方", "后退", "向后", "往后"],
            "pinyin": ["hou", "hou mian", "hou fang", "hou tui", "xiang hou", "wang hou"],
            "aliases": ["候", "厚", "后", "吼", "喉"]
        }
    },
    # 动作关键词（同样增强）
    "action": {
        "转": {
            "words": ["转", "转弯", "转向", "转动", "转方向"],
            "pinyin": ["zhuan", "zhuan wan", "zhuan xiang", "zhuan dong", "zhuan fang xiang"],
            "aliases": ["专", "砖", "传", "赚", "撰"]
        },
        "走": {
            "words": ["走", "行走", "移动", "行进", "行驶"],
            "pinyin": ["zou", "xing zou", "yi dong", "xing jin", "xing shi"],
            "aliases": ["奏", "邹", "揍", "驺"]
        },
        "停": {
            "words": ["停", "停止", "停下", "停车", "停住"],
            "pinyin": ["ting", "ting zhi", "ting xia", "ting che", "ting zhu"],
            "aliases": ["听", "厅", "廷", "亭", "婷"]
        },
        "开始": {
            "words": ["开始", "启动", "出发", "开动"],
            "pinyin": ["kai shi", "qi dong", "chu fa", "kai dong"],
            "aliases": ["开驶", "凯始", "开式", "开是"]
        }
    },
    # 环境关键词
    "environment": {
        "拥堵": {
            "words": ["拥堵", "堵车", "堵塞", "堵住", "塞车", "太挤", "拥挤", "挤"],
            "pinyin": ["yong du", "du che", "du sai", "du zhu", "sai che", "tai ji", "yong ji", "ji"],
            "aliases": ["拥度", "堵扯", "堵赛", "太急", "拥急"]
        },
        "障碍": {
            "words": ["障碍", "障碍物", "阻挡", "挡住", "阻拦", "挡路", "有东西"],
            "pinyin": ["zhang ai", "zhang ai wu", "zu dang", "dang zhu", "zu lan", "dang lu", "you dong xi"],
            "aliases": ["障爱", "障碍无", "阻当", "挡道"]
        },
        "畅通": {
            "words": ["畅通", "通畅", "顺畅", "无阻", "好走", "空"],
            "pinyin": ["chang tong", "tong chang", "shun chang", "wu zu", "hao zou", "kong"],
            "aliases": ["常通", "通长", "顺长", "好走"]
        },
        "危险": {
            "words": ["危险", "危急", "险情", "不安全", "小心", "注意"],
            "pinyin": ["wei xian", "wei ji", "xian qing", "bu an quan", "xiao xin", "zhu yi"],
            "aliases": ["危显", "危机", "险清", "不安全"]
        }
    },
    # 逻辑关键词
    "logic": {
        "需要": {
            "words": ["需要", "必须", "得", "要", "应该"],
            "pinyin": ["xu yao", "bi xu", "dei", "yao", "ying gai"],
            "aliases": ["须要", "必需", "德", "应该"]
        },
        "建议": {
            "words": ["建议", "推荐", "最好", "应该", "可以"],
            "pinyin": ["jian yi", "tui jian", "zui hao", "ying gai", "ke yi"],
            "aliases": ["建义", "推荐", "最号", "可以"]
        },
        "避免": {
            "words": ["避免", "避开", "绕开", "躲避", "别", "不要", "不用"],
            "pinyin": ["bi mian", "bi kai", "rao kai", "duo bi", "bie", "bu yao", "bu yong"],
            "aliases": ["必免", "避凯", "绕凯", "不要"]
        },
        "因为": {
            "words": ["因为", "由于", "鉴于", "既然", "所以"],
            "pinyin": ["yin wei", "you yu", "jian yu", "ji ran", "suo yi"],
            "aliases": ["音为", "尤于", "见於", "所以"]
        }
    },
    # 否定关键词（新增）
    "negation": {
        "否定": {
            "words": ["不", "别", "不要", "不用", "不能", "非", "没", "没有", "禁止", "停止"],
            "pinyin": ["bu", "bie", "bu yao", "bu yong", "bu neng", "fei", "mei", "mei you", "jin zhi", "ting zhi"],
            "aliases": ["甭", "勿", "莫", "休", "毋"]
        }
    },
    # 强度关键词（新增）
    "intensity": {
        "强烈": {
            "words": ["很", "非常", "特别", "太", "极其", "十分", "真的"],
            "pinyin": ["hen", "fei chang", "te bie", "tai", "ji qi", "shi fen", "zhen de"],
            "aliases": ["狠", "非常", "特备", "泰", "十分"]
        },
        "轻微": {
            "words": ["有点", "稍微", "略微", "稍稍", "一点"],
            "pinyin": ["you dian", "shao wei", "lue wei", "shao shao", "yi dian"],
            "aliases": ["有点", "稍微", "略为", "稍稍"]
        }
    }
}

# 增强语义规则库
semantic_rules = [
    # 环境+逻辑+方向规则
    {
        "name": "拥堵转向规则",
        "pattern": [("environment", "拥堵"), ("logic", "需要|建议|避免"), ("direction", "左|右")],
        "action": "turn",
        "priority": 10,
        "description": "前方拥堵，需要向左/右转"
    },
    {
        "name": "障碍避让规则",
        "pattern": [("environment", "障碍"), ("logic", "需要|建议|避免"), ("direction", "左|右")],
        "action": "avoid",
        "priority": 10,
        "description": "有障碍物，需要向左/右避让"
    },
    {
        "name": "危险规避规则",
        "pattern": [("environment", "危险"), ("logic", "需要|建议|避免"), ("direction", "左|右")],
        "action": "avoid",
        "priority": 15,  # 危险情况优先级更高
        "description": "有危险，需要向左/右规避"
    },

    # 否定+方向/动作规则
    {
        "name": "否定转向规则",
        "pattern": [("negation", "否定"), ("direction", "左|右"), ("action", "转")],
        "action": "avoid_turn",
        "priority": 12,
        "description": "不要向左/右转"
    },
    {
        "name": "否定前进规则",
        "pattern": [("negation", "否定"), ("direction", "前"), ("action", "走")],
        "action": "stop_or_back",
        "priority": 12,
        "description": "不要向前走"
    },

    # 直接指令规则
    {
        "name": "直接方向指令",
        "pattern": [("direction", "左|右"), ("action", "转")],
        "action": "turn",
        "priority": 5,
        "description": "向左/右转"
    },
    {
        "name": "前进指令",
        "pattern": [("direction", "前"), ("action", "走")],
        "action": "move_forward",
        "priority": 5,
        "description": "向前走"
    },
    {
        "name": "停止指令",
        "pattern": [("action", "停")],
        "action": "stop",
        "priority": 8,
        "description": "停止移动"
    },

    # 复杂情况规则
    {
        "name": "环境建议规则",
        "pattern": [("environment", "拥堵|障碍|危险"), ("logic", "建议"), ("direction", "左|右|前|后")],
        "action": "suggest",
        "priority": 7,
        "description": "根据环境建议方向"
    },
    {
        "name": "强度指示规则",
        "pattern": [("intensity", "强烈"), ("environment", "拥堵|障碍|危险"), ("direction", "左|右")],
        "action": "urgent_turn",
        "priority": 13,
        "description": "紧急需要转向"
    }
]

# 上下文记忆（用于处理多句话的连贯理解）
context_memory = {
    "last_direction": None,
    "last_action": None,
    "last_environment": None,
    "conversation_history": []
}


# 初始化分词词典
def init_jieba_dict():
    """初始化jieba分词词典，添加专业词汇"""
    # 添加自定义词汇以提高分词准确性
    custom_words = []
    for category, keywords in semantic_keywords.items():
        for subcategory, config in keywords.items():
            custom_words.extend(config["words"])
            custom_words.extend(config["aliases"])

    for word in set(custom_words):
        jieba.add_word(word)


# 初始化识别器
recognizer = KaldiRecognizer(model, 16000)

# 设置音频输入
p = pyaudio.PyAudio()
stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=4096)
stream.start_stream()

print("语音识别已启动，请说出指令...")
print(f"支持的指令: {list(command_config.keys())}")

# 初始化分词词典
init_jieba_dict()


def text_to_pinyin(text):
    """将文本转换为带声调的拼音字符串"""
    return ' '.join(lazy_pinyin(text, style=Style.TONE3))


def remove_tone(pinyin_str):
    """去除拼音中的声调数字"""
    return re.sub(r'\d', '', pinyin_str)


def levenshtein_distance(s1, s2):
    """计算两个字符串的编辑距离（用于模糊匹配）"""
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)

    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row

    return previous_row[-1]


def fuzzy_match_keyword(word, category, subcategory):
    """模糊匹配关键词，返回匹配分数和匹配类型"""
    if not word:
        return 0, None

    # 获取目标关键词配置
    target_config = semantic_keywords[category][subcategory]

    # 1. 精确匹配原词
    if word in target_config["words"]:
        return 1.0, "exact_word"

    # 2. 精确匹配别名
    if word in target_config["aliases"]:
        return 0.9, "exact_alias"

    # 3. 拼音匹配
    word_pinyin = remove_tone(text_to_pinyin(word))

    # 匹配目标拼音
    for target_pinyin in target_config["pinyin"]:
        target_pinyin_no_tone = remove_tone(target_pinyin)
        if word_pinyin == target_pinyin_no_tone:
            return 0.8, "exact_pinyin"

    # 4. 拼音模糊匹配
    best_pinyin_score = 0
    for target_pinyin in target_config["pinyin"]:
        target_pinyin_no_tone = remove_tone(target_pinyin)
        distance = levenshtein_distance(word_pinyin, target_pinyin_no_tone)
        max_len = max(len(word_pinyin), len(target_pinyin_no_tone))
        score = 1 - (distance / max_len) if max_len > 0 else 0

        if score > best_pinyin_score:
            best_pinyin_score = score

    if best_pinyin_score > 0.6:
        return best_pinyin_score, "fuzzy_pinyin"

    return 0, None


def extract_negation_context(semantic_features):
    """提取否定上下文，判断是否有否定词及其影响范围"""
    negation_positions = []

    for i, feature in enumerate(semantic_features):
        if feature['category'] == 'negation':
            negation_positions.append(i)

    negation_context = {}

    for neg_pos in negation_positions:
        # 检查否定词后面的词语（通常是否定的对象）
        for i in range(neg_pos + 1, min(neg_pos + 4, len(semantic_features))):
            feature = semantic_features[i]
            if feature['category'] in ['direction', 'action']:
                negation_context[feature['subcategory']] = True

    return negation_context


def analyze_sentence_structure(semantic_features):
    """分析句子结构，识别主要意图和次要意图（修复版）"""
    # 按位置排序特征
    sorted_features = sorted(semantic_features, key=lambda x: x['position'])

    # 提取否定上下文
    negation_context = extract_negation_context(sorted_features)

    # 识别意图关键词（用户明确表达意图的词）
    intent_keywords = ['要', '需要', '想', '应该', '必须', '得']
    intent_positions = []

    for i, feature in enumerate(sorted_features):
        if feature['word'] in intent_keywords:
            intent_positions.append(i)

    primary_actions = []
    primary_directions = []
    environment_info = []
    logic_info = []

    # 为每个特征分配权重：意图关键词后的特征权重更高
    for i, feature in enumerate(sorted_features):
        weight = 1.0  # 基础权重

        # 如果这个特征在意图关键词之后，增加权重
        for intent_pos in intent_positions:
            if i > intent_pos and i - intent_pos <= 3:  # 意图关键词后3个词内
                weight = 2.0  # 意图关键词后的特征权重加倍
                break

        # 创建带权重的特征副本
        weighted_feature = feature.copy()
        weighted_feature['weight'] = weight
        weighted_feature['weighted_score'] = feature['score'] * weight

        # 分类特征
        if feature['category'] == 'action' and feature['subcategory'] not in negation_context:
            primary_actions.append(weighted_feature)
        elif feature['category'] == 'direction' and feature['subcategory'] not in negation_context:
            primary_directions.append(weighted_feature)
        elif feature['category'] == 'environment':
            environment_info.append(weighted_feature)
        elif feature['category'] == 'logic':
            logic_info.append(weighted_feature)

    # 识别否定指令
    negative_actions = []
    negative_directions = []

    for feature in sorted_features:
        if (feature['category'] == 'action' and
                feature['subcategory'] in negation_context):
            negative_actions.append(feature)
        elif (feature['category'] == 'direction' and
              feature['subcategory'] in negation_context):
            negative_directions.append(feature)

    return {
        'primary_actions': primary_actions,
        'primary_directions': primary_directions,
        'negative_actions': negative_actions,
        'negative_directions': negative_directions,
        'environment_info': environment_info,
        'logic_info': logic_info,
        'negation_context': negation_context,
        'intent_positions': intent_positions
    }

def semantic_analysis(text):
    """语义分析和理解（增强版，支持复杂句子理解）"""
    if not text:
        return None, 0, "无输入文本"

    # 使用jieba进行分词和词性标注
    words = pseg.cut(text)

    # 提取语义特征（支持模糊匹配）
    semantic_features = []
    for word, flag in words:
        best_match_score = 0
        best_match_category = None
        best_match_subcategory = None
        best_match_type = None

        # 检查每个关键词类别
        for category, keywords in semantic_keywords.items():
            for subcategory, config in keywords.items():
                score, match_type = fuzzy_match_keyword(word, category, subcategory)
                if score > best_match_score:
                    best_match_score = score
                    best_match_category = category
                    best_match_subcategory = subcategory
                    best_match_type = match_type

        # 如果匹配度足够高，则添加到特征中
        if best_match_score > 0.6:
            semantic_features.append({
                'word': word,
                'category': best_match_category,
                'subcategory': best_match_subcategory,
                'score': best_match_score,
                'match_type': best_match_type,
                'position': len(semantic_features)
            })

    # 分析句子结构
    sentence_structure = analyze_sentence_structure(semantic_features)

    # 应用语义规则（考虑优先级）
    matched_rules = []

    for rule in semantic_rules:
        match_score = 0
        matched_features = []  # 记录匹配的特征详情

        for pattern_item in rule['pattern']:
            category, subcategory_pattern = pattern_item
            pattern_categories = subcategory_pattern.split('|')

            best_feature_match = None
            best_feature_score = 0

            # 查找最佳匹配的特征
            for feature in semantic_features:
                if (feature['category'] == category and
                        any(pattern_cat in feature['subcategory'] for pattern_cat in pattern_categories) and
                        feature not in matched_features):
                    if feature['score'] > best_feature_score:
                        best_feature_score = feature['score']
                        best_feature_match = feature

            if best_feature_match:
                match_score += best_feature_score
                matched_features.append(best_feature_match)

        # 计算匹配度
        rule_match_ratio = match_score / len(rule['pattern']) if rule['pattern'] else 0

        if rule_match_ratio > 0.6:
            matched_rules.append({
                'rule': rule,
                'score': rule_match_ratio,
                'priority': rule.get('priority', 0),
                'matched_features': matched_features  # 记录匹配的具体特征
            })

    # 按优先级和匹配度排序规则
    matched_rules.sort(key=lambda x: (x['priority'], x['score']), reverse=True)

    best_rule = matched_rules[0]['rule'] if matched_rules else None
    best_match_score = matched_rules[0]['score'] if matched_rules else 0

    # 提取方向信息（考虑否定上下文）
    direction = None
    direction_score = 0
    negation_context = sentence_structure['negation_context']

    for feature in semantic_features:
        if (feature['category'] == 'direction' and
                feature['score'] > direction_score and
                feature['subcategory'] not in negation_context):
            direction = feature['subcategory']
            direction_score = feature['score']

    # 如果没有明确方向，但有否定方向，则选择相反方向
    if not direction and sentence_structure['negative_directions']:
        # 简单的方向对立逻辑
        opposite_map = {'左': '右', '右': '左', '前': '后', '后': '前'}
        for neg_dir in sentence_structure['negative_directions']:
            if neg_dir['subcategory'] in opposite_map:
                direction = opposite_map[neg_dir['subcategory']]
                direction_score = 0.7  # 中等置信度
                break

    return best_rule, best_match_score, direction, semantic_features, sentence_structure


def fuzzy_match_command(text):
    """模糊匹配指令，返回最可能的指令及匹配分数"""
    if not text:
        return None, 0, None, None

    # 首先进行语义分析
    semantic_rule, semantic_score, direction, features, sentence_structure = semantic_analysis(text)

    # 提取文本中的中文字符
    chinese_text = re.findall(r'[\u4e00-\u9fff]+', text)
    if not chinese_text:
        return None, 0, semantic_rule, direction, sentence_structure
    chinese_text = ''.join(chinese_text)

    # 转换为拼音（带声调和平声调两种形式）
    text_pinyin_with_tone = text_to_pinyin(chinese_text)
    text_pinyin = remove_tone(text_pinyin_with_tone)

    best_match = None
    highest_score = 0

    # 检查每个指令
    for command, config in command_config.items():
        # 检查是否直接包含指令
        if command in chinese_text:
            return command, 1.0, semantic_rule, direction, sentence_structure  # 完全匹配，直接返回

        # 检查是否包含别名
        for alias in config["aliases"]:
            if alias in chinese_text:
                return command, 0.9, semantic_rule, direction, sentence_structure  # 别名匹配

        # 拼音模糊匹配
        command_pinyin = remove_tone(' '.join(config["pinyin"]))
        distance = levenshtein_distance(text_pinyin, command_pinyin)
        max_len = max(len(text_pinyin), len(command_pinyin))
        score = 1 - (distance / max_len) if max_len > 0 else 0

        # 如果拼音匹配度高，直接返回
        if score > 0.7 and score > highest_score:
            highest_score = score
            best_match = command

    return best_match, highest_score, semantic_rule, direction, sentence_structure


def extract_final_command(final_command):
    """从最终指令中提取简洁的指令（左、右、前、后、停等）"""
    if not final_command:
        return "无指令"

    # 提取基本指令
    if "左" in final_command:
        return "左"
    elif "右" in final_command:
        return "右"
    elif "前" in final_command:
        return "前"
    elif "后" in final_command:
        return "后"
    elif "停止" in final_command or "停" in final_command:
        return "停"
    elif "开始" in final_command or "启动" in final_command:
        return "开始"
    elif "建议" in final_command:
        # 提取建议中的方向
        if "左" in final_command:
            return "建议左"
        elif "右" in final_command:
            return "建议右"
        elif "前" in final_command:
            return "建议前"
        else:
            return "建议"
    else:
        return final_command  # 返回原指令


def determine_final_command(matched_command, match_score, semantic_rule, direction, sentence_structure):
    """根据匹配结果和语义分析确定最终指令（完整修复版）"""

    # 处理否定逻辑（最高优先级）
    if sentence_structure['negative_actions'] or sentence_structure['negative_directions']:
        # 处理否定逻辑（原有代码保持不变）
        if direction and semantic_rule and semantic_rule.get('action') in ['turn', 'avoid']:
            if direction == '左':
                return "向左转", max(match_score, 0.8), "否定逻辑处理"
            elif direction == '右':
                return "向右转", max(match_score, 0.8), "否定逻辑处理"
        if not direction and semantic_rule and semantic_rule.get('action') == 'stop_or_back':
            return "停止", max(match_score, 0.7), "否定停止指令"

    # 修复：基于权重选择主要方向
    primary_directions = sentence_structure['primary_directions']

    if primary_directions:
        # 按加权分数排序，选择权重最高的方向
        sorted_directions = sorted(primary_directions,
                                   key=lambda x: x['weighted_score'],
                                   reverse=True)

        best_direction = sorted_directions[0]
        direction = best_direction['subcategory']

        print(f"方向选择详情:")  # 调试信息
        for i, dir_feature in enumerate(sorted_directions):
            print(f"  方向{i + 1}: {dir_feature['subcategory']}, "
                  f"原始分数: {dir_feature['score']:.2f}, "
                  f"权重: {dir_feature['weight']}, "
                  f"加权分数: {dir_feature['weighted_score']:.2f}")

        # 根据语义规则类型确定动作
        if semantic_rule:
            rule_action = semantic_rule.get('action')

            if rule_action in ['turn', 'avoid', 'urgent_turn']:
                if direction == '左':
                    return "向左转", max(match_score, 0.8), "语义分析-转向"
                elif direction == '右':
                    return "向右转", max(match_score, 0.8), "语义分析-转向"
                elif direction == '前':
                    return "前进", max(match_score, 0.7), "语义分析-前进"
                elif direction == '后':
                    return "后退", max(match_score, 0.7), "语义分析-后退"

            elif rule_action == 'move_forward':
                return "前进", max(match_score, 0.8), "语义分析-前进"

            elif rule_action == 'stop':
                return "停止", max(match_score, 0.8), "语义分析-停止"

            elif rule_action == 'suggest':
                if direction == '左':
                    return "建议向左", max(match_score, 0.7), "环境建议"
                elif direction == '右':
                    return "建议向右", max(match_score, 0.7), "环境建议"
                elif direction == '前':
                    return "建议前进", max(match_score, 0.7), "环境建议"
                elif direction == '后':
                    return "建议后退", max(match_score, 0.7), "环境建议"

    # 如果有关键词匹配，使用关键词匹配结果
    if matched_command and match_score > 0.6:
        return matched_command, match_score, "关键词匹配"

    # 最后的fallback：使用加权分数最高的方向
    if primary_directions:
        sorted_directions = sorted(primary_directions,
                                   key=lambda x: x['weighted_score'],
                                   reverse=True)
        best_direction = sorted_directions[0]['subcategory']

        if best_direction == '左':
            return "向左", 0.6, "方向fallback"
        elif best_direction == '右':
            return "向右", 0.6, "方向fallback"
        elif best_direction == '前':
            return "前进", 0.6, "方向fallback"
        elif best_direction == '后':
            return "后退", 0.6, "方向fallback"

    return None, 0, "无匹配"
    if primary_directions:
        sorted_directions = sorted(primary_directions,
                                   key=lambda x: x['weighted_score'],
                                   reverse=True)
        direction = sorted_directions[0]['subcategory']  # 更新direction为选择的方向

    return final_command, final_score, reason, direction  # 返回更新后的direction
def update_context_memory(final_command, sentence_structure, text):
    """更新上下文记忆"""
    if final_command:
        # 提取方向信息
        if "左" in final_command:
            context_memory["last_direction"] = "左"
        elif "右" in final_command:
            context_memory["last_direction"] = "右"
        elif "前" in final_command:
            context_memory["last_direction"] = "前"
        elif "后" in final_command:
            context_memory["last_direction"] = "后"

        # 提取动作信息
        if "转" in final_command:
            context_memory["last_action"] = "转"
        elif "前进" in final_command or "向前" in final_command:
            context_memory["last_action"] = "前进"
        elif "停止" in final_command:
            context_memory["last_action"] = "停止"

        # 记录环境信息
        if sentence_structure['environment_info']:
            context_memory["last_environment"] = sentence_structure['environment_info'][0]['subcategory']

        # 记录对话历史（最近5条）
        context_memory["conversation_history"].append({
            "text": text,
            "command": final_command,
            "timestamp": len(context_memory["conversation_history"])
        })
        if len(context_memory["conversation_history"]) > 5:
            context_memory["conversation_history"] = context_memory["conversation_history"][-5:]


try:
    while True:
        data = stream.read(4096, exception_on_overflow=False)
        if recognizer.AcceptWaveform(data):
            result = json.loads(recognizer.Result())
            text = result.get('text', '').strip()
            if text:
                print(f"\n原始识别结果: {text}")

                # 进行模糊匹配和语义分析
                command, score, semantic_rule, direction, sentence_structure = fuzzy_match_command(text)

                # 确定最终指令
                final_command, final_score, reason = determine_final_command(
                    command, score, semantic_rule, direction, sentence_structure)

                # 提取简洁的最终指令
                simple_command = extract_final_command(final_command)

                if final_command and final_score > 0.6:
                    print(f"识别到指令: {final_command} (匹配度: {final_score:.2f})")
                    print(f"识别方式: {reason}")
                    print(f"最终指令: {simple_command}")

                    if semantic_rule:
                        print(f"语义规则: {semantic_rule['name']} - {semantic_rule['description']}")

                    # 只显示最终选择的方向，而不是所有方向
                    print(f"检测到方向: {direction}")  # 这里显示的是最终选择的方向

                    # 修改句子结构分析显示，只显示主要方向
                    print("句子结构分析:")
                    if sentence_structure['primary_actions']:
                        # 按加权分数排序动作
                        sorted_actions = sorted(sentence_structure['primary_actions'],
                                                key=lambda x: x['weighted_score'], reverse=True)
                        best_action = sorted_actions[0]
                        print(
                            f"  主要动作: {best_action['subcategory']}(加权分数: {best_action['weighted_score']:.2f})")

                    if sentence_structure['primary_directions']:
                        # 按加权分数排序方向，只显示最好的一个
                        sorted_directions = sorted(sentence_structure['primary_directions'],
                                                   key=lambda x: x['weighted_score'], reverse=True)
                        best_direction = sorted_directions[0]
                        print(
                            f"  主要方向: {best_direction['subcategory']}(加权分数: {best_direction['weighted_score']:.2f})")

                    # 更新上下文记忆
                    update_context_memory(final_command, sentence_structure, text)

                    # 在这里添加控制小车的代码
                    # 例如: control_car(simple_command)
                else:
                    print(f"未识别到有效指令 (最高匹配度: {final_score:.2f})")
                    if semantic_rule:
                        print(f"检测到语义模式: {semantic_rule['name']}，但置信度不足")
finally:
    stream.stop_stream()
    stream.close()
    p.terminate()