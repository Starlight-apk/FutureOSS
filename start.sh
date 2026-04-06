#!/usr/bin/env bash
# ═══════════════════════════════════════════════════════════
#  FutureOSS 启动脚本 — Linux / macOS
#  自动检测 Python / 依赖 / 守护 / 崩溃重启
# ═══════════════════════════════════════════════════════════

set -e

# ── 颜色 ──
RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'
CYAN='\033[0;36m'; WHITE='\033[1;37m'; BOLD='\033[1m'; NC='\033[0m'

LOGO="
 ███████╗ ██████╗  ██████╗  ██████╗ ██████╗  ██████╗
 ██╔════╝ ██╔══██╗ ██╔══██╗ ██╔══██╗ ██╔══██╗██╔════╝
 █████╗   ██████╔╝ ██████╔╝ ██████╔╝ ██║  ██║██║  ███╗
 ██╔══╝   ██╔══██╗ ██╔══██╗ ██╔══██╗ ██║  ██║██║   ██║
 ██║      ██║  ██║ ██║  ██║ ██║  ██║ ██████╔╝╚██████╔╝
 ╚═╝      ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═╝  ╚═╝ ╚═════╝  ╚═════╝"

info()  { echo -e "${CYAN}ℹ  $1${NC}"; }
ok()    { echo -e "${GREEN}✓  $1${NC}"; }
warn()  { echo -e "${YELLOW}⚠  $1${NC}"; }
err()   { echo -e "${RED}✗  $1${NC}"; }
title() { echo -e "\n${BOLD}$1${NC}"; }

# ── 守护参数 ──
DAEMON=false
if [[ "$1" == "--daemon" || "$1" == "-d" ]]; then
    DAEMON=true
fi

title "$LOGO"
echo -e "${WHITE}         一切皆为插件 · 零编译热插拔${NC}"
echo -e "${WHITE}         https://gitee.com/starlight-apk/feature-oss${NC}"
echo ""

# ── 目录 ──
PROJECT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$PROJECT_DIR"

# ═══════════════════════════════════════════════════════════
#  1. 检查 Python
# ═══════════════════════════════════════════════════════════
title "📦 环境检测"

find_python() {
    for cmd in python3 python python3.12 python3.11 python3.10; do
        if command -v "$cmd" &>/dev/null; then
            echo "$cmd"
            return
        fi
    done
    return 1
}

PYTHON_CMD=$(find_python || true)

if [[ -z "$PYTHON_CMD" ]]; then
    warn "未检测到 Python，正在自动安装..."
    if command -v apt-get &>/dev/null; then
        sudo apt-get update -qq && sudo apt-get install -y -qq python3 python3-pip python3-venv
    elif command -v yum &>/dev/null; then
        sudo yum install -y python3 python3-pip
    elif command -v pacman &>/dev/null; then
        sudo pacman -Sy --noconfirm python python-pip
    elif command -v brew &>/dev/null; then
        brew install python
    elif command -v apk &>/dev/null; then
        apk add python3 py3-pip
    else
        err "无法自动安装 Python，请手动安装 Python 3.10+"
        exit 1
    fi
    PYTHON_CMD=$(find_python || true)
    [[ -z "$PYTHON_CMD" ]] && { err "Python 安装失败"; exit 1; }
fi

PY_VER=$($PYTHON_CMD --version 2>&1)
ok "Python: $PY_VER ($PYTHON_CMD)"

# ═══════════════════════════════════════════════════════════
#  2. 虚拟环境 & 依赖
# ═══════════════════════════════════════════════════════════
title "📚 依赖安装"

VENV_DIR=".venv"
if [[ ! -d "$VENV_DIR" ]]; then
    info "创建虚拟环境..."
    $PYTHON_CMD -m venv "$VENV_DIR"
fi

source "$VENV_DIR/bin/activate"
PIP_CMD="$VENV_DIR/bin/pip"

if [[ -f "pyproject.toml" ]]; then
    info "安装项目依赖 (pyproject.toml)..."
    $PIP_CMD install -e . -q 2>/dev/null || $PIP_CMD install -e . --break-system-packages -q 2>/dev/null || true
fi

if [[ -f "requirements.txt" ]]; then
    info "安装 requirements.txt..."
    $PIP_CMD install -r requirements.txt -q 2>/dev/null || true
fi

# 核心依赖兜底
for pkg in click pyyaml websockets; do
    $PYTHON_CMD -c "import $pkg" 2>/dev/null || {
        info "安装 $pkg ..."
        $PIP_CMD install "$pkg" -q 2>/dev/null || $PIP_CMD install "$pkg" --break-system-packages -q 2>/dev/null || true
    }
done

ok "依赖就绪"

# ═══════════════════════════════════════════════════════════
#  3. 确保 data 目录
# ═══════════════════════════════════════════════════════════
mkdir -p data/html-render data/web-toolkit data/plugin-storage data/DCIM data/pkg

# ═══════════════════════════════════════════════════════════
#  4. 启动
# ═══════════════════════════════════════════════════════════
title "🚀 启动 FutureOSS"

if $DAEMON; then
    title "🔒 守护模式"
    LOG_FILE="logs/futureoss.log"
    mkdir -p logs
    PID_FILE="logs/futureoss.pid"

    if [[ -f "$PID_FILE" ]]; then
        OLD_PID=$(cat "$PID_FILE")
        if kill -0 "$OLD_PID" 2>/dev/null; then
            warn "已有进程运行 (PID: $OLD_PID)，正在停止..."
            kill "$OLD_PID" 2>/dev/null || true
            sleep 2
        fi
    fi

    nohup $PYTHON_CMD -m oss.cli serve > "$LOG_FILE" 2>&1 &
    NEW_PID=$!
    echo "$NEW_PID" > "$PID_FILE"
    ok "已启动守护进程 (PID: $NEW_PID)"
    info "日志: $LOG_FILE"
    info "停止: kill $(cat $PID_FILE) 或 bash start.sh stop"
    sleep 2
    curl -s http://localhost:8080/health &>/dev/null && ok "服务就绪: http://localhost:8080" || warn "服务启动中，请稍候..."
    exit 0
fi

# ── 前台模式 + 崩溃自动重启 ──
RESTART_DELAY=3
MAX_RESTARTS=0
RESTART_COUNT=0

run_server() {
    $PYTHON_CMD -m oss.cli serve
}

while true; do
    run_server
    EXIT_CODE=$?

    if [[ $EXIT_CODE -eq 0 ]]; then
        ok "服务正常退出"
        break
    fi

    RESTART_COUNT=$((RESTART_COUNT + 1))
    warn "服务异常退出 (code: $EXIT_CODE)，${RESTART_DELAY}s 后重启... (第 $RESTART_COUNT 次)"
    sleep $RESTART_DELAY

    # 指数退避，最大 30s
    if [[ $RESTART_DELAY -lt 30 ]]; then
        RESTART_DELAY=$((RESTART_DELAY * 2))
    fi
done

deactivate 2>/dev/null || true
