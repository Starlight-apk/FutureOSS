
    def check(self, filepath: str, content: str) -> list:
        issues = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    lines = node.end_lineno - node.lineno
                    if lines > 100:
                        issues.append({
                            "file": filepath,
                            "line": node.lineno,
                            "severity": "warning",
                            "type": "long_function",
                            "message": f"函数 {node.name} 过长 ({lines} 行)"
                        })
        except:
            pass

        return issues

    def _check_parameter_count(self, filepath: str, content: str) -> list:
        issues = []

        try:
            tree = ast.parse(content)
            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    complexity = self._calculate_complexity(node)
                    if complexity > 10:
                        issues.append({
                            "file": filepath,
                            "line": node.lineno,
                            "severity": "warning",
                            "type": "high_complexity",
                            "message": f"函数 {node.name} 复杂度过高 (圈复杂度: {complexity})"
                        })
        except:
            pass

        return issues

    def _calculate_complexity(self, node: ast.AST) -> int:
