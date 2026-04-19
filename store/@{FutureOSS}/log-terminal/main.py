"""LogTerminal 日志与终端插件"""
import os
import json
import subprocess
import threading
import time
from oss.logger.logger import Log
from oss.plugin.types import Plugin, Response, register_plugin_type


class LogTerminalPlugin(Plugin):
    """日志与终端插件 - 提供日志查看和 SSH 终端功能"""

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
                author="FutureOSS",
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
            
            # 注册日志查看页面
            self.webui.register_page(
                path='/logs',
                content_provider=self._render_logs,
                nav_item={'icon': 'ri-file-list-3-line', 'text': '日志'}
            )
            
            # 注册终端页面
            self.webui.register_page(
                path='/terminal',
                content_provider=self._render_terminal,
                nav_item={'icon': 'ri-terminal-box-line', 'text': '终端'}
            )
            
            Log.ok("log-terminal", "已注册日志与终端页面到 WebUI 导航")
        else:
            Log.warn("log-terminal", "警告: 未找到 WebUI 依赖")

        # 注册 API 路由（通过 http-api）
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
        
        # 启动日志同步线程
        self._log_sync_thread = threading.Thread(target=self._log_sync_worker, daemon=True)
        self._log_sync_thread.start()
        
        # 添加初始化日志
        self.add_log_entry("info", "log-terminal", "日志与终端插件已启动")
        self.add_log_entry("tip", "log-terminal", "日志查看: /logs | SSH 终端: /terminal")
        
        # 尝试捕获系统日志输出
        self._hook_system_log()
        
        Log.ok("log-terminal", "日志与终端插件已启动")

    def _hook_system_log(self):
        """拦截系统日志输出到我们的缓冲区"""
        try:
            from oss.logger.logger import Log as SystemLog
            
            # 保存原始方法
            original_info = SystemLog.info
            original_warn = SystemLog.warn
            original_error = SystemLog.error
            original_tip = SystemLog.tip
            original_ok = SystemLog.ok
            
            # 创建包装方法
            plugin_instance = self
            
            @classmethod
            def wrapped_info(cls, tag: str, msg: str):
                original_info(tag, msg)
                plugin_instance.add_log_entry("info", tag, msg)
            
            @classmethod
            def wrapped_warn(cls, tag: str, msg: str):
                original_warn(tag, msg)
                plugin_instance.add_log_entry("warn", tag, msg)
            
            @classmethod
            def wrapped_error(cls, tag: str, msg: str):
                original_error(tag, msg)
                plugin_instance.add_log_entry("error", tag, msg)
            
            @classmethod
            def wrapped_tip(cls, tag: str, msg: str):
                original_tip(tag, msg)
                plugin_instance.add_log_entry("tip", tag, msg)
            
            @classmethod
            def wrapped_ok(cls, tag: str, msg: str):
                original_ok(tag, msg)
                plugin_instance.add_log_entry("ok", tag, msg)
            
            # 替换方法（注意：这只影响未来的调用）
            SystemLog.info = wrapped_info
            SystemLog.warn = wrapped_warn
            SystemLog.error = wrapped_error
            SystemLog.tip = wrapped_tip
            SystemLog.ok = wrapped_ok
            
            Log.info("log-terminal", "系统日志拦截器已安装")
        except Exception as e:
            Log.warn("log-terminal", f"无法拦截系统日志: {e}")

    def stop(self):
        Log.info("log-terminal", "日志与终端插件停止中...")
        self._running = False
        
        # 关闭所有 SSH 会话
        for session_id, session in list(self._ssh_sessions.items()):
            try:
                if 'process' in session:
                    session['process'].terminate()
            except Exception:
                pass
        
        self._ssh_sessions.clear()
        Log.ok("log-terminal", "日志与终端插件已停止")

    def _log_sync_worker(self):
        """日志同步工作线程 - 持续捕获项目日志"""
        try:
            # 尝试从多个位置读取日志
            log_files = [
                '/var/log/syslog',
                '/var/log/messages',
                os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'system.log'),
            ]
            
            last_positions = {}
            
            while self._running:
                # 检查日志文件
                for log_file in log_files:
                    if os.path.exists(log_file) and os.path.isfile(log_file):
                        try:
                            with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                                # 获取文件位置
                                if log_file not in last_positions:
                                    # 首次读取，跳到文件末尾
                                    f.seek(0, 2)  # 2 = SEEK_END
                                    last_positions[log_file] = f.tell()
                                else:
                                    f.seek(last_positions[log_file])
                                
                                # 读取新行
                                lines = f.readlines()
                                if lines:
                                    last_positions[log_file] = f.tell()
                                    for line in lines[-50:]:  # 每次最多读取50行
                                        line = line.strip()
                                        if line:
                                            self.add_log_entry("info", "system", line)
                        except Exception as e:
                            pass
                
                # 等待下一次同步
                time.sleep(2)
                
        except Exception as e:
            Log.error("log-terminal", f"日志同步线程异常: {e}")

    def add_log_entry(self, level: str, tag: str, message: str):
        """向日志缓冲区添加日志条目"""
        import time
        timestamp = time.strftime('%Y-%m-%d %H:%M:%S')
        entry = {
            'timestamp': timestamp,
            'level': level,
            'tag': tag,
            'message': message
        }
        with self._log_lock:
            self._log_buffer.append(entry)
            # 限制日志缓冲区大小
            if len(self._log_buffer) > 10000:
                self._log_buffer = self._log_buffer[-5000:]

    def _get_logs(self, limit=100):
        """获取日志列表"""
        with self._log_lock:
            return self._log_buffer[-limit:]

    def _check_ssh_installed(self):
        """检查 SSH 是否已安装"""
        try:
            result = subprocess.run(['which', 'sshd'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except Exception:
            return False

    def _install_ssh(self):
        """自动安装 SSH 服务"""
        try:
            Log.info("log-terminal", "正在安装 SSH 服务...")
            # 检测包管理器
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
            Log.error("log-terminal", f"安装 SSH 服务时出错: {e}")
            return False

    def _start_ssh_server(self, port=8022):
        """启动 SSH 服务器"""
        try:
            # 检查 SSH 服务器是否已在运行
            result = subprocess.run(['pgrep', '-f', 'sshd'], capture_output=True, timeout=3)
            if result.returncode == 0:
                Log.tip("log-terminal", "SSH 服务器已在运行")
                return True
            
            # 启动 SSH 服务器
            Log.info("log-terminal", f"正在启动 SSH 服务器 (端口: {port})...")
            subprocess.run(['sshd', '-p', str(port)], capture_output=True, timeout=10)
            
            # 验证是否启动成功
            time.sleep(1)
            result = subprocess.run(['pgrep', '-f', f'sshd.*{port}'], capture_output=True, timeout=3)
            if result.returncode == 0:
                Log.ok("log-terminal", f"SSH 服务器已启动 (端口: {port})")
                return True
            else:
                Log.error("log-terminal", "SSH 服务器启动失败")
                return False
        except Exception as e:
            Log.error("log-terminal", f"启动 SSH 服务器时出错: {e}")
            return False

    def _handle_connect_ssh(self, request):
        """处理 SSH 连接请求"""
        try:
            body = json.loads(request.body)
            port = body.get('port', 8022)
            auto_install = body.get('auto_install', True)
            
            # 检查 SSH 是否已安装
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
            
            # 启动 SSH 服务器
            if not self._start_ssh_server(port):
                return Response(
                    status=500,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': False, 'error': 'SSH 服务器启动失败'})
                )
            
            # 创建新的终端会话 (使用 script 命令创建伪终端)
            self._session_counter += 1
            session_id = self._session_counter
            
            try:
                # 使用 script 命令创建交互式终端
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
                
                Log.info("log-terminal", f"SSH 终端会话 #{session_id} 已创建")
                
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
                Log.error("log-terminal", f"创建终端会话失败: {e}")
                return Response(
                    status=500,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': False, 'error': str(e)})
                )
                
        except Exception as e:
            Log.error("log-terminal", f"SSH 连接请求异常: {e}")
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': False, 'error': str(e)})
            )

    def _handle_send_command(self, request):
        """处理发送命令到终端"""
        try:
            body = json.loads(request.body)
            session_id = body.get('session_id')
            command = body.get('command', '')
            
            if session_id not in self._ssh_sessions:
                return Response(
                    status=400,
                    headers={"Content-Type": "application/json"},
                    body=json.dumps({'success': False, 'error': '会话不存在'})
                )
            
            session = self._ssh_sessions[session_id]
            process = session['process']
            
            # 发送命令
            process.stdin.write(command + '\n')
            process.stdin.flush()
            
            # 读取输出
            time.sleep(0.5)  # 等待命令执行
            output = ""
            try:
                while True:
                    line = process.stdout.readline()
                    if not line:
                        break
                    output += line
            except Exception:
                pass
            
            return Response(
                status=200,
                headers={"Content-Type": "application/json"},
                body=json.dumps({
                    'success': True,
                    'output': output
                })
            )
        except Exception as e:
            Log.error("log-terminal", f"发送命令时出错: {e}")
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': False, 'error': str(e)})
            )

    def _handle_disconnect_ssh(self, request):
        """处理断开 SSH 连接"""
        try:
            body = json.loads(request.body)
            session_id = body.get('session_id')
            
            if session_id in self._ssh_sessions:
                session = self._ssh_sessions[session_id]
                try:
                    session['process'].terminate()
                except Exception:
                    pass
                del self._ssh_sessions[session_id]
                Log.info("log-terminal", f"SSH 终端会话 #{session_id} 已断开")
                return Response(
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
            Log.error("log-terminal", f"断开连接时出错: {e}")
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': False, 'error': str(e)})
            )

    def _handle_list_sessions(self, request):
        """列出所有 SSH 会话"""
        try:
            sessions = []
            for session_id, session in self._ssh_sessions.items():
                sessions.append({
                    'session_id': session_id,
                    'port': session['port'],
                    'created_at': session['created_at'],
                    'uptime': time.time() - session['created_at']
                })
            
            return Response(
                status=200,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': True, 'sessions': sessions})
            )
        except Exception as e:
            return Response(
                status=500,
                headers={"Content-Type": "application/json"},
                body=json.dumps({'success': False, 'error': str(e)})
            )

    def _handle_get_logs(self, request):
        """获取日志"""
        try:
            from urllib.parse import parse_qs, urlparse
            
            # 解析路径中的查询参数
            parsed = urlparse(request.path)
            params = parse_qs(parsed.query)
            limit = int(params.get('limit', [100])[0])
            source = params.get('source', ['buffer'])[0]  # buffer 或 file
            
            logs = []
            
            if source == 'buffer':
                # 从内存缓冲区获取
                logs = self._get_logs(limit)
            else:
                # 从系统日志文件获取
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
        """从系统日志文件读取日志"""
        logs = []
        log_files = [
            '/var/log/syslog',
            '/var/log/messages',
            '/var/log/kern.log',
        ]
        
        for log_file in log_files:
            if os.path.exists(log_file):
                try:
                    with open(log_file, 'r', encoding='utf-8', errors='ignore') as f:
                        lines = f.readlines()
                        for line in lines[-limit:]:
                            line = line.strip()
                            if line:
                                # 尝试解析 syslog 格式
                                # 格式: "Apr 12 10:30:45 hostname service[pid]: message"
                                import re
                                match = re.match(r'(\w+\s+\d+\s+\d+:\d+:\d+)\s+(\S+)\s+(\S+?)(?:\[\d+\])?:\s+(.*)', line)
                                if match:
                                    logs.append({
                                        'timestamp': match.group(1),
                                        'level': 'info',
                                        'tag': match.group(3),
                                        'message': match.group(4)
                                    })
                                else:
                                    logs.append({
                                        'timestamp': time.strftime('%b %d %H:%M:%S'),
                                        'level': 'info',
                                        'tag': 'system',
                                        'message': line
                                    })
                except Exception:
                    pass
        
        return logs[-limit:]

    def _render_logs(self) -> str:
        """渲染日志查看界面"""
        try:
            php_file = os.path.join(self.views_dir, 'logs.php')
            if not os.path.exists(php_file):
                return "<p>日志视图文件丢失</p>"
            return self._execute_php(php_file, {})
        except Exception as e:
            return f"<p>日志视图渲染出错: {e}</p>"

    def _render_terminal(self) -> str:
        """渲染终端界面"""
        try:
            php_file = os.path.join(self.views_dir, 'terminal.php')
            if not os.path.exists(php_file):
                return "<p>终端视图文件丢失</p>"
            return self._execute_php(php_file, {})
        except Exception as e:
            return f"<p>终端视图渲染出错: {e}</p>"

    def _execute_php(self, php_file: str, variables: dict) -> str:
        """执行 PHP 文件"""
        php_vars = ""
        for key, value in variables.items():
            if isinstance(value, str):
                escaped = value.replace('\\', '\\\\').replace("'", "\\'").replace("\n", "\\n")
                php_vars += f"${key} = '{escaped}';\n"
            else:
                php_vars += f"${key} = {value};\n"

        with open(php_file, 'r', encoding='utf-8') as f:
            php_content = f.read()

        tmp_file = os.path.join(os.path.dirname(php_file), '.temp_lt.php')
        try:
            with open(tmp_file, 'w', encoding='utf-8') as f:
                f.write(f"<?php\n{php_vars}\n?>\n{php_content}")
            result = subprocess.run(
                ["php", "-f", tmp_file],
                capture_output=True, text=True, timeout=10,
                encoding='utf-8', errors='replace'
            )
            return result.stdout if result.returncode == 0 else f"<pre>{result.stderr}</pre>"
        finally:
            try:
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)
            except Exception:
                pass


register_plugin_type("LogTerminalPlugin", LogTerminalPlugin)


def New():
    return LogTerminalPlugin()
