<?php
ini_set("display_errors", 1); error_reporting(E_ALL);
require_once __DIR__ . '/../includes/Database.php';

header('Content-Type: application/json');
header('Access-Control-Allow-Origin: *');
header('Access-Control-Allow-Methods: GET, POST, OPTIONS');
header('Access-Control-Allow-Headers: Content-Type');

if ($_SERVER['REQUEST_METHOD'] === 'OPTIONS') {
    exit(0);
}

$action = $_GET['action'] ?? '';
$db = Database::getInstance();

try {
    switch ($action) {
        case 'posts':
            $page = max(1, (int)($_GET['page'] ?? 1));
            $limit = 20;
            $offset = ($page - 1) * $limit;
            $categoryId = $_GET['category_id'] ?? '';

            if ($categoryId) {
                $posts = $db->fetchAll(
                    "SELECT p.*, u.username, u.avatar, c.name as category_name 
                     FROM posts p 
                     JOIN users u ON p.user_id = u.id 
                     JOIN categories c ON p.category_id = c.id 
                     WHERE p.category_id = ? 
                     ORDER BY p.is_pinned DESC, p.created_at DESC 
                     LIMIT ? OFFSET ?",
                    [$categoryId, $limit, $offset]
                );
                $total = $db->fetchOne("SELECT COUNT(*) as count FROM posts WHERE category_id = ?", [$categoryId])['count'];
            } else {
                $posts = $db->fetchAll(
                    "SELECT p.*, u.username, u.avatar, c.name as category_name 
                     FROM posts p 
                     JOIN users u ON p.user_id = u.id 
                     JOIN categories c ON p.category_id = c.id 
                     ORDER BY p.is_pinned DESC, p.created_at DESC 
                     LIMIT ? OFFSET ?",
                    [$limit, $offset]
                );
                $total = $db->fetchOne("SELECT COUNT(*) as count FROM posts")['count'];
            }

            echo json_encode([
                'posts' => $posts,
                'total' => $total,
                'pages' => ceil($total / $limit)
            ]);
            break;

        case 'post':
            $id = (int)($_GET['id'] ?? 0);
            $post = $db->fetchOne(
                "SELECT p.*, u.username, u.avatar, u.role, c.name as category_name, c.slug as category_slug
                 FROM posts p 
                 JOIN users u ON p.user_id = u.id 
                 JOIN categories c ON p.category_id = c.id 
                 WHERE p.id = ?",
                [$id]
            );

            if (!$post) {
                http_response_code(404);
                echo json_encode(['error' => '帖子不存在']);
                exit;
            }

            // 更新浏览数
            $db->query("UPDATE posts SET views = views + 1 WHERE id = ?", [$id]);
            $post['views']++;

            // 获取回复
            $replies = $db->fetchAll(
                "SELECT r.*, u.username, u.avatar 
                 FROM replies r 
                 JOIN users u ON r.user_id = u.id 
                 WHERE r.post_id = ? 
                 ORDER BY r.is_solution DESC, r.created_at ASC",
                [$id]
            );

            echo json_encode(['post' => $post, 'replies' => $replies]);
            break;

        case 'categories':
            $categories = $db->fetchAll("SELECT * FROM categories ORDER BY sort_order ASC");
            echo json_encode(['categories' => $categories]);
            break;

        case 'stats':
            $stats = [
                'posts' => $db->fetchOne("SELECT COUNT(*) as count FROM posts")['count'],
                'replies' => $db->fetchOne("SELECT COUNT(*) as count FROM replies")['count'],
                'users' => $db->fetchOne("SELECT COUNT(*) as count FROM users")['count'],
                'hot_posts' => $db->fetchAll("SELECT id, title, views, likes FROM posts ORDER BY views DESC LIMIT 5"),
            ];
            echo json_encode($stats);
            break;

        default:
            echo json_encode(['error' => '未知操作']);
    }
} catch (Exception $e) {
    http_response_code(500);
    echo json_encode(['error' => $e->getMessage()]);
}
