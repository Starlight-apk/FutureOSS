<?php
session_start();
require_once 'includes/Database.php';

// 获取用户 ID（优先使用 GET 参数，否则使用当前登录用户）
$currentUserId = $_SESSION['user_id'] ?? null;
$viewUserId = (int)($_GET['id'] ?? $currentUserId);

if (!$viewUserId) {
    header('Location: login.php');
    exit;
}

$db = Database::getInstance();

// 获取用户信息
$user = $db->fetchOne(
    "SELECT id, username, email, avatar, role, bio, created_at FROM users WHERE id = ?",
    [$viewUserId]
);

if (!$user) {
    header('HTTP/1.0 404 Not Found');
    exit('用户不存在');
}

// 获取用户统计数据
$stats = $db->fetchOne(
    "SELECT 
        (SELECT COUNT(*) FROM posts WHERE user_id = ?) as post_count,
        (SELECT COUNT(*) FROM replies WHERE user_id = ?) as reply_count,
        (SELECT SUM(views) FROM posts WHERE user_id = ?) as total_views,
        (SELECT SUM(likes) FROM posts WHERE user_id = ?) as total_likes",
    [$viewUserId, $viewUserId, $viewUserId, $viewUserId]
);

// 获取用户的文章（最近 10 篇）
$posts = $db->fetchAll(
    "SELECT p.*, c.name as category_name, c.slug as category_slug,
            (SELECT COUNT(*) FROM replies r WHERE r.post_id = p.id) as reply_count
     FROM posts p
     JOIN categories c ON p.category_id = c.id
     WHERE p.user_id = ?
     ORDER BY p.created_at DESC
     LIMIT 10",
    [$viewUserId]
);

// 获取用户的最近回复
$replies = $db->fetchAll(
    "SELECT r.*, p.title as post_title, p.id as post_id
     FROM replies r
     JOIN posts p ON r.post_id = p.id
     WHERE r.user_id = ?
     ORDER BY r.created_at DESC
     LIMIT 5",
    [$viewUserId]
);

