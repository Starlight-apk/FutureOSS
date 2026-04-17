<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>
        .terminal-container { max-width: 1400px; margin: 0 auto; padding: 20px; height: calc(100vh - 100px); display: flex; flex-direction: column; }
        .terminal-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .terminal-title { font-size: 18px; font-weight: 600; color: #00bcd4; display: flex; align-items: center; gap: 10px; }
        .terminal-title i { font-size: 24px; }
        
        .terminal-controls { display: flex; gap: 10px; }
        .term-btn { padding: 6px 14px; background: #3b82f6; border: none; border-radius: 6px; color: white; cursor: pointer; font-size: 13px; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }
        .term-btn:hover { background: #2563eb; }
        .term-btn.connecting { background: #f59e0b; cursor: not-allowed; }
        .term-btn.disconnect { background: #ef4444; }
        .term-btn.disconnect:hover { background: #dc2626; }
        
        .terminal-status { display: flex; align-items: center; gap: 8px; padding: 4px 12px; background: #1e293b; border-radius: 12px; font-size: 12px; }
        .status-dot { width: 8px; height: 8px; border-radius: 50%; }
        .status-dot.connected { background: #34d399; animation: pulse 2s infinite; }
        .status-dot.disconnected { background: #f87171; }
        .status-dot.connecting { background: #fbbf24; animation: pulse 1s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.3); } }
        
        .terminal-wrapper { flex: 1; background: #0f172a; border-radius: 10px; padding: 16px; display: flex; flex-direction: column; }
        .terminal-info { display: flex; justify-content: space-between; align-items: center; padding: 8px 0; border-bottom: 1px solid #1e293b; margin-bottom: 12px; }
        .info-item { font-size: 12px; color: #94a3b8; display: flex; align-items: center; gap: 6px; }
        .info-item i { color: #3b82f6; }
        
        .terminal-output { flex: 1; overflow-y: auto; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; color: #e2e8f0; margin-bottom: 12px; }
        .terminal-output::-webkit-scrollbar { width: 8px; }
        .terminal-output::-webkit-scrollbar-track { background: #1e293b; border-radius: 4px; }
        .terminal-output::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }
        .terminal-output::-webkit-scrollbar-thumb:hover { background: #64748b; }
        
        .terminal-line { padding: 2px 0; }
        .terminal-line.command { color: #34d399; }
        .terminal-line.output { color: #e2e8f0; }
        .terminal-line.error { color: #f87171; }
        .terminal-line.info { color: #60a5fa; }
        .terminal-line.success { color: #34d399; }
        .terminal-line.warning { color: #fbbf24; }
        
        .terminal-input-wrapper { display: flex; gap: 8px; align-items: center; padding: 8px; background: #1e293b; border-radius: 6px; }
        .terminal-prompt { color: #34d399; font-weight: 600; white-space: nowrap; }
        .terminal-input { flex: 1; background: transparent; border: none; color: #e2e8f0; font-family: 'Courier New', monospace; font-size: 13px; outline: none; }
        .terminal-input::placeholder { color: #64748b; }
        
        .ssh-config { background: #1e293b; border-radius: 8px; padding: 16px; margin-bottom: 16px; }
        .config-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
        .config-row:last-child { margin-bottom: 0; }
        .config-label { font-size: 13px; color: #94a3b8; min-width: 100px; }
        .config-input { flex: 1; padding: 6px 12px; background: #0f172a; border: 1px solid #334155; border-radius: 6px; color: #e2e8f0; font-size: 13px; }
        .config-input:focus { outline: none; border-color: #3b82f6; }
        .config-checkbox { display: flex; align-items: center; gap: 8px; color: #e2e8f0; font-size: 13px; cursor: pointer; }
        .config-checkbox input[type="checkbox"] { cursor: pointer; }
        
        .empty-state { text-align: center; padding: 60px 20px; color: #64748b; }
        .empty-state i { font-size: 64px; margin-bottom: 16px; opacity: 0.3; }
        .empty-state p { font-size: 14px; margin-top: 8px; }
        
        .spinner { display: inline-block; width: 14px; height: 14px; border: 2px solid rgba(255,255,255,0.3); border-top-color: white; border-radius: 50%; animation: spin 0.8s linear infinite; }
        @keyframes spin { to { transform: rotate(360deg); } }
    </style>
</head>
<body>
<div class="terminal-container">
    <div class="terminal-header">
        <div class="terminal-title">
            <i class="ri-terminal-box-line"></i>
            <span>SSH 终端</span>
        </div>
        <div class="terminal-controls">
            <div class="terminal-status">
                <span class="status-dot disconnected" id="status-dot"></span>
                <span id="status-text">未连接</span>
            </div>
            <button class="term-btn" id="connect-btn" onclick="connectSSH()">
                <i class="ri-plug-line"></i>
                连接
            </button>
            <button class="term-btn disconnect" id="disconnect-btn" onclick="disconnectSSH()" style="display: none;">
                <i class="ri-close-line"></i>
                断开
            </button>
            <button class="term-btn" id="clear-btn" onclick="clearTerminal()">
                <i class="ri-delete-bin-line"></i>
                清空
            </button>
        </div>
    </div>
    
    <div class="ssh-config" id="ssh-config">
        <div class="config-row">
            <span class="config-label"><i class="ri-settings-3-line"></i> SSH 端口:</span>
            <input type="number" class="config-input" id="ssh-port" value="8022" min="1" max="65535">
        </div>
        <div class="config-row">
            <label class="config-checkbox">
                <input type="checkbox" id="auto-install" checked>
                自动安装 SSH 服务
            </label>
        </div>
    </div>
    
    <div class="terminal-wrapper">
        <div class="terminal-info">
            <div class="info-item">
                <i class="ri-server-line"></i>
                <span>端口: <strong id="info-port">8022</strong></span>
            </div>
            <div class="info-item">
                <i class="ri-time-line"></i>
                <span>运行时间: <strong id="info-uptime">-</strong></span>
            </div>
        </div>
        
        <div class="terminal-output" id="terminal-output">
            <div class="empty-state" id="empty-state">
                <i class="ri-terminal-box-line"></i>
                <p>点击"连接"按钮开始 SSH 终端会话</p>
                <p style="font-size: 12px; margin-top: 8px; opacity: 0.7;">支持自动安装 SSH 服务</p>
            </div>
        </div>
        
        <div class="terminal-input-wrapper" id="input-wrapper" style="display: none;">
            <span class="terminal-prompt">$</span>
            <input type="text" class="terminal-input" id="terminal-input" placeholder="输入命令..." onkeypress="handleKeyPress(event)">
        </div>
    </div>
</div>

<script>
    let sessionId = null;
    let isConnected = false;
    
    function updateStatus(status) {
        const dot = document.getElementById('status-dot');
        const text = document.getElementById('status-text');
        const connectBtn = document.getElementById('connect-btn');
        const disconnectBtn = document.getElementById('disconnect-btn');
        const inputWrapper = document.getElementById('input-wrapper');
        const sshConfig = document.getElementById('ssh-config');
        
        dot.className = 'status-dot ' + status;
        
        if (status === 'connected') {
            text.textContent = '已连接';
            connectBtn.style.display = 'none';
            disconnectBtn.style.display = 'flex';
            inputWrapper.style.display = 'flex';
            sshConfig.style.display = 'none';
            isConnected = true;
        } else if (status === 'connecting') {
            text.textContent = '连接中...';
            connectBtn.classList.add('connecting');
            connectBtn.innerHTML = '<span class="spinner"></span> 连接中';
        } else {
            text.textContent = '未连接';
            connectBtn.style.display = 'flex';
            connectBtn.classList.remove('connecting');
            connectBtn.innerHTML = '<i class="ri-plug-line"></i> 连接';
            disconnectBtn.style.display = 'none';
            inputWrapper.style.display = 'none';
            sshConfig.style.display = 'block';
            isConnected = false;
        }
    }
    
    async function connectSSH() {
        const port = document.getElementById('ssh-port').value;
        const autoInstall = document.getElementById('auto-install').checked;
        
        updateStatus('connecting');
        appendLine('info', '正在初始化 SSH 连接...');
        appendLine('info', `目标端口: ${port}`);
        
        if (autoInstall) {
            appendLine('info', '自动安装 SSH: 已启用');
            appendLine('tip', '智能检测 SSH 服务状态...');
        }
        
        try {
            const response = await fetch('/api/terminal/connect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ port: parseInt(port), auto_install: autoInstall })
            });
            
            const data = await response.json();
            
            if (data.success) {
                sessionId = data.session_id;
                document.getElementById('info-port').textContent = port;
                document.getElementById('info-uptime').textContent = '刚刚';
                updateStatus('connected');
                appendLine('success', `✓ SSH 终端已连接 (会话 #${sessionId})`);
                appendLine('output', '输入命令开始操作...');
                appendLine('output', '');
                document.getElementById('terminal-input').focus();
            } else {
                updateStatus('disconnected');
                appendLine('error', `✗ 连接失败: ${data.error}`);
            }
        } catch (error) {
            updateStatus('disconnected');
            appendLine('error', `✗ 连接异常: ${error.message}`);
        }
    }
    
    async function disconnectSSH() {
        if (!sessionId) return;
        
        try {
            await fetch('/api/terminal/disconnect', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
        } catch (error) {
            console.error('断开连接失败:', error);
        }
        
        sessionId = null;
        updateStatus('disconnected');
        appendLine('warning', 'SSH 终端已断开');
    }
    
    async function sendCommand(command) {
        if (!sessionId || !command.trim()) return;
        
        appendLine('command', `$ ${command}`);
        
        try {
            const response = await fetch('/api/terminal/send', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId, command: command })
            });
            
            const data = await response.json();
            
            if (data.success && data.output) {
                const lines = data.output.split('\n');
                lines.forEach(line => {
                    if (line.trim()) {
                        appendLine('output', line);
                    }
                });
            }
        } catch (error) {
            appendLine('error', `执行命令失败: ${error.message}`);
        }
    }
    
    function handleKeyPress(event) {
        if (event.key === 'Enter') {
            const input = document.getElementById('terminal-input');
            const command = input.value.trim();
            if (command) {
                sendCommand(command);
                input.value = '';
            }
        }
    }
    
    function appendLine(type, text) {
        const output = document.getElementById('terminal-output');
        const emptyState = document.getElementById('empty-state');
        
        if (emptyState) {
            emptyState.style.display = 'none';
        }
        
        const line = document.createElement('div');
        line.className = `terminal-line ${type}`;
        line.textContent = text;
        output.appendChild(line);
        output.scrollTop = output.scrollHeight;
    }
    
    function clearTerminal() {
        const output = document.getElementById('terminal-output');
        output.innerHTML = '<div class="empty-state"><i class="ri-terminal-box-line"></i><p>终端已清空</p></div>';
    }
</script>
</body>
</html>
