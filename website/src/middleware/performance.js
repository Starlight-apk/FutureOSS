/**
 * 性能优化中间件
 */

/**
 * 响应时间头中间件
 * 添加X-Response-Time头到响应中
 */
function responseTime(req, res, next) {
    const start = Date.now();
    
    // 保存原始的 end 方法
    const originalEnd = res.end;
    
    // 重写 end 方法以在响应发送前设置头部
    res.end = function(...args) {
        const duration = Date.now() - start;
        
        // 只有在头部尚未发送时才能设置
        if (!res.headersSent) {
            res.setHeader('X-Response-Time', `${duration}ms`);
        }
        
        // 记录慢响应
        if (duration > 1000) {
            console.warn(`慢响应: ${req.method} ${req.url} - ${duration}ms`);
        }
        
        // 调用原始的 end 方法
        return originalEnd.apply(this, args);
    };
    
    next();
}

/**
 * 压缩中间件
 * 已经使用compression，这里添加额外的压缩头
 */
function compressionHeaders(req, res, next) {
    // 为文本资源启用压缩
    if (req.url.match(/\.(html|css|js|json|xml)$/)) {
        res.setHeader('Vary', 'Accept-Encoding');
    }
    
    next();
}

/**
 * 缓存控制中间件
 */
function cacheControl(req, res, next) {
    // 静态资源缓存策略
    if (req.url.match(/\.(css|js|png|jpg|jpeg|gif|ico|svg|woff|woff2|ttf|eot)$/)) {
        // 静态资源缓存1年
        res.setHeader('Cache-Control', 'public, max-age=31536000, immutable');
    } else if (req.url.match(/\.(html)$/)) {
        // HTML文件不缓存
        res.setHeader('Cache-Control', 'no-cache, no-store, must-revalidate');
    } else {
        // 默认缓存策略
        res.setHeader('Cache-Control', 'no-cache');
    }
    
    next();
}

/**
 * 安全头中间件
 */
function securityHeaders(req, res, next) {
    // 防止MIME类型嗅探
    res.setHeader('X-Content-Type-Options', 'nosniff');
    
    // 防止点击劫持
    res.setHeader('X-Frame-Options', 'DENY');
    
    // XSS保护
    res.setHeader('X-XSS-Protection', '1; mode=block');
    
    // 推荐使用HTTPS
    res.setHeader('Strict-Transport-Security', 'max-age=31536000; includeSubDomains');
    
    // 内容安全策略
    const csp = [
        "default-src 'self'",
        "script-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com",
        "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com",
        "font-src 'self' https://cdnjs.cloudflare.com https://fonts.gstatic.com",
        "img-src 'self' data: https:",
        "connect-src 'self'",
        "frame-ancestors 'none'",
        "base-uri 'self'",
        "form-action 'self'"
    ].join('; ');
    
    res.setHeader('Content-Security-Policy', csp);
    
    next();
}

/**
 * Gzip预压缩中间件
 * 检查是否存在预压缩的.gz文件
 */
function gzipStatic(req, res, next) {
    const acceptEncoding = req.headers['accept-encoding'] || '';
    
    if (acceptEncoding.includes('gzip') && req.url.match(/\.(js|css|html|json)$/)) {
        req.url = req.url + '.gz';
        res.setHeader('Content-Encoding', 'gzip');
        
        // 设置正确的Content-Type
        if (req.url.endsWith('.js.gz')) {
            res.setHeader('Content-Type', 'application/javascript');
        } else if (req.url.endsWith('.css.gz')) {
            res.setHeader('Content-Type', 'text/css');
        } else if (req.url.endsWith('.html.gz')) {
            res.setHeader('Content-Type', 'text/html');
        }
    }
    
    next();
}

/**
 * 请求限流中间件（简单版本）
 */
function rateLimiter(maxRequests = 100, windowMs = 15 * 60 * 1000) {
    const requests = new Map();
    
    return function(req, res, next) {
        const ip = req.ip || req.connection.remoteAddress;
        const now = Date.now();
        
        if (!requests.has(ip)) {
            requests.set(ip, []);
        }
        
        const timestamps = requests.get(ip);
        
        // 清理过期的请求记录
        const windowStart = now - windowMs;
        while (timestamps.length && timestamps[0] < windowStart) {
            timestamps.shift();
        }
        
        // 检查是否超过限制
        if (timestamps.length >= maxRequests) {
            res.status(429).json({
                error: '请求过多',
                message: '请稍后再试'
            });
            return;
        }
        
        // 记录当前请求
        timestamps.push(now);
        
        // 设置限流头
        res.setHeader('X-RateLimit-Limit', maxRequests);
        res.setHeader('X-RateLimit-Remaining', maxRequests - timestamps.length);
        res.setHeader('X-RateLimit-Reset', Math.ceil((timestamps[0] + windowMs) / 1000));
        
        next();
    };
}

/**
 * 数据库查询优化中间件（示例）
 */
function queryOptimizer(req, res, next) {
    // 这里可以添加数据库查询优化逻辑
    // 例如：限制查询结果数量、添加索引提示等
    
    // 示例：为API请求添加默认分页
    if (req.path.startsWith('/api/') && req.method === 'GET') {
        req.query.limit = req.query.limit || '50';
        req.query.offset = req.query.offset || '0';
    }
    
    next();
}

/**
 * 内存使用监控
 */
function memoryMonitor(req, res, next) {
    const memoryUsage = process.memoryUsage();
    
    // 记录高内存使用
    if (memoryUsage.heapUsed > 500 * 1024 * 1024) { // 500MB
        console.warn('高内存使用:', {
            heapUsed: Math.round(memoryUsage.heapUsed / 1024 / 1024) + 'MB',
            heapTotal: Math.round(memoryUsage.heapTotal / 1024 / 1024) + 'MB',
            rss: Math.round(memoryUsage.rss / 1024 / 1024) + 'MB',
            url: req.url
        });
    }
    
    // 添加内存使用头（仅开发环境）
    if (process.env.NODE_ENV === 'development') {
        res.setHeader('X-Memory-Usage', Math.round(memoryUsage.heapUsed / 1024 / 1024) + 'MB');
    }
    
    next();
}

module.exports = {
    responseTime,
    compressionHeaders,
    cacheControl,
    securityHeaders,
    gzipStatic,
    rateLimiter,
    queryOptimizer,
    memoryMonitor
};