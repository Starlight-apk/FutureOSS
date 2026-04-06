/**
 * OSS Community - 文章抽屉交互逻辑
 */
document.addEventListener('DOMContentLoaded', () => {
    initPostDrawer();
});

let drawerInitialized = false;
let currentDrawerPostId = null;
let drawerPollTimer = null;

function initPostDrawer() {
    if (drawerInitialized) return;
    drawerInitialized = true;

    createDrawerElements();

    // 全局点击事件委托
    document.addEventListener('click', (e) => {
        const postCard = e.target.closest('.post-card');
        if (postCard && postCard.dataset.postId) {
            e.preventDefault();
            e.stopPropagation();
            openPostDrawer(postCard.dataset.postId);
        }
    });

    const overlay = document.getElementById('postDrawerOverlay');
    if (overlay) overlay.addEventListener('click', closePostDrawer);

    const closeBtn = document.getElementById('postDrawerClose');
    if (closeBtn) closeBtn.addEventListener('click', closePostDrawer);

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape') closePostDrawer();
    });

    // 监听轮询数据更新抽屉内的 views/likes
    if (window.Polling) {
        window.Polling.on('posts', (data) => {
            if (!data.posts || !currentDrawerPostId) return;
            const post = data.posts.find(p => p.id == currentDrawerPostId);
            if (post) updateDrawerStats(post);
        });
    }
}

function createDrawerElements() {
    if (document.getElementById('postDrawerOverlay')) return;

    // 创建遮罩层
    const overlay = document.createElement('div');
    overlay.id = 'postDrawerOverlay';
    overlay.className = 'post-drawer-overlay';

    // 创建抽屉
    const drawer = document.createElement('div');
    drawer.id = 'postDrawer';
    drawer.className = 'post-drawer';
    drawer.innerHTML = `
        <div class="post-drawer-header">
            <button class="post-drawer-close" id="postDrawerClose" aria-label="关闭">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <line x1="18" y1="6" x2="6" y2="18"/>
                    <line x1="6" y1="6" x2="18" y2="18"/>
                </svg>
            </button>
            <h2 class="post-drawer-title" id="postDrawerTitle"></h2>
            <div class="post-drawer-meta" id="postDrawerMeta"></div>
        </div>
        <div class="post-drawer-body">
            <div class="post-drawer-content" id="postDrawerContent"></div>
        </div>
        <div class="post-drawer-footer" id="postDrawerFooter"></div>
    `;

    document.body.appendChild(overlay);
    document.body.appendChild(drawer);

    // 绑定关闭按钮
    document.getElementById('postDrawerClose').addEventListener('click', closePostDrawer);
}

