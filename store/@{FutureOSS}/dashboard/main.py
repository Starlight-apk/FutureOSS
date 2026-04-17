"""Dashboard 仪表盘插件"""
import os
import time
import json
import socket
import subprocess
import platform
import psutil
from collections import deque
from oss.logger.logger import Log
from oss.plugin.types import Plugin, Response, register_plugin_type


class DashboardPlugin(Plugin):
    """仪表盘插件 - 依赖 WebUI 容器"""

    def __init__(self):
        self.webui = None
        self.views_dir = os.path.join(os.path.dirname(__file__), 'views')
        self._start_time = time.time()  # 记录插件启动时间（即项目启动时间）
        self._history_len = 60
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
                author="FutureOSS",
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
        """计算项目运行时间（从插件启动时算起）"""
        elapsed = time.time() - self._start_time
        days = int(elapsed // 86400)
        hours = int((elapsed % 86400) // 3600)
        minutes = int((elapsed % 3600) // 60)
        seconds = int(elapsed % 60)
        if days > 0:
            return f"{days}天{hours}时{minutes}分{seconds}秒"
        elif hours > 0:
            return f"{hours}时{minutes}分{seconds}秒"
        elif minutes > 0:
            return f"{minutes}分{seconds}秒"
        else:
            return f"{seconds}秒"

    def _get_network_stats(self):
        try:
            net = psutil.net_io_counters()
            now = time.time()
            if self._last_net is None:
                self._last_net = (now, net.bytes_recv, net.bytes_sent)
                return {'recv_rate': 0, 'sent_rate': 0, 'total_recv': net.bytes_recv, 'total_sent': net.bytes_sent}
            elapsed = now - self._last_net[0]
            if elapsed <= 0: elapsed = 1
            recv_rate = (net.bytes_recv - self._last_net[1]) / elapsed
            sent_rate = (net.bytes_sent - self._last_net[2]) / elapsed
            self._last_net = (now, net.bytes_recv, net.bytes_sent)
            return {'recv_rate': round(recv_rate, 1), 'sent_rate': round(sent_rate, 1), 'total_recv': net.bytes_recv, 'total_sent': net.bytes_sent}
        except Exception:
            return {'recv_rate': 0, 'sent_rate': 0, 'total_recv': 0, 'total_sent': 0}

    def _get_disk_io_stats(self):
        try:
            disk_io = psutil.disk_io_counters()
            if not disk_io:
                return {'read_rate': 0, 'write_rate': 0}
            now = time.time()
            if self._last_disk is None:
                self._last_disk = (now, disk_io.read_bytes, disk_io.write_bytes)
                return {'read_rate': 0, 'write_rate': 0}
            elapsed = now - self._last_disk[0]
            if elapsed <= 0: elapsed = 1
            read_rate = (disk_io.read_bytes - self._last_disk[1]) / elapsed
            write_rate = (disk_io.write_bytes - self._last_disk[2]) / elapsed
            self._last_disk = (now, disk_io.read_bytes, disk_io.write_bytes)
            return {'read_rate': round(read_rate, 1), 'write_rate': round(write_rate, 1)}
        except Exception:
            return {'read_rate': 0, 'write_rate': 0}

    def _get_network_latency(self) -> float:
        """测量到公共 DNS 8.8.8.8 的 TCP 连接延迟（真实网络波动）"""
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(2)
            start = time.time()
            s.connect(('8.8.8.8', 53))
            elapsed = (time.time() - start) * 1000  # 毫秒
            s.close()
            return round(elapsed, 1)
        except Exception:
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
        except Exception:
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
        try:
            php_file = os.path.join(self.views_dir, 'dashboard.php')
            if not os.path.exists(php_file):
                return "<p>仪表盘视图文件丢失</p>"

            cpu_percent = psutil.cpu_percent(interval=0.5)
            cpu_cores = psutil.cpu_count(logical=True)
            mem = psutil.virtual_memory()
            ram_percent = round(mem.percent, 1)
            ram_used_gb = round(mem.used / (1024**3), 1)
            ram_total_gb = round(mem.total / (1024**3), 1)
            disk = psutil.disk_usage('/')
            disk_percent = round(disk.percent, 1)
            disk_used_gb = round(disk.used / (1024**3), 1)
            disk_total_gb = round(disk.total / (1024**3), 1)
            net = self._get_network_stats()
            disk_io = self._get_disk_io_stats()
            load = self._get_load_info()
            net_interfaces = self._get_network_interfaces()
            processes = len(psutil.pids())

            if disk_percent < 50:
                disk_color = 'gauge-green'
            elif disk_percent < 80:
                disk_color = 'gauge-orange'
            else:
                disk_color = 'gauge-blue'

            circumference = 2 * 3.14159 * 52
            cpu_dash_offset = round(circumference - (cpu_percent / 100) * circumference, 1)
            ram_dash_offset = round(circumference - (ram_percent / 100) * circumference, 1)
            disk_dash_offset = round(circumference - (disk_percent / 100) * circumference, 1)

            uptime_str = self._get_uptime_str()

            def fmt_speed(bps):
                if bps >= 1024 * 1024:
                    return f"{round(bps / (1024*1024), 1)} MB/s"
                elif bps >= 1024:
                    return f"{round(bps / 1024, 1)} KB/s"
                else:
                    return f"{round(bps, 0)} B/s"

            variables = {
                'cpuPercent': int(cpu_percent),
                'cpuDashArray': str(circumference),
                'cpuDashOffset': str(cpu_dash_offset),
                'cpuCores': str(cpu_cores),
                'ramPercent': ram_percent,
                'ramDashArray': str(circumference),
                'ramDashOffset': str(ram_dash_offset),
                'ramUsed': f"{ram_used_gb} GB",
                'ramTotal': f"{ram_total_gb} GB",
                'diskPercent': disk_percent,
                'diskDashArray': str(circumference),
                'diskDashOffset': str(disk_dash_offset),
                'diskUsed': f"{disk_used_gb} GB",
                'diskTotal': f"{disk_total_gb} GB",
                'diskColorClass': disk_color,
                'uptime': uptime_str,
                'osName': f"{platform.system()} {platform.release()}",
                'pythonVersion': platform.python_version(),
                'phpVersion': self._get_php_version(),
                'hostname': platform.node(),
                'netRecvSpeed': fmt_speed(net['recv_rate']),
                'netSentSpeed': fmt_speed(net['sent_rate']),
                'diskReadSpeed': fmt_speed(disk_io['read_rate']),
                'diskWriteSpeed': fmt_speed(disk_io['write_rate']),
                'load1': str(load['load1']),
                'load5': str(load['load5']),
                'load15': str(load['load15']),
                'processes': str(processes),
                'netInterfaces': json.dumps(net_interfaces),
            }

            return self._execute_php(php_file, variables)
        except Exception as e:
            return f"<p>仪表盘渲染出错: {e}</p>"

    def _execute_php(self, php_file: str, variables: dict) -> str:
        php_vars = ""
        for key, value in variables.items():
            if isinstance(value, str):
                escaped = value.replace('\\', '\\\\').replace("'", "\\'").replace("\n", "\\n")
                php_vars += f"${key} = '{escaped}';\n"
            else:
                php_vars += f"${key} = {value};\n"

        with open(php_file, 'r', encoding='utf-8') as f:
            php_content = f.read()

        tmp_file = os.path.join(os.path.dirname(php_file), '.temp_dashboard.php')
        try:
            with open(tmp_file, 'w', encoding='utf-8') as f:
                f.write(f"<?php\n{php_vars}\n?>\n{php_content}")
            result = subprocess.run(
                ["php", "-f", tmp_file],
                capture_output=True, text=True, timeout=10
            )
            return result.stdout if result.returncode == 0 else f"<pre>{result.stderr}</pre>"
        finally:
            try:
                if os.path.exists(tmp_file):
                    os.unlink(tmp_file)
            except Exception:
                pass

    @staticmethod
    def _get_php_version() -> str:
        try:
            res = subprocess.run(['php', '-r', 'echo phpversion();'], capture_output=True, text=True, timeout=5)
            return res.stdout if res.returncode == 0 else 'N/A'
        except Exception:
            return 'N/A'


register_plugin_type("DashboardPlugin", DashboardPlugin)


def New():
    return DashboardPlugin()
