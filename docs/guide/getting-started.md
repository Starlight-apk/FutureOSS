# 快速开始

## 前置条件

- Python >= 3.10
- Linux / macOS / WSL2

## 安装

```bash
git clone https://github.com/Starlight-apk/NebulaShell.git
cd NebulaShell
pip install -r requirements.txt
```

## 启动

```bash
python main.py
```

启动后访问 http://localhost:8080 进入管理控制台。

## 配置

首次启动会自动生成 `oss.config.json`，位于项目根目录。主要配置项：

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `HOST` | `127.0.0.1` | 监听地址 |
| `HTTP_API_PORT` | `8080` | HTTP 服务端口 |
| `STORE_DIR` | `store` | 插件存放目录 |
| `DATA_DIR` | `data` | 数据存储目录 |
| `API_KEY` | 空 | API 认证密钥（为空时禁用认证） |
