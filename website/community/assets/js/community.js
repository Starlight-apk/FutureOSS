/**
 * OSS Community Module
 * Handles rendering of categories, stats, and posts list.
 * Designed to be SPA-friendly (re-initializable).
 */

// Global state variables
let currentPage = 1;
let currentCategory = '';
let currentSort = 'latest';

// Expose initialization function globally for SPA Router
window.initCommunity = function() {
    // Check if we are deep-linked (e.g. ?page=2)
    const params = new URLSearchParams(window.location.search);
    if(params.has('page')) currentPage = parseInt(params.get('page'));

    // Fetch and Render Data
    loadCategories();
    loadStats();
    loadPosts();

    // Bind Events (to the new DOM elements created by SPA)
    bindCommunityEvents();
};

function bindCommunityEvents() {
    const catList = document.getElementById('categoryList');
    if (catList) {
        catList.addEventListener('click', e => {
            const li = e.target.closest('li');
            if (!li) return;

            document.querySelectorAll('.category-list li').forEach(el => el.classList.remove('active'));
            li.classList.add('active');

            currentCategory = li.dataset.id || '';
            currentPage = 1;
            document.getElementById('currentCategory').textContent = li.querySelector('span:nth-child(2)').textContent + '帖子';
            loadPosts();
        });
    }

    const sortOptions = document.querySelector('.sort-options');
    if (sortOptions) {
        sortOptions.addEventListener('click', e => {
            if (!e.target.classList.contains('sort-btn')) return;
            document.querySelectorAll('.sort-btn').forEach(btn => btn.classList.remove('active'));
            e.target.classList.add('active');
            currentSort = e.target.dataset.sort;
            currentPage = 1;
            loadPosts();
        });
    }
}

// --- Data Loading Functions ---

const API = './api/index.php'; // Relative to community/ directory

async function loadCategories() {
    try {
        const res = await fetch(`${API}?action=categories`);
        const data = await res.json();

        const list = document.getElementById('categoryList');
        if (!list) return;

        // Keep the "All" item (first child) if it exists
        const allItem = list.firstElementChild;
        list.innerHTML = '';
        if (allItem) list.appendChild(allItem);

        data.categories.forEach(cat => {
            const li = document.createElement('li');
            li.dataset.id = cat.id;
            li.innerHTML = `<span class="cat-icon">${getIconSvg(cat.icon)}</span><span>${cat.name}</span>`;
            list.appendChild(li);
        });
    } catch (e) {
        console.error('Failed to load categories', e);
    }
}

async function loadStats() {
    try {
        const res = await fetch(`${API}?action=stats`);
        const data = await res.json();

        animateValue('statPosts', 0, data.posts, 1000);
        animateValue('statReplies', 0, data.replies, 1000);
        animateValue('statUsers', 0, data.users, 1000);
        const countAll = document.getElementById('countAll');
        if (countAll) countAll.textContent = data.posts;
    } catch (e) {
        console.error('Failed to load stats', e);
    }
}

async function loadPosts() {
    const list = document.getElementById('postsList');
    if (!list) return;
    
    list.innerHTML = '<div class="empty-state"><div class="loading-spinner"></div><p>正在连接节点...</p></div>';

    try {
        const params = new URLSearchParams({ action: 'posts', page: currentPage });
        if (currentCategory) params.append('category_id', currentCategory);

        const res = await fetch(`${API}?${params}`);
        const data = await res.json();

        list.innerHTML = '';

        if (data.posts.length === 0) {
            list.innerHTML = `
                <div class="empty-state">
                    <div class="empty-state-icon">📭</div>
                    <h3>暂无帖子</h3>
                    <p>成为第一个发帖的人吧！</p>
                </div>
            `;
            return;
        }

        data.posts.forEach((post, index) => {
            const card = document.createElement('div');
            card.className = 'post-card';
            card.dataset.postId = post.id;
            card.style.animationDelay = `${index * 0.1}s`;
            
            card.innerHTML = `
                <div class="post-header">
                    <div class="post-avatar">${post.username[0].toUpperCase()}</div>
                    <div class="post-meta">
                        <div class="post-author">${escapeHtml(post.username)}</div>
                        <div class="post-time">${timeAgo(post.created_at)}</div>
                    </div>
                    <div class="post-tags">
                        <span class="tag">${post.category_name}</span>
                        ${post.is_pinned ? '<span class="pinned-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" width="12" height="12"><path d="M12 2l3.09 6.26L22 9.27l-5 4.87 1.18 6.88L12 17.77l-6.18 3.25L7 14.14 2 9.27l6.91-1.01L12 2z"/></svg> 置顶</span>' : ''}
                    </div>
                </div>
                <div class="post-title">${escapeHtml(post.title)}</div>
                <div class="post-excerpt">${escapeHtml(post.content.substring(0, 150))}...</div>
                <div class="post-stats">
                    <span>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/><circle cx="12" cy="12" r="3"/></svg>
                        ${post.views}
                    </span>
                    <span>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M20.84 4.61a5.5 5.5 0 0 0-7.78 0L12 5.67l-1.06-1.06a5.5 5.5 0 0 0-7.78 7.78l1.06 1.06L12 21.23l7.78-7.78 1.06-1.06a5.5 5.5 0 0 0 0-7.78z"/></svg>
                        ${post.likes}
                    </span>
                    <span>
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"/></svg>
                        ${post.reply_count || 0}
                    </span>
                </div>
            `;
            list.appendChild(card);
        });

        renderPagination(data.pages);
    } catch (e) {
        list.innerHTML = '<div class="empty-state"><p>加载失败，请稍后重试</p></div>';
    }
}

