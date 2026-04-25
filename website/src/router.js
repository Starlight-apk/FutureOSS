/**
 * FutureOSS 网站路由配置
 * 一个文件只管一个功能：路由只负责路由，不处理业务逻辑
 */

const express = require('express');
const router = express.Router();
const path = require('path');

// 导入页面控制器
const pagesController = require('./controllers/pagesController');
const apiController = require('./controllers/apiController');

// API路由
router.get('/api/health', apiController.healthCheck);
router.get('/api/metrics', apiController.performanceMetrics);
router.get('/api/info', apiController.serverInfo);
router.get('/api/stress-test', apiController.stressTest);

// 页面路由 - 每个路由对应一个独立的页面文件
router.get('/', pagesController.renderHome);
router.get('/features', pagesController.renderFeatures);
router.get('/architecture', pagesController.renderArchitecture);
router.get('/plugins', pagesController.renderPlugins);

// 静态文件路由（备用）
router.get('/static/*', (req, res) => {
  const filePath = path.join(__dirname, '../public', req.params[0]);
  res.sendFile(filePath, (err) => {
    if (err) {
      res.status(404).json({ error: '文件未找到' });
    }
  });
});

// 重定向旧路由（如果需要）
router.get('/home', (req, res) => res.redirect('/'));
router.get('/index', (req, res) => res.redirect('/'));

module.exports = router;