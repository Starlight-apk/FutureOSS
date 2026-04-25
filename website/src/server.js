/**
 * FutureOSS 官方网站服务器
 * 支持端口自动切换：8080被占用则使用8081
 */

const express = require('express');
const morgan = require('morgan');
const cors = require('cors');
const compression = require('compression');
const path = require('path');
const fs = require('fs');
const expressLayouts = require('express-ejs-layouts');
const performanceMiddleware = require('./middleware/performance');

// 创建Express应用
const app = express();

// 中间件配置
app.use(morgan('dev')); // 日志
app.use(cors()); // CORS支持
app.use(compression()); // 压缩响应
app.use(performanceMiddleware.responseTime); // 响应时间监控
app.use(performanceMiddleware.compressionHeaders); // 压缩头
app.use(performanceMiddleware.cacheControl); // 缓存控制
app.use(performanceMiddleware.securityHeaders); // 安全头
app.use(performanceMiddleware.memoryMonitor); // 内存监控
app.use(express.json()); // JSON解析
app.use(express.urlencoded({ extended: true })); // URL编码解析

// 静态文件服务
app.use(express.static(path.join(__dirname, '../public')));

// 设置视图引擎和布局
app.use(expressLayouts);
app.set('layout', 'layouts/main');
app.set('view engine', 'ejs');
app.set('views', path.join(__dirname, '../views'));

// 导入路由
const router = require('./router');
app.use('/', router);

// 错误处理中间件
app.use((err, req, res, next) => {
  console.error('服务器错误:', err);
  res.status(500).json({ 
    error: '服务器内部错误',
    message: process.env.NODE_ENV === 'development' ? err.message : undefined
  });
});

// 404处理
app.use((req, res) => {
  res.status(404).json({ error: '页面未找到' });
});

/**
 * 检查端口是否可用
 * @param {number} port - 要检查的端口
 * @returns {Promise<boolean>} - 端口是否可用
 */
function checkPort(port) {
  return new Promise((resolve) => {
    const net = require('net');
    const server = net.createServer();
    
    server.once('error', (err) => {
      if (err.code === 'EADDRINUSE') {
        console.log(`端口 ${port} 已被占用`);
        resolve(false);
      } else {
        resolve(false);
      }
    });
    
    server.once('listening', () => {
      server.close();
      console.log(`端口 ${port} 可用`);
      resolve(true);
    });
    
    server.listen(port);
  });
}

/**
 * 获取可用端口
 * @param {number} startPort - 起始端口
 * @param {number} maxAttempts - 最大尝试次数
 * @returns {Promise<number>} - 可用的端口
 */
async function getAvailablePort(startPort = 8080, maxAttempts = 10) {
  for (let i = 0; i < maxAttempts; i++) {
    const port = startPort + i;
    const isAvailable = await checkPort(port);
    if (isAvailable) {
      return port;
    }
  }
  throw new Error(`在端口 ${startPort} 到 ${startPort + maxAttempts - 1} 范围内找不到可用端口`);
}

/**
 * 启动服务器
 */
async function startServer() {
  try {
    // 获取可用端口
    const port = await getAvailablePort(8080, 5);
    
    // 启动服务器
    const server = app.listen(port, () => {
      console.log(`
╔══════════════════════════════════════════════════════════╗
║                    FutureOSS 官方网站                    ║
╠══════════════════════════════════════════════════════════╣
║ 服务器已启动！                                           ║
║                                                          ║
║ 本地访问: http://localhost:${port}                      ║
║ 环境: ${process.env.NODE_ENV || 'development'}          ║
║ 进程ID: ${process.pid}                                  ║
║                                                          ║
║ 可用路由:                                               ║
║   • GET  /              - 首页                          ║
║   • GET  /features      - 特性页面                      ║
║   • GET  /architecture  - 架构页面                      ║
║   • GET  /plugins       - 插件页面                      ║
║   • GET  /api/health    - 健康检查                      ║
║                                                          ║
║ 按 Ctrl+C 停止服务器                                    ║
╚══════════════════════════════════════════════════════════╝
      `);
    });

    // 优雅关闭
    const signals = ['SIGINT', 'SIGTERM', 'SIGQUIT'];
    signals.forEach(signal => {
      process.on(signal, () => {
        console.log(`\n接收到 ${signal} 信号，正在关闭服务器...`);
        server.close(() => {
          console.log('服务器已关闭');
          process.exit(0);
        });
        
        // 5秒后强制退出
        setTimeout(() => {
          console.error('强制关闭服务器');
          process.exit(1);
        }, 5000);
      });
    });

    // 未捕获异常处理
    process.on('uncaughtException', (err) => {
      console.error('未捕获异常:', err);
      server.close(() => process.exit(1));
    });

    process.on('unhandledRejection', (reason, promise) => {
      console.error('未处理的Promise拒绝:', reason);
    });

    return server;
  } catch (error) {
    console.error('启动服务器失败:', error);
    process.exit(1);
  }
}

// 如果是直接运行此文件，则启动服务器
if (require.main === module) {
  startServer();
}

module.exports = { app, startServer };