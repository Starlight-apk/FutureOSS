<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?= htmlspecialchars($pageTitle ?? 'FutureOSS') ?></title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/remixicon/4.1.0/remixicon.min.css">
    <link rel="stylesheet" href="/static/css/main.css">
    <script src="https://cdn.jsdelivr.net/npm/alpinejs@3.13.3/dist/cdn.min.js" defer></script>
</head>
<body>
    <div class="app">
        <aside class="sidebar">
            <nav class="sidebar-nav">
                <?php if (!empty($navItems)): ?>
                    <?php foreach ($navItems as $item): ?>
                        <?php
                            $url = $item['url'] ?? '#';
                            $isActive = ($currentPage ?? '') === $url;
                            $icon = $item['icon'] ?? 'ri-dashboard-line';
                            // 如果图标是 emoji，转换为 remixicon 类名
                            $iconMap = [
                                '🏠' => 'ri-home-4-line',
                                '📊' => 'ri-dashboard-line',
                                '📋' => 'ri-file-list-3-line',
                                '🧩' => 'ri-puzzle-line',
                                '⚙️' => 'ri-settings-3-line',
                                '🔌' => 'ri-plug-line',
                                '📦' => 'ri-box-3-line',
                                '🌐' => 'ri-global-line',
                            ];
                            $riIcon = $iconMap[$icon] ?? $icon;
                        ?>
                        <a href="<?= htmlspecialchars($url) ?>"
                           class="nav-item <?= $isActive ? 'active' : '' ?>"
                           title="<?= htmlspecialchars($item['text'] ?? '') ?>">
                            <i class="<?= htmlspecialchars($riIcon) ?>"></i>
                        </a>
                    <?php endforeach; ?>
                <?php endif; ?>
            </nav>
            <div class="sidebar-footer">
                <button class="settings-btn" title="设置">
                    <i class="ri-settings-3-line"></i>
                </button>
            </div>
        </aside>

        <main class="content">
            <div class="content-body">
                <?php if (isset($content)): ?>
                    <?= $content ?>
                <?php else: ?>
                    <div class="empty-state">
                        <p>暂无内容</p>
                    </div>
                <?php endif; ?>
            </div>
        </main>
    </div>

    <script src="/static/js/main.js"></script>
</body>
</html>