function renderPagination(pages) {
    const container = document.getElementById('pagination');
    if (!container) return;
    
    container.innerHTML = '';
    if (pages <= 1) return;

    for (let i = 1; i <= pages; i++) {
        const btn = document.createElement('button');
        btn.className = `page-btn ${i === currentPage ? 'active' : ''}`;
        btn.textContent = i;
        btn.onclick = () => { 
            currentPage = i; 
            loadPosts(); 
            window.scrollTo({ top: 0, behavior: 'smooth' }); 
        };
        container.appendChild(btn);
    }
}

// --- Utilities ---

function animateValue(id, start, end, duration) {
    const obj = document.getElementById(id);
    if (!obj) return;
    let startTimestamp = null;
    const step = (timestamp) => {
        if (!startTimestamp) startTimestamp = timestamp;
        const progress = Math.min((timestamp - startTimestamp) / duration, 1);
        obj.textContent = Math.floor(progress * (end - start) + start);
        if (progress < 1) {
            window.requestAnimationFrame(step);
        }
    };
    window.requestAnimationFrame(step);
}

function timeAgo(dateStr) {
    const now = new Date();
    const date = new Date(dateStr);
    const seconds = Math.floor((now - date) / 1000);
    const intervals = [
        [31536000, '年'], [2592000, '个月'], [604800, '周'],
        [86400, '天'], [3600, '小时'], [60, '分钟']
    ];
    for (const [secondsCount, label] of intervals) {
        const count = Math.floor(seconds / secondsCount);
        if (count >= 1) return `${count}${label}前`;
    }
    return '刚刚';
}

function escapeHtml(str) {
    if (!str) return '';
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

function getIconSvg(name) {
    const icons = {
        megaphone: '<svg viewBox="0 0 24 24"><path d="M3 11l18-5v12L3 13v-2zm11.5 1a1.5 1.5 0 1 1 0-3 1.5 1.5 0 0 1 0 3zM7 20v-2h10v2H7z"/></svg>',
        question: '<svg viewBox="0 0 24 24"><path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm1 17h-2v-2h2v2zm2.07-7.75l-.9.92C13.45 12.9 13 13.5 13 15h-2v-.5c0-1.1.45-2.1 1.17-2.83l1.24-1.26c.37-.36.59-.86.59-1.41 0-1.1-.9-2-2-2s-2 .9-2 2H8c0-2.21 1.79-4 4-4s4 1.79 4 4c0 .88-.36 1.68-.93 2.25z"/></svg>',
        chat: '<svg viewBox="0 0 24 24"><path d="M20 2H4c-1.1 0-2 .9-2 2v18l4-4h14c1.1 0 2-.9 2-2V4c0-1.1-.9-2-2-2zm0 14H6l-2 2V4h16v12z"/></svg>',
        puzzle: '<svg viewBox="0 0 24 24"><path d="M20.5 11H19V7c0-1.1-.9-2-2-2h-4V3.5C13 2.12 11.88 1 10.5 1S8 2.12 8 3.5V5H4c-1.1 0-2 .9-2 2v3.8h1.5c1.49 0 2.7 1.21 2.7 2.7s-1.21 2.7-2.7 2.7H2V20c0 1.1.9 2 2 2h3.8v-1.5c0-1.49 1.21-2.7 2.7-2.7s2.7 1.21 2.7 2.7V22H17c1.1 0 2-.9 2-2v-4h1.5c1.38 0 2.5-1.12 2.5-2.5S21.88 11 20.5 11z"/></svg>',
        bug: '<svg viewBox="0 0 24 24"><path d="M14 12c0 1.1-.9 2-2 2s-2-.9-2-2 .9-2 2-2 2 .9 2 2zM7.56 14.05l1.66-1.66c.36.36.87.59 1.44.65.24.02.47.04.69.04.48 0 .94-.07 1.39-.2l1.32 1.32c-.65.18-1.33.28-2.03.32C10.18 14.64 8.72 14.33 7.56 14.05zM17.77 9.48l-1.32 1.32c-.45-.13-.91-.2-1.39-.2-.22 0-.45.02-.69.04-.57.06-1.08.29-1.44.65l-1.66-1.66c1.16-.28 2.62-.59 4.48-.47.69.04 1.37.14 2.02.32zM12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8z"/></svg>'
    };
    return icons[name] || icons['chat'];
}

// showCreateModal 函数已移至 post-modal.php 中定义
// 此处仅保留兼容性封装
window.showCreateModal = window.showCreateModal || function() {
    if (typeof window.showCreatePostModal === 'function') {
        window.showCreatePostModal();
    } else {
        console.warn('发帖模态框未加载');
    }
};

// Auto-init if not loaded via SPA (Hard refresh case)
document.addEventListener('DOMContentLoaded', () => {
    if (typeof AppRouter === 'undefined') {
        window.initCommunity();
    }
});