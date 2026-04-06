<?php
/**
 * OSS Community 认证 API
 * 处理登录和注册请求
 */

session_start();
require_once __DIR__ . '/../includes/Database.php';

header('Content-Type: application/json');

// 获取操作类型
$action = $_GET['action'] ?? '';

// check 和 logout 允许 GET 请求，其他只允许 POST
if (in_array($action, ['check', 'logout', 'current-user']) && $_SERVER['REQUEST_METHOD'] === 'GET') {
    // 允许 GET
} elseif ($_SERVER['REQUEST_METHOD'] !== 'POST') {
    http_response_code(405);
    echo json_encode(['success' => false, 'message' => '请求方法不允许']);
    exit;
}

if ($action === 'login') {
    handleLogin();
} elseif ($action === 'register') {
    handleRegister();
} elseif ($action === 'logout') {
    handleLogout();
} elseif ($action === 'check') {
    handleCheck();
} elseif ($action === 'my-post-count') {
    handleMyPostCount();
} elseif ($action === 'current-user') {
    handleCurrentUser();
} else {
    http_response_code(400);
    echo json_encode(['success' => false, 'message' => '无效的操作类型']);
}

/**
 * 处理登录
 */
function handleLogin() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (empty($input['username']) || empty($input['password'])) {
        echo json_encode(['success' => false, 'message' => '用户名和密码不能为空']);
        return;
    }

    $username = trim($input['username']);
    $password = $input['password'];
    $remember = $input['remember'] ?? false;

    try {
        $db = Database::getInstance();
        
        // 查询用户（支持用户名或邮箱登录）
        $user = $db->fetchOne(
            "SELECT id, username, email, password_hash, role, avatar FROM users WHERE username = ? OR email = ?",
            [$username, $username]
        );

        if (!$user) {
            echo json_encode(['success' => false, 'message' => '用户名或密码错误']);
            return;
        }

        // 验证密码
        if (!password_verify($password, $user['password_hash'])) {
            echo json_encode(['success' => false, 'message' => '用户名或密码错误']);
            return;
        }

        // 设置 session
        $_SESSION['user_id'] = $user['id'];
        $_SESSION['username'] = $user['username'];
        $_SESSION['role'] = $user['role'];
        $_SESSION['avatar'] = $user['avatar'];

        // 如果勾选记住我，设置更长的 session 生命周期
        if ($remember) {
            ini_set('session.gc_maxlifetime', 30 * 24 * 60 * 60); // 30天
            session_set_cookie_params(30 * 24 * 60 * 60);
        }

        echo json_encode([
            'success' => true,
            'message' => '登录成功',
            'user' => [
                'id' => $user['id'],
                'username' => $user['username'],
                'role' => $user['role'],
                'avatar' => $user['avatar']
            ]
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => '服务器错误：' . $e->getMessage()]);
    }
}

/**
 * 处理注册
 */
function handleRegister() {
    $input = json_decode(file_get_contents('php://input'), true);
    
    if (empty($input['username']) || empty($input['email']) || empty($input['password'])) {
        echo json_encode(['success' => false, 'message' => '所有字段都不能为空']);
        return;
    }

    $username = trim($input['username']);
    $email = trim($input['email']);
    $password = $input['password'];

    // 验证用户名格式
    if (!preg_match('/^[a-zA-Z0-9_]{3,50}$/', $username)) {
        echo json_encode(['success' => false, 'message' => '用户名只能包含字母、数字和下划线，长度 3-50 个字符']);
        return;
    }

    // 验证邮箱格式
    if (!filter_var($email, FILTER_VALIDATE_EMAIL)) {
        echo json_encode(['success' => false, 'message' => '邮箱格式不正确']);
        return;
    }

    // 验证密码长度
    if (strlen($password) < 6) {
        echo json_encode(['success' => false, 'message' => '密码长度至少 6 个字符']);
        return;
    }

    try {
        $db = Database::getInstance();

        // 检查用户名是否已存在
        $existingUser = $db->fetchOne("SELECT id FROM users WHERE username = ?", [$username]);
        if ($existingUser) {
            echo json_encode(['success' => false, 'message' => '用户名已被使用']);
            return;
        }

        // 检查邮箱是否已存在
        $existingEmail = $db->fetchOne("SELECT id FROM users WHERE email = ?", [$email]);
        if ($existingEmail) {
            echo json_encode(['success' => false, 'message' => '邮箱已被注册']);
            return;
        }

        // 密码哈希
        $passwordHash = password_hash($password, PASSWORD_DEFAULT);

        // 插入新用户
        $db->query(
            "INSERT INTO users (username, email, password_hash, role) VALUES (?, ?, ?, 'member')",
            [$username, $email, $passwordHash]
        );

        $userId = $db->lastInsertId();

        echo json_encode([
            'success' => true,
            'message' => '注册成功',
            'user' => [
                'id' => $userId,
                'username' => $username,
                'role' => 'member'
            ]
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => '服务器错误：' . $e->getMessage()]);
    }
}

