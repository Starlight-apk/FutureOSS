# 🔥 Firewall Plugin - 动态防火墙

## 📖 功能概述

动态防火墙插件提供企业级的网络安全防护，支持多种防火墙后端（iptables/UFW），具备以下核心能力：

### ✨ 核心特性

| 特性 | 描述 | 状态 |
|:-----|:-----|:----:|
| 🔍 **状态检测引擎** | 基于连接状态的智能规则匹配（NEW/ESTABLISHED/RELATED） | ✅ |
| 🔄 **热加载能力** | 无需重启即可更新防火墙策略 | ✅ |
| 📊 **实时流量分析** | 可视化展示入站/出站流量统计 | ✅ |
| 🚨 **异常行为熔断** | 检测到攻击自动触发保护机制 | ✅ |
| 📋 **多后端支持** | iptables/UFW/模拟模式自动检测 | ✅ |
| 🌐 **WebUI 集成** | 通过 HTTP API 进行规则配置 | ✅ |
| ⏱️ **速率限制** | 基于 IP 的请求频率控制 | ✅ |
| ⚪⚫ **黑白名单** | IP 白名单和黑名单管理 | ✅ |
| 💾 **规则持久化** | 自动保存和加载规则配置 | ✅ |

---

## 🚀 快速开始

### 1. 安装系统依赖

```bash
# Debian/Ubuntu
sudo apt-get install -y iptables

# CentOS/RHEL
sudo yum install -y iptables-services

# 启用并启动 iptables
sudo systemctl enable iptables
sudo systemctl start iptables
```

### 2. 插件配置

在 `manifest.json` 中配置防火墙参数：

```json
{
  "metadata": {
    "name": "firewall",
    "version": "1.1.0"
  },
  "config": {
    "enabled": true,
    "args": {
      "default_policy": "ACCEPT",
      "whitelist_enabled": false,
      "blacklist_enabled": true,
      "rate_limit_enabled": true,
      "rate_limit_requests": 100,
      "rate_limit_window": 60,
      "rules_file": "config/firewall_rules.json",
      "auto_block_enabled": true,
      "threat_threshold": 100
    }
  },
  "system_dependencies": ["iptables"]
}
```

### 3. 启动插件

```python
from oss.plugin.loader import PluginLoader

loader = PluginLoader.get_instance()
firewall = loader.load_plugin('firewall')
```

---

## 📚 API 使用指南

### 通过 PL 注入接口调用

```python
from oss.plugin.loader import PluginLoader

loader = PluginLoader.get_instance()
firewall = loader.get_plugin('firewall')

# 1. 添加防火墙规则
result = firewall.execute('add_rule', 
    protocol='tcp',
    dst_port=80,
    action='ACCEPT',
    src_ip='192.168.1.0/24'
)
print(result)
# {'success': True, 'rule': {...}, 'message': '规则添加成功'}

# 2. 删除规则
result = firewall.execute('remove_rule', rule_id='0')
print(result)

# 3. 列出所有规则
result = firewall.execute('list_rules')
print(result)
# {'success': True, 'rules': [...], 'total': 5}

# 4. 添加 IP 到白名单
result = firewall.execute('whitelist_add', ip='10.0.0.1')
print(result)

# 5. 添加 IP 到黑名单
result = firewall.execute('blacklist_add', ip='192.168.100.100')
print(result)

# 6. 设置速率限制
result = firewall.execute('rate_limit', 
    ip='172.16.0.50', 
    requests=50, 
    window=60
)
print(result)

# 7. 获取统计信息
result = firewall.execute('get_stats')
print(result)
# {'success': True, 'stats': {'packets_processed': 1000, ...}}

# 8. 重新加载规则（热更新）
result = firewall.execute('reload')
print(result)

# 9. 获取运行状态
result = firewall.execute('status')
print(result)
# {'success': True, 'status': {'running': True, 'backend': 'IptablesBackend', ...}}
```

---

## 🔧 高级功能

### 1. 状态检测规则

```python
# 允许已建立的连接
firewall.execute('add_rule',
    protocol='tcp',
    state='ESTABLISHED,RELATED',
    action='ACCEPT'
)

# 允许新的 SSH 连接
firewall.execute('add_rule',
    protocol='tcp',
    dst_port=22,
    state='NEW',
    action='ACCEPT'
)
```

### 2. 端口范围规则

```python
# 开放端口范围
firewall.execute('add_rule',
    protocol='tcp',
    dst_port='3000:3010',  # 端口范围
    action='ACCEPT'
)
```

### 3. 接口绑定

```python
# 仅允许特定网络接口的流量
firewall.execute('add_rule',
    protocol='tcp',
    dst_port=80,
    interface='eth0',
    action='ACCEPT'
)
```

### 4. 批量操作

```python
# 批量添加白名单 IPs
whitelist_ips = ['10.0.0.1', '10.0.0.2', '10.0.0.3']
for ip in whitelist_ips:
    firewall.execute('whitelist_add', ip=ip)

# 批量封禁恶意 IP
malicious_ips = ['192.168.100.1', '192.168.100.2', '192.168.100.3']
for ip in malicious_ips:
    firewall.execute('blacklist_add', ip=ip)
```

---

## 📊 监控与告警

### 实时统计

```python
stats = firewall.execute('get_stats')
print(f"处理的数据包：{stats['stats']['packets_processed']}")
print(f"丢弃的数据包：{stats['stats']['packets_dropped']}")
print(f"接受的数据包：{stats['stats']['packets_accepted']}")
print(f"当前规则数：{stats['stats']['rules_count']}")
print(f"白名单 IP 数：{stats['stats']['whitelist_count']}")
print(f"黑名单 IP 数：{stats['stats']['blacklist_count']}")
print(f"活跃封禁数：{stats['stats']['blocked_ips']}")
```

