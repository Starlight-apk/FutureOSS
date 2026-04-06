<?php
/**
 * OSS Community - 发帖/编辑页面
 */
session_start();
require_once __DIR__ . '/includes/Database.php';

if (!isset($_SESSION['user_id'])) { header('Location: login.php'); exit; }

$postId = isset($_GET['id']) ? (int)$_GET['id'] : 0;
$isEdit = $postId > 0;
$postData = null;

if ($isEdit) {
    $db = Database::getInstance();
    $post = $db->fetchOne("SELECT * FROM posts WHERE id = ? AND user_id = ?", [$postId, $_SESSION['user_id']]);
    if (!$post) { http_response_code(404); die('帖子不存在或无权编辑'); }
    $postData = $post;
}

$db = Database::getInstance();
$categories = $db->fetchAll("SELECT * FROM categories ORDER BY sort_order ASC");
$allTags = $db->fetchAll("SELECT * FROM tags ORDER BY name ASC");
$postTags = [];
if ($postData) {
    $postTags = $db->fetchAll("SELECT t.* FROM tags t JOIN post_tags pt ON t.id = pt.tag_id WHERE pt.post_id = ?", [$postId]);
}
?>
<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title><?php echo $isEdit ? '编辑帖子' : '发布新帖'; ?> - OSS Community</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="../css/main.css" />
    <link rel="stylesheet" href="../css/dock.css" />
    <link rel="stylesheet" href="assets/css/editor.css" />
    <script src="https://cdn.jsdelivr.net/npm/marked/marked.min.js"></script>
