<?php
/**
 * 首页视图
 * 这是 webui 插件的默认首页
 * 其他插件可以替换或扩展此页面
 */

$pageTitle = $config['title'] ?? 'FutureOSS';
$currentPage = 'home';

// 默认导航项（其他插件可以添加更多）
$navItems = [];

// 内容区（其他插件可以注入内容）
$content = '<div class="empty-state"><p>暂无内容</p></div>';

include __DIR__ . '/layout.php';
