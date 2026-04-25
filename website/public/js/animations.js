/**
 * 动画和过渡效果管理
 */

/**
 * 初始化所有动画
 */
function initAnimations() {
    console.log('初始化动画系统...');
    
    // 初始化滚动动画
    initScrollAnimations();
    
    // 初始化视差效果
    initParallaxEffects();
    
    // 初始化计数器动画
    initCounterAnimations();
    
    // 初始化进度条动画
    initProgressBars();
    
    // 初始化打字机效果
    initTypewriterEffects();
    
    // 初始化骨架屏
    initSkeletonScreens();
    
    console.log('动画系统初始化完成');
}

/**
 * 初始化滚动动画
 */
function initScrollAnimations() {
    const animatedElements = document.querySelectorAll('.animate-on-scroll');
    
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) {
                    entry.target.classList.add('animated');
                    observer.unobserve(entry.target);
                }
            });
        }, {
            threshold: 0.1,
            rootMargin: '0px 0px -50px 0px'
        });
        
        animatedElements.forEach(element => observer.observe(element));
    } else {
        // 回退方案：直接添加动画类
        animatedElements.forEach(element => {
            element.classList.add('animated');
        });
    }
}

/**
 * 初始化视差效果
 */
function initParallaxEffects() {
    const parallaxElements = document.querySelectorAll('.parallax');
    
    if (parallaxElements.length === 0) return;
    
    window.addEventListener('scroll', () => {
        const scrolled = window.pageYOffset;
        
        parallaxElements.forEach(element => {
            const speed = parseFloat(element.dataset.speed) || 0.5;
            const yPos = -(scrolled * speed);
            element.style.transform = `translateY(${yPos}px)`;
        });
    });
}

/**
 * 初始化计数器动画
 */
function initCounterAnimations() {
    const counters = document.querySelectorAll('.counter');
    
    if (counters.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const counter = entry.target;
                const target = parseInt(counter.dataset.target) || 0;
                const duration = parseInt(counter.dataset.duration) || 2000;
                const increment = target / (duration / 16); // 60fps
                let current = 0;
                
                const updateCounter = () => {
                    current += increment;
                    if (current < target) {
                        counter.textContent = Math.floor(current).toLocaleString();
                        requestAnimationFrame(updateCounter);
                    } else {
                        counter.textContent = target.toLocaleString();
                    }
                };
                
                updateCounter();
                observer.unobserve(counter);
            }
        });
    });
    
    counters.forEach(counter => observer.observe(counter));
}

/**
 * 初始化进度条动画
 */
function initProgressBars() {
    const progressBars = document.querySelectorAll('.progress-bar');
    
    if (progressBars.length === 0) return;
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                const progressBar = entry.target;
                const width = progressBar.dataset.width || '100%';
                const duration = parseInt(progressBar.dataset.duration) || 1000;
                
                progressBar.style.transition = `width ${duration}ms ease`;
                progressBar.style.width = width;
                
                observer.unobserve(progressBar);
            }
        });
    });
    
    progressBars.forEach(bar => observer.observe(bar));
}

/**
 * 初始化打字机效果
 */
function initTypewriterEffects() {
    const typewriters = document.querySelectorAll('.typewriter');
    
    typewriters.forEach(element => {
        const text = element.textContent;
        element.textContent = '';
        element.style.width = '0';
        
        let i = 0;
        const type = () => {
            if (i < text.length) {
                element.textContent += text.charAt(i);
                element.style.width = `${(i + 1) / text.length * 100}%`;
                i++;
                setTimeout(type, 100);
            }
        };
        
        // 延迟开始打字效果
        setTimeout(type, 500);
    });
}

/**
 * 初始化骨架屏
 */
function initSkeletonScreens() {
    const skeletonElements = document.querySelectorAll('.skeleton');
    
    if (skeletonElements.length === 0) return;
    
    // 模拟内容加载
    setTimeout(() => {
        skeletonElements.forEach(element => {
            element.classList.remove('skeleton');
            element.classList.add('fade-in-load');
        });
    }, 1000);
}

/**
 * 创建骨架屏占位符
 * @param {HTMLElement} container - 容器元素
 * @param {number} count - 骨架屏数量
 * @param {string} type - 骨架屏类型: 'text', 'card', 'image'
 */
function createSkeletonPlaceholders(container, count = 3, type = 'card') {
    const skeletonClasses = {
        'text': 'skeleton skeleton-text',
        'card': 'skeleton skeleton-card',
        'image': 'skeleton skeleton-image'
    };
    
    const skeletonClass = skeletonClasses[type] || skeletonClasses.card;
    
    for (let i = 0; i < count; i++) {
        const skeleton = document.createElement('div');
        skeleton.className = skeletonClass;
        container.appendChild(skeleton);
    }
}

/**
 * 显示页面切换动画
 * @param {string} direction - 切换方向: 'left', 'right', 'up', 'down'
 */
function showPageTransition(direction = 'right') {
    const transition = document.getElementById('page-transition');
    if (!transition) return;
    
    const directions = {
        'left': 'slideInLeft',
        'right': 'slideInRight',
        'up': 'slideInUp',
        'down': 'slideInDown'
    };
    
    const animation = directions[direction] || 'slideInRight';
    transition.className = `page-transition animate-${animation}`;
    transition.classList.add('active');
    
    return new Promise(resolve => {
        setTimeout(() => {
            transition.classList.remove('active');
            setTimeout(resolve, 300);
        }, 300);
    });
}

/**
 * 显示元素动画
 * @param {HTMLElement} element - 要动画的元素
 * @param {string} animation - 动画名称
 * @param {number} duration - 动画持续时间(毫秒)
 */