/**
 * 处理登出
 */
function handleLogout() {
    session_destroy();
    echo json_encode(['success' => true, 'message' => '已成功退出']);
}

/**
 * 检查登录状态
 */
function handleCheck() {
    if (isset($_SESSION['user_id'])) {
        echo json_encode([
            'success' => true,
            'logged_in' => true,
            'user' => [
                'id' => $_SESSION['user_id'],
                'username' => $_SESSION['username'],
                'role' => $_SESSION['role'] ?? 'member',
                'avatar' => $_SESSION['avatar'] ?? ''
            ]
        ]);
    } else {
        echo json_encode([
            'success' => true,
            'logged_in' => false
        ]);
    }
}

/**
 * 获取用户文章数量
 */
function handleMyPostCount() {
    if (!isset($_SESSION['user_id'])) {
        echo json_encode(['success' => false, 'message' => '未登录']);
        return;
    }

    try {
        $db = Database::getInstance();
        $count = $db->fetchOne(
            "SELECT COUNT(*) as count FROM posts WHERE user_id = ?",
            [$_SESSION['user_id']]
        )['count'];

        echo json_encode([
            'success' => true,
            'count' => (int)$count
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => '服务器错误：' . $e->getMessage()]);
    }
}

/**
 * 获取当前登录用户信息（用于轮询）
 */
function handleCurrentUser() {
    if (!isset($_SESSION['user_id'])) {
        echo json_encode(['success' => false, 'message' => '未登录']);
        return;
    }

    try {
        $db = Database::getInstance();
        $user = $db->fetchOne(
            "SELECT id, username, email, avatar, role, title, bio, created_at FROM users WHERE id = ?",
            [$_SESSION['user_id']]
        );

        if (!$user) {
            echo json_encode(['success' => false, 'message' => '用户不存在']);
            return;
        }

        // 获取统计数据
        $stats = $db->fetchOne(
            "SELECT 
                (SELECT COUNT(*) FROM posts WHERE user_id = ?) as post_count,
                (SELECT COUNT(*) FROM replies WHERE user_id = ?) as reply_count",
            [$user['id'], $user['id']]
        );

        echo json_encode([
            'success' => true,
            'user' => $user,
            'stats' => [
                'post_count' => (int)$stats['post_count'],
                'reply_count' => (int)$stats['reply_count']
            ],
            'permissions' => [
                'can_manage_users' => in_array($user['role'], ['admin']),
                'can_manage_posts' => in_array($user['role'], ['admin', 'moderator']),
                'can_pin_posts' => in_array($user['role'], ['admin', 'moderator']),
                'can_lock_posts' => in_array($user['role'], ['admin', 'moderator']),
                'can_delete_any_post' => in_array($user['role'], ['admin']),
                'can_manage_titles' => in_array($user['role'], ['admin'])
            ]
        ]);
    } catch (Exception $e) {
        http_response_code(500);
        echo json_encode(['success' => false, 'message' => '服务器错误：' . $e->getMessage()]);
    }
}
