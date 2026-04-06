<?php
/**
 * 数据库迁移脚本 - 添加 bio 字段到 users 表
 * 运行方式: php migrate-add-bio.php
 */

require_once __DIR__ . '/includes/Database.php';

echo "开始迁移：添加 bio 字段到 users 表...\n";

try {
    $db = Database::getInstance();
    
    // 检查字段是否已存在
    $columns = $db->fetchAll("SHOW COLUMNS FROM users LIKE 'bio'");
    
    if (empty($columns)) {
        // 字段不存在，添加
        $db->query("ALTER TABLE users ADD COLUMN bio TEXT AFTER avatar");
        echo "✓ 成功添加 bio 字段\n";
    } else {
        echo "✓ bio 字段已存在，无需迁移\n";
    }
    
    echo "迁移完成！\n";
} catch (Exception $e) {
    echo "✗ 迁移失败：" . $e->getMessage() . "\n";
    exit(1);
}
