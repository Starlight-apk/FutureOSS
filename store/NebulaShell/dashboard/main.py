
    def __init__(self):
        self.webui = None
        self.views_dir = os.path.join(os.path.dirname(__file__), 'views')
        self._start_time = time.time()        self._history_len = 60
        self._cpu_history = deque(maxlen=self._history_len)
        self._ram_history = deque(maxlen=self._history_len)
        self._net_recv_history = deque(maxlen=self._history_len)
        self._net_sent_history = deque(maxlen=self._history_len)
        self._disk_read_history = deque(maxlen=self._history_len)
        self._disk_write_history = deque(maxlen=self._history_len)
        self._net_latency_history = deque(maxlen=self._history_len)
        self._last_net = None
        self._last_disk = None

    def meta(self):
        from oss.plugin.types import Metadata, PluginConfig, Manifest
        return Manifest(
            metadata=Metadata(
                name="dashboard",
                version="2.0.0",
                author="NebulaShell",
                description="WebUI 仪表盘"
            ),
            config=PluginConfig(enabled=True, args={}),
            dependencies=["http-api", "webui"]
        )

    def set_webui(self, webui):
        self.webui = webui

    def init(self, deps: dict = None):
        if self.webui:
            Log.info("dashboard", "已获取 WebUI 引用")
            self.webui.register_page(
                path='/dashboard',
                content_provider=self._render_content,
                nav_item={'icon': 'ri-dashboard-line', 'text': '仪表盘'}
            )
            if hasattr(self.webui, 'server') and self.webui.server:
                self.webui.server.router.get("/api/dashboard/stats", self._handle_stats_api)
                self.webui.server.router.get("/api/dashboard/history", self._handle_history_api)
            Log.info("dashboard", "已注册到 WebUI 导航")
        else:
            Log.warn("dashboard", "警告: 未找到 WebUI 依赖")

    def _get_uptime_str(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            start = time.time()
            s.connect(('8.8.8.8', 53))
            elapsed = (time.time() - start) * 1000            s.close()
            return round(elapsed, 1)
        except Exception as e:
            import traceback; print(f"[main.py] 错误:{type(e).__name__}:{e}"); traceback.print_exc()
            return 0.0

    def _get_network_interfaces(self):
        try:
            interfaces = []
            addrs = psutil.net_if_addrs()
            stats = psutil.net_if_stats()
            for name, addr_list in addrs.items():
                if name == 'lo':
                    continue
                info = {'name': name, 'ip': 'N/A', 'mac': 'N/A', 'is_up': False, 'speed': 0}
                for addr in addr_list:
                    if addr.family == socket.AF_INET:
                        info['ip'] = addr.address
                    elif hasattr(psutil, 'AF_LINK') and addr.family == psutil.AF_LINK:
                        info['mac'] = addr.address
                if name in stats:
                    info['is_up'] = stats[name].isup
                    info['speed'] = stats[name].speed
                interfaces.append(info)
            return interfaces
        except Exception as e:
            import traceback; print(f"[main.py] 错误:{type(e).__name__}:{e}"); traceback.print_exc()
            return []

    def _get_load_info(self):
        try:
            load1, load5, load15 = os.getloadavg()
            return {'load1': round(load1, 2), 'load5': round(load5, 2), 'load15': round(load15, 2)}
        except (OSError, AttributeError):
            return {'load1': 0, 'load5': 0, 'load15': 0}

    def _handle_stats_api(self, request):
        try:
            cpu_percent = psutil.cpu_percent(interval=0.3)
            mem = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            net = self._get_network_stats()
            disk_io = self._get_disk_io_stats()
            load = self._get_load_info()
            latency = self._get_network_latency()

            self._cpu_history.append(round(cpu_percent, 1))
            self._ram_history.append(round(mem.percent, 1))
            self._net_recv_history.append(net['recv_rate'])
            self._net_sent_history.append(net['sent_rate'])
            self._disk_read_history.append(disk_io['read_rate'])
            self._disk_write_history.append(disk_io['write_rate'])
            self._net_latency_history.append(latency)

            uptime_str = self._get_uptime_str()

            data = {
                'cpu': {'percent': round(cpu_percent, 1), 'cores': psutil.cpu_count(logical=True)},
                'ram': {'percent': round(mem.percent, 1), 'used': round(mem.used / (1024**3), 1), 'total': round(mem.total / (1024**3), 1)},
                'disk': {'percent': round(disk.percent, 1), 'used': round(disk.used / (1024**3), 1), 'total': round(disk.total / (1024**3), 1)},
                'network': net,
                'disk_io': disk_io,
                'load': load,
                'latency': latency,
                'processes': len(psutil.pids()),
                'uptime': uptime_str
            }
            return Response(status=200, headers={"Content-Type": "application/json"}, body=json.dumps(data))
        except Exception as e:
            return Response(status=500, headers={"Content-Type": "application/json"}, body=json.dumps({'error': str(e)}))

    def _handle_history_api(self, request):
        try:
            data = {
                'cpu': list(self._cpu_history),
                'ram': list(self._ram_history),
                'net_recv': list(self._net_recv_history),
                'net_sent': list(self._net_sent_history),
                'disk_read': list(self._disk_read_history),
                'disk_write': list(self._disk_write_history),
                'latency': list(self._net_latency_history)
            }
            return Response(status=200, headers={"Content-Type": "application/json"}, body=json.dumps(data))
        except Exception as e:
            return Response(status=500, headers={"Content-Type": "application/json"}, body=json.dumps({'error': str(e)}))

    def start(self):
        Log.info("dashboard", "仪表盘已启动")

    def stop(self):
        Log.error("dashboard", "仪表盘已停止")

    def _render_content(self) -> str:
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>系统仪表盘</title>
    <link rel="stylesheet" href="/assets/remixicon.css">
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{ font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; background:        .container {{ max-width: 1400px; margin: 0 auto; }}
        .card {{ background: white; border-radius: 10px; box-shadow: 0 2px 10px rgba(0,0,0,0.1); padding: 20px; margin-bottom: 20px; }}
        .card-title {{ font-size: 18px; font-weight: 600; color:        .stats-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 20px; }}
        .stat-card {{ background:        .stat-icon {{ width: 60px; height: 60px; margin: 0 auto 15px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 28px; color: white; }}
        .stat-icon.cpu {{ background: linear-gradient(135deg,        .stat-icon.ram {{ background: linear-gradient(135deg,        .stat-icon.disk {{ background: linear-gradient(135deg,        .stat-value {{ font-size: 24px; font-weight: 700; color:        .stat-label {{ font-size: 14px; color:        .gauge-container {{ position: relative; width: 120px; height: 120px; margin: 0 auto; }}
        .gauge-svg {{ transform: rotate(-90deg); }}
        .gauge-bg {{ fill: none; stroke:        .gauge-fill {{ fill: none; stroke:        .gauge-green .gauge-fill {{ stroke:        .gauge-orange .gauge-fill {{ stroke:        .gauge-blue .gauge-fill {{ stroke:        .gauge-text {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 18px; font-weight: 600; color:        .info-grid {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 15px; margin-top: 20px; }}
        .info-item {{ background:        .info-label {{ font-size: 12px; color:        .info-value {{ font-size: 14px; color:    </style>
</head>
<body>
    <div class="container">
        <div class="card">
            <h2 class="card-title"><i class="ri-dashboard-line"></i> 系统仪表盘</h2>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-icon cpu"><i class="ri-cpu-line"></i></div>
                    <div class="stat-value">{cpu_percent}%</div>
                    <div class="stat-label">CPU 使用率 ({cpu_cores} 核心)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon ram"><i class="ri-memory-line"></i></div>
                    <div class="stat-value">{ram_percent}%</div>
                    <div class="stat-label">内存使用 ({ram_used_gb} GB / {ram_total_gb} GB)</div>
                </div>
                <div class="stat-card">
                    <div class="stat-icon disk"><i class="ri-hard-drive-line"></i></div>
                    <div class="stat-value">{disk_percent}%</div>
                    <div class="stat-label">磁盘使用 ({disk_used_gb} GB / {disk_total_gb} GB)</div>
                </div>
            </div>
            <div class="info-grid">
                <div class="info-item">
                    <div class="info-label">系统运行时间</div>
                    <div class="info-value">{uptime_str}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">操作系统</div>
                    <div class="info-value">{platform.system()} {platform.release()}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">Python 版本</div>
                    <div class="info-value">{platform.python_version()}</div>
                </div>
                <div class="info-item">
                    <div class="info-label">主机名</div>
                    <div class="info-value">{platform.node()}</div>
                </div>
            </div>
        </div>
    </div>
    <script>
        setTimeout(() => location.reload(), 30000);
    </script>
</body>
</html>"""
            return html
        except Exception as e:
            return f"<p>仪表盘渲染出错：{{e}}</p>"

register_plugin_type("DashboardPlugin", DashboardPlugin)


def New():
    return DashboardPlugin()
