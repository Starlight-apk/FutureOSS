<?php
// 检查登录状态
session_start();
$isLoggedIn = isset($_SESSION['user_id']);
$username = $_SESSION['username'] ?? '';

// 从数据库读取最新的 role 和 title
$role = 'Member';
$userTitle = '';
if ($isLoggedIn) {
    require_once __DIR__ . '/Database.php';
    try {
        $db = Database::getInstance();
        $userData = $db->fetchOne("SELECT role, title FROM users WHERE id = ?", [$_SESSION['user_id']]);
        if ($userData) {
            $role = isset($userData['role']) ? ucfirst($userData['role']) : 'Member';
            $userTitle = $userData['title'] ?? '';
            // 更新 session 中的 role
            $_SESSION['role'] = $userData['role'] ?? 'member';
        }
    } catch (Exception $e) {
        // 忽略错误，继续执行
    }
}

// 构建 tooltip 文本
$tooltipText = $userTitle ? "{$username} - {$userTitle}" : $username;
?>
<aside id="dock" data-logged-in="<?php echo $isLoggedIn ? '1' : '0'; ?>">
    <!-- 导航组 -->
    <a href="../index.html" class="dock-item" data-tooltip="首页">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>
    </a>
    <a href="../features.html" class="dock-item" data-tooltip="特性">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z"/></svg>
    </a>
    <a href="../plugins.html" class="dock-item" data-tooltip="插件">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z"/></svg>
    </a>
    <a href="../architecture.html" class="dock-item" data-tooltip="架构">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z"/></svg>
    </a>

    <div class="dock-separator"></div>

    <!-- 快速开始 & 源码 -->
    <a href="../quickstart.html" class="dock-item" data-tooltip="快速开始">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 10V3L4 14h7v7l9-11h-7z"/></svg>
    </a>
    <a href="https://gitee.com/starlight-apk/feature-oss" target="_blank" class="dock-item" data-tooltip="源码">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4"/></svg>
    </a>

    <!-- 社区专属操作组 -->
    <div class="dock-separator"></div>

    <?php if ($isLoggedIn): ?>
        <!-- 已登录：显示用户头像和发帖按钮 -->
        <a href="profile.php" class="dock-item dock-user-avatar" data-tooltip="<?php echo htmlspecialchars($tooltipText); ?>" id="dockUserAvatar">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/></svg>
            <?php if ($userTitle): ?>
                <span class="user-title-badge"><?php echo htmlspecialchars($userTitle); ?></span>
            <?php endif; ?>
        </a>
        <a href="editor.php" class="dock-item dock-action-btn" data-tooltip="发布新帖">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 5v14m-7-7h14"/></svg>
        </a>

    <?php else: ?>
        <!-- 未登录：显示登录/注册按钮 -->
        <a href="login.php" class="dock-item dock-action-btn" data-tooltip="登录">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 16l-4-4m0 0l4-4m-4 4h14m-5 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h7a3 3 0 013 3v1"/></svg>
        </a>
    <?php endif; ?>
</aside>