</head>
<body>
    <canvas id="particles"></canvas>
    <?php require_once 'includes/dock.php'; ?>

    <main class="editor-page">
        <div class="editor-container">
            <!-- 顶部工具栏 -->
            <header class="editor-toolbar">
                <div class="toolbar-left">
                    <a href="index.php" class="back-btn">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M15 19l-7-7 7-7"/></svg>
                        返回
                    </a>
                    <h1 class="toolbar-title"><?php echo $isEdit ? '编辑帖子' : '发布新帖'; ?></h1>
                </div>
                <div class="toolbar-right">
                    <button type="button" class="btn btn-primary" id="savePostBtn">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
                        <?php echo $isEdit ? '保存修改' : '发布帖子'; ?>
                    </button>
                </div>
            </header>

            <form id="postEditorForm" class="editor-form">
                <input type="hidden" id="editPostId" value="<?php echo $postId; ?>" />

                <!-- 标题 -->
                <div class="editor-header">
                    <input type="text" id="postTitle" name="title" class="title-input" placeholder="帖子标题..." value="<?php echo $postData ? htmlspecialchars($postData['title']) : ''; ?>" required maxlength="200" />
                </div>

                <!-- 两栏工作区 -->
                <div class="editor-workspace">
                    <!-- 左栏：Markdown 编辑器 -->
                    <div class="editor-panel" id="editorPanel">
                        <div class="panel-header">
                            <span class="panel-title">Markdown 编辑器</span>
                            <div class="panel-actions">
                                <button type="button" class="md-btn" data-md="bold" title="粗体"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 4h8a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/><path d="M6 12h9a4 4 0 0 1 4 4 4 4 0 0 1-4 4H6z"/></svg></button>
                                <button type="button" class="md-btn" data-md="italic" title="斜体"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="19" y1="4" x2="10" y2="4"/><line x1="14" y1="20" x2="5" y2="20"/><line x1="15" y1="4" x2="9" y2="20"/></svg></button>
                                <button type="button" class="md-btn" data-md="heading" title="标题"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M6 4v16"/><path d="M18 4v16"/><path d="M6 12h12"/></svg></button>
                                <button type="button" class="md-btn" data-md="quote" title="引用"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M3 21c3 0 7-1 7-8V5c0-1.25-.756-2.017-2-2H4c-1.25 0-2 .75-2 1.972V11c0 1.25.75 2 2 2 1 0 1 0 1 1v1c0 1-1 2-2 2s-1 .008-1 1.031V20c0 1 0 1 1 1z"/></svg></button>
                                <button type="button" class="md-btn" data-md="code" title="代码"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="16 18 22 12 16 6"/><polyline points="8 6 2 12 8 18"/></svg></button>
                                <button type="button" class="md-btn" data-md="link" title="链接"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"/><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"/></svg></button>
                                <button type="button" class="md-btn" data-md="list" title="列表"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><line x1="8" y1="6" x2="21" y2="6"/><line x1="8" y1="12" x2="21" y2="12"/><line x1="8" y1="18" x2="21" y2="18"/><line x1="3" y1="6" x2="3.01" y2="6"/><line x1="3" y1="12" x2="3.01" y2="12"/><line x1="3" y1="18" x2="3.01" y2="18"/></svg></button>
                            </div>
                        </div>
                        <textarea id="postContent" name="content" class="editor-textarea" placeholder="开始写作...&#10;&#10;# 标题&#10;**粗体** *斜体*&#10;- 列表&#10;> 引用&#10;`代码`"><?php echo $postData ? htmlspecialchars($postData['content']) : ''; ?></textarea>
                    </div>

                    <!-- 右栏：标签和分类 -->
                    <aside class="sidebar-panel">
                        <div class="sidebar-section">
                            <div class="sidebar-title">分类</div>
                            <select id="postCategory" name="category_id" class="meta-select-large" required>
                                <option value="">选择分类</option>
                                <?php foreach ($categories as $cat): ?>
                                    <?php
                                    if ($cat['slug'] === 'announcements') continue;
                                    ?>
                                    <option value="<?php echo $cat['id']; ?>" <?php echo ($postData && $postData['category_id'] == $cat['id']) ? 'selected' : ''; ?>><?php echo htmlspecialchars($cat['name']); ?></option>
                                <?php endforeach; ?>
                            </select>
                        </div>

                        <div class="sidebar-section">
                            <div class="sidebar-title">标签</div>
                            <input type="text" id="tagInput" class="tag-input" placeholder="输入标签后按回车..." />
                            <div class="tags-container" id="tagsContainer">
                                <?php foreach ($postTags as $tag): ?>
                                    <span class="tag-item">
                                        <?php echo htmlspecialchars($tag['name']); ?>
                                        <button type="button" class="tag-remove" onclick="this.parentElement.remove()">&times;</button>
                                    </span>
                                <?php endforeach; ?>
                            </div>
                            <div class="tags-suggestions">
                                <?php foreach ($allTags as $tag): ?>
                                    <span class="tag-suggestion" onclick="addTag('<?php echo addslashes($tag['name']); ?>')"><?php echo htmlspecialchars($tag['name']); ?></span>
                                <?php endforeach; ?>
                            </div>
                        </div>

                        <div class="sidebar-section">
                            <div class="sidebar-title">Markdown 语法</div>
                            <div class="markdown-help">
                                <div class="help-item"><code># 标题</code> 一级标题</div>
                                <div class="help-item"><code>## 标题</code> 二级标题</div>
                                <div class="help-item"><code>**粗体**</code> 粗体文字</div>
                                <div class="help-item"><code>*斜体*</code> 斜体文字</div>
                                <div class="help-item"><code>`代码`</code> 行内代码</div>
                                <div class="help-item"><code>> 引用</code> 引用块</div>
                                <div class="help-item"><code>- 列表</code> 无序列表</div>
                                <div class="help-item"><code>[链接](url)</code> 超链接</div>
                            </div>
                        </div>
                    </aside>
                </div>
            </form>
        </div>
    </main>

    <div id="successToast" class="toast toast-success" style="display: none;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/></svg>
        <span id="successMessage"></span>
    </div>
    <div id="errorToast" class="toast toast-error" style="display: none;">
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/></svg>
        <span id="errorMessage"></span>
    </div>

    <script src="../js/particles.js"></script>
    <script src="assets/js/editor.js"></script>
</body>
</html>
