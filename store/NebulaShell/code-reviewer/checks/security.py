
    def check(self, filepath: str, content: str) -> list:
        issues = []
        patterns = ['password', 'secret', 'token', 'api_key', 'access_token']

        for i, line in enumerate(content.split('\n'), 1):
            stripped = line.strip()
            if stripped.startswith('                continue

            for pattern in patterns:
                if pattern + ' = "' in line.lower() or pattern + " = '" in line.lower():
                    issues.append({
                        "file": filepath,
                        "line": i,
                        "severity": "critical",
                        "type": "hardcoded_secret",
                        "message": f"发现硬编码密钥: {line.strip()[:50]}"
                    })

        return issues

    def _check_dangerous_functions(self, filepath: str, content: str) -> list:
        issues = []

        if '../' in content and 'open(' in content:
            issues.append({
                "file": filepath,
                "line": 0,
                "severity": "warning",
                "type": "path_traversal_risk",
                "message": "可能存在路径穿越漏洞"
            })

        return issues
