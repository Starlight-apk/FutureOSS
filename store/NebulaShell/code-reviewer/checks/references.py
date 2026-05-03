class ReferenceCheck:
    STD_MODULES = {
        'os', 'sys', 'json', 're', 'time', 'datetime', 'pathlib',
        'typing', 'collections', 'functools', 'itertools', 'io',
        'string', 'math', 'random', 'hashlib', 'hmac', 'secrets',
        'urllib', 'http', 'email', 'html', 'xml', 'csv', 'configparser',
        'logging', 'warnings', 'traceback', 'inspect', 'importlib',
        'threading', 'multiprocessing', 'subprocess', 'socket',
        'asyncio', 'concurrent', 'queue', 'contextlib', 'abc',
        'enum', 'dataclasses', 'copy', 'pprint', 'textwrap',
        'struct', 'codecs', 'locale', 'gettext', 'argparse',
        'unittest', 'doctest', 'pdb', 'profile', 'timeit',
        'tempfile', 'glob', 'fnmatch', 'stat', 'fileinput',
        'shutil', 'pickle', 'shelve', 'sqlite3', 'dbm',
        'gzip', 'bz2', 'lzma', 'zipfile', 'tarfile',
        'base64', 'binascii', 'quopri', 'uu',
    }

    BUILTINS = {
        'print', 'len', 'str', 'int', 'float', 'bool', 'list', 'dict',
        'set', 'tuple', 'range', 'enumerate', 'zip', 'map', 'filter',
        'sorted', 'reversed', 'min', 'max', 'sum', 'abs', 'round',
        'isinstance', 'issubclass', 'type', 'id', 'hash', 'repr',
        'True', 'False', 'None', 'Exception', 'ValueError', 'TypeError',
        'KeyError', 'AttributeError', 'ImportError', 'FileNotFoundError',
        'IndexError', 'RuntimeError', 'StopIteration', 'GeneratorExit',
        'staticmethod', 'classmethod', 'property', 'super',
        'open', 'input', 'format', 'hex', 'oct', 'bin', 'chr', 'ord',
        'dir', 'vars', 'locals', 'globals', 'callable', 'getattr',
        'setattr', 'hasattr', 'delattr', 'exec', 'eval', 'compile',
        'any', 'all', 'slice', 'frozenset', 'bytearray', 'bytes',
        'memoryview', 'complex', 'divmod', 'pow', 'object',
        'dict', 'list', 'str', 'int', 'float', 'bool', 'set',
        'tuple', 'Exception', 'ValueError', 'TypeError', 'KeyError',
        'self', 'cls', 'args', 'kwargs',
    }

    def __init__(self, project_root: str = "."):
        self.project_root = Path(project_root)
        self._available_modules = set(self.STD_MODULES)
        self._scan_project_modules()

    def _scan_project_modules(self):
        if dir_path.exists():
            for item in dir_path.iterdir():
                if item.is_file() and item.name.endswith(".py") and item.name != "__init__.py":
                    module_name = item.name[:-3]
                    full_name = f"{base_name}.{module_name}"
                    self._available_modules.add(full_name)
                elif item.is_dir() and (item / "__init__.py").exists():
                    full_name = f"{base_name}.{item.name}"
                    self._available_modules.add(full_name)
                    self._scan_module_dir(item, full_name)

    def _scan_plugin_modules(self, plugin_dir: Path, base_name: str):
        if dir_path.exists():
            for item in dir_path.iterdir():
                if item.is_file() and item.name.endswith(".py") and item.name != "__init__.py":
                    module_name = item.name[:-3]
                    self._available_modules.add(f"{base_name}.{module_name}")
                elif item.is_dir() and (item / "__init__.py").exists():
                    self._add_module_from_dir(item, f"{base_name}.{item.name}")

    def check(self, filepath: str, content: str) -> list:
        issues = []
        file_path = Path(filepath)

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.startswith('oss.') or alias.name == 'oss':
                        continue
                    if alias.name in ('websockets', 'yaml', 'click'):
                        continue
                    if not self._is_module_available(alias.name, file_path):
                        issues.append({
                            "file": filepath,
                            "line": node.lineno,
                            "severity": "critical",
                            "type": "import_error",
                            "message": f"无法导入模块: {alias.name}"
                        })

            elif isinstance(node, ast.ImportFrom):
                if node.level and node.level > 0:
                    continue

                if node.module and (node.module.startswith('oss.') or node.module == 'oss'):
                    continue

                if node.module and node.module.split('.')[0] in ('websockets', 'yaml', 'click'):
                    continue

                if node.module:
                    if not self._is_module_available(node.module, file_path):
                        issues.append({
                            "file": filepath,
                            "line": node.lineno,
                            "severity": "critical",
                            "type": "import_error",
                            "message": f"无法导入模块: {node.module}"
                        })

        return issues

    def _check_variable_references(self, filepath: str, tree: ast.AST, content: str) -> list:
        issues = []

        for node in ast.walk(tree):
            if isinstance(node, ast.Attribute):
                if isinstance(node.value, ast.Name):
                    var_name = node.value.id
                    if var_name in ('None', 'True', 'False'):
                        issues.append({
                            "file": filepath,
                            "line": node.lineno,
                            "severity": "critical",
                            "type": "attribute_error",
                            "message": f"尝试访问 {var_name} 的属性: {node.attr}"
                        })

        return issues

    def _check_function_calls(self, filepath: str, tree: ast.AST, content: str) -> list:
        if module_name in self._available_modules:
            return True

        base_module = module_name.split('.')[0]
        if base_module in self.STD_MODULES:
            return True

        if module_name.startswith('oss.') or module_name == 'oss':
            return True

        third_party = {'websockets', 'yaml', 'click', 'requests', 'flask', 'django', 'numpy', 'pandas'}
        if module_name.split('.')[0] in third_party:
            return True

        if file_path:
            file_dir = file_path.parent
            sibling_module = file_dir / f"{module_name}.py"
            if sibling_module.exists():
                return True
            sibling_pkg = file_dir / module_name
            if sibling_pkg.is_dir() and (sibling_pkg / "__init__.py").exists():
                return True
            store_dir = self.project_root / "store"
            if store_dir.exists():
                for author_dir in store_dir.iterdir():
                    if author_dir.is_dir():
                        for plugin_dir in author_dir.iterdir():
                            if plugin_dir.is_dir() and plugin_dir.name == module_name.split('.')[0]:
                                return True

        return False

    def _is_name_defined(self, name: str, tree: ast.AST, line: int) -> bool:
        pass
