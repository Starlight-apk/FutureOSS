// 前端路由系统

/**
 * 路由配置
 */
const routes = {
    '/': {
        name: 'home',
        title: 'FutureOSS - 插件化运行时框架',
        description: 'FutureOSS 是一个高度插件化的运行时框架，专为现代应用设计。'
    },
    '/features': {
        name: 'features',
        title: '核心特性 - FutureOSS',
        description: 'FutureOSS 的六大核心特性，专为现代开发需求设计。'
    },
    '/architecture': {
        name: 'architecture',
        title: '系统架构 - FutureOSS',
        description: '深入了解 FutureOSS 的微内核架构和插件化设计。'
    },
    '/plugins': {
        name: 'plugins',
        title: '插件生态 - FutureOSS',
        description: '探索 FutureOSS 丰富的插件生态系统。'
    }
};

/**
 * 初始化路由
 */
function initRouter() {
    console.log('初始化前端路由...');
    
    // 监听浏览器前进/后退
    window.addEventListener('popstate', handlePopState);
    
    // 拦截链接点击
    document.addEventListener('click', handleLinkClick);
    
    // 初始路由处理
    handleRoute(window.location.pathname);
    
    console.log('路由初始化完成');
}

/**
 * 处理路由
 * @param {string} path - 路径
 */
function handleRoute(path) {
    const route = routes[path] || routes['/'];
    
    // 更新页面状态
    updatePageState(route.name);
    
    // 更新文档标题和描述
    document.title = route.title;
    updateMetaDescription(route.description);
    
    // 触发路由变化事件
    window.dispatchEvent(new CustomEvent('routechange', {
        detail: { route: route.name, path: path }
    }));
    
    console.log(`路由切换到: ${path} (${route.name})`);
}

/**
 * 更新页面状态
 * @param {string} pageName - 页面名称
 */
function updatePageState(pageName) {
    // 更新body类名
    const bodyClass = document.body.className;
    const newClass = bodyClass.replace(/page-\w+/, `page-${pageName}`);
    document.body.className = newClass.includes('page-') ? newClass : `${newClass} page-${pageName}`;
    
    // 更新导航栏激活状态
    updateNavActiveState(pageName);
    
    // 滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * 更新导航栏激活状态
 * @param {string} pageName - 页面名称
 */
function updateNavActiveState(pageName) {
    const navLinks = document.querySelectorAll('.navbar-link');
    navLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === pageName) {
            link.classList.add('active');
        }
    });
}

/**
 * 更新meta描述
 * @param {string} description - 描述内容
 */
function updateMetaDescription(description) {
    let metaDescription = document.querySelector('meta[name="description"]');
    if (!metaDescription) {
        metaDescription = document.createElement('meta');
        metaDescription.name = 'description';
        document.head.appendChild(metaDescription);
    }
    metaDescription.content = description;
}

/**
 * 处理链接点击
 * @param {Event} event - 点击事件
 */
function handleLinkClick(event) {
    const link = event.target.closest('a[data-page]');
    if (!link) return;
    
    const href = link.getAttribute('href');
    const page = link.getAttribute('data-page');
    
    // 如果是内部链接且不是当前页面
    if (href === '#' && page) {
        event.preventDefault();
        
        const currentPage = document.body.className.match(/page-(\w+)/)?.[1];
        if (page === currentPage) return;
        
        // 显示页面切换动画
        showPageTransition();
        
        // 延迟导航
        setTimeout(() => {
            navigateTo(page);
        }, 300);
    }
}

/**
 * 处理浏览器前进/后退
 * @param {PopStateEvent} event - popstate事件
 */
function handlePopState(event) {
    if (event.state && event.state.page) {
        handleRoute(`/${event.state.page === 'home' ? '' : event.state.page}`);
    } else {
        handleRoute(window.location.pathname);
    }
}

/**
 * 导航到指定页面
 * @param {string} pageName - 页面名称
 */
function navigateTo(pageName) {
    const path = pageName === 'home' ? '/' : `/${pageName}`;
    const route = routes[path];
    
    if (!route) {
        console.error(`路由未找到: ${pageName}`);
        return;
    }
    
    // 更新浏览器历史
    window.history.pushState({ page: pageName }, route.title, path);
    
    // 处理路由
    handleRoute(path);
    
    // 隐藏页面切换动画
    hidePageTransition();
}

/**
 * 显示页面切换动画
 */
function showPageTransition() {
    const transition = document.getElementById('page-transition');
    if (transition) {
        transition.classList.add('active');
    }
}

/**
 * 隐藏页面切换动画
 */
function hidePageTransition() {
    const transition = document.getElementById('page-transition');
    if (transition) {
        setTimeout(() => {
            transition.classList.remove('active');
        }, 300);
    }
}

/**
 * 获取当前路由信息
 * @returns {Object} 当前路由信息
 */
function getCurrentRoute() {
    const path = window.location.pathname;
    return routes[path] || routes['/'];
}

/**
 * 检查路由是否存在
 * @param {string} path - 路径
 * @returns {boolean} 是否存在
 */
function routeExists(path) {
    return routes.hasOwnProperty(path);
}

/**
 * 添加路由
 * @param {string} path - 路径
 * @param {Object} config - 路由配置
 */
function addRoute(path, config) {
    if (routes[path]) {
        console.warn(`路由已存在: ${path}`);
        return false;
    }
    
    routes[path] = {
        name: config.name || path.slice(1),
        title: config.title || 'FutureOSS',
        description: config.description || ''
    };
    
    console.log(`路由添加成功: ${path}`);
    return true;
}

/**
 * 移除路由
 * @param {string} path - 路径
 */
function removeRoute(path) {
    if (!routes[path]) {
        console.warn(`路由不存在: ${path}`);
        return false;
    }
    
    delete routes[path];
    console.log(`路由移除成功: ${path}`);
    return true;
}

// 导出路由函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initRouter,
        navigateTo,
        getCurrentRoute,
        routeExists,
        addRoute,
        removeRoute,
        routes
    };
}