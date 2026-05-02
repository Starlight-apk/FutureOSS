    capabilities: set[str] = set()
    main_file = plugin_dir / "main.py"

    if not main_file.exists():
        return capabilities

    with open(main_file, "r", encoding="utf-8") as f:
        source = f.read()

    tree = ast.parse(source)


    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            class_name = node.name
            if class_name.endswith("Provider"):
                cap_name = class_name.replace("Provider", "").lower()
                capabilities.add(cap_name)
            elif class_name.endswith("Mixin"):
                cap_name = class_name.replace("Mixin", "").lower()
                capabilities.add(cap_name)
            elif class_name.endswith("Support"):
                cap_name = class_name.replace("Support", "").lower()
                capabilities.add(cap_name)

        elif isinstance(node, ast.FunctionDef):
            func_name = node.name
            for decorator in node.decorator_list:
                if isinstance(decorator, ast.Name):
                    if decorator.id.startswith("provides_"):
                        cap_name = decorator.id.replace("provides_", "")
                        capabilities.add(cap_name)
                elif isinstance(decorator, ast.Attribute):
                    if decorator.attr.startswith("provides_"):
                        cap_name = decorator.attr.replace("provides_", "")
                        capabilities.add(cap_name)

        elif isinstance(node, ast.Import):
            for alias in node.names:
                if "circuit" in alias.name.lower() or "breaker" in alias.name.lower():
                    capabilities.add("circuit_breaker")
                elif "retry" in alias.name.lower():
                    capabilities.add("retry")
                elif "cache" in alias.name.lower():
                    capabilities.add("cache")

        elif isinstance(node, ast.ImportFrom):
            if node.module:
                if "circuit" in node.module.lower() or "breaker" in node.module.lower():
                    capabilities.add("circuit_breaker")
                elif "retry" in node.module.lower():
                    capabilities.add("retry")
                elif "cache" in node.module.lower():
                    capabilities.add("cache")

    return capabilities
