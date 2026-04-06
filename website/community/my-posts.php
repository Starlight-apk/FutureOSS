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
$user = $db->fetchOne("SELECT id, username FROM users WHERE id = ?", [$viewUserId]);

if (!$user) {
    header('HTTP/1.0 404 Not Found');
    exit('用户不存在');
}

$isCurrentUser = ($currentUserId == $viewUserId);

// 获取用户文章
$page = max(1, (int)($_GET['page'] ?? 1));
$limit = 20;
$offset = ($page - 1) * $limit;

$posts = $db->fetchAll(
    "SELECT p.*, c.name as category_name, c.slug as category_slug,
            (SELECT COUNT(*) FROM replies r WHERE r.post_id = p.id) as reply_count
     FROM posts p
     JOIN categories c ON p.category_id = c.id
     WHERE p.user_id = ?
     ORDER BY p.is_pinned DESC, p.created_at DESC
     LIMIT ? OFFSET ?",
    [$viewUserId, $limit, $offset]
);

$total = $db->fetchOne("SELECT COUNT(*) as count FROM posts WHERE user_id = ?", [$viewUserId])['count'];
$pages = ceil($total / $limit);
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($user['username']) ?> 的文章 - OSS Community</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="../css/main.css" />
    <link rel="stylesheet" href="../css/dock.css" />
    <link rel="stylesheet" href="assets/css/community.css" />
    <link rel="stylesheet" href="assets/css/dock-popover.css" />
    <style>
        .my-posts-main {
            padding: 40px 0 40px 0;
            max-width: 1100px;
            margin: 0 100px 0 40px; /* 右侧留出 Dock 空间 */
        }

        .my-posts-header {
            margin-bottom: 32px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
        }

        .my-posts-title {
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #06b6d4, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .my-posts-subtitle {
            color: #9ca3af;
            font-size: 14px;
        }

        .my-posts-stats {
            display: flex;
            gap: 24px;
            margin-bottom: 32px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            animation-delay: 0.1s;
        }

        .stat-card {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 20px 24px;
            flex: 1;
        }

        .stat-card-num {
            font-size: 28px;
            font-weight: 800;
            color: #06b6d4;
            margin-bottom: 4px;
        }

        .stat-card-label {
            font-size: 13px;
            color: #6b7280;
            font-weight: 500;
        }

        .my-posts-list {
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            animation-delay: 0.2s;
        }

        .my-post-item {
            background: rgba(255, 255, 255, 0.02);
            border: 1px solid rgba(255, 255, 255, 0.05);
            border-radius: 16px;
            padding: 24px;
            margin-bottom: 16px;
            transition: all 0.3s;
            animation: cardEnter 0.5s ease forwards;
            opacity: 0;
        }

        .my-post-item:hover {
            border-color: rgba(6, 182, 212, 0.3);
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(6, 182, 212, 0.1);
        }

        .my-post-header {
            display: flex;
            align-items: center;
            justify-content: space-between;
            margin-bottom: 12px;
        }

        .my-post-title {
            font-size: 18px;
            font-weight: 700;
            color: #fff;
            text-decoration: none;
            transition: color 0.2s;
        }

        .my-post-title:hover {
            color: #22d3ee;
        }

        .my-post-badges {
            display: flex;
            gap: 8px;
        }

        .badge {
            font-size: 11px;
            font-weight: 600;
            padding: 4px 10px;
            border-radius: 8px;
            background: rgba(99, 102, 241, 0.2);
            color: #c7d2fe;
        }

        .badge-pinned {
            background: rgba(6, 182, 212, 0.2);
            color: #a5f3fc;
        }

        .badge-solved {
            background: rgba(34, 197, 94, 0.2);
            color: #bbf7d0;
        }

        .my-post-excerpt {
            color: #9ca3af;
            font-size: 14px;
            line-height: 1.6;
            margin-bottom: 16px;
            display: -webkit-box;
            -webkit-line-clamp: 2;
            -webkit-box-orient: vertical;
            overflow: hidden;
        }

        .my-post-meta {
            display: flex;
            gap: 16px;
            color: #6b7280;
            font-size: 13px;
            font-weight: 500;
        }

        .my-post-meta span {
            display: flex;
            align-items: center;
            gap: 4px;
        }

        .my-post-actions {
            display: flex;
            gap: 12px;
            margin-top: 16px;
            padding-top: 16px;
            border-top: 1px solid rgba(255, 255, 255, 0.05);
        }

        .my-post-action {
            font-size: 13px;
            font-weight: 500;
            padding: 6px 14px;
            border-radius: 8px;
            text-decoration: none;
            transition: all 0.2s;
            display: flex;
            align-items: center;
            gap: 6px;
        }

        .btn-edit {
            background: rgba(99, 102, 241, 0.2);
            color: #c7d2fe;
            border: 1px solid rgba(99, 102, 241, 0.3);
        }

        .btn-edit:hover {
            background: rgba(99, 102, 241, 0.3);
            color: #fff;
        }

        .btn-delete {
            background: rgba(239, 68, 68, 0.1);
            color: #fca5a5;
            border: 1px solid rgba(239, 68, 68, 0.2);
        }

        .btn-delete:hover {
            background: rgba(239, 68, 68, 0.2);
            color: #fff;
        }

        .empty-state {
            text-align: center;
            padding: 80px 24px;
            color: #6b7280;
        }

        .empty-state svg {
            width: 64px;
            height: 64px;
            margin-bottom: 16px;
            opacity: 0.5;
        }

        .empty-state h3 {
            font-size: 18px;
            font-weight: 600;
            color: #9ca3af;
            margin-bottom: 8px;
        }

        .empty-state p {
            font-size: 14px;
            margin-bottom: 24px;
        }

        .empty-state a {
            display: inline-flex;
            align-items: center;
            gap: 8px;
            padding: 10px 20px;
            background: linear-gradient(135deg, #06b6d4, #3b82f6);
            color: #fff;
            text-decoration: none;
            border-radius: 10px;
            font-weight: 600;
            transition: all 0.3s;
        }

        .empty-state a:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(6, 182, 212, 0.3);
        }

        .pagination {
            display: flex;
            justify-content: center;
            gap: 8px;
            margin-top: 32px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            animation-delay: 0.3s;
        }

        .pagination button {
            padding: 8px 14px;
            border-radius: 8px;
            border: 1px solid rgba(255, 255, 255, 0.1);
            background: rgba(255, 255, 255, 0.02);
            color: #9ca3af;
            font-size: 13px;
            font-weight: 500;
            cursor: pointer;
            transition: all 0.2s;
        }

        .pagination button:hover:not(:disabled) {
            border-color: rgba(6, 182, 212, 0.3);
            color: #06b6d4;
        }

        .pagination button.active {
            background: rgba(6, 182, 212, 0.2);
            border-color: rgba(6, 182, 212, 0.4);
            color: #06b6d4;
        }

        .pagination button:disabled {
            opacity: 0.3;
            cursor: not-allowed;
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

        @keyframes cardEnter {
            from {
                opacity: 0;
                transform: translateY(20px);
            }
            to {
                opacity: 1;
                transform: translateY(0);
            }
        }

        @media (max-width: 768px) {
            .my-posts-main {
                padding: 24px 16px 100px;
            }

            .my-posts-stats {
                flex-direction: column;
            }

            .my-post-header {
                flex-direction: column;
                align-items: flex-start;
                gap: 12px;
            }

            .my-post-actions {
                flex-wrap: wrap;
            }
        }
    </style>
</head>
<body>
    <canvas id="particles"></canvas>

    <?php require_once 'includes/dock.php'; ?>

    <main class="my-posts-main">
        <div class="my-posts-header">
            <h1 class="my-posts-title"><?= $isCurrentUser ? '我的文章' : htmlspecialchars($user['username']) . ' 的文章' ?></h1>
            <p class="my-posts-subtitle"><?= $isCurrentUser ? '管理您发表的所有文章' : '查看此用户发表的所有文章' ?></p>
        </div>

        <div class="my-posts-stats">
            <div class="stat-card">
                <div class="stat-card-num"><?= $total ?></div>
                <div class="stat-card-label">文章总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-num"><?= array_sum(array_column($posts, 'views')) ?></div>
                <div class="stat-card-label">总浏览量</div>
            </div>
            <div class="stat-card">
                <div class="stat-card-num"><?= array_sum(array_column($posts, 'likes')) ?></div>
                <div class="stat-card-label">总点赞数</div>
            </div>
        </div>

        <div class="my-posts-list">
            <?php if (empty($posts)): ?>
                <div class="empty-state">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path stroke-linecap="round" stroke-linejoin="round" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
                    </svg>
                    <h3>还没有发表文章</h3>
                    <p>开始创作您的第一篇文章吧！</p>
                    <a href="editor.php">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M12 5v14m-7-7h14"/>
                        </svg>
                        发表文章
                    </a>
                </div>
            <?php else: ?>
                <?php foreach ($posts as $index => $post): ?>
                    <div class="my-post-item" style="animation-delay: <?= $index * 0.05 ?>s">
                        <div class="my-post-header">
                            <a href="post.php?id=<?= $post['id'] ?>" class="my-post-title"><?= htmlspecialchars($post['title']) ?></a>
                            <div class="my-post-badges">
                                <?php if ($post['is_pinned']): ?>
                                    <span class="badge badge-pinned">📌 置顶</span>
                                <?php endif; ?>
                                <?php if ($post['is_solved']): ?>
                                    <span class="badge badge-solved">✓ 已解决</span>
                                <?php endif; ?>
                                <span class="badge"><?= htmlspecialchars($post['category_name']) ?></span>
                            </div>
                        </div>
                        <div class="my-post-excerpt"><?= htmlspecialchars(substr($post['content'], 0, 200)) ?>...</div>
                        <div class="my-post-meta">
                            <span>📅 <?= date('Y-m-d H:i', strtotime($post['created_at'])) ?></span>
                            <span>👁️ <?= $post['views'] ?> 浏览</span>
                            <span>❤️ <?= $post['likes'] ?> 点赞</span>
                            <span>💬 <?= $post['reply_count'] ?> 回复</span>
                        </div>
                        <div class="my-post-actions">
                            <?php if ($isCurrentUser): ?>
                                <a href="editor.php?id=<?= $post['id'] ?>" class="my-post-action btn-edit">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                                    </svg>
                                    编辑
                                </a>
                                <button class="my-post-action btn-delete" onclick="deletePost(<?= $post['id'] ?>)">
                                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="14" height="14">
                                        <polyline points="3 6 5 6 21 6"/>
                                        <path stroke-linecap="round" stroke-linejoin="round" d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
                                    </svg>
                                    删除
                                </button>
                            <?php endif; ?>
                        </div>
                    </div>
                <?php endforeach; ?>

                <?php if ($pages > 1): ?>
                    <div class="pagination">
                        <button <?= $page <= 1 ? 'disabled' : '' ?> onclick="window.location.href='?page=<?= $page - 1 ?>'">上一页</button>
                        <?php for ($i = 1; $i <= $pages; $i++): ?>
                            <button class="<?= $i === $page ? 'active' : '' ?>" onclick="window.location.href='?page=<?= $i ?>'"><?= $i ?></button>
                        <?php endfor; ?>
                        <button <?= $page >= $pages ? 'disabled' : '' ?> onclick="window.location.href='?page=<?= $page + 1 ?>'">下一页</button>
                    </div>
                <?php endif; ?>
            <?php endif; ?>
        </div>
    </main>

    <script src="../js/particles.js"></script>
    <script src="assets/js/dock-popover.js"></script>
    <script>
        async function deletePost(postId) {
            if (!confirm('确定要删除这篇文章吗？\n此操作不可撤销。')) {
                return;
            }

            try {
                const res = await fetch('api/posts.php', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ action: 'delete', post_id: postId })
                });

                const data = await res.json();

                if (data.success) {
                    alert('文章已删除');
                    window.location.reload();
                } else {
                    alert('删除失败：' + (data.message || '未知错误'));
                }
            } catch (err) {
                console.error('Delete post error:', err);
                alert('删除失败，请稍后重试');
            }
        }
    </script>
</body>
</html>