### 自动威胁检测

插件内置自动威胁检测机制：

- **阈值检测**: 当丢包数超过 1000 时发出警告
- **自动封禁**: 检测到异常流量自动将 IP 加入黑名单
- **定时解封**: 封禁的 IP 在 1 小时后自动解封（可配置）

---

## 💾 规则持久化

规则自动保存到配置文件：

```json
// config/firewall_rules.json
{
  "rules": [
    {
      "protocol": "tcp",
      "dst_port": 80,
      "action": "ACCEPT",
      "src_ip": "192.168.1.0/24"
    },
    {
      "protocol": "tcp",
      "dst_port": 443,
      "action": "ACCEPT"
    }
  ],
  "whitelist": ["10.0.0.1", "10.0.0.2"],
  "blacklist": ["192.168.100.100"]
}
```

插件启动时自动加载这些规则，停止时自动保存更改。

---

## 🔒 安全最佳实践

### 1. 默认拒绝策略

```python
# 设置默认策略为 DROP（谨慎使用，确保先添加允许规则）
firewall.execute('add_rule',
    protocol='tcp',
    dst_port=22,  # 先允许 SSH
    action='ACCEPT'
)
firewall.execute('add_rule',
    protocol='tcp',
    dst_port=80,  # 允许 HTTP
    action='ACCEPT'
)
firewall.execute('add_rule',
    protocol='tcp',
    dst_port=443,  # 允许 HTTPS
    action='ACCEPT'
)
```

### 2. 最小权限原则

只开放必要的端口和服务：

```python
# 仅允许特定 IP 访问管理端口
firewall.execute('add_rule',
    protocol='tcp',
    dst_port=8080,
    src_ip='10.0.0.0/8',  # 仅内网
    action='ACCEPT'
)
```

### 3. 速率限制防护

```python
# 对公共 API 实施严格的速率限制
firewall.execute('rate_limit',
    ip='0.0.0.0/0',  # 所有 IP
    requests=100,     # 每分钟最多 100 次请求
    window=60
)
```

---

## 🛠️ 故障排查

### 检查防火墙状态

```python
status = firewall.execute('status')
print(status)
```

### 查看后端类型

```python
stats = firewall.execute('get_stats')
print(f"后端类型：{stats['stats']['backend_type']}")
```

### 手动重载规则

```python
result = firewall.execute('reload')
if result['success']:
    print("规则重载成功")
else:
    print(f"规则重载失败：{result.get('error')}")
```

### 日志位置

防火墙日志输出到：
- 控制台输出
- 系统日志（如果使用 iptables）

---

## 📋 完整 API 参考

| API 端点 | 参数 | 描述 | 返回值 |
|:---------|:-----|:-----|:-------|
| `add_rule` | `protocol`, `src_ip`, `dst_ip`, `src_port`, `dst_port`, `action`, `state`, `interface` | 添加防火墙规则 | `{success, rule, message}` |
| `remove_rule` | `rule_id` | 删除指定规则 | `{success, rule_id, message}` |
| `list_rules` | - | 列出所有规则 | `{success, rules, total}` |
| `whitelist_add` | `ip` | 添加 IP 到白名单 | `{success, ip, message}` |
| `blacklist_add` | `ip` | 添加 IP 到黑名单 | `{success, ip, message}` |
| `rate_limit` | `ip`, `requests`, `window` | 设置速率限制 | `{success, ip, limit, message}` |
| `get_stats` | - | 获取统计信息 | `{success, stats}` |
| `reload` | - | 重新加载规则 | `{success, message}` |
| `status` | - | 获取运行状态 | `{success, status}` |

---

## 🎯 使用场景

### 场景 1: Web 服务器防护

```python
# 允许 HTTP/HTTPS
firewall.execute('add_rule', protocol='tcp', dst_port=80, action='ACCEPT')
firewall.execute('add_rule', protocol='tcp', dst_port=443, action='ACCEPT')

# 允许 SSH（仅管理 IP）
firewall.execute('add_rule', protocol='tcp', dst_port=22, src_ip='10.0.0.0/8', action='ACCEPT')

# 封禁已知恶意 IP 段
firewall.execute('blacklist_add', ip='192.168.100.0/24')

# 启用速率限制
firewall.execute('rate_limit', ip='0.0.0.0/0', requests=100, window=60)
```

### 场景 2: 数据库服务器

```python
# 仅允许应用服务器访问数据库端口
firewall.execute('add_rule', 
    protocol='tcp', 
    dst_port=3306, 
    src_ip='10.0.1.0/24',  # 应用服务器网段
    action='ACCEPT'
)

# 拒绝其他所有访问
firewall.execute('add_rule', 
    protocol='tcp', 
    dst_port=3306, 
    action='DROP'
)
```

### 场景 3: 开发环境

```python
# 开放开发所需端口
ports = [3000, 4000, 5000, 8000, 8080, 9000]
for port in ports:
    firewall.execute('add_rule', protocol='tcp', dst_port=port, action='ACCEPT')

# 仅内网访问
firewall.execute('add_rule', 
    protocol='tcp', 
    dst_port=27017,  # MongoDB
    src_ip='127.0.0.1', 
    action='ACCEPT'
)
```

---

## 🤝 贡献指南

欢迎提交 Issue 和 Pull Request 来改进防火墙插件！

### 待办事项

- [ ] 支持 nftables 后端
- [ ] IPv6 支持
- [ ] 更复杂的规则组合（AND/OR逻辑）
- [ ] 地理 IP 封锁
- [ ] 与威胁情报源集成
- [ ] WebUI 可视化配置界面

---

## 📄 许可证

Apache License 2.0