async function openPostDrawer(postId) {
    const drawer = document.getElementById('postDrawer');
    const overlay = document.getElementById('postDrawerOverlay');
    const titleEl = document.getElementById('postDrawerTitle');
    const metaEl = document.getElementById('postDrawerMeta');
    const contentEl = document.getElementById('postDrawerContent');
    const footerEl = document.getElementById('postDrawerFooter');

    if (!drawer || !overlay) return;

    // 显示加载状态
    titleEl.textContent = '加载中...';
    metaEl.innerHTML = '';
    contentEl.innerHTML = '<div style="text-align:center;padding:40px;color:#64748b;">正在加载文章内容...</div>';
    footerEl.innerHTML = '';

    // 显示抽屉（先滑入，再加载内容）
    overlay.classList.add('active');
    drawer.classList.add('active');
    document.body.style.overflow = 'hidden';

    try {
        const response = await fetch(`api/index.php?action=post&id=${postId}`);
        if (!response.ok) throw new Error('加载失败');

        const data = await response.json();
        if (!data.post) throw new Error('帖子不存在');

        const post = data.post;
        const replies = data.replies || [];

        currentDrawerPostId = post.id;

        // 更新标题和元信息
        titleEl.textContent = post.title;
        metaEl.innerHTML = `
            <div class="post-drawer-avatar">${post.username.charAt(0).toUpperCase()}</div>
            <div class="post-drawer-user-info">
                <div class="post-drawer-username">${escapeHtml(post.username)}</div>
                <div class="post-drawer-date">${formatDate(post.created_at)}</div>
            </div>
            <span class="post-drawer-category">${escapeHtml(post.category_name)}</span>
        `;

        // 更新内容（使用 marked 解析 Markdown）
        if (typeof marked !== 'undefined') {
            contentEl.innerHTML = marked.parse(post.content);
        } else {
            contentEl.innerHTML = escapeHtml(post.content).replace(/\n/g, '<br>');
        }

        // 更新底部统计
        footerEl.innerHTML = `
            <div class="post-drawer-stat">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                ${post.views} 浏览
            </div>
            <div class="post-drawer-stat">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                ${post.likes} 点赞
            </div>
            <div class="post-drawer-stat">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"/></svg>
                ${replies.length} 回复
            </div>
        `;

        // 如果有回复，在内容下方显示
        if (replies.length > 0) {
            contentEl.innerHTML += `
                <hr style="margin:2em 0;border:none;height:1px;background:rgba(99,102,241,0.2);">
                <h3 style="color:#e2e8f0;margin-bottom:1em;font-size:18px;">回复 (${replies.length})</h3>
                ${replies.map(reply => `
                    <div style="padding:16px;background:rgba(30,41,59,0.4);border-radius:12px;margin-bottom:12px;border:1px solid rgba(99,102,241,0.1);">
                        <div style="display:flex;align-items:center;gap:8px;margin-bottom:8px;">
                            <div style="width:28px;height:28px;border-radius:6px;background:linear-gradient(135deg,#6366f1,#8b5cf6);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;color:white;flex-shrink:0;">
                                ${reply.username.charAt(0).toUpperCase()}
                            </div>
                            <span style="color:#e2e8f0;font-weight:600;font-size:13px;">${escapeHtml(reply.username)}</span>
                            <span style="color:#64748b;font-size:12px;margin-left:auto;">${formatDate(reply.created_at)}</span>
                        </div>
                        <div style="color:#cbd5e1;font-size:14px;line-height:1.6;">${escapeHtml(reply.content).replace(/\n/g, '<br>')}</div>
                    </div>
                `).join('')}
            `;
        }

    } catch (error) {
        console.error('Failed to load post:', error);
        contentEl.innerHTML = `
            <div style="text-align:center;padding:40px;color:#ef4444;">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width:48px;height:48px;margin:0 auto 16px;opacity:0.5;">
                    <circle cx="12" cy="12" r="10"/>
                    <line x1="12" y1="8" x2="12" y2="12"/>
                    <line x1="12" y1="16" x2="12.01" y2="16"/>
                </svg>
                <p style="font-size:16px;font-weight:600;margin-bottom:8px;">加载失败</p>
                <p style="font-size:14px;">${error.message || '未知错误，请稍后重试'}</p>
            </div>
        `;
    }
}

function closePostDrawer() {
    const drawer = document.getElementById('postDrawer');
    const overlay = document.getElementById('postDrawerOverlay');

    if (drawer) drawer.classList.remove('active');
    if (overlay) overlay.classList.remove('active');
    document.body.style.overflow = '';
    currentDrawerPostId = null;
}

function updateDrawerStats(post) {
    const footerEl = document.getElementById('postDrawerFooter');
    if (!footerEl || !currentDrawerPostId) return;

    footerEl.innerHTML = `
        <div class="post-drawer-stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
            ${post.views} 浏览
        </div>
        <div class="post-drawer-stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
            ${post.likes} 点赞
        </div>
        <div class="post-drawer-stat">
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
            ${post.reply_count || 0} 回复
        </div>
    `;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function formatDate(dateString) {
    const date = new Date(dateString);
    const now = new Date();
    const diff = now - date;
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(diff / 3600000);
    const days = Math.floor(diff / 86400000);

    if (minutes < 1) return '刚刚';
    if (minutes < 60) return `${minutes} 分钟前`;
    if (hours < 24) return `${hours} 小时前`;
    if (days < 7) return `${days} 天前`;
    return date.toLocaleDateString('zh-CN', { year: 'numeric', month: '2-digit', day: '2-digit' });
}
