/**
 * 极简软重定向 (SPA Router)
 * 拦截所有站内链接，使用 fetch + DOM 替换实现无刷新跳转
 */
(function() {
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a');
        if (!link || link.target === '_blank' || link.href.startsWith('javascript:')) return;
        
        const url = new URL(link.href);
        if (url.origin !== window.location.origin) return; // 仅拦截站内

        e.preventDefault();
        navigate(url.pathname + url.search, true);
    });

    window.addEventListener('popstate', function(e) {
        if (e.state && e.state.html) {
            document.title = e.state.title;
            document.querySelector('main').innerHTML = e.state.html;
            initPage();
        } else {
            navigate(window.location.pathname + window.location.search, false);
        }
    });

    async function navigate(url, push) {
        try {
            const res = await fetch(url);
            if (!res.ok) { window.location.href = url; return; }
            
            const html = await res.text();
            const doc = new DOMParser().parseFromString(html, 'text/html');
            
            // 1. 更新标题
            document.title = doc.title;
            
            // 2. 替换 Main 内容
            const newMain = doc.querySelector('main');
            const oldMain = document.querySelector('main');
            if (newMain && oldMain) {
                oldMain.innerHTML = newMain.innerHTML;
            }

            // 3. 更新 URL
            if (push) {
                history.pushState({ 
                    url: url, 
                    html: newMain ? newMain.innerHTML : '', 
                    title: doc.title 
                }, '', url);
                window.scrollTo(0, 0);
            }

            // 4. 更新 Dock 高亮
            document.querySelectorAll('#dock .dock-item').forEach(el => {
                const href = el.getAttribute('href');
                el.classList.toggle('active', href && url.startsWith(href));
            });

            // 5. 重新注入脚本/逻辑
            injectScripts(doc);
            initPage();

        } catch (err) {
            console.error(err);
            window.location.href = url;
        }
    }

    function injectScripts(doc) {
        doc.scripts.forEach(oldScript => {
            const newScript = document.createElement('script');
            Array.from(oldScript.attributes).forEach(attr => newScript.setAttribute(attr.name, attr.value));
            if (oldScript.src) {
                newScript.src = oldScript.src;
                document.body.appendChild(newScript);
            } else {
                newScript.textContent = oldScript.textContent;
                document.body.appendChild(newScript);
            }
        });
    }

    // 通用页面初始化入口
    function initPage() {
        // 尝试调用社区模块初始化
        if (typeof initCommunity === 'function') {
            // 如果脚本已加载，直接调用
            initCommunity();
        } else {
            // 否则动态加载
            if (location.pathname.includes('/community/') || location.pathname.endsWith('/community/')) {
                const s = document.createElement('script');
                s.src = '/community/assets/js/community.js';
                document.body.appendChild(s);
            }
        }
    }
})();