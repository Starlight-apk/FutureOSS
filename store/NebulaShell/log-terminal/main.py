
    def __init__(self):
        self.webui = None
        self.http_api = None
        self.views_dir = os.path.join(os.path.dirname(__file__), 'views')
        self._log_buffer = []
        self._log_lock = threading.Lock()
        self._ssh_sessions = {}
        self._session_counter = 0
        self._log_sync_thread = None
        self._running = False

    def meta(self):
        from oss.plugin.types import Metadata, PluginConfig, Manifest
        return Manifest(
            metadata=Metadata(
                name="log-terminal",
                version="1.0.0",
                author="NebulaShell",
                description="日志查看器与 SSH 终端"
            ),
            config=PluginConfig(enabled=True, args={}),
            dependencies=["http-api", "webui"]
        )

    def set_webui(self, webui):
        self.webui = webui

    def set_http_api(self, http_api):
        self.http_api = http_api

    def init(self, deps: dict = None):
        if self.webui:
            Log.info("log-terminal", "已获取 WebUI 引用")
            
            self.webui.register_page(
                path='/logs',
                content_provider=self._render_logs,
                nav_item={'icon': 'ri-file-list-3-line', 'text': '日志'}
            )
            
            self.webui.register_page(
                path='/terminal',
                content_provider=self._render_terminal,
                nav_item={'icon': 'ri-terminal-box-line', 'text': '终端'}
            )
            
            Log.ok("log-terminal", "已注册日志与终端页面到 WebUI 导航")
        else:
            Log.warn("log-terminal", "警告: 未找到 WebUI 依赖")

        if self.http_api and self.http_api.router:
            self.http_api.router.get("/api/logs/get", self._handle_get_logs)
            self.http_api.router.post("/api/terminal/connect", self._handle_connect_ssh)
            self.http_api.router.post("/api/terminal/send", self._handle_send_command)
            self.http_api.router.post("/api/terminal/disconnect", self._handle_disconnect_ssh)
            self.http_api.router.get("/api/terminal/sessions", self._handle_list_sessions)
            Log.ok("log-terminal", "已注册 API 路由")
        else:
            Log.warn("log-terminal", "警告: 未找到 http-api 依赖")

    def start(self):
        Log.info("log-terminal", "日志与终端插件启动中...")
        self._running = True
        
        self._log_sync_thread = threading.Thread(target=self._log_sync_worker, daemon=True)
        self._log_sync_thread.start()
        
        self.add_log_entry("info", "log-terminal", "日志与终端插件已启动")
        self.add_log_entry("tip", "log-terminal", "日志查看: /logs | SSH 终端: /terminal")
        
        self._hook_system_log()
        
        Log.ok("log-terminal", "日志与终端插件已启动")

    def _hook_system_log(self):
        try:
            log_files = [
                '/var/log/syslog',
                '/var/log/messages',
                os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'system.log'),
            ]
            
            last_positions = {}
            
            while self._running:
                for log_file in log_files:
                    if os.path.exists(log_file) and os.path.isfile(log_file):
                        try:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                if log_file not in last_positions:
                                    f.seek(0, 2)                                    last_positions[log_file] = f.tell()
                                else:
                                    f.seek(last_positions[log_file])
                                
                                lines = f.readlines()
                                if lines:
                                    last_positions[log_file] = f.tell()
                                    for line in lines[-50:]:                                        line = line.strip()
                                        if line:
                                            self.add_log_entry("info", "system", line)
                        except Exception as e:
                            import traceback
                            traceback.print_exc()
                
                time.sleep(2)
                
        except Exception as e:
            Log.error("log-terminal", f"日志同步线程异常: {type(e).__name__}: {e}")

    def add_log_entry(self, level: str, tag: str, message: str):
        with self._log_lock:
            return self._log_buffer[-limit:]

    def _check_ssh_installed(self):
        try:
            Log.info("log-terminal", "正在安装 SSH 服务...")
            for pkg_manager in ['apt-get', 'yum', 'dnf', 'pacman']:
                result = subprocess.run(['which', pkg_manager], capture_output=True, timeout=3)
                if result.returncode == 0:
                    if pkg_manager == 'apt-get':
                        subprocess.run([pkg_manager, 'update'], capture_output=True, timeout=30)
                        result = subprocess.run(
                            [pkg_manager, 'install', '-y', 'openssh-server'],
                            capture_output=True, text=True, timeout=120
                        )
                    elif pkg_manager in ['yum', 'dnf']:
                        result = subprocess.run(
                            [pkg_manager, 'install', '-y', 'openssh-server'],
                            capture_output=True, text=True, timeout=120
                        )
                    elif pkg_manager == 'pacman':
                        result = subprocess.run(
                            [pkg_manager, '-S', '--noconfirm', 'openssh'],
                            capture_output=True, text=True, timeout=120
                        )
                    
                    if result.returncode == 0:
                        Log.ok("log-terminal", "SSH 服务安装成功")
                        return True
                    else:
                        Log.error("log-terminal", f"SSH 服务安装失败: {result.stderr}")
                        return False
            
            Log.error("log-terminal", "未找到支持的包管理器")
            return False
        except Exception as e:
            Log.error("log-terminal", f"安装 SSH 服务时出错: {type(e).__name__}: {e}")
            return False

    def _start_ssh_server(self, port=8022):
        try:
            body = json.loads(request.body)
            port = body.get('port', 8022)
            auto_install = body.get('auto_install', True)
            
            if not self._check_ssh_installed():
                if auto_install:
                    if not self._install_ssh():
                        return Response(
                            status=500,
                            headers={"Content-Type": "application/json"},
                            body=json.dumps({'success': False, 'error': 'SSH 安装失败'})
                        )
                else:
                    return Response(
                        status=400,
                        headers={"Content-Type": "application/json"},
                        body=json.dumps({'success': False, 'error': 'SSH 未安装，请先安装 SSH 服务'})
                    )
            
            if not self._start_ssh_server(port):
                return Response(
                    status=500,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': False, 'error': 'SSH 服务器启动失败'})
                )
            
            self._session_counter += 1
            session_id = self._session_counter
            
            try:
                process = subprocess.Popen(
                    ['script', '-q', '-c', '/bin/bash', '/dev/null'],
                    stdin=subprocess.PIPE,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    bufsize=1
                )
                
                self._ssh_sessions[session_id] = {
                    'process': process,
                    'created_at': time.time(),
                    'port': port
                }
                
                Log.info("log-terminal", f"SSH 终端会话                
                return Response(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({
                        'success': True,
                        'session_id': session_id,
                        'message': 'SSH 终端已连接'
                    })
                )
            except Exception as e:
                Log.error("log-terminal", f"创建终端会话失败: {type(e).__name__}: {e}")
                return Response(
                    status=500,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': False, 'error': str(e)})
                )
                
        except Exception as e:
            Log.error("log-terminal", f"SSH 连接请求异常: {type(e).__name__}: {e}")
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': False, 'error': str(e)})
            )

    def _handle_send_command(self, request):
        try:
            body = json.loads(request.body)
            session_id = body.get('session_id')
            
            if session_id in self._ssh_sessions:
                session = self._ssh_sessions[session_id]
                try:
                    session['process'].terminate()
                except Exception as e:
                    import traceback; print(f"[main.py] 错误:{type(e).__name__}:{e}"); traceback.print_exc()
                    pass
                del self._ssh_sessions[session_id]
                Log.info("log-terminal", f"SSH 终端会话                return Response(
                    status=200,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': True, 'message': '已断开连接'})
                )
            else:
                return Response(
                    status=400,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': False, 'error': '会话不存在'})
                )
        except Exception as e:
            Log.error("log-terminal", f"断开连接时出错: {type(e).__name__}: {e}")
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': False, 'error': str(e)})
            )

    def _handle_list_sessions(self, request):
        try:
            from urllib.parse import parse_qs, urlparse
            
            parsed = urlparse(request.path)
            params = parse_qs(parsed.query)
            limit = int(params.get('limit', [100])[0])
            source = params.get('source', ['buffer'])[0]            
            logs = []
            
            if source == 'buffer':
                logs = self._get_logs(limit)
            else:
                logs = self._read_system_logs(limit)
            
            return Response(
                status=200,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': True, 'logs': logs})
            )
        except Exception as e:
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': False, 'error': str(e)})
            )

    def _read_system_logs(self, limit=100):
        try:
            logs = self._get_logs(limit=100)
            log_rows = ""
            for log in logs:
                level_class = {
                    'info': 'log-info',
                    'warn': 'log-warn',
                    'error': 'log-error',
                    'ok': 'log-ok',
                    'tip': 'log-tip'
                }.get(log['level'], 'log-info')
                log_rows += f
            
            html = f
            return html
        except Exception as e:
            return f"<p>日志视图渲染出错：{e}</p>"
    def _render_terminal(self) -> str:
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>SSH 终端</title>
    <link rel="stylesheet" href="/assets/remixicon.css">
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background:        .container { max-width: 1400px; margin: 0 auto; width: 100%; flex: 1; display: flex; flex-direction: column; }
        .card { background:        .card-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px; }
        .card-title { font-size: 18px; font-weight: 600; color:        .btn { padding: 8px 16px; border: none; border-radius: 6px; cursor: pointer; font-size: 14px; transition: all 0.3s; }
        .btn-primary { background:        .btn-primary:hover { background:        .btn-danger { background:        .btn-danger:hover { background:        .terminal-container { flex: 1; background:        .terminal-output { flex: 1; overflow-y: auto; white-space: pre-wrap; word-wrap: break-word; color:        .terminal-input { display: flex; margin-top: 10px; }
        .terminal-input input { flex: 1; background:        .terminal-input input:focus { border-color:        .status-bar { display: flex; justify-content: space-between; padding: 10px; background:        .status-item { display: flex; align-items: center; gap: 8px; }
        .status-dot { width: 10px; height: 10px; border-radius: 50%; }
        .status-connected { background:        .status-disconnected { background:        ::-webkit-scrollbar { width: 8px; }
        ::-webkit-scrollbar-track { background:        ::-webkit-scrollbar-thumb { background:    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <div class="card-header">
                <h2 class="card-title"><i class="ri-terminal-box-line"></i> SSH 终端</h2>
                <div>
                    <button class="btn btn-primary" id="connectBtn" onclick="connectTerminal()">连接</button>
                    <button class="btn btn-danger" id="disconnectBtn" onclick="disconnectTerminal()" style="display:none;">断开</button>
                </div>
            </div>
            <div class="status-bar">
                <div class="status-item">
                    <span class="status-dot status-disconnected" id="statusDot"></span>
                    <span id="statusText">未连接</span>
                </div>
                <div class="status-item">
                    <span>会话 ID: <strong id="sessionId">-</strong></span>
                </div>
            </div>
        </div>
        <div class="terminal-container">
            <div class="terminal-output" id="terminalOutput">欢迎使用 SSH 终端！点击"连接"按钮开始...</div>
            <div class="terminal-input">
                <input type="text" id="commandInput" placeholder="输入命令..." disabled onkeypress="handleKeyPress(event)">
            </div>
        </div>
    </div>
    <script>
        let sessionId = null;
        const output = document.getElementById('terminalOutput');
        const input = document.getElementById('commandInput');
        const connectBtn = document.getElementById('connectBtn');
        const disconnectBtn = document.getElementById('disconnectBtn');
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        const sessionIdEl = document.getElementById('sessionId');

        function connectTerminal() {
            output.textContent = '正在连接...';
            fetch('/api/terminal/connect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({port: 8022, auto_install: true})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    sessionId = data.session_id;
                    sessionIdEl.textContent = sessionId;
                    statusDot.className = 'status-dot status-connected';
                    statusText.textContent = '已连接';
                    input.disabled = false;
                    connectBtn.style.display = 'none';
                    disconnectBtn.style.display = 'inline-block';
                    output.textContent = 'SSH 终端已连接。输入命令开始使用...
';
                    input.focus();
                } else {
                    output.textContent = '连接失败：' + data.error;
                }
            })
            .catch(e => {
                output.textContent = '连接错误：' + e.message;
            });
        }

        function disconnectTerminal() {
            if (!sessionId) return;
            fetch('/api/terminal/disconnect', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: sessionId})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    sessionId = null;
                    sessionIdEl.textContent = '-';
                    statusDot.className = 'status-dot status-disconnected';
                    statusText.textContent = '未连接';
                    input.disabled = true;
                    connectBtn.style.display = 'inline-block';
                    disconnectBtn.style.display = 'none';
                    output.textContent += '
会话已断开。';
                }
            });
        }

        function sendCommand(cmd) {
            if (!sessionId) return;
            fetch('/api/terminal/send', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({session_id: sessionId, command: cmd})
            })
            .then(r => r.json())
            .then(data => {
                if (data.success) {
                    output.textContent += '$ ' + cmd + '
' + data.output;
                    output.scrollTop = output.scrollHeight;
                } else {
                    output.textContent += '
命令执行失败：' + data.error;
                }
            });
        }

        function handleKeyPress(e) {
            if (e.key === 'Enter') {
                sendCommand(input.value);
                input.value = '';
            }
        }
    </script>
</body>
</html>"""
            return html
        except Exception as e:
            return f"<p>终端视图渲染出错：{e}</p>"

register_plugin_type("LogTerminalPlugin", LogTerminalPlugin)


def New():
    return LogTerminalPlugin()
