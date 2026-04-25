"""__hidden__ - 隐藏的秘密模块

这个文件本身就是一个彩蛋。
如果你发现了这个文件，说明你是一个真正的探索者。

触发方式：
1. 文件名本身就是触发条件 (__hidden__.py)
2. 尝试导入这个模块会显示特殊消息
3. 调用 reveal_truth() 会揭示终极秘密
"""

from oss.easter_eggs import check_file_signature, _unlock_achievement


def reveal_truth():
    """揭示终极秘密"""
    # 检查文件签名并解锁成就
    result = check_file_signature(__file__)
    
    print("""
    ╔═══════════════════════════════════════════════════╗
    ║                                                   ║
    ║   🌟 恭喜你找到了这个隐藏的文件！🌟               ║
    ║                                                   ║
    ║   你不是普通的用户，你是真正的探索者。           ║
    ║                                                   ║
    ║   记住：                                          ║
    ║   "代码不仅仅是工具，它是创造力的延伸。"          ║
    ║                                                   ║
    ║   继续探索，继续创造，继续改变世界。              ║
    ║                                                   ║
    ║   - Future OSS 开发团队                           ║
    ║                                                   ║
    ╚═══════════════════════════════════════════════════╝
    """)
    return "🎁 获得成就：truth_seeker"


def get_secret_code():
    """获取秘密代码"""
    # 这是一个永远返回 42 的函数
    # 因为 42 是生命、宇宙以及一切的终极答案
    return 42


# 自动执行的隐藏逻辑
if __name__ == "__main__":
    reveal_truth()
