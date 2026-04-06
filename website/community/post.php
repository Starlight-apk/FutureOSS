<?php
require_once __DIR__ . '/includes/Database.php';

$id = (int)($_GET['id'] ?? 0);
if (!$id) { header('Location: index.php'); exit; }

$db = Database::getInstance();
$post = $db->fetchOne(
    "SELECT p.*, u.username, u.avatar, u.role, c.name as category_name 
     FROM posts p JOIN users u ON p.user_id = u.id 
     JOIN categories c ON p.category_id = c.id WHERE p.id = ?",
    [$id]
);

if (!$post) { header('HTTP/1.0 404 Not Found'); exit('帖子不存在'); }

$db->query("UPDATE posts SET views = views + 1 WHERE id = ?", [$id]);
$replies = $db->fetchAll(
    "SELECT r.*, u.username, u.avatar FROM replies r JOIN users u ON r.user_id = u.id WHERE r.post_id = ? ORDER BY r.created_at ASC",
    [$id]
);
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($post['title']) ?> - OSS Community</title>
    <meta name="description" content="<?= htmlspecialchars(mb_substr(strip_tags($post['content']), 0, 150)) ?>..." />
    <meta name="keywords" content="<?= htmlspecialchars($post['title']) ?>, 技术讨论, 开发者社区, 经验分享" />
    <meta name="author" content="Falck" />
    <meta property="og:title" content="<?= htmlspecialchars($post['title']) ?>" />
    <meta property="og:description" content="<?= htmlspecialchars(mb_substr(strip_tags($post['content']), 0, 150)) ?>" />
    <meta property="og:type" content="article" />
    <link rel="canonical" href="https://oss-runtime.dev/community/post.php?id=<?= $post['id'] ?>" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="../css/main.css" />
    <link rel="stylesheet" href="../css/dock.css" />
    <style>
        /* 帖子详情页样式 - 对齐官网 */
        :root { --bg: #030712; --bg-card: rgba(255, 255, 255, 0.02); --border: rgba(255, 255, 255, 0.05); --cyan: #06b6d4; --cyan-light: #22d3ee; --text: #fff; --text-secondary: #9ca3af; --text-muted: #6b7280; }
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { font-family: 'Inter', sans-serif; background: var(--bg); color: var(--text); line-height: 1.6; }
        a { color: var(--cyan); text-decoration: none; }
        body::before { content: ''; position: fixed; inset: 0; background-image: linear-gradient(rgba(6, 182, 212, 0.03) 1px, transparent 1px), linear-gradient(90deg, rgba(6, 182, 212, 0.03) 1px, transparent 1px); background-size: 60px 60px; pointer-events: none; z-index: -1; }
        .header { padding: 20px 24px 20px 80px; display: flex; align-items: center; gap: 16px; }
        .back-link { color: var(--text-muted); transition: all 0.3s; display: flex; align-items: center; gap: 4px; }
        .back-link:hover { color: var(--cyan-light); transform: translateX(-4px); }
        .container { max-width: 800px; margin: 0 auto; padding: 24px; }
        .post-header { margin-bottom: 32px; animation: fadeInUp 0.6s ease forwards; opacity: 0; }
        .post-title { font-size: 32px; font-weight: 800; margin-bottom: 16px; line-height: 1.2; }
        .post-meta { display: flex; align-items: center; gap: 12px; color: var(--text-muted); font-size: 14px; }
        .avatar { width: 44px; height: 44px; border-radius: 12px; background: linear-gradient(135deg, var(--cyan), #3b82f6); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 18px; color: #fff; }
        .post-content { font-size: 16px; line-height: 1.8; margin-bottom: 32px; white-space: pre-wrap; background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 24px; }
        .post-stats { display: flex; gap: 16px; color: var(--text-muted); font-size: 13px; margin-bottom: 40px; font-weight: 500; }
        .replies-header { font-size: 20px; font-weight: 700; margin-bottom: 24px; padding-top: 24px; border-top: 1px solid var(--border); }
        .reply-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 16px; padding: 24px; margin-bottom: 16px; transition: all 0.3s; animation: cardEnter 0.5s ease forwards; opacity: 0; }
        .reply-card:hover { border-color: var(--border-hover); }
        .reply-content { margin-top: 12px; white-space: pre-wrap; color: var(--text-secondary); line-height: 1.7; }
        .empty-replies { color: var(--text-muted); text-align: center; padding: 60px 0; }
        @keyframes fadeInUp { to { opacity: 1; transform: translateY(0); } }
        @keyframes cardEnter { to { opacity: 1; transform: translateY(0); } }
    </style>
</head>
<body>
    <?php require_once 'includes/dock.php'; ?>

    <header class="header">
        <a href="index.php" class="back-link">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="20" height="20"><path stroke-linecap="round" stroke-linejoin="round" d="M10 19l-7-7m0 0l7-7m-7 7h18"/></svg>
            返回列表
        </a>
    </header>

    <main class="container">
        <article>
            <div class="post-header">
                <h1 class="post-title"><?= htmlspecialchars($post['title']) ?></h1>
                <div class="post-meta">
                    <div class="avatar"><?= $post['username'][0] ?></div>
                    <div>
                        <div style="color: var(--text); font-weight: 600;"><?= htmlspecialchars($post['username']) ?></div>
                        <div><?= date('Y-m-d H:i', strtotime($post['created_at'])) ?> · <span style="color:var(--cyan)"><?= htmlspecialchars($post['category_name']) ?></span></div>
                    </div>
                </div>
            </div>
            <div class="post-content"><?= nl2br(htmlspecialchars($post['content'])) ?></div>
            <div class="post-stats">
                <span>👁️ <?= $post['views'] ?> 浏览</span>
                <span>❤️ <?= $post['likes'] ?> 点赞</span>
                <span>💬 <?= count($replies) ?> 回复</span>
            </div>
        </article>

        <section>
            <h2 class="replies-header">回复 (<?= count($replies) ?>)</h2>
            <?php if (empty($replies)): ?>
                <div class="empty-replies">暂无回复，抢沙发吧！</div>
            <?php else: ?>
                <?php foreach ($replies as $reply): ?>
                    <div class="reply-card" style="animation-delay: <?= $reply['id'] * 0.05 ?>s">
                        <div class="post-meta">
                            <div class="avatar" style="width:36px;height:36px;font-size:15px;border-radius:10px;"><?= $reply['username'][0] ?></div>
                            <div>
                                <div style="color:var(--text);font-weight:600;"><?= htmlspecialchars($reply['username']) ?></div>
                                <div><?= date('Y-m-d H:i', strtotime($reply['created_at'])) ?></div>
                            </div>
                        </div>
                        <div class="reply-content"><?= nl2br(htmlspecialchars($reply['content'])) ?></div>
                    </div>
                <?php endforeach; ?>
            <?php endif; ?>
        </section>
    </main>
    <script src="../js/particles.js"></script>
</body>
</html>
