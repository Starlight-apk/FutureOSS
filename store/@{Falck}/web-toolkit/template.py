"""模板引擎"""
import re
import ast
from pathlib import Path
from typing import Any, Optional


class TemplateEngine:
    """简单模板引擎"""

    def __init__(self, root: str = "./templates"):
        self.root = root
        self._cache: dict[str, str] = {}
        self._ensure_root()

    def _ensure_root(self):
        """确保模板目录存在"""
        Path(self.root).mkdir(parents=True, exist_ok=True)

    def set_root(self, path: str):
        """设置模板根目录"""
        self.root = path
        self._ensure_root()
        self._cache.clear()

    def render(self, name: str, context: dict[str, Any]) -> str:
        """渲染模板"""
        template = self._load_template(name)
        return self._render_template(template, context)

    def _load_template(self, name: str) -> str:
        """加载模板"""
        if name in self._cache:
            return self._cache[name]

        template_path = Path(self.root) / name
        if not template_path.exists():
            raise FileNotFoundError(f"模板不存在: {name}")

        content = template_path.read_text(encoding="utf-8")
        self._cache[name] = content
        return content

    def _safe_eval(self, expression: str, context: dict) -> Any:
        """安全评估表达式（仅允许简单的属性访问和比较）"""
        # 只允许访问 context 中的变量
        # 支持的运算符: and, or, not, ==, !=, <, >, <=, >=, in
        # 不允许函数调用、导入、属性访问等
        
        # 使用 AST 解析并验证
        try:
            tree = ast.parse(expression, mode='eval')
        except SyntaxError:
            return False
        
        # 验证 AST 节点
        if not self._validate_ast(tree.body[0].value, set(context.keys())):
            return False
        
        # 在受限环境中评估
        try:
            return eval(expression, {"__builtins__": {}}, context)
        except Exception:
            return False

    def _validate_ast(self, node: ast.AST, allowed_names: set) -> bool:
        """验证 AST 只包含安全的操作"""
        if isinstance(node, ast.Name):
            return node.id in allowed_names or node.id in ('True', 'False', 'None')
        elif isinstance(node, ast.Constant):
            return True
        elif isinstance(node, ast.BoolOp):
            return all(self._validate_ast(v, allowed_names) for v in node.values)
        elif isinstance(node, ast.Compare):
            return (self._validate_ast(node.left, allowed_names) and 
                    all(self._validate_ast(c, allowed_names) for c in node.comparators))
        elif isinstance(node, ast.UnaryOp) and isinstance(node.op, ast.Not):
            return self._validate_ast(node.operand, allowed_names)
        elif isinstance(node, ast.Attribute):
            # 不允许属性访问（防止绕过安全限制）
            return False
        elif isinstance(node, ast.Call):
            # 不允许函数调用
            return False
        elif isinstance(node, ast.Subscript):
            # 允许简单的索引访问
            return (self._validate_ast(node.value, allowed_names) and 
                    self._validate_ast(node.slice, allowed_names))
        return False

    def _render_template(self, template: str, context: dict[str, Any]) -> str:
        """渲染模板内容"""
        # 替换 {{ variable }}
        def replace_var(match):
            var_name = match.group(1).strip()
            value = context.get(var_name, "")
            if isinstance(value, (dict, list)):
                import json
                return json.dumps(value, ensure_ascii=False)
            return str(value)

        result = re.sub(r'\{\{(.*?)\}\}', replace_var, template)

        # 处理 {% if condition %} ... {% endif %}
        result = self._process_if(result, context)

        # 处理 {% for item in list %} ... {% endfor %}
        result = self._process_for(result, context)

        return result

    def _process_if(self, template: str, context: dict) -> str:
        """处理 if 条件"""
        pattern = r'\{%\s*if\s+(.*?)\s*%\}(.*?){%\s*endif\s*%\}'

        def replace_if(match):
            condition = match.group(1).strip()
            content = match.group(2)
            # 安全条件评估
            value = self._safe_eval(condition, context)
            return content if value else ""

        return re.sub(pattern, replace_if, template, flags=re.DOTALL)

    def _process_for(self, template: str, context: dict) -> str:
        """处理 for 循环"""
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
                result += self._render_template(content, loop_context)
            return result

        return re.sub(pattern, replace_for, template, flags=re.DOTALL)
