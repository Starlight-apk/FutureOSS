<?php
/**
 * OSS Community 帖子管理 API
 * 处理帖子创建、编辑、删除、置顶等操作
 */

session_start();
require_once __DIR__ . '/../includes/Database.php';

header('Content-Type: application/json');

// 只允许 POST 请求
if ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => '请求方法不允许']);
    exit;
}

$action = $_GET['action'] ?? '';

// 检查登录状态（除了查看操作）
$requireAuth = in_array($action, ['create', 'update', 'delete', 'pin', 'lock']);
if ($requireAuth && !isset($_SESSION['user_id'])) {
    echo json_encode(['success' => false, 'message' => '请先登录']);
    exit;
}

switch ($action) {
    case 'create':
        handleCreatePost();
        break;
    case 'update':
        handleUpdatePost();
        break;
    case 'delete':
        handleDeletePost();
        break;
    case 'pin':
        handlePinPost();
        break;
    case 'lock':
        handleLockPost();
        break;
    default:
        http_response_code(400);
        echo json_encode(['success' => false, 'message' => '无效的操作类型']);
}

/**
 * 创建帖子
 */
function handleCreatePost() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (empty($input['title']) || empty($input['content']) || empty($input['category_id'])) {
        echo json_encode(['success' => false, 'message' => '标题、内容和分类不能为空']);
        return;
    }

    $title = trim($input['title']);
    $content = trim($input['content']);
    $categoryId = (int)$input['category_id'];
    $tags = $input['tags'] ?? [];

    // 验证标题长度
    if (mb_strlen($title) < 5 || mb_strlen($title) > 200) {
        echo json_encode(['success' => false, 'message' => '标题长度必须在 5-200 个字符之间']);
        return;
    }

    // 验证内容长度
    if (mb_strlen($content) < 10) {
        echo json_encode(['success' => false, 'message' => '内容至少 10 个字符']);
        return;
    }

    try {
        $db = Database::getInstance();
        $userId = $_SESSION['user_id'];
        $userRole = $_SESSION['role'] ?? 'member';

        // 验证分类是否存在
        $category = $db->fetchOne("SELECT * FROM categories WHERE id = ?", [$categoryId]);
        if (!$category) {
            echo json_encode(['success' => false, 'message' => '分类不存在']);
            return;
        }

        // 公告分类：禁止通过 API 发帖（只能通过 SQL 直接插入）
        if ($category['slug'] === 'announcements') {
            echo json_encode(['success' => false, 'message' => '公告不能通过发帖功能创建，请联系管理员通过数据库添加']);
            return;
        }

        // 生成 slug
        $slug = generateSlug($title);
        
        // 检查 slug 是否重复
        $existing = $db->fetchOne("SELECT id FROM posts WHERE slug = ?", [$slug]);
        if ($existing) {
            $slug .= '-' . time();
        }

        // 插入帖子
        $db->query(
            "INSERT INTO posts (user_id, category_id, title, slug, content) VALUES (?, ?, ?, ?, ?)",
            [$userId, $categoryId, $title, $slug, $content]
        );

        $postId = $db->lastInsertId();

        // 保存标签
        if (!empty($tags)) {
            saveTags($db, $postId, $tags);
        }

        echo json_encode([
            'success' => true,
            'message' => '发帖成功',
            'post_id' => $postId
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => '服务器错误：' . $e->getMessage()]);
    }
}

/**
 * 更新帖子
 */
function handleUpdatePost() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (empty($input['id']) || empty($input['title']) || empty($input['content'])) {
        echo json_encode(['success' => false, 'message' => '标题和内容不能为空']);
        return;
    }

    $postId = (int)$input['id'];
    $title = trim($input['title']);
    $content = trim($input['content']);
    $tags = $input['tags'] ?? [];

    try {
        $db = Database::getInstance();
        $userId = $_SESSION['user_id'];

        // 检查帖子是否存在且属于当前用户
        $post = $db->fetchOne("SELECT user_id FROM posts WHERE id = ?", [$postId]);
        if (!$post) {
            echo json_encode(['success' => false, 'message' => '帖子不存在']);
            return;
        }

        // 只有作者可以编辑
        if ($post['user_id'] != $userId) {
            echo json_encode(['success' => false, 'message' => '无权编辑此帖子']);
            return;
        }

        // 更新帖子
        $db->query(
            "UPDATE posts SET title = ?, content = ?, updated_at = NOW() WHERE id = ?",
            [$title, $content, $postId]
        );

        // 更新标签
        if (!empty($tags)) {
            saveTags($db, $postId, $tags);
        }

        echo json_encode([
            'success' => true,
            'message' => '更新成功'
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => '服务器错误：' . $e->getMessage()]);
    }
}

