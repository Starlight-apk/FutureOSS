-- 添加称号系统到 users 表
ALTER TABLE users ADD COLUMN IF NOT EXISTS title VARCHAR(100) DEFAULT '' COMMENT '用户称号';

-- 设置 admin 用户的称号
UPDATE users SET title = '你猜为什么是DeepSeek' WHERE role = 'admin' AND username = 'admin';

-- 创建称号配置表（可选，用于管理称号）
CREATE TABLE IF NOT EXISTS titles (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE COMMENT '称号名称',
    color VARCHAR(7) DEFAULT '#06b6d4' COMMENT '称号颜色',
    description VARCHAR(255) DEFAULT '' COMMENT '称号描述',
    is_admin_only TINYINT(1) DEFAULT 0 COMMENT '是否仅管理员可用',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- 插入预设称号
INSERT IGNORE INTO titles (name, color, description, is_admin_only) VALUES
('你猜为什么是DeepSeek', '#f59e0b', '神秘的管理称号', 1),
('管理员', '#ef4444', '网站管理员', 1),
('版主', '#22c55e', '社区版主', 1),
('活跃用户', '#3b82f6', '经常发帖的活跃用户', 0),
('新手', '#6b7280', '新加入的用户', 0),
('技术达人', '#8b5cf6', '技术方面的大神', 0),
('社区元老', '#f97316', '在很久的时间前就加入社区的用户', 0);
