<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>
        .log-container { max-width: 1400px; margin: 0 auto; padding: 20px; height: calc(100vh - 100px); display: flex; flex-direction: column; }
        .log-header { display: flex; justify-content: space-between; align-items: center; margin-bottom: 16px; }
        .log-title { font-size: 18px; font-weight: 600; color: #00bcd4; display: flex; align-items: center; gap: 10px; }
        .log-title i { font-size: 24px; }
        .live-indicator { display: inline-flex; align-items: center; gap: 6px; padding: 4px 12px; background: #064e3b; border-radius: 12px; font-size: 12px; color: #34d399; }
        .live-dot { width: 8px; height: 8px; background: #34d399; border-radius: 50%; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.3); } }
        
        .log-controls { display: flex; gap: 10px; align-items: center; }
        .log-btn { padding: 6px 14px; background: #3b82f6; border: none; border-radius: 6px; color: white; cursor: pointer; font-size: 13px; transition: all 0.2s; display: flex; align-items: center; gap: 6px; }
        .log-btn:hover { background: #2563eb; }
        .log-btn.paused { background: #f59e0b; }
        .log-btn.paused:hover { background: #d97706; }
        
        .log-filters { display: flex; gap: 8px; margin-bottom: 12px; }
        .filter-btn { padding: 4px 12px; border-radius: 16px; font-size: 12px; border: 1px solid #334155; background: #1e293b; color: #94a3b8; cursor: pointer; transition: all 0.2s; }
        .filter-btn:hover { background: #334155; }
        .filter-btn.active { background: #3b82f6; border-color: #3b82f6; color: white; }
        
        .log-content { flex: 1; overflow-y: auto; background: #0f172a; border-radius: 10px; padding: 16px; font-family: 'Courier New', monospace; font-size: 13px; line-height: 1.6; }
        .log-content::-webkit-scrollbar { width: 8px; }
        .log-content::-webkit-scrollbar-track { background: #1e293b; border-radius: 4px; }
        .log-content::-webkit-scrollbar-thumb { background: #475569; border-radius: 4px; }
        .log-content::-webkit-scrollbar-thumb:hover { background: #64748b; }
        
        .log-entry { padding: 4px 0; border-bottom: 1px solid #1e293b; animation: fadeIn 0.3s ease-in; }
        @keyframes fadeIn { from { opacity: 0; transform: translateY(-5px); } to { opacity: 1; transform: translateY(0); } }
        .log-entry:last-child { border-bottom: none; }
        
        .log-timestamp { color: #64748b; margin-right: 8px; }
        .log-level { padding: 2px 8px; border-radius: 4px; font-size: 11px; font-weight: 600; margin-right: 8px; display: inline-block; min-width: 50px; text-align: center; }
        .log-tag { color: #3b82f6; margin-right: 8px; font-weight: 500; }
        .log-message { color: #e2e8f0; }
        
        .log-level.info { background: #1e3a8a; color: #60a5fa; }
        .log-level.ok { background: #064e3b; color: #34d399; }
        .log-level.warn { background: #78350f; color: #fbbf24; }
        .log-level.error { background: #7f1d1d; color: #f87171; }
        .log-level.tip { background: #1e3a5f; color: #38bdf8; }
        
        .empty-state { text-align: center; padding: 60px 20px; color: #64748b; }
        .empty-state i { font-size: 64px; margin-bottom: 16px; opacity: 0.3; }
        .empty-state p { font-size: 14px; }
    </style>
</head>
<body>
<div class="log-container">
    <div class="log-header">
        <div class="log-title">
            <i class="ri-file-list-3-line"></i>
            <span>系统日志</span>
            <span class="live-indicator" id="live-indicator">
                <span class="live-dot"></span>
                实时同步
            </span>
        </div>
        <div class="log-controls">
            <button class="log-btn" id="clear-btn" onclick="clearLogs()">
                <i class="ri-delete-bin-line"></i>
                清空
            </button>
            <button class="log-btn" id="pause-btn" onclick="togglePause()">
                <i class="ri-pause-line" id="pause-icon"></i>
                <span id="pause-text">暂停</span>
            </button>
        </div>
    </div>
    
    <div class="log-filters">
        <button class="filter-btn active" data-level="all" onclick="setFilter('all')">全部</button>
        <button class="filter-btn" data-level="info" onclick="setFilter('info')">信息</button>
        <button class="filter-btn" data-level="ok" onclick="setFilter('ok')">成功</button>
        <button class="filter-btn" data-level="warn" onclick="setFilter('warn')">警告</button>
        <button class="filter-btn" data-level="error" onclick="setFilter('error')">错误</button>
        <button class="filter-btn" data-level="tip" onclick="setFilter('tip')">提示</button>
    </div>
    
    <div class="log-content" id="log-content">
        <div class="empty-state" id="empty-state">
            <i class="ri-file-list-3-line"></i>
            <p>正在加载日志...</p>
        </div>
    </div>
</div>

<script>
    let isPaused = false;
    let currentFilter = 'all';
    let syncInterval = null;
    
    function setFilter(level) {
        currentFilter = level;
        document.querySelectorAll('.filter-btn').forEach(btn => {
            btn.classList.remove('active');
            if (btn.dataset.level === level) {
                btn.classList.add('active');
            }
        });
        filterLogs();
    }
    
    function togglePause() {
        isPaused = !isPaused;
        const pauseBtn = document.getElementById('pause-btn');
        const pauseIcon = document.getElementById('pause-icon');
        const pauseText = document.getElementById('pause-text');
        const indicator = document.getElementById('live-indicator');
        
        if (isPaused) {
            pauseBtn.classList.add('paused');
            pauseIcon.className = 'ri-play-line';
            pauseText.textContent = '继续';
            indicator.style.opacity = '0.5';
        } else {
            pauseBtn.classList.remove('paused');
            pauseIcon.className = 'ri-pause-line';
            pauseText.textContent = '暂停';
            indicator.style.opacity = '1';
            fetchLogs();
        }
    }
    
    function clearLogs() {
        const content = document.getElementById('log-content');
        content.innerHTML = '<div class="empty-state"><i class="ri-file-list-3-line"></i><p>日志已清空</p></div>';
    }
    
    async function fetchLogs() {
        if (isPaused) return;
        
        try {
            // 先尝试从缓冲区获取
            const response = await fetch('/api/logs/get?limit=100&source=buffer');
            const data = await response.json();
            
            if (data.success) {
                // 如果缓冲区为空，尝试从系统日志读取
                if (!data.logs || data.logs.length === 0) {
                    const fileResponse = await fetch('/api/logs/get?limit=100&source=file');
                    const fileData = await fileResponse.json();
                    
                    if (fileData.success) {
                        renderLogs(fileData.logs || []);
                    }
                } else {
                    renderLogs(data.logs);
                }
            }
        } catch (error) {
            console.error('获取日志失败:', error);
            // 错误时也要显示状态
            const content = document.getElementById('log-content');
            const emptyState = document.getElementById('empty-state');
            emptyState.style.display = 'block';
            emptyState.innerHTML = '<i class="ri-error-warning-line"></i><p>获取日志失败</p><p style="font-size: 12px; margin-top: 8px; opacity: 0.7;">' + error.message + '</p>';
        }
    }
    
    function renderLogs(logs) {
        const content = document.getElementById('log-content');
        const emptyState = document.getElementById('empty-state');
        
        if (logs.length === 0) {
            emptyState.style.display = 'block';
            emptyState.innerHTML = '<i class="ri-file-list-3-line"></i><p>暂无日志</p>';
            return;
        }
        
        emptyState.style.display = 'none';
        
        const filteredLogs = currentFilter === 'all' 
            ? logs 
            : logs.filter(log => log.level === currentFilter);
        
        const html = filteredLogs.map(log => `
            <div class="log-entry" data-level="${log.level}">
                <span class="log-timestamp">${log.timestamp}</span>
                <span class="log-level ${log.level}">${log.level.toUpperCase()}</span>
                <span class="log-tag">[${log.tag}]</span>
                <span class="log-message">${escapeHtml(log.message)}</span>
            </div>
        `).join('');
        
        content.innerHTML = html;
        content.scrollTop = content.scrollHeight;
    }
    
    function filterLogs() {
        const entries = document.querySelectorAll('.log-entry');
        entries.forEach(entry => {
            if (currentFilter === 'all' || entry.dataset.level === currentFilter) {
                entry.style.display = 'block';
            } else {
                entry.style.display = 'none';
            }
        });
    }
    
    function escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    // 初始化
    document.addEventListener('DOMContentLoaded', () => {
        fetchLogs();
        syncInterval = setInterval(fetchLogs, 2000);  // 每2秒同步一次
    });
</script>
</body>
</html>