function animateElement(element, animation = 'fadeIn', duration = 300) {
    if (!element) return;
    
    element.style.animation = `${animation} ${duration}ms ease`;
    element.classList.add('animated');
    
    // 动画完成后移除动画类
    setTimeout(() => {
        element.style.animation = '';
    }, duration);
}

/**
 * 创建波纹效果
 * @param {Event} event - 点击事件
 * @param {string} color - 波纹颜色
 */
function createRippleEffect(event, color = 'rgba(255, 255, 255, 0.7)') {
    const button = event.currentTarget;
    const circle = document.createElement('span');
    const diameter = Math.max(button.clientWidth, button.clientHeight);
    const radius = diameter / 2;
    
    circle.style.width = circle.style.height = `${diameter}px`;
    circle.style.left = `${event.clientX - button.offsetLeft - radius}px`;
    circle.style.top = `${event.clientY - button.offsetTop - radius}px`;
    circle.style.backgroundColor = color;
    circle.style.position = 'absolute';
    circle.style.borderRadius = '50%';
    circle.style.transform = 'scale(0)';
    circle.style.animation = 'ripple 600ms linear';
    
    const ripple = button.querySelector('.ripple');
    if (ripple) {
        ripple.remove();
    }
    
    button.appendChild(circle);
    
    // 动画完成后移除波纹元素
    setTimeout(() => {
        if (circle.parentNode === button) {
            button.removeChild(circle);
        }
    }, 600);
}

/**
 * 添加波纹效果到按钮
 * @param {string} selector - 按钮选择器
 */
function addRippleEffectToButtons(selector = '.btn') {
    const buttons = document.querySelectorAll(selector);
    
    buttons.forEach(button => {
        button.style.position = 'relative';
        button.style.overflow = 'hidden';
        
        button.addEventListener('click', function(event) {
            createRippleEffect(event);
        });
    });
    
    // 添加波纹动画CSS
    if (!document.querySelector('#ripple-styles')) {
        const style = document.createElement('style');
        style.id = 'ripple-styles';
        style.textContent = `
            @keyframes ripple {
                to {
                    transform: scale(4);
                    opacity: 0;
                }
            }
        `;
        document.head.appendChild(style);
    }
}

/**
 * 初始化图片加载动画
 */
function initImageLoadingAnimations() {
    const images = document.querySelectorAll('img:not([data-src])');
    
    images.forEach(img => {
        if (!img.complete) {
            img.classList.add('loading');
            
            img.addEventListener('load', function() {
                this.classList.remove('loading');
                this.classList.add('loaded');
                animateElement(this, 'scaleIn', 500);
            });
            
            img.addEventListener('error', function() {
                this.classList.remove('loading');
                this.classList.add('error');
                console.error('图片加载失败:', this.src);
            });
        } else {
            img.classList.add('loaded');
        }
    });
}

/**
 * 添加滚动到顶部按钮
 */
function initScrollToTopButton() {
    // 创建按钮
    const button = document.createElement('button');
    button.id = 'scroll-to-top';
    button.className = 'scroll-to-top-btn';
    button.innerHTML = '<i class="fas fa-chevron-up"></i>';
    button.title = '回到顶部';
    button.style.cssText = `
        position: fixed;
        bottom: 30px;
        right: 30px;
        width: 50px;
        height: 50px;
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 50%;
        cursor: pointer;
        opacity: 0;
        visibility: hidden;
        transition: all 0.3s ease;
        box-shadow: var(--shadow-lg);
        z-index: 1000;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
    `;
    
    document.body.appendChild(button);
    
    // 滚动事件监听
    window.addEventListener('scroll', () => {
        if (window.pageYOffset > 300) {
            button.style.opacity = '1';
            button.style.visibility = 'visible';
            button.style.transform = 'translateY(0)';
        } else {
            button.style.opacity = '0';
            button.style.visibility = 'hidden';
            button.style.transform = 'translateY(20px)';
        }
    });
    
    // 点击事件
    button.addEventListener('click', () => {
        window.scrollTo({
            top: 0,
            behavior: 'smooth'
        });
    });
    
    // 添加悬停效果
    button.addEventListener('mouseenter', () => {
        button.style.backgroundColor = 'var(--primary-dark)';
        button.style.transform = 'scale(1.1)';
    });
    
    button.addEventListener('mouseleave', () => {
        button.style.backgroundColor = 'var(--primary-color)';
        button.style.transform = 'scale(1)';
    });
}

/**
 * 性能优化：减少重绘
 */
function optimizeForPerformance() {
    // 为动画元素添加 will-change
    const animatedElements = document.querySelectorAll('.animate-on-scroll, .parallax, .counter');
    animatedElements.forEach(element => {
        element.style.willChange = 'transform, opacity';
    });
    
    // 使用 requestAnimationFrame 优化动画
    let ticking = false;
    
    window.addEventListener('scroll', () => {
        if (!ticking) {
            window.requestAnimationFrame(() => {
                // 执行滚动相关的动画
                ticking = false;
            });
            ticking = true;
        }
    });
    
    // 使用 transform 和 opacity 进行动画（GPU加速）
    console.log('性能优化已应用：使用GPU加速动画');
}

// DOM加载完成后初始化动画
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        initAnimations();
        addRippleEffectToButtons();
        initImageLoadingAnimations();
        initScrollToTopButton();
        optimizeForPerformance();
    });
} else {
    initAnimations();
    addRippleEffectToButtons();
    initImageLoadingAnimations();
    initScrollToTopButton();
    optimizeForPerformance();
}

// 导出函数
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initAnimations,
        showPageTransition,
        animateElement,
        createSkeletonPlaceholders,
        addRippleEffectToButtons
    };
}