$isCurrentUser = ($currentUserId == $viewUserId);
$isAdminOrMod = in_array($_SESSION['role'] ?? '', ['admin', 'moderator']);
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($user['username']) ?> - OSS Community</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="../css/main.css" />
    <link rel="stylesheet" href="../css/dock.css" />
    <link rel="stylesheet" href="assets/css/dock-popover.css" />
    <style>
        :root {
            --bg: #030712;
            --bg-card: rgba(255, 255, 255, 0.02);
            --border: rgba(255, 255, 255, 0.05);
            --border-hover: rgba(6, 182, 212, 0.3);
            --cyan: #06b6d4;
            --cyan-light: #22d3ee;
            --text: #fff;
            --text-secondary: #9ca3af;
            --text-muted: #6b7280;
        }

        * { margin: 0; padding: 0; box-sizing: border-box; }
        body {
            font-family: 'Inter', sans-serif;
            background: var(--bg);
            color: var(--text);
            line-height: 1.6;
            min-height: 100vh;
        }
        body::before {
            content: '';
            position: fixed;
            inset: 0;
            background-image: 
                linear-gradient(rgba(6, 182, 212, 0.03) 1px, transparent 1px),
                linear-gradient(90deg, rgba(6, 182, 212, 0.03) 1px, transparent 1px);
            background-size: 60px 60px;
            pointer-events: none;
            z-index: -1;
        }

        a { color: var(--cyan); text-decoration: none; transition: color 0.2s; }
        a:hover { color: var(--cyan-light); }

        .profile-main {
            padding: 40px 0 40px 0;
            max-width: 1100px;
            margin: 0 100px 0 40px; /* 右侧留出 Dock 空间 */
        }

        /* 用户头部信息 */
        .profile-header {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 24px;
            padding: 40px;
            margin-bottom: 32px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            position: relative;
            overflow: hidden;
        }

        .profile-header::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 120px;
            background: linear-gradient(135deg, rgba(6, 182, 212, 0.1), rgba(59, 130, 246, 0.1));
            z-index: 0;
        }

        .profile-info {
            position: relative;
            z-index: 1;
            display: flex;
            gap: 32px;
            align-items: flex-start;
        }

        .profile-avatar {
            width: 120px;
            height: 120px;
            border-radius: 24px;
            background: linear-gradient(135deg, var(--cyan), #3b82f6);
            display: flex;
            align-items: center;
            justify-content: center;
            font-weight: 800;
            font-size: 48px;
            color: #fff;
            flex-shrink: 0;
            box-shadow: 0 8px 32px rgba(6, 182, 212, 0.3);
            position: relative;
        }

        .profile-avatar::after {
            content: '';
            position: absolute;
            inset: -4px;
            border-radius: 28px;
            border: 2px solid rgba(6, 182, 212, 0.3);
        }

        .profile-details {
            flex: 1;
            min-width: 0;
        }

        .profile-name-row {
            display: flex;
            align-items: center;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 8px;
        }

        .profile-name {
            font-size: 32px;
            font-weight: 800;
            background: linear-gradient(135deg, #fff, var(--cyan-light));
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .profile-title {
            font-size: 14px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 12px;
            background: linear-gradient(135deg, #f59e0b, #f97316);
            color: #fff;
            box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3);
            animation: titleGlow 2s ease-in-out infinite alternate;
        }

        @keyframes titleGlow {
            from { box-shadow: 0 2px 8px rgba(245, 158, 11, 0.3); }
            to { box-shadow: 0 2px 16px rgba(245, 158, 11, 0.6); }
        }

        .profile-badge {
            font-size: 11px;
            font-weight: 600;
            padding: 4px 12px;
            border-radius: 12px;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        .badge-admin {
            background: rgba(239, 68, 68, 0.2);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.3);
        }

        .badge-moderator {
            background: rgba(34, 197, 94, 0.2);
            color: #bbf7d0;
            border: 1px solid rgba(34, 197, 94, 0.3);
        }

        .badge-member {
            background: rgba(99, 102, 241, 0.2);
            color: #c7d2fe;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        .profile-bio {
            color: var(--text-secondary);
            font-size: 15px;
            line-height: 1.6;
            margin-bottom: 16px;
            white-space: pre-wrap;
        }

        .profile-meta {
            display: flex;
            gap: 24px;
            color: var(--text-muted);
            font-size: 13px;
            font-weight: 500;
        }

        .profile-meta span {
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .profile-actions {
            display: flex;
            gap: 12px;
            margin-top: 20px;
        }

        .btn-profile {
            padding: 10px 20px;
            border-radius: 12px;
            font-size: 13px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
            text-decoration: none;
        }

        .btn-edit-profile {
            background: linear-gradient(135deg, var(--cyan), #3b82f6);
            color: #fff;
        }

        .btn-edit-profile:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(6, 182, 212, 0.3);
        }

        /* 统计卡片 */
        .profile-stats {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 16px;
            margin-bottom: 32px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            animation-delay: 0.1s;
        }

        .stat-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
            text-align: center;
            transition: all 0.3s;
        }

        .stat-card:hover {
            border-color: var(--border-hover);
            transform: translateY(-4px);
            box-shadow: 0 8px 24px rgba(6, 182, 212, 0.1);
        }

        .stat-num {
            font-size: 36px;
            font-weight: 800;
            background: linear-gradient(135deg, var(--cyan), #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
            margin-bottom: 8px;
        }

        .stat-label {
            font-size: 13px;
            color: var(--text-muted);
            font-weight: 500;
            text-transform: uppercase;
            letter-spacing: 0.5px;
        }

        /* 内容区域 */
        .profile-content {
            display: grid;
            grid-template-columns: 2fr 1fr;
            gap: 24px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            animation-delay: 0.2s;
        }

        .section {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 28px;
        }

        .section-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 24px;
            padding-bottom: 16px;
            border-bottom: 1px solid var(--border);
        }

        .section-title {
            font-size: 20px;
            font-weight: 700;
            display: flex;
            align-items: center;
            gap: 10px;
        }

        .section-title svg {
            width: 20px;
            height: 20px;
            color: var(--cyan);
        }

        .section-link {
            font-size: 13px;
            font-weight: 500;
            color: var(--cyan);
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* 文章列表 */
        .post-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .post-item {
            padding: 20px;
            border-radius: 14px;
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid transparent;
            transition: all 0.3s;
        }

        .post-item:hover {
            border-color: var(--border-hover);
            background: rgba(6, 182, 212, 0.03);
        }

        .post-item-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 10px;
        }

        .post-item-title {
            font-size: 16px;
            font-weight: 600;
            color: var(--text);
            text-decoration: none;
            transition: color 0.2s;
        }

        .post-item-title:hover {
            color: var(--cyan-light);
        }

        .post-item-category {
            font-size: 11px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 8px;
            background: rgba(99, 102, 241, 0.2);
            color: #c7d2fe;
        }

        .post-item-excerpt {
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.5;
            margin-bottom: 12px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .post-item-meta {
            display: flex;
            gap: 16px;
            color: var(--text-muted);
            font-size: 12px;
            font-weight: 500;
        }

        .post-item-meta span {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        /* 回复列表 */
        .reply-list {
            display: flex;
            flex-direction: column;
            gap: 16px;
        }

        .reply-item {
            padding: 16px;
            border-radius: 12px;
            background: rgba(255, 255, 255, 0.01);
            border: 1px solid transparent;
            transition: all 0.3s;
        }

        .reply-item:hover {
            border-color: var(--border-hover);
        }

        .reply-item-title {
            font-size: 14px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 8px;
        }

        .reply-item-excerpt {
            color: var(--text-secondary);
            font-size: 13px;
            line-height: 1.5;
            margin-bottom: 8px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .reply-item-meta {
            color: var(--text-muted);
            font-size: 12px;
        }

        .empty-state {
            text-align: center;
            padding: 40px 20px;
            color: var(--text-muted);
        }

        .empty-state svg {
            width: 48px;
            height: 48px;
            margin-bottom: 12px;
            opacity: 0.4;
        }

        .empty-state p {
            font-size: 14px;
        }

        @keyframes fadeInUp {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @media (max-width: 1024px) {
            .profile-content {
                grid-template-columns: 1fr;
            }
        }

        @media (max-width: 768px) {
            .profile-main {
                padding: 24px 16px 100px;
            }

            .profile-header {
                padding: 24px;
            }

            .profile-info {
                flex-direction: column;
                align-items: center;
                text-align: center;
            }

            .profile-avatar {
                width: 100px;
                height: 100px;
                font-size: 40px;
            }

            .profile-name {
                font-size: 24px;
            }

            .profile-name-row {
                flex-direction: column;
            }

            .profile-meta {
                flex-wrap: wrap;
                justify-content: center;
            }

            .profile-actions {
                justify-content: center;
                flex-wrap: wrap;
            }

            .profile-stats {
                grid-template-columns: repeat(2, 1fr);
            }
        }
    </style>
</head>
<body>
    <canvas id="particles"></canvas>

    <?php require_once 'includes/dock.php'; ?>

    <main class="profile-main">
        <!-- 用户信息头部 -->
        <div class="profile-header">
            <div class="profile-info">
                <div class="profile-avatar"><?= strtoupper(substr($user['username'], 0, 1)) ?></div>
                <div class="profile-details">
                    <div class="profile-name-row">
                        <h1 class="profile-name"><?= htmlspecialchars($user['username']) ?></h1>
                        <?php if ($user['title']): ?>
                            <span class="profile-title"><?= htmlspecialchars($user['title']) ?></span>
                        <?php endif; ?>
                        <span class="profile-badge badge-<?= $user['role'] ?>">
                            <?= $user['role'] === 'admin' ? '👑 管理员' : ($user['role'] === 'moderator' ? '🛡️ 版主' : '👤 成员') ?>
                        </span>
                    </div>
                    <?php if ($user['bio']): ?>
                        <p class="profile-bio"><?= htmlspecialchars($user['bio']) ?></p>
                    <?php endif; ?>
                    <div class="profile-meta">
                        <span>
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path stroke-linecap="round" stroke-linejoin="round" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z"/></svg>
                            注册于 <?= date('Y-m-d', strtotime($user['created_at'])) ?>
                        </span>
                        <?php if ($isCurrentUser): ?>
                            <span>
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>
                                <?= htmlspecialchars($user['email']) ?>
                            </span>
                        <?php endif; ?>
                    </div>
                    <?php if ($isCurrentUser): ?>
                        <div class="profile-actions">
                            <a href="edit-profile.php" class="btn-profile btn-edit-profile">
                                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/></svg>
                                编辑资料
                            </a>
                        </div>
                    <?php endif; ?>
                </div>
            </div>
        </div>

        <!-- 统计卡片 -->
        <div class="profile-stats">
            <div class="stat-card">
                <div class="stat-num"><?= $stats['post_count'] ?></div>
                <div class="stat-label">文章</div>
            </div>
            <div class="stat-card">
                <div class="stat-num"><?= $stats['reply_count'] ?></div>
                <div class="stat-label">回复</div>
            </div>
            <div class="stat-card">
                <div class="stat-num"><?= $stats['total_views'] ?: 0 ?></div>
                <div class="stat-label">浏览</div>
            </div>
            <div class="stat-card">
                <div class="stat-num"><?= $stats['total_likes'] ?: 0 ?></div>
                <div class="stat-label">点赞</div>
            </div>
        </div>

        <!-- 内容区域 -->
        <div class="profile-content">
            <!-- 文章列表 -->
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        文章
                    </h2>
                    <?php if (count($posts) >= 10): ?>
                        <a href="my-posts.php?id=<?= $user['id'] ?>" class="section-link">
                            查看全部
                            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14"><path stroke-linecap="round" stroke-linejoin="round" d="M9 5l7 7-7 7"/></svg>
                        </a>
                    <?php endif; ?>
                </div>
                <?php if (empty($posts)): ?>
                    <div class="empty-state">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/></svg>
                        <p>还没有发表文章</p>
                    </div>
                <?php else: ?>
                    <div class="post-list">
                        <?php foreach ($posts as $post): ?>
                            <div class="post-item">
                                <div class="post-item-header">
                                    <a href="post.php?id=<?= $post['id'] ?>" class="post-item-title"><?= htmlspecialchars($post['title']) ?></a>
                                    <span class="post-item-category"><?= htmlspecialchars($post['category_name']) ?></span>
                                </div>
                                <div class="post-item-excerpt"><?= htmlspecialchars(substr($post['content'], 0, 150)) ?>...</div>
                                <div class="post-item-meta">
                                    <span>📅 <?= date('Y-m-d H:i', strtotime($post['created_at'])) ?></span>
                                    <span>👁️ <?= $post['views'] ?></span>
                                    <span>❤️ <?= $post['likes'] ?></span>
                                    <span>💬 <?= $post['reply_count'] ?></span>
                                </div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </div>

            <!-- 最近回复 -->
            <div class="section">
                <div class="section-header">
                    <h2 class="section-title">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
                        回复
                    </h2>
                </div>
                <?php if (empty($replies)): ?>
                    <div class="empty-state">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"/></svg>
                        <p>还没有回复</p>
                    </div>
                <?php else: ?>
                    <div class="reply-list">
                        <?php foreach ($replies as $reply): ?>
                            <div class="reply-item">
                                <a href="post.php?id=<?= $reply['post_id'] ?>" class="reply-item-title">Re: <?= htmlspecialchars($reply['post_title']) ?></a>
                                <div class="reply-item-excerpt"><?= htmlspecialchars(substr($reply['content'], 0, 100)) ?>...</div>
                                <div class="reply-item-meta"><?= date('Y-m-d H:i', strtotime($reply['created_at'])) ?></div>
                            </div>
                        <?php endforeach; ?>
                    </div>
                <?php endif; ?>
            </div>
        </div>
    </main>

    <script src="../js/particles.js"></script>
    <script src="assets/js/polling-system.js"></script>
    <script src="assets/js/title-updater.js"></script>
</body>
</html>
