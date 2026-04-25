/**
 * API控制器
 * 提供系统状态和健康检查接口
 */

/**
 * 健康检查
 */
exports.healthCheck = (req, res) => {
  const health = {
    status: 'healthy',
    timestamp: new Date().toISOString(),
    uptime: process.uptime(),
    memory: process.memoryUsage(),
    nodeVersion: process.version,
    platform: process.platform,
    pid: process.pid
  };
  
  res.json(health);
};

/**
 * 性能指标
 */
exports.performanceMetrics = (req, res) => {
  const metrics = {
    timestamp: new Date().toISOString(),
    memory: {
      heapUsed: process.memoryUsage().heapUsed,
      heapTotal: process.memoryUsage().heapTotal,
      rss: process.memoryUsage().rss
    },
    cpu: process.cpuUsage(),
    uptime: process.uptime(),
    activeHandles: process._getActiveHandles().length,
    activeRequests: process._getActiveRequests().length
  };
  
  res.json(metrics);
};

/**
 * 服务器信息
 */
exports.serverInfo = (req, res) => {
  const info = {
    name: 'FutureOSS 官方网站',
    version: '1.0.0',
    description: 'FutureOSS 插件化运行时框架官方网站',
    repository: 'https://gitee.com/starlight-apk/future-oss',
    endpoints: [
      { path: '/', method: 'GET', description: '首页' },
      { path: '/features', method: 'GET', description: '特性页面' },
      { path: '/architecture', method: 'GET', description: '架构页面' },
      { path: '/plugins', method: 'GET', description: '插件页面' },
      { path: '/api/health', method: 'GET', description: '健康检查' },
      { path: '/api/metrics', method: 'GET', description: '性能指标' },
      { path: '/api/info', method: 'GET', description: '服务器信息' }
    ],
    environment: process.env.NODE_ENV || 'development'
  };
  
  res.json(info);
};

/**
 * 压力测试端点（仅开发环境）
 */
exports.stressTest = (req, res) => {
  if (process.env.NODE_ENV !== 'development') {
    return res.status(403).json({ error: '仅开发环境可用' });
  }
  
  const n = parseInt(req.query.n) || 1000000;
  let result = 0;
  
  // 模拟CPU密集型操作
  for (let i = 0; i < n; i++) {
    result += Math.sqrt(i) * Math.sin(i);
  }
  
  res.json({
    result: result,
    iterations: n,
    message: '压力测试完成'
  });
};