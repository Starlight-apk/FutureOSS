/**
 * 页面控制器
 * 每个方法只负责渲染一个页面，业务逻辑分离
 */

/**
 * 渲染首页
 */
exports.renderHome = (req, res) => {
  res.render('pages/home', {
    title: 'FutureOSS - 一切皆为插件的开发者运行时框架',
    page: 'home',
    description: 'FutureOSS 是一款面向开发者的插件化运行时框架，秉承「一切皆为插件」的设计理念，让功能扩展变得前所未有的简单。'
  });
};

/**
 * 渲染特性页面
 */
exports.renderFeatures = (req, res) => {
  res.render('pages/features', {
    title: '核心特性 - FutureOSS',
    page: 'features',
    description: 'FutureOSS 的核心特性：插件化架构、安全沙箱、热重载支持、可视化控制台、双协议服务、依赖自动解析。'
  });
};

/**
 * 渲染架构页面
 */
exports.renderArchitecture = (req, res) => {
  res.render('pages/architecture', {
    title: '技术架构 - FutureOSS',
    page: 'architecture',
    description: '深入了解 FutureOSS 的技术架构和设计思想，包括插件系统架构、安全机制、数据流等。'
  });
};

/**
 * 渲染插件页面
 */
exports.renderPlugins = (req, res) => {
  res.render('pages/plugins', {
    title: '插件生态系统 - FutureOSS',
    page: 'plugins',
    description: 'FutureOSS 插件生态系统：核心插件、社区插件、插件开发指南、插件市场。'
  });
};