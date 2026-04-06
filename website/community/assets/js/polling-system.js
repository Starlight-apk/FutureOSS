/**
 * OSS Community - 实时轮询系统
 * 每2秒从数据库刷新所有数据
 */

class CommunityPollingSystem {
    constructor() {
        this.interval = 2000;
        this.timer = null;
        this.isRunning = false;
        this.listeners = { user: [], posts: [], stats: [], categories: [] };
        this.cache = { user: null, posts: null, stats: null, categories: null };
    }

    start() {
        if (this.isRunning) return;
        this.isRunning = true;
        this._fetchAll();
        this.timer = setInterval(() => this._fetchAll(), this.interval);
    }

    stop() {
        clearInterval(this.timer);
        this.isRunning = false;
        this.timer = null;
    }

    on(event, callback) {
        if (this.listeners[event]) this.listeners[event].push(callback);
    }

    async _fetch(url) {
        try {
            const res = await fetch(url);
            return res.ok ? await res.json() : null;
        } catch { return null; }
    }

    async _fetchAll() {
        // 并行请求所有接口
        const [userData, postsData, statsData, catsData] = await Promise.all([
            this._fetch('api/auth.php?action=current-user'),
            this._fetch('api/index.php?action=posts'),
            this._fetch('api/index.php?action=stats'),
            this._fetch('api/index.php?action=categories')
        ]);

        // 用户数据
        if (userData && userData.success) {
            const changed = JSON.stringify(userData) !== JSON.stringify(this.cache.user);
            this.cache.user = userData;
            if (changed) this._notify('user', userData);
        }

        // 帖子数据（含 views, likes, replies）
        if (postsData && postsData.posts) {
            const changed = JSON.stringify(postsData.posts) !== JSON.stringify(this.cache.posts);
            this.cache.posts = postsData.posts;
            if (changed) this._notify('posts', postsData);
        }

        // 统计数据（含 hot_posts）
        if (statsData) {
            const changed = JSON.stringify(statsData) !== JSON.stringify(this.cache.stats);
            this.cache.stats = statsData;
            if (changed) this._notify('stats', statsData);
        }

        // 分类
        if (catsData && catsData.categories) {
            const changed = JSON.stringify(catsData.categories) !== JSON.stringify(this.cache.categories);
            this.cache.categories = catsData.categories;
            if (changed) this._notify('categories', catsData);
        }
    }

    _notify(event, data) {
        (this.listeners[event] || []).forEach(fn => {
            try { fn(data); } catch(e) {}
        });
    }
}

window.Polling = new CommunityPollingSystem();

document.addEventListener('DOMContentLoaded', () => {
    const dock = document.getElementById('dock');
    if (dock && dock.dataset.loggedIn === '1') {
        window.Polling.start();
    }
});
