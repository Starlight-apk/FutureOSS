/**
 * Dock 侧边栏组件
 * 在所有 HTML 页面中统一引用
 */

(function () {
    'use strict';

    // 获取当前页面相对于网站根目录的深度
    // 返回 '../' 或 '../../' 等，根目录页面返回 ''
    function getPathPrefix() {
        const path = window.location.pathname;
        // 去掉文件名，得到目录部分
        const dir = path.substring(0, path.lastIndexOf('/') + 1);
        // 计算目录层级数（排除开头的 /）
        const segments = dir.split('/').filter(s => s.length > 0);
        // 每个层级需要一个 '../'
        return segments.map(() => '../').join('');
    }

    // Dock HTML 模板
    // current: 当前页面文件名，用于设置 active 状态
    function renderDock(current) {
        const prefix = getPathPrefix();
        const items = [
            { href: prefix + 'index.html', tooltip: '首页', svg: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
            { href: prefix + 'features.html', tooltip: '特性', svg: 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z' },
            { href: prefix + 'docs/index.html', tooltip: '文档', svg: 'M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253' },
            { href: prefix + 'plugins.html', tooltip: '插件', svg: 'M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z' },
            { href: prefix + 'architecture.html', tooltip: '架构', svg: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z' },
            { separator: true },
            { href: 'https://gitee.com/starlight-apk/feature-oss', tooltip: '源码', svg: 'M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4', target: '_blank' }
        ];

        let html = '<aside id="dock">\n';

        items.forEach(item => {
            if (item.separator) {
                html += '        <div class="dock-separator"></div>\n';
            } else {
                const isActive = item.href === current ? ' active' : '';
                const targetAttr = item.target ? ` target="${item.target}"` : '';
                html += `        <a href="${item.href}" class="dock-item${isActive}" data-tooltip="${item.tooltip}"${targetAttr}>\n`;
                html += `            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="${item.svg}"/></svg>\n`;
                html += `        </a>\n`;
            }
        });

        html += '    </aside>';
        return html;
    }

    // 获取当前页面文件名
    function getCurrentPage() {
        const path = window.location.pathname;
        const filename = path.substring(path.lastIndexOf('/') + 1);
        return filename || 'index.html';
    }

    // 初始化：将 dock 插入到 body 的第一个子元素之前
    function initDock() {
        const current = getCurrentPage();
        const dockHTML = renderDock(current);
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = dockHTML;
        const dockElement = tempDiv.firstElementChild;

        const body = document.body;
        const firstChild = body.firstChild;
        if (firstChild) {
            body.insertBefore(dockElement, firstChild);
        } else {
            body.appendChild(dockElement);
        }
    }

    // DOM 加载完成后初始化
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initDock);
    } else {
        initDock();
    }

    // 对外暴露（如果需要手动调用）
    window.OSSDock = { init: initDock, render: renderDock };
})();
