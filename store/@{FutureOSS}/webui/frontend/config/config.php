<?php
/**
 * FutureOSS WebUI 配置文件
 */

return [
    // 数据库配置
    'database' => [
        'host' => 'localhost',
        'port' => 3306,
        'username' => 'root',
        'password' => '',
        'dbname' => 'futureoss',
        'charset' => 'utf8mb4'
    ],
    
    // 应用配置
    'app' => [
        'title' => 'FutureOSS',
        'theme' => 'dark',
        'version' => '1.0.0'
    ],
    
    // 其他插件可以添加配置
    'plugins' => []
];
