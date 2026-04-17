<?php
/**
 * 数据库连接类
 * 提供 MySQL 数据库连接和基础查询功能
 */

class Database {
    private static $instance = null;
    private $connection;
    private $config;

    private function __construct() {
        $configFile = __DIR__ . '/../config/config.php';
        
        if (!file_exists($configFile)) {
            throw new Exception('配置文件不存在: ' . $configFile);
        }

        $this->config = include $configFile;
        $dbConfig = $this->config['database'];

        try {
            $dsn = "mysql:host={$dbConfig['host']};port={$dbConfig['port']};dbname={$dbConfig['dbname']};charset={$dbConfig['charset']}";
            $this->connection = new PDO($dsn, $dbConfig['username'], $dbConfig['password']);
            $this->connection->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
            $this->connection->setAttribute(PDO::ATTR_DEFAULT_FETCH_MODE, PDO::FETCH_ASSOC);
        } catch (PDOException $e) {
            // 数据库连接失败时记录日志但不阻止页面加载
            error_log('[FutureOSS WebUI] 数据库连接失败: ' . $e->getMessage());
            $this->connection = null;
        }
    }

    /**
     * 获取单例实例
     */
    public static function getInstance() {
        if (self::$instance === null) {
            self::$instance = new self();
        }
        return self::$instance;
    }

    /**
     * 获取数据库连接
     */
    public function getConnection() {
        return $this->connection;
    }

    /**
     * 检查数据库是否可用
     */
    public function isConnected() {
        return $this->connection !== null;
    }

    /**
     * 执行查询
     */
    public function query($sql, $params = []) {
        if (!$this->isConnected()) {
            return false;
        }

        try {
            $stmt = $this->connection->prepare($sql);
            $stmt->execute($params);
            return $stmt;
        } catch (PDOException $e) {
            error_log('[FutureOSS WebUI] 数据库查询错误: ' . $e->getMessage());
            return false;
        }
    }

    /**
     * 获取所有结果
     */
    public function fetchAll($sql, $params = []) {
        $stmt = $this->query($sql, $params);
        return $stmt ? $stmt->fetchAll() : [];
    }

    /**
     * 获取单条结果
     */
    public function fetchOne($sql, $params = []) {
        $stmt = $this->query($sql, $params);
        return $stmt ? $stmt->fetch() : null;
    }

    /**
     * 插入数据并返回 ID
     */
    public function insert($sql, $params = []) {
        $stmt = $this->query($sql, $params);
        return $stmt ? $this->connection->lastInsertId() : false;
    }

    /**
     * 防止 SQL 注入
     */
    public function escape($value) {
        if (!$this->isConnected()) {
            return addslashes($value);
        }
        return $this->connection->quote($value);
    }

    // 防止克隆
    private function __clone() {}
    public function __wakeup() {
        throw new Exception("Cannot unserialize singleton");
    }
}
