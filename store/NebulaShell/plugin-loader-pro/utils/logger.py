
class ProLogger:
    _COLORS = {
        "reset": "\033[0m",
        "white": "\033[0;37m",
        "yellow": "\033[1;33m",
        "blue": "\033[1;34m",
        "red": "\033[1;31m",
    }

    @staticmethod
    def _colorize(text: str, color: str) -> str:
        tag = ProLogger._colorize(f"[pro:{component}]", "white")
        msg = ProLogger._colorize(message, "white")
        print(f"{tag} {msg}")

    @staticmethod
    def warn(component: str, message: str):
        tag = ProLogger._colorize(f"[pro:{component}]", "red")
        icon = ProLogger._colorize("✗", "red")
        msg = ProLogger._colorize(message, "red")
        print(f"{tag} {icon} {msg}")

    @staticmethod
    def debug(component: str, message: str):
        tag = ProLogger._colorize(f"[pro:{component}]", "blue")
        icon = ProLogger._colorize("→", "blue")
        msg = ProLogger._colorize(message, "blue")
        print(f"{tag} {icon} {msg}")
