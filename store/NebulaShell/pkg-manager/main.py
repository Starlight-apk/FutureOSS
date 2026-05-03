def _gitee_request(url, timeout=30):
    req = urllib.request.Request(url)
    req.add_header("User-Agent", "NebulaShell-PkgManager")
    if GITEE_TOKEN:
        req.add_header("Authorization", f"token {GITEE_TOKEN}")
    return urllib.request.urlopen(req, timeout=timeout)


class PkgManagerPlugin(Plugin):
    def __init__(self):
        if not self.webui:
            Log.warn("pkg-manager", "警告: 未找到 WebUI 依赖")
            return

        self.webui.register_page(
            path='/packages',
            content_provider=self._packages_content,
            nav_item={'icon': 'ri-apps-line', 'text': '插件管理'}
        )
        self.webui.register_page(
            path='/store',
            content_provider=self._store_content,
            nav_item={'icon': 'ri-store-2-line', 'text': '插件商店'}
        )
        Log.info("pkg-manager", "已注册到 WebUI 导航")

    def start(self):
        try:
            plugins = self._get_installed_plugins()
            plugin_rows = ""
            for pkg_name, info in plugins.items():
                status_class = "success" if info.get('enabled', False) else "secondary"
                status_text = "已启用" if info.get('enabled', False) else "已禁用"
                safe_pkg_name = html.escape(pkg_name)
                safe_version = html.escape(str(info.get('version', '未知')))
                safe_author = html.escape(str(info.get('author', '未知')))
                plugin_rows += f"<tr><td>{safe_pkg_name}</td><td>{safe_version}</td><td>{safe_author}</td></tr>"
            
            html = f"<table>{plugin_rows}</table>"
            return html
        except Exception as e:
            return f"<p>插件管理页面渲染出错: {e}</p>"

    def _store_content(self) -> str:
        try:
            html = ""
            for pkg in self._fetch_remote_plugins():
                safe_name = html.escape(pkg.get('name', ''))
                safe_desc = html.escape(pkg.get('description', ''))
                safe_version = html.escape(pkg.get('version', '未知'))
                safe_author = html.escape(pkg.get('author', '未知'))
                action_btn = '<button class="btn btn-success">安装</button>'
                html += f"""<div class="plugin-card">
                    <div class="plugin-icon"><i class="ri-plug-line"></i></div>
                    <h3>{safe_name}</h3>
                    <p class="plugin-desc">{safe_desc}</p>
                    <div class="plugin-meta">
                        <span>版本: {safe_version}</span>
                        <span>作者: {safe_author}</span>
                    </div>
                    <div class="plugin-actions">
                        {action_btn}
                    </div>
                </div>"""
            html = f"""<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>插件商店</title>
    <link rel="stylesheet" href="/assets/remixicon.css">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background: #f5f5f5; }}
        .container {{ max-width: 1400px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }}
        .card-header {{ margin-bottom: 20px; }}
        .card-title {{ font-size: 18px; font-weight: 600; color: #333; }}
        .btn {{ padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; transition: all 0.3s; }}
        .btn-success {{ background: #67c23a; color: white; }}
        .btn-success:hover {{ background: #5daf34; }}
        .btn-secondary {{ background: #909399; color: white; }}
        .plugins-grid {{ display: grid; grid-template-columns: repeat(auto-fill, minmax(300px, 1fr)); gap: 20px; }}
        .plugin-card {{ background: white; border-radius: 8px; padding: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.06); }}
        .plugin-card:hover {{ transform: translateY(-5px); box-shadow: 0 5px 15px rgba(0,0,0,0.1); }}
        .plugin-icon {{ width: 48px; height: 48px; background: #ecf5ff; border-radius: 12px; display: flex; align-items: center; justify-content: center; margin-bottom: 12px; }}
        .plugin-card h3 {{ font-size: 16px; color: #333; margin-bottom: 8px; }}
        .plugin-desc {{ color: #666; font-size: 13px; margin-bottom: 12px; }}
        .plugin-meta {{ display: flex; justify-content: space-between; font-size: 12px; color: #999; }}
        .plugin-actions {{ display: flex; gap: 10px; }}
    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h2 class="card-title"><i class="ri-store-line"></i> 插件商店</h2>
            </div>
            <div class="plugins-grid">
                {html}
            </div>
        </div>
    </div>
    <script>
        function installPlugin(name) {{
            fetch('/api/plugins/install', {{
                method: 'POST',
                headers: {{'Content-Type': 'application/json'}},
                body: JSON.stringify({{plugin: name}})
            }}).then(r => r.json()).then(data => {{
                if (data.success) {{
                    alert('安装成功!');
                    location.reload();
                }} else {{
                    alert('安装失败: ' + data.error);
                }}
            }});
        }}
    </script>
</body>
</html>"""
            return html
        except Exception as e:
            return f"<p>插件商店页面渲染出错: {e}</p>"



    def _handle_list_plugins(self, request):
        plugin_name = request.path_params.get('name', '')
        schema = self._load_config_schema(plugin_name)
        current = self._load_plugin_config(plugin_name)
        return Response(status=200, headers={"Content-Type": "application/json"}, body=json.dumps({
            "schema": schema,
            "current": current
        }, ensure_ascii=False))

    def _handle_save_config(self, request):
        plugin_name = request.path_params.get('name', '')
        info = self._get_plugin_detailed_info(plugin_name)
        return Response(status=200, headers={"Content-Type": "application/json"}, body=json.dumps(info, ensure_ascii=False))

    def _handle_uninstall(self, request):
        try:
            plugins = self._fetch_remote_plugins()
            return Response(status=200, headers={"Content-Type": "application/json"}, body=json.dumps(plugins, ensure_ascii=False))
        except Exception as e:
            return Response(status=500, body=json.dumps({"error": str(e)}))

    def _handle_store_install(self, request):
        import time
        now = time.time()
        if self._remote_cache and (now - self._cache_time) < self._cache_ttl:
            return self._remote_cache

        plugins = []
        try:
            store_url = f"{GITEE_API_BASE}/store"
            for attempt in range(3):
                try:
                    with _gitee_request(store_url, timeout=15) as resp:
                        dirs = json.loads(resp.read().decode("utf-8"))
                    break
                except Exception as e:
                    if attempt < 2:
                        time.sleep(1 + attempt)
                        continue
                    raise

            time.sleep(0.5)

            for dir_info in dirs:
                if dir_info.get("type") != "dir":
                    continue
                author = dir_info.get("name", "")
                if not author.startswith("@{"):
                    continue

                author_url = f"{GITEE_API_BASE}/store/{urllib.parse.quote(author, safe='')}"
                for attempt in range(3):
                    try:
                        with _gitee_request(author_url, timeout=15) as resp:
                            plugin_dirs = json.loads(resp.read().decode("utf-8"))
                        break
                    except Exception as e:
                        import traceback; print(f"[main.py] 错误:{type(e).__name__}:{e}"); traceback.print_exc()
                        if attempt < 2:
                            time.sleep(1 + attempt)
                            continue
                        raise

                time.sleep(0.5)

                for plugin_dir in plugin_dirs:
                    if plugin_dir.get("type") != "dir":
                        continue
                    plugin_name = plugin_dir.get("name", "")

                    manifest_url = f"{GITEE_API_BASE}/store/{urllib.parse.quote(author, safe='')}/{plugin_name}/manifest.json"
                    manifest = {}
                    for attempt in range(3):
                        try:
                            with _gitee_request(manifest_url, timeout=15) as resp:
                                manifest = json.loads(resp.read().decode("utf-8"))
                            break
                        except Exception as e:
                            import traceback; print(f"[main.py] 错误:{type(e).__name__}:{e}"); traceback.print_exc()
                            if attempt < 2:
                                time.sleep(1 + attempt)
                                continue

                    plugins.append({
                        "name": plugin_name,
                        "author": author,
                        "full_name": f"{author}/{plugin_name}",
                        "metadata": manifest.get("metadata", {}),
                        "dependencies": manifest.get("dependencies", []),
                        "has_config": False,
                        "is_installed": self._is_plugin_installed(plugin_name, author)
                    })

                time.sleep(0.5)

            self._remote_cache = plugins
            self._cache_time = now
        except Exception as e:
            Log.error("pkg-manager", f"获取远程插件列表失败: {type(e).__name__}: {e}")

        return plugins

    def _install_from_gitee(self, plugin_name: str, author: str) -> bool:
        import time
        try:
            api_url = f"{GITEE_API_BASE}/store/{author}/{plugin}/{sub_dir}"
            with _gitee_request(api_url, timeout=15) as resp:
                items = json.loads(resp.read().decode("utf-8"))

            local_dir.mkdir(parents=True, exist_ok=True)
            for item in items:
                if item.get("type") == "file":
                    filename = item.get("name")
                    raw_url = f"{GITEE_RAW_BASE}/store/{author}/{plugin}/{sub_dir}/{filename}"
                    try:
                        with _gitee_request(raw_url, timeout=15) as resp:
                            content = resp.read()
                        with open(local_dir / filename, 'wb') as f:
                            f.write(content)
                    except:
                        pass
                elif item.get("type") == "dir":
                    self._download_dir_raw(author, plugin, f"{sub_dir}/{item.get('name')}", local_dir / item.get("name"))
        except:
            pass


    def _scan_all_plugins(self) -> list:
        plugin_dir = self.store_dir / author / plugin_name
        return (plugin_dir / "main.py").exists()

    def _find_plugin_dir(self, plugin_name: str) -> Path | None:
        plugin_dir = self._find_plugin_dir(plugin_name)
        if not plugin_dir:
            return {}
        schema_path = plugin_dir / "config.json"
        if not schema_path.exists():
            return {}
        with open(schema_path, 'r', encoding='utf-8') as f:
            return json.load(f)

    def _load_plugin_config(self, plugin_name: str) -> dict:
        if self.storage:
            storage_instance = self.storage.get_storage("pkg-manager")
            return storage_instance.get(f"plugin_config.{plugin_name}", {})
        return {}

    def _get_plugin_detailed_info(self, plugin_name: str) -> dict:
        return {}
