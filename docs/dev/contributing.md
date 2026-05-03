# 贡献指南

## 提交规范

采用 Conventional Commits 格式：

```
<type>: <描述>

feat: 新功能
fix: 修复 bug
refactor: 代码重构
docs: 文档变更
test: 测试相关
chore: 构建/工具/依赖
perf: 性能优化
style: 代码风格调整
```

## 开发环境

```bash
# 克隆并安装
git clone https://github.com/Starlight-apk/NebulaShell.git
cd NebulaShell
python -m venv venv
source venv/bin/activate
pip install -r requirements-dev.txt

# 创建特性分支
git checkout -b feature/your-feature
```

## 代码规范

- Python 代码遵循 PEP 8
- 使用 `black` 格式化（行长度 88）
- 使用 `pylint` 进行静态检查

```bash
# 代码格式化
black oss/ store/

# 语法检查
python -m pylint oss/ store/ --exit-zero
```

## 语法检查

所有 `.py` 文件必须通过 `py_compile` 检查：

```bash
find . -name "*.py" \
  -not -path "./venv/*" \
  -not -path "./.git/*" \
  | xargs -I{} python3 -m py_compile {}
```

## 测试

```bash
pytest oss/tests/
```

## Pull Request

1. 确保代码通过语法检查和测试
2. 更新相关文档
3. 提交 PR 时描述变更内容和动机
