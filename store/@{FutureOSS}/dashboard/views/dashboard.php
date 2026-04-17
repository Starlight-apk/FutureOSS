<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <style>
        .dashboard-container { max-width: 1400px; margin: 0 auto; padding: 20px; }
        .section-title { font-size: 18px; font-weight: 600; color: #00bcd4; margin-bottom: 16px; padding-left: 12px; border-left: 4px solid #3b82f6; }

        .gauges-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 16px; margin-bottom: 28px; }
        .gauge-card { background: #1e293b; border-radius: 12px; padding: 20px; display: flex; flex-direction: column; align-items: center; position: relative; }
        .gauge-card .label { font-size: 14px; color: #94a3b8; margin-bottom: 8px; }
        .gauge-circle { position: relative; width: 120px; height: 120px; }
        .gauge-circle svg { transform: rotate(-90deg); }
        .gauge-circle .bg { fill: none; stroke: #334155; stroke-width: 8; }
        .gauge-circle .progress { fill: none; stroke: #3b82f6; stroke-width: 8; stroke-linecap: round; transition: stroke-dashoffset 0.8s ease; }
        .gauge-circle .value { position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 24px; font-weight: 700; color: #f1f5f9; }
        .gauge-circle .unit { font-size: 12px; color: #94a3b8; }
        .gauge-card .detail { margin-top: 8px; font-size: 12px; color: #64748b; }
        .gauge-green { stroke: #22c55e; }
        .gauge-orange { stroke: #f59e0b; }
        .gauge-blue { stroke: #3b82f6; }
        .gauge-red { stroke: #ef4444; }

        .io-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 16px; margin-bottom: 28px; }
        .io-card { background: #1e293b; border-radius: 12px; padding: 20px; }
        .io-card .card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
        .io-card .card-header i { font-size: 20px; color: #3b82f6; }
        .io-card .card-header span { font-size: 15px; font-weight: 600; color: #e2e8f0; }
        .io-row { display: flex; justify-content: space-between; padding: 8px 0; border-bottom: 1px solid #334155; }
        .io-row:last-child { border-bottom: none; }
        .io-row .io-label { color: #94a3b8; font-size: 13px; }
        .io-row .io-value { color: #f1f5f9; font-size: 14px; font-weight: 500; }

        .info-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(300px, 1fr)); gap: 16px; margin-bottom: 28px; }
        .info-card { background: #1e293b; border-radius: 12px; padding: 20px; }
        .info-card .card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
        .info-card .card-header i { font-size: 20px; color: #3b82f6; }
        .info-card .card-header span { font-size: 15px; font-weight: 600; color: #e2e8f0; }
        .info-table { width: 100%; }
        .info-row { display: flex; justify-content: space-between; padding: 10px 0; border-bottom: 1px solid #334155; }
        .info-row:last-child { border-bottom: none; }
        .info-row .info-label { color: #94a3b8; font-size: 13px; }
        .info-row .info-value { color: #f1f5f9; font-size: 14px; font-weight: 500; }

        .net-ifaces { margin-top: 12px; }
        .net-iface { background: #0f172a; border-radius: 8px; padding: 12px; margin-bottom: 8px; display: flex; justify-content: space-between; align-items: center; }
        .net-iface .iface-name { font-weight: 600; color: #e2e8f0; }
        .net-iface .iface-info { font-size: 12px; color: #94a3b8; }
        .net-iface .iface-status { padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: 500; }
        .status-up { background: #064e3b; color: #34d399; }
        .status-down { background: #7f1d1d; color: #f87171; }

        .chart-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(450px, 1fr)); gap: 16px; margin-bottom: 28px; }
        .chart-card { background: #1e293b; border-radius: 12px; padding: 20px; }
        .chart-card .card-header { display: flex; align-items: center; gap: 10px; margin-bottom: 14px; }
        .chart-card .card-header i { font-size: 20px; color: #3b82f6; }
        .chart-card .card-header span { font-size: 15px; font-weight: 600; color: #e2e8f0; }
        .chart-wrapper { position: relative; height: 200px; }

        .live-dot { width: 8px; height: 8px; background: #22c55e; border-radius: 50%; display: inline-block; margin-right: 6px; animation: pulse 2s infinite; }
        @keyframes pulse { 0%, 100% { opacity: 1; transform: scale(1); } 50% { opacity: 0.5; transform: scale(1.3); } }
    </style>
</head>
<body>
<div class="dashboard-container">

    <div class="section-title"><span class="live-dot"></span>实时指标</div>
    <div class="gauges-grid">
        <div class="gauge-card">
            <div class="label">CPU 使用率</div>
            <div class="gauge-circle">
                <svg width="120" height="120"><circle class="bg" cx="60" cy="60" r="52" stroke-dasharray="<?= $cpuDashArray ?>"></circle><circle class="progress gauge-blue" id="cpu-gauge" cx="60" cy="60" r="52" stroke-dasharray="<?= $cpuDashArray ?>" stroke-dashoffset="<?= $cpuDashOffset ?>"></circle></svg>
                <div class="value"><span id="cpu-val"><?= $cpuPercent ?></span><span class="unit">%</span></div>
            </div>
            <div class="detail"><?= $cpuCores ?> 核心</div>
        </div>
        <div class="gauge-card">
            <div class="label">内存使用</div>
            <div class="gauge-circle">
                <svg width="120" height="120"><circle class="bg" cx="60" cy="60" r="52" stroke-dasharray="<?= $ramDashArray ?>"></circle><circle class="progress gauge-green" id="ram-gauge" cx="60" cy="60" r="52" stroke-dasharray="<?= $ramDashArray ?>" stroke-dashoffset="<?= $ramDashOffset ?>"></circle></svg>
                <div class="value"><span id="ram-val"><?= $ramPercent ?></span><span class="unit">%</span></div>
            </div>
            <div class="detail"><?= $ramUsed ?> / <?= $ramTotal ?></div>
        </div>
        <div class="gauge-card">
            <div class="label">磁盘使用</div>
            <div class="gauge-circle">
                <svg width="120" height="120"><circle class="bg" cx="60" cy="60" r="52" stroke-dasharray="<?= $diskDashArray ?>"></circle><circle class="progress <?= $diskColorClass ?>" id="disk-gauge" cx="60" cy="60" r="52" stroke-dasharray="<?= $diskDashArray ?>" stroke-dashoffset="<?= $diskDashOffset ?>"></circle></svg>
                <div class="value"><span id="disk-val"><?= $diskPercent ?></span><span class="unit">%</span></div>
            </div>
            <div class="detail"><?= $diskUsed ?> / <?= $diskTotal ?></div>
        </div>
        <div class="gauge-card">
            <div class="label">系统负载</div>
            <div class="gauge-circle">
                <svg width="120" height="120"><circle class="bg" cx="60" cy="60" r="52" stroke-dasharray="326.73"></circle><circle class="progress gauge-orange" cx="60" cy="60" r="52" stroke-dasharray="326.73" stroke-dashoffset="0"></circle></svg>
                <div class="value" style="font-size:16px" id="load-val"><?= $load1 ?></div>
            </div>
            <div class="detail">1m / 5m / 15m: <?= $load1 ?> / <?= $load5 ?> / <?= $load15 ?></div>
        </div>
    </div>

    <div class="section-title">网络 & 磁盘 I/O</div>
    <div class="io-grid">
        <div class="io-card">
            <div class="card-header"><i class="ri-global-line"></i><span>网络流量</span></div>
            <div class="io-row"><span class="io-label">下载速度</span><span class="io-value" id="net-recv"><?= $netRecvSpeed ?></span></div>
            <div class="io-row"><span class="io-label">上传速度</span><span class="io-value" id="net-sent"><?= $netSentSpeed ?></span></div>
        </div>
        <div class="io-card">
            <div class="card-header"><i class="ri-hard-drive-3-line"></i><span>磁盘 I/O</span></div>
            <div class="io-row"><span class="io-label">读取速度</span><span class="io-value" id="disk-read"><?= $diskReadSpeed ?></span></div>
            <div class="io-row"><span class="io-label">写入速度</span><span class="io-value" id="disk-write"><?= $diskWriteSpeed ?></span></div>
        </div>
        <div class="io-card">
            <div class="card-header"><i class="ri-stack-line"></i><span>系统概况</span></div>
            <div class="io-row"><span class="io-label">运行进程</span><span class="io-value" id="proc-count"><?= $processes ?></span></div>
            <div class="io-row"><span class="io-label">运行时间</span><span class="io-value" id="uptime-val"><?= $uptime ?></span></div>
        </div>
    </div>

    <div class="section-title">历史趋势</div>
    <div class="chart-grid">
        <div class="chart-card">
            <div class="card-header"><i class="ri-cpu-line"></i><span>CPU & 内存趋势</span></div>
            <div class="chart-wrapper"><canvas id="chart-cpu"></canvas></div>
        </div>
        <div class="chart-card">
            <div class="card-header"><i class="ri-exchange-line"></i><span>网络吞吐</span></div>
            <div class="chart-wrapper"><canvas id="chart-net"></canvas></div>
        </div>
        <div class="chart-card">
            <div class="card-header"><i class="ri-hard-drive-3-line"></i><span>磁盘读写</span></div>
            <div class="chart-wrapper"><canvas id="chart-disk-io"></canvas></div>
        </div>
        <div class="chart-card">
            <div class="card-header"><i class="ri-pulse-line"></i><span>网络延迟</span></div>
            <div class="chart-wrapper"><canvas id="chart-latency"></canvas></div>
        </div>
    </div>

    <div class="section-title">系统信息</div>
    <div class="info-grid">
        <div class="info-card">
            <div class="card-header"><i class="ri-settings-4-line"></i><span>系统详情</span></div>
            <div class="info-table">
                <div class="info-row"><span class="info-label">主机名</span><span class="info-value"><?= $hostname ?></span></div>
                <div class="info-row"><span class="info-label">操作系统</span><span class="info-value"><?= $osName ?></span></div>
                <div class="info-row"><span class="info-label">Python</span><span class="info-value"><?= $pythonVersion ?></span></div>
                <div class="info-row"><span class="info-label">PHP</span><span class="info-value"><?= $phpVersion ?></span></div>
                <div class="info-row"><span class="info-label">运行时间</span><span class="info-value" id="uptime-info"><?= $uptime ?></span></div>
            </div>
        </div>
        <div class="info-card">
            <div class="card-header"><i class="ri-router-line"></i><span>网络接口</span></div>
            <div class="net-ifaces" id="net-ifaces">
                <script type="application/json" id="ifaces-data"><?= htmlspecialchars($netInterfaces, ENT_QUOTES, 'UTF-8') ?></script>
            </div>
        </div>
    </div>
</div>

<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.0/dist/chart.umd.min.js"></script>
<script>
(function(){
    const $ = id => document.getElementById(id);
    const circumference = 2 * Math.PI * 52;

    Chart.defaults.color = '#94a3b8';
    Chart.defaults.borderColor = '#334155';
    Chart.defaults.font.size = 11;

    const fmtBytes = v => {
        if (v >= 1048576) return (v/1048576).toFixed(1) + ' MB/s';
        if (v >= 1024) return (v/1024).toFixed(1) + ' KB/s';
        return Math.round(v) + ' B/s';
    };

    const cpuChart = new Chart($('chart-cpu'), {
        type: 'line',
        data: { labels: [], datasets: [
            { label: 'CPU %', data: [], borderColor: '#3b82f6', backgroundColor: 'rgba(59,130,246,0.1)', tension: 0.4, fill: true, pointRadius: 0 },
            { label: '内存 %', data: [], borderColor: '#22c55e', backgroundColor: 'rgba(34,197,94,0.1)', tension: 0.4, fill: true, pointRadius: 0 }
        ]},
        options: {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 1500, easing: 'easeInOutCubic' },
            plugins: { legend: { display: true } },
            scales: { x: { display: false }, y: { min: 0, max: 100, grid: { color: '#334155' } } }
        }
    });

    const netChart = new Chart($('chart-net'), {
        type: 'line',
        data: { labels: [], datasets: [
            { label: '下载', data: [], borderColor: '#06b6d4', tension: 0.4, fill: false, pointRadius: 0 },
            { label: '上传', data: [], borderColor: '#f59e0b', tension: 0.4, fill: false, pointRadius: 0 }
        ]},
        options: {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 1500, easing: 'easeInOutCubic' },
            plugins: { legend: { display: true }, tooltip: { callbacks: { label: ctx => ctx.dataset.label + ': ' + fmtBytes(ctx.raw) } } },
            scales: { x: { display: false }, y: { grid: { color: '#334155' }, ticks: { callback: v => fmtBytes(v) } } }
        }
    });

    const diskIoChart = new Chart($('chart-disk-io'), {
        type: 'line',
        data: { labels: [], datasets: [
            { label: '读取', data: [], borderColor: '#8b5cf6', tension: 0.4, fill: false, pointRadius: 0 },
            { label: '写入', data: [], borderColor: '#ec4899', tension: 0.4, fill: false, pointRadius: 0 }
        ]},
        options: {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 1500, easing: 'easeInOutCubic' },
            plugins: { legend: { display: true }, tooltip: { callbacks: { label: ctx => ctx.dataset.label + ': ' + fmtBytes(ctx.raw) } } },
            scales: { x: { display: false }, y: { grid: { color: '#334155' }, ticks: { callback: v => fmtBytes(v) } } }
        }
    });

    const latencyChart = new Chart($('chart-latency'), {
        type: 'line',
        data: { labels: [], datasets: [
            { label: '延迟 ms', data: [], borderColor: '#f43f5e', backgroundColor: 'rgba(244,63,94,0.1)', tension: 0.4, fill: true, pointRadius: 0 }
        ]},
        options: {
            responsive: true, maintainAspectRatio: false,
            animation: { duration: 1500, easing: 'easeInOutCubic' },
            plugins: { legend: { display: true } },
            scales: { x: { display: false }, y: { grid: { color: '#334155' }, beginAtZero: true } }
        }
    });

    // 加载历史
    const MAX_POINTS = 10;

    // 初始化空图表
    [cpuChart, netChart, diskIoChart, latencyChart].forEach(c => {
        for (let i = 0; i < MAX_POINTS; i++) c.data.labels.push('');
    });

    fetch('/api/dashboard/history').then(r => r.json()).then(hist => {
        const data = {
            cpu: hist.cpu, ram: hist.ram,
            net_recv: hist.net_recv, net_sent: hist.net_sent,
            disk_read: hist.disk_read, disk_write: hist.disk_write,
            latency: hist.latency || []
        };
        const start = Math.max(0, data.cpu.length - MAX_POINTS);
        const slice = data.cpu.slice(start);

        cpuChart.data.datasets[0].data = data.cpu.slice(start);
        cpuChart.data.datasets[1].data = data.ram.slice(start);
        netChart.data.datasets[0].data = data.net_recv.slice(start);
        netChart.data.datasets[1].data = data.net_sent.slice(start);
        diskIoChart.data.datasets[0].data = data.disk_read.slice(start);
        diskIoChart.data.datasets[1].data = data.disk_write.slice(start);
        latencyChart.data.datasets[0].data = data.latency.slice(start);

        // 不足10个补默认值
        const pad = (chart, vals) => {
            const diff = MAX_POINTS - chart.data.datasets[0].data.length;
            for (let i = 0; i < diff; i++) {
                chart.data.datasets[0].data.push(vals[0]);
                if (chart.data.datasets[1]) chart.data.datasets[1].data.push(vals[1] ?? vals[0]);
            }
        };
        pad(cpuChart, [50, 50]);
        pad(netChart, [0, 0]);
        pad(diskIoChart, [0, 0]);
        pad(latencyChart, [0]);

        cpuChart.update(); netChart.update(); diskIoChart.update(); latencyChart.update();
    }).catch(() => {
        // 加载失败也补默认
        [cpuChart, netChart, diskIoChart, latencyChart].forEach(c => {
            c.data.datasets.forEach(ds => {
                while (ds.data.length < MAX_POINTS) ds.data.push(0);
            });
            c.update();
        });
    });

    // 渲染网络接口
    try {
        const el = $('ifaces-data');
        if (el) {
            const ifaces = JSON.parse(el.textContent);
            const container = $('net-ifaces');
            if (ifaces.length === 0) {
                container.innerHTML = '<div class="net-iface"><div class="iface-info">暂无网络接口</div></div>';
            } else {
                let html = '';
                ifaces.forEach(iface => {
                    html += `<div class="net-iface"><div><div class="iface-name">${iface.name}</div><div class="iface-info">${iface.ip}</div></div><span class="iface-status ${iface.is_up ? 'status-up' : 'status-down'}">${iface.is_up ? 'UP' : 'DOWN'}</span></div>`;
                });
                container.innerHTML = html;
            }
        }
    } catch(e) {}

    // 定时刷新
    setInterval(() => {
        fetch('/api/dashboard/stats').then(r => r.json()).then(d => {
            const setGauge = (id, pct) => {
                const el = $(id);
                if (el) el.setAttribute('stroke-dashoffset', circumference - (pct/100)*circumference);
            };
            setGauge('cpu-gauge', d.cpu.percent);
            setGauge('ram-gauge', d.ram.percent);
            setGauge('disk-gauge', d.disk.percent);
            $('cpu-val').textContent = d.cpu.percent;
            $('ram-val').textContent = d.ram.percent;
            $('disk-val').textContent = d.disk.percent;
            $('load-val').textContent = d.load.load1;
            $('net-recv').textContent = fmtBytes(d.network.recv_rate);
            $('net-sent').textContent = fmtBytes(d.network.sent_rate);
            $('disk-read').textContent = fmtBytes(d.disk_io.read_rate);
            $('disk-write').textContent = fmtBytes(d.disk_io.write_rate);
            $('proc-count').textContent = d.processes;
            $('uptime-val').textContent = d.uptime;
            $('uptime-info').textContent = d.uptime;

            // 刷新：固定10个点，数据向左平滑滚动
            const pushChart = (chart, v1, v2) => {
                // 移除最左边旧数据
                chart.data.datasets[0].data.shift();
                // 新数据从右边加入
                chart.data.datasets[0].data.push(v1);
                if (chart.data.datasets[1]) {
                    chart.data.datasets[1].data.shift();
                    chart.data.datasets[1].data.push(v2);
                }
                // 触发 Chart.js 内置过渡动画
                chart.update('default');
            };
            pushChart(cpuChart, d.cpu.percent, d.ram.percent);
            pushChart(netChart, d.network.recv_rate, d.network.sent_rate);
            pushChart(diskIoChart, d.disk_io.read_rate, d.disk_io.write_rate);

            // 网络延迟图
            latencyChart.data.datasets[0].data.shift();
            latencyChart.data.datasets[0].data.push(d.latency || 0);
            latencyChart.update('default');
        }).catch(() => {});
    }, 2000);
})();
</script>
</body>
</html>
