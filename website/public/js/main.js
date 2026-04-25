// 主JavaScript文件

/**
 * 初始化导航栏
 */
function initNavigation() {
    const navbarLinks = document.querySelectorAll('.navbar-link');
    const currentPage = document.body.classList.contains('page-home') ? 'home' :
                       document.body.classList.contains('page-features') ? 'features' :
                       document.body.classList.contains('page-architecture') ? 'architecture' :
                       document.body.classList.contains('page-plugins') ? 'plugins' : 'home';
    
    navbarLinks.forEach(link => {
        if (link.getAttribute('data-page') === currentPage) {
            link.classList.add('active');
        }
        
        // 添加点击事件
        link.addEventListener('click', function(e) {
            if (this.getAttribute('href') === '#') {
                e.preventDefault();
                const page = this.getAttribute('data-page');
                if (page && page !== currentPage) {
                    navigateToPage(page);
                }
            }
        });
    });
}

/**
 * 初始化页面切换
 */
function initPageTransitions() {
    const pageTransition = document.getElementById('page-transition');
    if (!pageTransition) return;
    
    // 监听页面链接点击
    document.addEventListener('click', function(e) {
        const link = e.target.closest('a[data-page]');
        if (link && link.getAttribute('href') === '#') {
            e.preventDefault();
            const page = link.getAttribute('data-page');
            const currentPage = document.body.className.match(/page-(\w+)/)?.[1];
            
            if (page && page !== currentPage) {
                // 显示页面切换动画
                pageTransition.classList.add('active');
                
                // 延迟导航
                setTimeout(() => {
                    navigateToPage(page);
                }, 300);
            }
        }
    });
}

/**
 * 导航到指定页面
 * @param {string} page - 页面名称
 */
function navigateToPage(page) {
    console.log(`导航到页面: ${page}`);
    
    // 这里应该使用前端路由或实际页面跳转
    // 目前先更新URL和页面状态
    const url = `/${page === 'home' ? '' : page}`;
    window.history.pushState({ page }, '', url);
    
    // 更新页面内容
    updatePageContent(page);
    
    // 更新导航栏激活状态
    updateNavigation(page);
    
    // 隐藏页面切换动画
    const pageTransition = document.getElementById('page-transition');
    if (pageTransition) {
        setTimeout(() => {
            pageTransition.classList.remove('active');
        }, 300);
    }
}

/**
 * 更新页面内容
 * @param {string} page - 页面名称
 */
function updatePageContent(page) {
    // 更新body类名
    document.body.className = document.body.className.replace(/page-\w+/, `page-${page}`);
    
    // 更新页面标题
    const pageTitles = {
        'home': 'FutureOSS - 插件化运行时框架',
        'features': '核心特性 - FutureOSS',
        'architecture': '系统架构 - FutureOSS',
        'plugins': '插件生态 - FutureOSS'
    };
    
    document.title = pageTitles[page] || pageTitles.home;
    
    // 这里应该加载新的页面内容
    // 目前先滚动到顶部
    window.scrollTo({ top: 0, behavior: 'smooth' });
}

/**
 * 更新导航栏激活状态
 * @param {string} page - 页面名称
 */
function updateNavigation(page) {
    const navbarLinks = document.querySelectorAll('.navbar-link');
    navbarLinks.forEach(link => {
        link.classList.remove('active');
        if (link.getAttribute('data-page') === page) {
            link.classList.add('active');
        }
    });
}

/**
 * 初始化按钮交互
 */
function initButtonInteractions() {
    // 为所有按钮添加悬停效果
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-2px)';
        });
        
        button.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
    
    // 为卡片添加悬停效果
    const cards = document.querySelectorAll('.card, .feature-card');
    cards.forEach(card => {
        card.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-4px)';
        });
        
        card.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
}

/**
 * 初始化滚动效果
 */
function initScrollEffects() {
    let lastScrollTop = 0;
    const navbar = document.querySelector('.navbar');
    
    if (!navbar) return;
    
    window.addEventListener('scroll', function() {
        const scrollTop = window.pageYOffset || document.documentElement.scrollTop;
        
        // 隐藏/显示导航栏
        if (scrollTop > lastScrollTop && scrollTop > 100) {
            // 向下滚动，隐藏导航栏
            navbar.style.transform = 'translateY(-100%)';
        } else {
            // 向上滚动，显示导航栏
            navbar.style.transform = 'translateY(0)';
        }
        
        lastScrollTop = scrollTop;
        
        // 添加滚动阴影
        if (scrollTop > 10) {
            navbar.style.boxShadow = 'var(--shadow-md)';
        } else {
            navbar.style.boxShadow = 'var(--shadow-sm)';
        }
    });
}

/**
 * 显示消息提示
 * @param {string} message - 消息内容
 * @param {string} type - 消息类型: 'success', 'error', 'info', 'warning'
 */
