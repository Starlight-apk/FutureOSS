"""日志系统 - 空壳，由日志插件提供实际功能"""
class Logger:
    """日志记录器（空壳）"""

    def info(self, msg: str, **kwargs):
        print(f"[INFO] {msg}")

    def warn(self, msg: str, **kwargs):
        print(f"[WARN] {msg}")

    def error(self, msg: str, **kwargs):
        print(f"[ERROR] {msg}")

    def debug(self, msg: str, **kwargs):
        print(f"[DEBUG] {msg}")
