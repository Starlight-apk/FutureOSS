
    def __init__(self, root: str = "./templates", max_depth: int = 10):
        self.root = root
        self._cache: dict[str, str] = {}
        self.max_depth = max_depth
        self._ensure_root()

    def _ensure_root(self):
        self.root = path
        self._ensure_root()
        self._cache.clear()

    def render(self, name: str, context: dict[str, Any]) -> str:
        if name in self._cache:
            return self._cache[name]

        template_path = Path(self.root) / name
        if not template_path.exists():
            raise FileNotFoundError(f"模板不存在: {name}")

        content = template_path.read_text(encoding="utf-8")
        self._cache[name] = content
        return content

    def _safe_eval(self, expression: str, context: dict) -> Any:
        if isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Name):
            return context.get(node.id, False)
        elif isinstance(node, ast.BoolOp):
            if isinstance(node.op, ast.And):
                return all(self._eval_ast(v, context) for v in node.values)
            elif isinstance(node.op, ast.Or):
                return any(self._eval_ast(v, context) for v in node.values)
        elif isinstance(node, ast.Compare):
            return self._eval_compare(node, context)
        elif isinstance(node, ast.UnaryOp):
            if isinstance(node.op, ast.Not):
                return not self._eval_ast(node.operand, context)
        elif isinstance(node, ast.Subscript):
            return self._eval_subscript(node, context)
        return False

    def _eval_compare(self, node: ast.Compare, context: dict) -> bool:
        value = self._eval_ast(node.value, context)
        key = self._eval_ast(node.slice, context)
        if isinstance(value, (dict, list, str)):
            return value[key]
        return None

    def _validate_ast(self, node: ast.AST, allowed_names: set) -> bool:
        
        Args:
            template: 模板内容
            context: 上下文变量
            depth: 当前递归深度
        
        Raises:
            RecursionError: 当嵌套深度超过 max_depth 时
        if depth > self.max_depth:
            raise RecursionError(
                f"模板嵌套深度超过限制 ({self.max_depth})，可能存在无限递归"
            )
        
        def replace_var(match):
            var_name = match.group(1).strip()
            value = context.get(var_name, "")
            if isinstance(value, (dict, list)):
                import json
                return json.dumps(value, ensure_ascii=False)
            return str(value)

        result = re.sub(r'\{\{(.*?)\}\}', replace_var, template)

        result = self._process_if(result, context, depth)

        result = self._process_for(result, context, depth)

        return result

    def _process_if(self, template: str, context: dict, depth: int = 0) -> str:
        pattern = r'\{%\s*for\s+(\w+)\s+in\s+(\w+)\s*%\}(.*?){%\s*endfor\s*%\}'

        def replace_for(match):
            item_name = match.group(1)
            list_name = match.group(2)
            content = match.group(3)

            items = context.get(list_name, [])
            if not isinstance(items, list):
                return ""

            result = ""
            for item in items:
                loop_context = {**context, item_name: item}
                result += self._render_template(content, loop_context, depth + 1)
            return result

        return re.sub(pattern, replace_for, template, flags=re.DOTALL)
