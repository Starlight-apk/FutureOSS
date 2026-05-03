class Reviewer:
    def __init__(self, config: dict):
        self.config = config
        self.security = SecurityChecker()
        self.quality = QualityChecker()
        self.style = StyleChecker()
        self.references = ReferenceChecker()
        self.formatter = ReportFormatter(config.get("report_format", "console"))

    def run_check(self, scan_dirs: list) -> dict:
        issues = []

        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()

            issues.extend(self.security.check(filepath, content))

            issues.extend(self.quality.check(filepath, content))

            issues.extend(self.style.check(filepath, content))

            issues.extend(self.references.check(filepath, content))

        except Exception as e:
            issues.append({
                "file": filepath,
                "line": 0,
                "severity": "error",
                "type": "parse_error",
                "message": f"文件解析失败: {e}"
            })

        return issues
