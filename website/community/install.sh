#!/bin/bash
# OSS Community 安装脚本

set -e

echo "========================================"
echo "  OSS Community 安装向导"
echo "========================================"
echo ""

# 1. 检测 PHP
echo -ne "[1/4] 检测 PHP 环境..."
if command -v php &> /dev/null; then
    echo -e " \033[0;32m已安装 ($(php -v | head -n1 | awk '{print $2}'))\033[0m"
else
    echo -e " \033[1;33m未安装 PHP\033[0m"
    echo "请运行: sudo apt install php php-mysql php-pdo php-json"
    exit 1
fi

# 2. 检测 MySQL
echo -ne "[2/4] 检测 MySQL 环境..."
if command -v mysql &> /dev/null; then
    echo -e " \033[0;32m已安装\033[0m"
else
    echo -e " \033[1;33m未安装 MySQL\033[0m"
    echo "请运行: sudo apt install mysql-server"
    exit 1
fi

# 3. 数据库配置
echo ""
echo "请输入 MySQL 配置:"
read -p "  数据库主机 [127.0.0.1]: " DB_HOST
DB_HOST=${DB_HOST:-127.0.0.1}
read -p "  数据库端口 [3306]: " DB_PORT
DB_PORT=${DB_PORT:-3306}
read -p "  数据库用户名 [root]: " DB_USER
DB_USER=${DB_USER:-root}
read -sp "  数据库密码: " DB_PASS
echo ""
read -p "  数据库名 [oss_community]: " DB_NAME
DB_NAME=${DB_NAME:-oss_community}

# 写入配置
cat > config.php << EOF
<?php
return [
    'host' => '$DB_HOST',
    'port' => '$DB_PORT',
    'dbname' => '$DB_NAME',
    'username' => '$DB_USER',
    'password' => '$DB_PASS',
    'charset' => 'utf8mb4',
];
EOF

# 4. 导入数据库
echo -ne "[3/4] 导入数据库结构..."
if mysql -u "$DB_USER" -p"$DB_PASS" -h "$DB_HOST" -P "$DB_PORT" < schema.sql 2>/dev/null; then
    echo -e " \033[0;32m导入成功\033[0m"
else
    echo -e " \033[0;31m导入失败，请检查 MySQL 连接信息\033[0m"
    exit 1
fi

# 5. 启动 PHP 内置服务器
echo -ne "[4/4] 启动社区服务器..."
echo -e " \033[0;32m完成\033[0m"

echo ""
echo "========================================"
echo "  安装完成！"
echo "========================================"
echo ""
echo "访问 http://localhost:8081/community/ 查看社区"
echo ""
echo "启动命令: php -S localhost:8081 -t ../"
echo ""
