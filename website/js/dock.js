/**
 * Dock 侧边栏组件
 * 在所有 HTML 页面中统一引用
 */

(function () {
    'use strict';

    // Dock HTML 模板
    // current: 当前页面文件名，用于设置 active 状态
    function renderDock(current) {
        const items = [
            { href: 'index.html', tooltip: '首页', svg: 'M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6' },
            { href: 'features.html', tooltip: '特性', svg: 'M5 3v4M3 5h4M6 17v4m-2-2h4m5-16l2.286 6.857L21 12l-5.714 2.143L13 21l-2.286-6.857L5 12l5.714-2.143L13 3z' },
            { href: 'plugins.html', tooltip: '插件', svg: 'M11 4a2 2 0 114 0v1a1 1 0 001 1h3a1 1 0 011 1v3a1 1 0 01-1 1h-1a2 2 0 100 4h1a1 1 0 011 1v3a1 1 0 01-1 1h-3a1 1 0 01-1-1v-1a2 2 0 10-4 0v1a1 1 0 01-1 1H7a1 1 0 01-1-1v-3a1 1 0 00-1-1H4a2 2 0 110-4h1a1 1 0 001-1V7a1 1 0 011-1h3a1 1 0 001-1V4z' },
            { href: 'architecture.html', tooltip: '架构', svg: 'M4 5a1 1 0 011-1h14a1 1 0 011 1v2a1 1 0 01-1 1H5a1 1 0 01-1-1V5zM4 13a1 1 0 011-1h6a1 1 0 011 1v6a1 1 0 01-1 1H5a1 1 0 01-1-1v-6zM16 13a1 1 0 011-1h2a1 1 0 011 1v6a1 1 0 01-1 1h-2a1 1 0 01-1-1v-6z' },
            { separator: true },
            { href: 'quickstart.html', tooltip: '快速开始', svg: 'M13 10V3L4 14h7v7l9-11h-7z' },
            { separator: true },
            { href: 'community/', tooltip: '社区', svg: 'M17 20h5v-2a3 3 0 00-5.356-1.857M17 20H7m10 0v-2c0-.656-.126-1.283-.356-1.857M7 20H2v-2a3 3 0 015.356-1.857M7 20v-2c0-.656.126-1.283.356-1.857m0 0a5.002 5.002 0 019.288 0M15 7a3 3 0 11-6 0 3 3 0 016 0zm6 3a2 2 0 11-4 0 2 2 0 014 0zM7 10a2 2 0 11-4 0 2 2 0 014 0z' },
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
