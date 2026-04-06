/**
 * OSS Community - 轮询数据实时更新
 */

document.addEventListener('DOMContentLoaded', () => {
    if (!window.Polling) return;

    // ========== 用户数据（称号、权限） ==========
    let prevTitle = '', prevPerms = {};
    window.Polling.on('user', (data) => {
        if (!data.success || !data.user) return;
        const { title, role } = data.user;

        // 更新称号徽章
        if (title !== prevTitle) {
            prevTitle = title;
            const avatar = document.getElementById('dockUserAvatar');
            if (avatar) {
                const name = avatar.dataset.tooltip.split(' - ')[0] || avatar.dataset.tooltip;
                avatar.dataset.tooltip = title ? `${name} - ${title}` : name;
            }
            let badge = document.querySelector('.user-title-badge');
            if (title) {
                if (!badge) { badge = document.createElement('span'); badge.className = 'user-title-badge'; if (avatar) avatar.appendChild(badge); }
                badge.textContent = title;
            } else if (badge) badge.remove();
        }

        // 权限控制
        if (data.permissions && JSON.stringify(data.permissions) !== JSON.stringify(prevPerms)) {
            prevPerms = data.permissions;
            document.querySelectorAll('.admin-only').forEach(el => el.style.display = prevPerms.can_manage_users ? '' : 'none');
            document.querySelectorAll('.moderator-only').forEach(el => el.style.display = prevPerms.can_manage_posts ? '' : 'none');
        }
    });

    // ========== 帖子数据实时更新 views/likes/replies ==========
    window.Polling.on('posts', (data) => {
        if (!data.posts || !Array.isArray(data.posts)) return;

        data.posts.forEach(post => {
            // 更新帖子卡片上的浏览、点赞、回复数
            const cards = document.querySelectorAll(`.post-card[data-post-id="${post.id}"]`);
            cards.forEach(card => {
                const statsEls = card.querySelectorAll('.post-stats span');
                if (statsEls.length >= 3) {
                    // views
                    const viewsSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>';
                    // likes
                    const likesSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>';
                    // replies
                    const repliesSvg = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>';

                    statsEls[0].innerHTML = viewsSvg + ` ${post.views}`;
                    statsEls[1].innerHTML = likesSvg + ` ${post.likes}`;
                    statsEls[2].innerHTML = repliesSvg + ` ${post.reply_count || 0}`;
                }
            });

            // 更新个人主页帖子列表的 stats
            const myListItems = document.querySelectorAll(`.my-post-item[data-post-id="${post.id}"] .my-post-meta`);
            myListItems.forEach(meta => {
                const spans = meta.querySelectorAll('span');
                if (spans.length >= 4) {
                    spans[1].textContent = `👁️ ${post.views} 浏览`;
                    spans[2].textContent = `❤️ ${post.likes} 点赞`;
                    spans[3].textContent = `💬 ${post.reply_count || 0} 回复`;
                }
            });
        });
    });

    // ========== 统计数字实时更新 ==========
    window.Polling.on('stats', (data) => {
        if (data.posts !== undefined) animateNumber('statPosts', data.posts);
        if (data.replies !== undefined) animateNumber('statReplies', data.replies);
        if (data.users !== undefined) animateNumber('statUsers', data.users);
        const countAll = document.getElementById('countAll');
        if (countAll) countAll.textContent = data.posts || 0;

        // 更新热门帖子 views（如果有这个区域）
        if (data.hot_posts && Array.isArray(data.hot_posts)) {
            data.hot_posts.forEach(hp => {
                const hotItems = document.querySelectorAll(`.hot-post-item[data-post-id="${hp.id}"]`);
                hotItems.forEach(item => {
                    const viewsEl = item.querySelector('.hot-views');
                    if (viewsEl) viewsEl.textContent = hp.views;
                });
            });
        }
    });

    // ========== 分类更新 ==========
    window.Polling.on('categories', (data) => {
        if (!data.categories) return;
        const countAll = document.getElementById('countAll');
        if (countAll) countAll.textContent = data.posts || data.categories.length;
    });
});

// 数字动画
function animateNumber(id, target) {
    const el = document.getElementById(id);
    if (!el) return;
    const current = parseInt(el.textContent) || 0;
    if (current === target) return;
    el.textContent = target;
}
