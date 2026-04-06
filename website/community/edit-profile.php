<?php
session_start();
if (!isset($_SESSION['user_id'])) {
    header('Location: login.php');
    exit;
}

require_once 'includes/Database.php';

$db = Database::getInstance();
$userId = $_SESSION['user_id'];

// 获取用户信息
$user = $db->fetchOne(
    "SELECT id, username, email, bio FROM users WHERE id = ?",
    [$userId]
);

$success = $_GET['success'] ?? '';
$error = $_GET['error'] ?? '';

// 处理表单提交
if ($_SERVER['REQUEST_METHOD'] === 'POST') {
    $bio = trim($_POST['bio'] ?? '');
    
    try {
        $db->query(
            "UPDATE users SET bio = ? WHERE id = ?",
            [$bio, $userId]
        );
        header('Location: edit-profile.php?success=1');
        exit;
    } catch (Exception $e) {
        $error = '保存失败：' . $e->getMessage();
    }
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>编辑资料 - OSS Community</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
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
            --success: #22c55e;
            --error: #ef4444;
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

        .edit-profile-main {
            padding: 40px 100px 40px 24px;
            max-width: 900px;
            margin: 0 auto;
        }

        .edit-profile-header {
            margin-bottom: 32px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
        }

        .edit-profile-title {
            font-size: 32px;
            font-weight: 800;
            margin-bottom: 12px;
            background: linear-gradient(135deg, #06b6d4, #3b82f6);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            background-clip: text;
        }

        .edit-profile-subtitle {
            color: var(--text-secondary);
            font-size: 14px;
        }

        .alert {
            padding: 16px 20px;
            border-radius: 12px;
            margin-bottom: 24px;
            font-size: 14px;
            font-weight: 500;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
        }

        .alert-success {
            background: rgba(34, 197, 94, 0.1);
            border: 1px solid rgba(34, 197, 94, 0.3);
            color: #86efac;
        }

        .alert-error {
            background: rgba(239, 68, 68, 0.1);
            border: 1px solid rgba(239, 68, 68, 0.3);
            color: #fca5a5;
        }

        .edit-profile-form {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 20px;
            padding: 32px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            animation-delay: 0.1s;
        }

        .form-group {
            margin-bottom: 24px;
        }

        .form-label {
            display: block;
            font-size: 14px;
            font-weight: 600;
            color: var(--text);
            margin-bottom: 8px;
        }

        .form-label-hint {
            font-size: 12px;
            color: var(--text-muted);
            font-weight: 400;
            margin-left: 8px;
        }

        .form-input,
        .form-textarea {
            width: 100%;
            padding: 12px 16px;
            border-radius: 12px;
            border: 1px solid var(--border);
            background: rgba(255, 255, 255, 0.02);
            color: var(--text);
            font-family: 'Inter', sans-serif;
            font-size: 14px;
            transition: all 0.2s;
        }

        .form-input:focus,
        .form-textarea:focus {
            outline: none;
            border-color: var(--cyan);
            background: rgba(6, 182, 212, 0.05);
        }

        .form-input:disabled {
            opacity: 0.5;
            cursor: not-allowed;
        }

        .form-textarea {
            min-height: 120px;
            resize: vertical;
            line-height: 1.6;
        }

        .form-actions {
            display: flex;
            gap: 12px;
            justify-content: flex-end;
            padding-top: 24px;
            border-top: 1px solid var(--border);
        }

        .btn {
            padding: 12px 24px;
            border-radius: 12px;
            font-size: 14px;
            font-weight: 600;
            cursor: pointer;
            border: none;
            transition: all 0.3s;
            display: flex;
            align-items: center;
            gap: 8px;
        }

        .btn-primary {
            background: linear-gradient(135deg, var(--cyan), #3b82f6);
            color: #fff;
        }

        .btn-primary:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 24px rgba(6, 182, 212, 0.3);
        }

        .btn-secondary {
            background: rgba(255, 255, 255, 0.05);
            color: var(--text-secondary);
            border: 1px solid var(--border);
        }

        .btn-secondary:hover {
            background: rgba(255, 255, 255, 0.1);
            color: var(--text);
        }

        .preview-section {
            margin-top: 32px;
            animation: fadeInUp 0.6s ease forwards;
            opacity: 0;
            animation-delay: 0.2s;
        }

        .preview-title {
            font-size: 20px;
            font-weight: 700;
            margin-bottom: 16px;
        }

        .preview-card {
            background: var(--bg-card);
            border: 1px solid var(--border);
            border-radius: 16px;
            padding: 24px;
        }

        .preview-bio {
            color: var(--text-secondary);
            font-size: 14px;
            line-height: 1.6;
            white-space: pre-wrap;
            margin-top: 12px;
        }

        .preview-empty {
            color: var(--text-muted);
            font-style: italic;
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

        @media (max-width: 768px) {
            .edit-profile-main {
                padding: 24px 16px 100px;
            }

            .edit-profile-form {
                padding: 24px;
            }

            .form-actions {
                flex-direction: column;
            }

            .btn {
                width: 100%;
                justify-content: center;
            }
        }
    </style>
</head>
<body>
    <canvas id="particles"></canvas>

    <?php require_once 'includes/dock.php'; ?>

    <main class="edit-profile-main">
        <div class="edit-profile-header">
            <h1 class="edit-profile-title">编辑个人资料</h1>
            <p class="edit-profile-subtitle">更新您的个人简介和公开信息</p>
        </div>

        <?php if ($success): ?>
            <div class="alert alert-success">
                ✓ 资料已成功更新
            </div>
        <?php endif; ?>

        <?php if ($error): ?>
            <div class="alert alert-error">
                ✗ <?= htmlspecialchars($error) ?>
            </div>
        <?php endif; ?>

        <form class="edit-profile-form" method="POST">
            <div class="form-group">
                <label class="form-label">用户名</label>
                <input type="text" class="form-input" value="<?= htmlspecialchars($user['username']) ?>" disabled>
            </div>

            <div class="form-group">
                <label class="form-label">邮箱</label>
                <input type="email" class="form-input" value="<?= htmlspecialchars($user['email']) ?>" disabled>
            </div>

            <div class="form-group">
                <label class="form-label">
                    个人简介
                    <span class="form-label-hint">这段介绍将显示在您的个人主页上</span>
                </label>
                <textarea name="bio" id="bioInput" class="form-textarea" placeholder="介绍一下自己吧！例如：您的技术栈、兴趣爱好、项目经验等..."><?= htmlspecialchars($user['bio'] ?? '') ?></textarea>
            </div>

            <div class="form-actions">
                <a href="profile.php" class="btn btn-secondary">
                    取消
                </a>
                <button type="submit" class="btn btn-primary">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="16" height="16"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
                    保存更改
                </button>
            </div>
        </form>

        <div class="preview-section">
            <h2 class="preview-title">预览</h2>
            <div class="preview-card">
                <div style="display: flex; align-items: center; gap: 16px; margin-bottom: 16px;">
                    <div style="width: 60px; height: 60px; border-radius: 16px; background: linear-gradient(135deg, #06b6d4, #3b82f6); display: flex; align-items: center; justify-content: center; font-weight: 800; font-size: 24px; color: #fff; flex-shrink: 0;">
                        <?= strtoupper(substr($user['username'], 0, 1)) ?>
                    </div>
                    <div>
                        <div style="font-size: 20px; font-weight: 700;"><?= htmlspecialchars($user['username']) ?></div>
                        <div style="font-size: 12px; color: var(--text-muted); text-transform: uppercase;"><?= $user['role'] ?></div>
                    </div>
                </div>
                <div id="bioPreview" class="preview-bio">
                    <?= $user['bio'] ? htmlspecialchars($user['bio']) : '<span class="preview-empty">暂无简介</span>' ?>
                </div>
            </div>
        </div>
    </main>

    <script src="../js/particles.js"></script>
    <script src="assets/js/dock-popover.js"></script>
    <script>
        // 实时更新预览
        const bioInput = document.getElementById('bioInput');
        const bioPreview = document.getElementById('bioPreview');

        bioInput.addEventListener('input', () => {
            const value = bioInput.value.trim();
            if (value) {
                bioPreview.textContent = value;
            } else {
                bioPreview.innerHTML = '<span class="preview-empty">暂无简介</span>';
            }
        });
    </script>
</body>
</html>
