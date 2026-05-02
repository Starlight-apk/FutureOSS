

def register(injector):
    
    from pathlib import Path
    
    current_file = Path(__file__)
    plugin_dir = current_file.parent.parent
    
    main_file = plugin_dir / "main.py"
    
    safe_builtins_dict = {
        "True": True, "False": False, "None": None,
        "dict": dict, "list": list, "str": str, "int": int,
        "float": float, "bool": bool, "tuple": tuple, "set": set,
        "len": len, "range": range, "enumerate": enumerate,
        "zip": zip, "map": map, "filter": filter,
        "sorted": sorted, "reversed": reversed,
        "min": min, "max": max, "sum": sum, "abs": abs,
        "round": round, "isinstance": isinstance, "issubclass": issubclass,
        "type": type, "id": id, "hash": hash, "repr": repr,
        "print": print, "object": object, "property": property,
        "staticmethod": staticmethod, "classmethod": classmethod,
        "super": super, "iter": iter, "next": next,
        "any": any, "all": all, "callable": callable,
        "hasattr": hasattr, "getattr": getattr, "setattr": setattr,
        "Exception": Exception, "BaseException": BaseException,
    }
    safe_globals = {
        "bi": safe_builtins_dict,
        "__name__": "plugin.auto-dependency",
        "__package__": "plugin.auto-dependency",
        "__file__": str(main_file),
        "Path": Path,
    }
    safe_globals["__builtins__"] = safe_builtins_dict
    
    try:
        with open(main_file, "r", encoding="utf-8") as f:
            source = f.read()
        
        code = compile(source, str(main_file), "exec")
        exec(code, safe_globals)
        
        new_func = safe_globals.get("New")
        if new_func and callable(new_func):
            plugin_instance = new_func()
            
            plugin_instance.init({
                "scan_dirs": ["store"],
                "auto_install": True
            })
            
            plugin_instance.register_pl_functions(injector)
            
    except Exception as e:
        print(f"[auto-dependency] PL 注册失败：{e}")