/**
 * 删除帖子
 */
function handleDeletePost() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (empty($input['id'])) {
        echo json_encode(['success' => false, 'message' => '帖子 ID 不能为空']);
        return;
    }

    $postId = (int)$input['id'];

    try {
        $db = Database::getInstance();
        $userId = $_SESSION['user_id'];
        $userRole = $_SESSION['role'] ?? 'member';

        // 检查帖子是否存在
        $post = $db->fetchOne("SELECT user_id FROM posts WHERE id = ?", [$postId]);
        if (!$post) {
            echo json_encode(['success' => false, 'message' => '帖子不存在']);
            return;
        }

        // 只有作者或管理员可以删除
        if ($post['user_id'] != $userId && !in_array($userRole, ['admin', 'moderator'])) {
            echo json_encode(['success' => false, 'message' => '无权删除此帖子']);
            return;
        }

        // 删除帖子（外键级联删除回复和点赞）
        $db->query("DELETE FROM posts WHERE id = ?", [$postId]);

        echo json_encode([
            'success' => true,
            'message' => '删除成功'
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => '服务器错误：' . $e->getMessage()]);
    }
}

/**
 * 置顶/取消置顶
 */
function handlePinPost() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (empty($input['id'])) {
        echo json_encode(['success' => false, 'message' => '帖子 ID 不能为空']);
        return;
    }

    $postId = (int)$input['id'];
    $pinned = (bool)($input['pinned'] ?? false);

    try {
        $db = Database::getInstance();
        $userRole = $_SESSION['role'] ?? 'member';

        // 只有管理员或版主可以置顶
        if (!in_array($userRole, ['admin', 'moderator'])) {
            echo json_encode(['success' => false, 'message' => '无权置顶帖子']);
            return;
        }

        $db->query("UPDATE posts SET is_pinned = ? WHERE id = ?", [(int)$pinned, $postId]);

        echo json_encode([
            'success' => true,
            'message' => $pinned ? '已置顶' : '已取消置顶'
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => '服务器错误：' . $e->getMessage()]);
    }
}

/**
 * 锁定/解锁帖子
 */
function handleLockPost() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (empty($input['id'])) {
        echo json_encode(['success' => false, 'message' => '帖子 ID 不能为空']);
        return;
    }

    $postId = (int)$input['id'];
    $locked = (bool)($input['locked'] ?? false);

    try {
        $db = Database::getInstance();
        $userRole = $_SESSION['role'] ?? 'member';

        // 只有管理员或版主可以锁定
        if (!in_array($userRole, ['admin', 'moderator'])) {
            echo json_encode(['success' => false, 'message' => '无权锁定帖子']);
            return;
        }

        $db->query("UPDATE posts SET is_locked = ? WHERE id = ?", [(int)$locked, $postId]);

        echo json_encode([
            'success' => true,
            'message' => $locked ? '已锁定' : '已解锁'
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => '服务器错误：' . $e->getMessage()]);
    }
}

/**
 * 保存标签
 */
function saveTags($db, $postId, $tags) {
    // 先删除旧标签关联
    $db->query("DELETE FROM post_tags WHERE post_id = ?", [$postId]);

    foreach ($tags as $tagName) {
        $tagName = trim($tagName);
        if (empty($tagName)) continue;

        // 查找或创建标签
        $slug = strtolower(preg_replace('/[^a-zA-Z0-9\x{4e00}-\x{9fa5}]/u', '-', $tagName));
        $tag = $db->fetchOne("SELECT id FROM tags WHERE name = ?", [$tagName]);
        
        if (!$tag) {
            $db->query(
                "INSERT INTO tags (name, slug) VALUES (?, ?)",
                [$tagName, $slug]
            );
            $tagId = $db->lastInsertId();
        } else {
            $tagId = $tag['id'];
        }

        // 关联标签
        $db->query(
            "INSERT IGNORE INTO post_tags (post_id, tag_id) VALUES (?, ?)",
            [$postId, $tagId]
        );
    }
}

/**
 * 生成 slug
 */
function generateSlug($title) {
    // 简单处理：移除特殊字符，替换空格为连字符
    $slug = preg_replace('/[^\p{L}\p{N}\s]/u', '', $title);
    $slug = preg_replace('/\s+/', '-', $slug);
    $slug = mb_strtolower($slug, 'UTF-8');
    return mb_substr($slug, 0, 100);
}
