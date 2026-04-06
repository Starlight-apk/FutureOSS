<?php
/**
 * OSS 官网自动更新系统 (全自动版)
 *
 * 功能：
 * 1. 用户访问网站时，自动在后台检查更新。
 * 2. 频率控制：每 5 分钟最多执行一次。
 * 3. 智能对比：通过 Git SHA 对比远程与本地文件。
 * 4. 自动更新：缺失文件自动下载，已修改文件自动覆盖。
 * 5. 零阻塞：更新在后台异步执行，不影响用户访问。
 *
 * 使用方式：
 *   - 在 router.php 或 index.php 顶部添加：include 'update.php';
 *   - 或配置 PHP auto_prepend_file
 */

if (defined('UPDATE_CHECK_RUNNING')) return;
define('UPDATE_CHECK_RUNNING', true);

define('GITEE_OWNER', 'starlight-apk');
define('GITEE_REPO', 'feature-oss');
define('GITEE_BRANCH', 'main');
define('GITEE_API_BASE', 'https://gitee.com/api/v5/repos');
define('CACHE_DIR', __DIR__ . '/.cache');
define('UPDATE_INTERVAL', 300); // 5 分钟

function autoUpdateWebsite() {
    if (!is_dir(CACHE_DIR)) @mkdir(CACHE_DIR, 0755, true);

    $lockFile = CACHE_DIR . '/update.lock';
    $shouldUpdate = true;

    if (file_exists($lockFile)) {
        if ((time() - filemtime($lockFile)) < UPDATE_INTERVAL) $shouldUpdate = false;
    }

    if (!$shouldUpdate) return;
    @touch($lockFile);

    if (function_exists('fastcgi_finish_request')) fastcgi_finish_request();
    ignore_user_abort(true);
    set_time_limit(120);

    $logFile = CACHE_DIR . '/update.log';
    $log = "[" . date('Y-m-d H:i:s') . "] 触发自动更新检查...\n";

    try {
        $treeUrl = sprintf('%s/%s/%s/git/trees/%s?recursive=1', GITEE_API_BASE, GITEE_OWNER, GITEE_REPO, GITEE_BRANCH);
        $treeData = httpGetJson($treeUrl);
        if (!$treeData || !isset($treeData['tree'])) {
            $log .= "错误: 无法获取远程文件树\n";
            @file_put_contents($logFile, $log, FILE_APPEND);
            return;
        }

        $websiteFiles = [];
        foreach ($treeData['tree'] as $item) {
            $path = $item['path'];
            if ($item['type'] === 'blob' && strpos($path, 'website/') === 0 && $path !== 'website/') {
                $websiteFiles[] = ['path' => $path, 'sha' => $item['sha'], 'size' => $item['size'] ?? 0];
            }
        }

        $log .= "获取到 " . count($websiteFiles) . " 个远程文件\n";

        $updated = 0; $created = 0; $errors = 0;
        $shaCacheFile = CACHE_DIR . '/file_shas.json';
        $localShas = file_exists($shaCacheFile) ? json_decode(@file_get_contents($shaCacheFile), true) : [];
        if (!is_array($localShas)) $localShas = [];

        foreach ($websiteFiles as $file) {
            $relativePath = substr($file['path'], strlen('website/'));
            $localPath = __DIR__ . '/' . $relativePath;
            $remoteSha = $file['sha'];

            $dir = dirname($localPath);
            if (!is_dir($dir)) @mkdir($dir, 0755, true);

            $needsUpdate = false;
            $reason = '';

            if (!file_exists($localPath)) {
                $needsUpdate = true; $reason = '文件缺失';
            } else {
                $localSha = $localShas[$relativePath] ?? '';
                if ($localSha !== $remoteSha) { $needsUpdate = true; $reason = '内容已变更'; }
            }

            if ($needsUpdate) {
                $contentUrl = sprintf('%s/%s/%s/contents/%s?ref=%s', GITEE_API_BASE, GITEE_OWNER, GITEE_REPO, $file['path'], GITEE_BRANCH);
                $contentData = httpGetJson($contentUrl);
                if ($contentData && isset($contentData['content'])) {
                    $content = base64_decode(str_replace(["\n", "\r"], '', $contentData['content']));
                    if (@file_put_contents($localPath, $content) !== false) {
                        $localShas[$relativePath] = $remoteSha;
                        if ($reason === '文件缺失') { $created++; $log .= "✅ 创建: $relativePath\n"; }
                        else { $updated++; $log .= "🔄 更新: $relativePath ($reason)\n"; }
                    } else { $errors++; $log .= "❌ 写入失败: $relativePath\n"; }
                } else { $errors++; $log .= "❌ 获取内容失败: $relativePath\n"; }
            }
        }

        @file_put_contents($shaCacheFile, json_encode($localShas));
        @file_put_contents(CACHE_DIR . '/update_check.json', json_encode([
            'timestamp' => time(), 'files' => count($websiteFiles),
            'updated' => $updated, 'created' => $created, 'errors' => $errors
        ], JSON_PRETTY_PRINT));

        $log .= "完成: 更新 $updated 个，创建 $created 个，错误 $errors 个\n";
        $log .= "下次检查: " . date('Y-m-d H:i:s', time() + UPDATE_INTERVAL) . "\n\n";
        @file_put_contents($logFile, $log, FILE_APPEND);

    } catch (Exception $e) {
        $log .= "异常: " . $e->getMessage() . "\n";
        @file_put_contents($logFile, $log, FILE_APPEND);
    }
}

function httpGetJson($url) {
    $context = stream_context_create(['http' => ['method' => 'GET', 'header' => ['User-Agent: OSS-AutoUpdate/1.0', 'Accept: application/json'], 'timeout' => 30], 'ssl' => ['verify_peer' => true, 'verify_peer_name' => true]]);
    $response = @file_get_contents($url, false, $context);
    if ($response === false) return null;
    return json_decode($response, true);
}

register_shutdown_function('autoUpdateWebsite');
