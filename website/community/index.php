<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>OSS Community - 开发者社区</title>
    <meta name="description" content="OSS 开发者社区：技术讨论、经验分享、插件开发交流、问题求助。" />
    <meta name="keywords" content="开发者社区, 技术论坛, OSS交流, 插件开发讨论, 技术问题, 经验分享" />
    <meta name="author" content="Falck" />
    <meta property="og:title" content="OSS Community - 开发者社区" />
    <meta property="og:description" content="技术讨论、经验分享、插件开发交流" />
    <meta property="og:type" content="website" />
    <link rel="canonical" href="https://oss-runtime.dev/community/" />
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="../css/main.css" />
    <link rel="stylesheet" href="../css/dock.css" />
    <link rel="stylesheet" href="assets/css/community.css" />
    <link rel="stylesheet" href="assets/css/post-drawer.css" />
</head>
<body>
    <canvas id="particles"></canvas>

    <!-- 引入官网 Dock -->
    <?php require_once 'includes/dock.php'; ?>

    <main class="comm-main">
        <div class="comm-container">
            <!-- 左侧分类导航 -->
            <aside class="comm-sidebar">
                <div class="page-title">
                    <h2>社区</h2>
                </div>
                <div class="sidebar-section">
                    <h3>分类</h3>
                    <ul class="category-list" id="categoryList">
                        <li class="active" data-id="">
                            <span class="cat-icon"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><rect x="3" y="3" width="7" height="7"/><rect x="14" y="3" width="7" height="7"/><rect x="14" y="14" width="7" height="7"/><rect x="3" y="14" width="7" height="7"/></svg></span>
                            <span>全部</span>
                            <span class="cat-count" id="countAll"></span>
                        </li>
                    </ul>
                </div>

                <div class="sidebar-section">
                    <h3>统计</h3>
                    <div class="stats-grid" id="statsGrid">
                        <div class="stat-item">
                            <span class="stat-num" id="statPosts">0</span>
                            <span class="stat-label">帖子</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-num" id="statReplies">0</span>
                            <span class="stat-label">回复</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-num" id="statUsers">0</span>
                            <span class="stat-label">用户</span>
                        </div>
                    </div>
                </div>
            </aside>

            <!-- 右侧帖子列表 -->
            <section class="comm-content">
                <div class="content-header">
                    <h2 id="currentCategory">全部帖子</h2>
                    <div class="sort-options">
                        <button class="sort-btn active" data-sort="latest">最新</button>
                        <button class="sort-btn" data-sort="hot">热门</button>
                        <button class="sort-btn" data-sort="solved">已解决</button>
                    </div>
                </div>

                <div class="posts-list" id="postsList">
                    <!-- 帖子卡片由 JS 动态生成 -->
                </div>

                <div class="pagination" id="pagination"></div>
            </section>
        </div>
    </main>

    <script src="../js/particles.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
    <script src="assets/js/polling-system.js"></script>
    <script src="assets/js/title-updater.js"></script>
    <script src="assets/js/community.js"></script>
    <script src="assets/js/post-drawer.js"></script>
</body>
</html>
