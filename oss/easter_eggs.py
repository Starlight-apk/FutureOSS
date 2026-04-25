"""彩蛋模块 - Easter Eggs for Future OSS

这个模块包含了一些隐藏的有趣功能，供用户发现。
真正的彩蛋应该埋得深、触发条件隐蔽、带来惊喜。
"""
import random
import sys
import os
import hashlib
from datetime import datetime
from typing import Optional
from pathlib import Path

# 隐藏计数器 - 只有连续触发才会生效
_hidden_counter = 0
_last_trigger_time = None

# Konami 代码 (需要在特定条件下输入)
_konami_sequence = []
_konami_code = ["up", "up", "down", "down", "left", "right", "left", "right", "b", "a"]
_konami_unlocked = False

# 隐藏成就系统 - 深度埋藏，多种触发方式
_achievements = set()
_achievement_triggers = {}  # 记录成就触发次数
_achievements_file = None

def _init_achievements():
    """初始化成就系统，从文件加载已解锁的成就"""
    global _achievements, _achievements_file
    
    if _achievements_file is not None:
        return  # 已经初始化过
    
    # 尝试找到数据目录
    try:
        from pathlib import Path
        import os
        
        # 优先使用配置的数据目录
        data_dir = None
        try:
            from oss.config import get_config
            config = get_config()
            data_dir = config.data_dir
        except:
            pass
        
        if data_dir is None:
            # 回退到默认位置
            data_dir = Path("/workspace/data")
        
        _achievements_file = data_dir / ".achievements"
        
        # 确保目录存在
        _achievements_file.parent.mkdir(parents=True, exist_ok=True)
        
        # 加载已保存的成就
        if _achievements_file.exists():
            try:
                with open(_achievements_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        ach_id = line.strip()
                        if ach_id and ach_id in ALL_ACHIEVEMENTS:
                            _achievements.add(ach_id)
            except Exception:
                pass
    except Exception:
        _achievements_file = None


def _save_achievements():
    """保存成就到文件"""
    if _achievements_file is None:
        return
    
    try:
        with open(_achievements_file, 'w', encoding='utf-8') as f:
            for ach_id in sorted(_achievements):
                f.write(f"{ach_id}\n")
    except Exception:
        pass

# 完整成就列表（隐藏）
ALL_ACHIEVEMENTS = {
    "file_hunter": {"name": "文件发现者", "desc": "发现隐藏的配置文件", "icon": "📁"},
    "config_explorer": {"name": "配置探索者", "desc": "探索隐藏配置路径", "icon": "🗝️"},
    "time_traveler": {"name": "时光旅行者", "desc": "在正确的时间出现 (42 秒)", "icon": "⏰"},
    "palindromic_master": {"name": "回文大师", "desc": "进程 ID 是回文数", "icon": "🔢"},
    "retro_gamer": {"name": "复古游戏", "desc": "输入 Konami 代码", "icon": "🎮"},
    "persistent_seeker": {"name": "坚持探索者", "desc": "连续触发隐藏内容", "icon": "💪"},
    "hash_master": {"name": "哈希大师", "desc": "找到以 0000 开头的 MD5", "icon": "🔐"},
    "truth_seeker": {"name": "真实探索者", "desc": "运行__hidden__.py", "icon": "👁️"},
    "lucky_star": {"name": "幸运之星", "desc": "获得幸运数字 77", "icon": "⭐"},
    "morning_bird": {"name": "早起的鸟儿", "desc": "在早上 5-7 点使用系统", "icon": "🌅"},
    "night_owl": {"name": "夜猫子", "desc": "在凌晨 0-3 点使用系统", "icon": "🦉"},
    "philosopher": {"name": "哲学家", "desc": "收集 5 条名人名言", "icon": "🤔"},
    "knowledge_seeker": {"name": "求知者", "desc": "阅读 10 条冷知识", "icon": "📚"},
    "fortune_teller": {"name": "预言家", "desc": "连续 5 次获取运势", "icon": "🔮"},
    "artist": {"name": "艺术家", "desc": "欣赏 ASCII 艺术", "icon": "🎨"},
    "special_day": {"name": "特殊日子", "desc": "在特殊节日使用系统", "icon": "🎊"},
    "secret_agent": {"name": "秘密特工", "desc": "触发所有开发者彩蛋", "icon": "🕵️"},
    "code_poet": {"name": "代码诗人", "desc": "发现代码中的诗意", "icon": "📝"},
    "infinity_seeker": {"name": "无限探索者", "desc": "解锁 15+ 成就", "icon": "♾️"},
    "master_explorer": {"name": "探索大师", "desc": "解锁所有成就", "icon": "👑"},
}

# 各种彩蛋消息
FORTUNE_MESSAGES = [
    "🚀 今天是个适合部署的好日子！",
    "💡 提示：试试输入 'oss help' 看看所有可用命令",
    "🎉 你发现了第一个彩蛋！继续保持好奇心！",
    "🐛 今天的 Bug 数量：0（暂时的）",
    "☕ 记得休息一下，喝杯咖啡！",
    "🌟 你是最棒的开发者！",
    "🔮 预测：你的代码今天会一次运行成功！",
    "🎮 游戏玩家？试试 Konami 代码！",
    "📦 一切皆为插件，包括这个彩蛋！",
    "⚡ 闪电般快速的响应，这就是 Future OSS！",
]

QUOTES = [
    ("Linus Torvalds", "Talk is cheap. Show me the code."),
    ("Alan Kay", "Simple things should be simple, complex things should be possible."),
    ("Grace Hopper", "The most dangerous phrase in the language is: We've always done it this way."),
    ("Donald Knuth", "Premature optimization is the root of all evil."),
    ("Brian Kernighan", "Debugging is twice as hard as writing the code in the first place."),
    ("Kent Beck", "Make it work, make it right, make it fast."),
    ("Martin Fowler", "Any fool can write code that a computer can understand. Good programmers write code that humans can understand."),
    ("Rita Mae Brown", "The problem with troubleshooting is that trouble shoots back."),
    ("Edsger Dijkstra", "Simplicity is prerequisite for reliability."),
    ("Jamie Zawinski", "Some people, when confronted with a problem, think 'I know, I'll use regular expressions.' Now they have two problems."),
]


def _check_secret_rune(text: str) -> bool:
    """检查是否触发了隐藏符文
    
    触发条件：
    - 在 version 命令后连续调用 3 次 fortune
    - 或者在 info 命令输出中包含特定哈希值
    """
    global _hidden_counter, _last_trigger_time
    
    now = datetime.now()
    
    # 如果距离上次触发超过 5 分钟，重置计数器
    if _last_trigger_time and (now - _last_trigger_time).seconds > 300:
        _hidden_counter = 0
    
    _last_trigger_time = now
    _hidden_counter += 1
    
    # 连续 3 次触发隐藏内容
    if _hidden_counter >= 3:
        return True
    
    return False


def _unlock_achievement(name: str, silent: bool = False):
    """解锁隐藏成就
    
    Args:
        name: 成就 ID
        silent: 是否静默解锁（不显示通知）
    """
    # 确保初始化
    _init_achievements()
    
    if name not in _achievements and name in ALL_ACHIEVEMENTS:
        _achievements.add(name)
        # 记录触发
        _achievement_triggers[name] = _achievement_triggers.get(name, 0) + 1
        
        # 保存成就
        _save_achievements()
        
        # 检查连锁成就
        _check_chain_achievements(name)
        
        if not silent:
            _print_achievement_notification(name)


def _track_trigger(trigger_name: str):
    """跟踪触发次数用于成就解锁"""
    _achievement_triggers[trigger_name] = _achievement_triggers.get(trigger_name, 0) + 1
    return _achievement_triggers[trigger_name]


def _check_chain_achievements(unlocked: str):
    """检查连锁成就（基于已解锁成就数量）"""
    count = len(_achievements)
    
    if count >= 15 and "infinity_seeker" not in _achievements:
        _unlock_achievement("infinity_seeker")
    
    if count == len(ALL_ACHIEVEMENTS) and "master_explorer" not in _achievements:
        _unlock_achievement("master_explorer")


def get_fortune(silent_mode: bool = False) -> str:
    """获取今日运势/幸运消息
    
    Args:
        silent_mode: 静默模式，不显示普通消息，只在特定条件下触发彩蛋
    """
    # 跟踪使用次数
    count = _track_trigger("fortune_used")
    
    # 检查时间成就
    hour = datetime.now().hour
    if 5 <= hour < 7 and "morning_bird" not in _achievements:
        _unlock_achievement("morning_bird")
    elif 0 <= hour < 3 and "night_owl" not in _achievements:
        _unlock_achievement("night_owl")
    
    # 检查特殊日期
    special = check_special_date()
    if special and "special_day" not in _achievements:
        _unlock_achievement("special_day")
        return f"{special} 🎁 解锁成就：特殊日子！\n\n{random.choice(FORTUNE_MESSAGES)}"
    
    if silent_mode and _check_secret_rune("fortune"):
        if "persistent_seeker" not in _achievements:
            _unlock_achievement("persistent_seeker")
        return "🌌 你发现了隐藏的宇宙真理：代码即艺术！"
    
    # 连续 5 次获取运势
    if count >= 5 and "fortune_teller" not in _achievements:
        _unlock_achievement("fortune_teller")
    
    return random.choice(FORTUNE_MESSAGES)


def get_quote() -> tuple[str, str]:
    """获取名人名言"""
    count = _track_trigger("quote_used")
    
    # 收集 5 条名言解锁哲学家成就
    if count >= 5 and "philosopher" not in _achievements:
        _unlock_achievement("philosopher")
    
    return random.choice(QUOTES)


def check_konami(key: str) -> bool:
    """检查 Konami 代码输入
    
    Args:
        key: 输入的按键
        
    Returns:
        是否完成了 Konami 代码
    """
    global _konami_sequence, _konami_unlocked
    
    if _konami_unlocked:
        return True
    
    _konami_sequence.append(key.lower())
    
    # 保持序列长度不超过 Konami 代码长度
    if len(_konami_sequence) > len(_konami_code):
        _konami_sequence.pop(0)
    
    # 检查是否匹配
    if _konami_sequence == _konami_code:
        _konami_unlocked = True
        if "retro_gamer" not in _achievements:
            _unlock_achievement("retro_gamer")
        return True
    
    return False


def reset_konami():
    """重置 Konami 代码状态"""
    global _konami_sequence, _konami_unlocked
    _konami_sequence = []
    _konami_unlocked = False


def is_konami_unlocked() -> bool:
    """检查 Konami 代码是否已解锁"""
    return _konami_unlocked


def get_secret_message() -> str:
    """获取秘密消息（Konami 解锁后）"""
    secrets = [
        "🎉 恭喜！你解锁了 Konami 彩蛋！",
        "🕹️ 经典游戏玩家认证通过！",
        "💫 隐藏成就已解锁：复古游戏大师",
        "🌈 彩虹模式已激活（并没有这个功能）",
        "🤫 这是我们之间的秘密...",
    ]
    return random.choice(secrets)


def get_time_based_greeting() -> str:
    """根据时间获取问候语"""
    hour = datetime.now().hour
    
    if 5 <= hour < 12:
        return "🌅 早上好！新的一天开始了！"
    elif 12 <= hour < 14:
        return "☀️ 中午好！该休息一会儿了！"
    elif 14 <= hour < 18:
        return "🌤️ 下午好！继续加油！"
    elif 18 <= hour < 22:
        return "🌆 晚上好！工作辛苦了！"
    else:
        return "🌙 夜深了，早点休息吧！"


def get_random_fact() -> str:
    """获取随机冷知识"""
    count = _track_trigger("fact_used")
    
    # 阅读 10 条冷知识解锁求知者成就
    if count >= 10 and "knowledge_seeker" not in _achievements:
        _unlock_achievement("knowledge_seeker")
    
    facts = [
        "💻 Python 的名字来自蒙提·派森的飞行马戏团，而不是蟒蛇。",
        "🐧 Linux 的吉祥物 Tux 是一只企鹅。",
        "🌐 第一个网站 info.cern.ch 至今仍然在线！",
        "🔢 世界上第一个计算机 bug 是一只真正的飞蛾。",
        "📱 第一部手机重达 1.1 公斤。",
        "💾 保存图标 💾 代表的是软盘，现在的孩子可能都不认识它了。",
        "🎵 MP3 格式已经 30 多岁了。",
        "🔒 HTTPS 中的 S 代表 Secure（安全）。",
        "🌍 每天约有 350 万封电子邮件被发送。",
        "⌨️ QWERTY 键盘布局是为了防止打字机卡键而设计的。",
    ]
    return random.choice(facts)


def print_easter_egg_art():
    """打印彩蛋 ASCII 艺术"""
    art = r"""
    🥚🥚🥚🥚🥚🥚🥚🥚🥚🥚
    🥚              🥚
    🥚   FUTURE     🥚
    🥚     OSS      🥚
    🥚   EASTER     🥚
    🥚     EGG      🥚
    🥚              🥚
    🥚🥚🥚🥚🥚🥚🥚🥚🥚🥚
    
    ✨ 恭喜你发现了隐藏内容！✨
    """
    # 解锁艺术家成就
    if "artist" not in _achievements:
        _unlock_achievement("artist")
    print(art)


def generate_lucky_number() -> int:
    """生成今日幸运数字"""
    # 基于日期生成一个"伪随机"但每天固定的数字
    today = datetime.now().timetuple().tm_yday
    lucky = (today * 7 + 42) % 100 + 1
    
    # 如果是 77，解锁幸运之星成就
    if lucky == 77 and "lucky_star" not in _achievements:
        _unlock_achievement("lucky_star")
    
    return lucky


def check_special_date() -> Optional[str]:
    """检查是否是特殊日期"""
    today = datetime.now()
    month_day = (today.month, today.day)
    
    special_dates = {
        (1, 1): "🎊 新年快乐！",
        (2, 14): "💝 情人节快乐！",
        (3, 14): "🥧 圆周率日快乐！3.14159...",
        (4, 1): "🃏 愚人节快乐！小心被整蛊！",
        (5, 4): "🌟 原力与你同在！（星球大战日）",
        (6, 1): "🎈 儿童节快乐！",
        (7, 1): "🇨🇦 加拿大国庆日！",
        (8, 15): "🎑 日本终战纪念日",
        (9, 1): "📚 开学季到了！",
        (10, 24) : "👨‍💻 程序员节快乐！",
        (10, 31): "🎃 万圣节快乐！不给糖就捣蛋！",
        (11, 11): "🛍️ 双 11 购物节快乐！",
        (12, 25): "🎄 圣诞快乐！",
        (12, 31): "🎆 跨年夜快乐！",
    }
    
    return special_dates.get(month_day)


def _check_developer_easter_egg(config_path: str = "") -> bool:
    """检查是否触发开发者彩蛋
    
    触发条件：
    1. 配置文件路径包含 '.secret' 或 'hidden'
    2. 或者当前时间的秒数为 42
    3. 或者进程 ID 是回文数
    """
    triggered = False
    
    # 条件 1: 配置文件路径
    if '.secret' in config_path or 'hidden' in config_path.lower():
        if "config_explorer" not in _achievements:
            _unlock_achievement("config_explorer")
        triggered = True
    
    # 条件 2: 时间彩蛋 (42 是生命、宇宙以及一切的终极答案)
    if datetime.now().second == 42:
        if "time_traveler" not in _achievements:
            _unlock_achievement("time_traveler")
        triggered = True
    
    # 条件 3: PID 回文数
    pid = str(os.getpid())
    if pid == pid[::-1] and len(pid) > 1:
        if "palindromic_master" not in _achievements:
            _unlock_achievement("palindromic_master")
        triggered = True
    
    # 检查是否解锁秘密特工成就（触发所有开发者彩蛋）
    developer_achievements = {"config_explorer", "time_traveler", "palindromic_master"}
    if developer_achievements.issubset(_achievements) and "secret_agent" not in _achievements:
        _unlock_achievement("secret_agent")
    
    return triggered


def _get_hidden_config_message() -> str:
    """获取隐藏配置消息"""
    messages = [
        "🗝️ 你找到了隐藏的密钥！但其实什么用都没有...",
        "🕳️ 凝视深渊时，深渊也在凝视你的配置文件",
        "🎭 你以为这是彩蛋？不，这只是另一层伪装！",
        "🌀 欢迎来到递归彩蛋：这个彩蛋里面还有彩蛋！",
        "🔮 预言：你会把这个截图发到群里炫耀",
    ]
    return random.choice(messages)


def check_file_signature(filepath: str) -> Optional[str]:
    """检查文件是否有隐藏签名
    
    触发条件：当用户尝试加载一个名为 'easter_egg.py' 或 '__hidden__.py' 的文件时
    """
    filename = Path(filepath).name
    
    if filename in ['easter_egg.py', '__hidden__.py', 'surprise.py']:
        if "file_hunter" not in _achievements:
            _unlock_achievement("file_hunter")
        
        # 如果是__hidden__.py，额外解锁真实探索者成就
        if filename == '__hidden__.py' and "truth_seeker" not in _achievements:
            _unlock_achievement("truth_seeker")
        
        return "📜 检测到古老的神秘符号...这只是一个测试文件！"
    
    return None


def _generate_secret_hash(input_text: str) -> str:
    """生成秘密哈希
    
    如果输入文本的 MD5 哈希以 '0000' 开头，触发超级彩蛋
    （几乎不可能自然发生，需要刻意寻找）
    """
    md5_hash = hashlib.md5(input_text.encode()).hexdigest()
    
    if md5_hash.startswith('0000'):
        if "hash_master" not in _achievements:
            _unlock_achievement("hash_master")
        return f"🌟 奇迹发生了！MD5: {md5_hash} - 你是天选之子！"
    
    return f"普通哈希：{md5_hash[:8]}..."


def get_achievements() -> set:
    """获取所有已解锁的成就"""
    return _achievements.copy()


def get_all_achievements_info() -> dict:
    """获取所有成就信息（包括已解锁和未解锁）"""
    result = {}
    for ach_id, ach_info in ALL_ACHIEVEMENTS.items():
        result[ach_id] = {
            **ach_info,
            "unlocked": ach_id in _achievements
        }
    return result


def get_achievement_progress() -> tuple[int, int]:
    """获取成就进度 (已解锁数，总数)"""
    return len(_achievements), len(ALL_ACHIEVEMENTS)


def _print_achievement_notification(achievement: str):
    """打印成就解锁通知 - 优化样式"""
    if achievement not in ALL_ACHIEVEMENTS:
        return
    
    ach_info = ALL_ACHIEVEMENTS[achievement]
    icon = ach_info.get("icon", "🏆")
    name = ach_info.get("name", achievement)
    
    notification = f"""
╔═══════════════════════════════════════════╗
║   {icon}  成就解锁：{name:<18} ║
╠═══════════════════════════════════════════╣
║   {ach_info.get('desc', ''):<36} ║
╚═══════════════════════════════════════════╝
"""
    print(notification)


def print_achievements_list():
    """打印成就列表 - 精美样式"""
    unlocked = get_achievements()
    total = len(ALL_ACHIEVEMENTS)
    count = len(unlocked)
    
    print("\n" + "="*50)
    print(f"🏆  成就系统  ({count}/{total})")
    print("="*50)
    
    # 已解锁的成就
    if unlocked:
        print("\n✨ 已解锁:")
        for ach_id in sorted(unlocked):
            if ach_id in ALL_ACHIEVEMENTS:
                info = ALL_ACHIEVEMENTS[ach_id]
                print(f"   {info['icon']}  {info['name']}: {info['desc']}")
    
    # 未解锁的成就
    locked = set(ALL_ACHIEVEMENTS.keys()) - unlocked
    if locked:
        print("\n🔒 未解锁:")
        for ach_id in sorted(locked):
            info = ALL_ACHIEVEMENTS[ach_id]
            print(f"   🔒  {info['name']}: {info['desc']}")
    
    # 进度条
    progress = int(count / total * 20)
    bar = "█" * progress + "░" * (20 - progress)
    percentage = int(count / total * 100)
    
    print(f"\n进度：[{bar}] {percentage}%")
    print("="*50 + "\n")


__all__ = [
    "get_fortune",
    "get_quote", 
    "check_konami",
    "reset_konami",
    "is_konami_unlocked",
    "get_secret_message",
    "get_time_based_greeting",
    "get_random_fact",
    "print_easter_egg_art",
    "generate_lucky_number",
    "check_special_date",
    "check_file_signature",
    "get_achievements",
    "get_all_achievements_info",
    "get_achievement_progress",
    "print_achievements_list",
    "_check_developer_easter_egg",
    "_get_hidden_config_message",
]
