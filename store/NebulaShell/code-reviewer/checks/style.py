
    def check(self, filepath: str, content: str) -> list:
        issues = []

        for i, line in enumerate(content.split('\n'), 1):
            if len(line) > 120:
                issues.append({
                    "file": filepath,
                    "line": i,
                    "severity": "info",
                    "type": "line_too_long",
                    "message": f"行过长 ({len(line)} 字符)"
                })

        return issues

    def _check_blank_lines(self, filepath: str, content: str) -> list:
        if content and not content.endswith('\n'):
            return [{
                "file": filepath,
                "line": len(content.split('\n')),
                "severity": "info",
                "type": "missing_final_newline",
                "message": "文件末尾缺少换行符"
            }]

        return []