function showMessage(message, type = 'info') {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message message-${type}`;
    messageDiv.textContent = message;
    messageDiv.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background-color: ${getMessageColor(type)};
        color: white;
        border-radius: var(--radius-md);
        box-shadow: var(--shadow-lg);
        z-index: 9999;
        animation: fadeIn 0.3s ease;
    `;
    
    document.body.appendChild(messageDiv);
    
    // 3秒后自动消失
    setTimeout(() => {
        messageDiv.style.animation = 'fadeOut 0.3s ease';
        setTimeout(() => {
            if (messageDiv.parentNode) {
                messageDiv.parentNode.removeChild(messageDiv);
            }
        }, 300);
    }, 3000);
}

/**
 * 获取消息颜色
 * @param {string} type - 消息类型
 * @returns {string} - 颜色值
 */
function getMessageColor(type) {
    const colors = {
        'success': 'var(--success-color)',
        'error': 'var(--danger-color)',
        'info': 'var(--info-color)',
        'warning': 'var(--warning-color)'
    };
    return colors[type] || colors.info;
}

/**
 * 防抖函数
 * @param {Function} func - 要执行的函数
 * @param {number} wait - 等待时间(毫秒)
 * @returns {Function} - 防抖后的函数
 */
function debounce(func, wait) {
    let timeout;
    return function executedFunction(...args) {
        const later = () => {
            clearTimeout(timeout);
            func(...args);
        };
        clearTimeout(timeout);
        timeout = setTimeout(later, wait);
    };
}

/**
 * 节流函数
 * @param {Function} func - 要执行的函数
 * @param {number} limit - 限制时间(毫秒)
 * @returns {Function} - 节流后的函数
 */
function throttle(func, limit) {
    let inThrottle;
    return function(...args) {
        if (!inThrottle) {
            func.apply(this, args);
            inThrottle = true;
            setTimeout(() => inThrottle = false, limit);
        }
    };
}

/**
 * 隐藏加载动画
 */
function hideLoadingAnimation() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        // 简单隐藏
        loadingOverlay.style.display = 'none';
    }
}

/**
 * 显示加载动画
 */
function showLoadingAnimation() {
    const loadingOverlay = document.getElementById('loading-overlay');
    if (loadingOverlay) {
        loadingOverlay.style.display = 'flex';
    }
}

/**
 * 初始化页面
 */
function initPage() {
    console.log('FutureOSS 网站初始化...');
    
    // 确保加载动画被隐藏
    setTimeout(() => {
        hideLoadingAnimation();
    }, 100);
    
    // 初始化导航栏
    initNavigation();
    
    // 初始化页面切换
    initPageTransitions();
    
    // 初始化按钮交互
    initButtonInteractions();
    
    // 初始化滚动效果
    initScrollEffects();
    
    // 初始化图片懒加载
    initLazyLoading();
    
    console.log('页面初始化完成');
}

/**
 * 初始化图片懒加载
 */
function initLazyLoading() {
    const lazyImages = document.querySelectorAll('img[data-src]');
    
    if ('IntersectionObserver' in window) {
        const imageObserver = new IntersectionObserver((entries, observer) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    const img = entry.target;
                    img.src = img.dataset.src;
                    img.classList.remove('lazy-image');
                    observer.unobserve(img);
                }
            });
        });
        
        lazyImages.forEach(img => imageObserver.observe(img));
    } else {
        // 回退方案：直接加载所有图片
        lazyImages.forEach(img => {
            img.src = img.dataset.src;
            img.classList.remove('lazy-image');
        });
    }
}

/**
 * 性能监控
 */
function initPerformanceMonitoring() {
    // 监控页面加载性能
    window.addEventListener('load', () => {
        if (window.performance) {
            const timing = performance.timing;
            const loadTime = timing.loadEventEnd - timing.navigationStart;
            console.log(`页面加载时间: ${loadTime}ms`);
            
            if (loadTime > 3000) {
                console.warn('页面加载时间过长，建议优化');
            }
        }
    });
    
    // 监控长任务
    if ('PerformanceObserver' in window) {
        const observer = new PerformanceObserver((list) => {
            for (const entry of list.getEntries()) {
                if (entry.duration > 50) {
                    console.warn('检测到长任务:', entry);
                }
            }
        });
        
        observer.observe({ entryTypes: ['longtask'] });
    }
}

// 页面加载完成后初始化
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOMContentLoaded 事件触发');
    initPerformanceMonitoring();
    initPage();
});

// 窗口加载完成事件作为最后保障
window.addEventListener('load', () => {
    console.log('window.load 事件触发');
    // 确保加载动画被隐藏
    hideLoadingAnimation();
});

// 立即隐藏加载动画（如果可能）
if (document.readyState !== 'loading') {
    console.log('文档已加载完成，直接初始化');
    initPerformanceMonitoring();
    initPage();
}

// 导出函数供其他模块使用
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initPage,
        navigateToPage,
        showMessage,
        debounce,
        throttle
    };
}