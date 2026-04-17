<?php
/**
 * 仪表盘页面视图
 */

$pageTitle = 'FutureOSS - 仪表盘';
$currentPage = 'dashboard';

// 内容区直接包含仪表盘内容
if (isset($dashboardContent)) {
    $content = $dashboardContent;
} else {
    $content = '<div class="empty-state"><p>仪表盘内容加载中...</p></div>';
}

// 复用 layout
include __DIR__ . '/layout.php';
