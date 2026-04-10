// 统一视差追踪器
// 自动检测并使用最佳输入源：鼠标 > 陀螺仪 > 触摸滑动

class ParallaxTracker {
    constructor() {
        this.smoothX = 0;
        this.smoothY = 0;
        this.targetX = 0;
        this.targetY = 0;
        this.elements = [];
        this.listeners = [];
        this.maxMove = 100; // 最大移动像素
        this.smoothing = 0.08; // 平滑系数
        this.isReducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
        this.activeSource = null; // 'mouse' | 'gyro' | 'touch'
        this.rafId = null;

        if (this.isReducedMotion) {
            console.log('[Parallax] 用户偏好减少动画，已跳过');
            return;
        }

        this._init();
    }

    _init() {
        // 自动检测文档页面
        const docsContent = document.querySelector('.docs-content');
        if (docsContent && !docsContent.hasAttribute('data-parallax-speed')) {
            docsContent.setAttribute('data-parallax-speed', '0.5');
        }

        // 自动检测首页
        const heroContent = document.querySelector('.hero-content');
        if (heroContent && !heroContent.hasAttribute('data-parallax-speed')) {
            heroContent.setAttribute('data-parallax-speed', '0.5');
        }

        const heroSection = document.querySelector('.page-hero');
        if (heroSection && !heroSection.hasAttribute('data-parallax-speed')) {
            heroSection.setAttribute('data-parallax-speed', '0.5');
        }

        // 查找视差元素
        document.querySelectorAll('[data-parallax-speed]').forEach(el => {
            const speed = parseFloat(el.dataset.parallaxSpeed) || 0.1;
            this.elements.push({ el, speed });
            el.style.willChange = 'transform';
        });

        if (this.elements.length === 0) return;

        const isMobile = this._isMobileDevice();

        // 按优先级尝试输入源
        if (isMobile) {
            // 移动端优先使用陀螺仪
            if (this._initGyroscope()) {
                this.activeSource = 'gyro';
                console.log('[Parallax] 使用陀螺仪输入');
            } else {
                // 陀螺仪不可用时使用触摸滑动
                this._initTouchFallback();
                this.activeSource = 'touch';
                console.log('[Parallax] 使用触摸滑动输入');
            }
        } else {
            // 桌面端使用鼠标
            this._initMouse();
            this.activeSource = 'mouse';
            console.log('[Parallax] 使用鼠标输入');
        }

        // 启动动画循环
        this._animate();
        console.log(`[Parallax] 已初始化 ${this.elements.length} 个元素，输入源: ${this.activeSource}`);
    }

    // 检测是否为移动设备
    _isMobileDevice() {
        return /Android|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent)
            || (navigator.maxTouchPoints && navigator.maxTouchPoints > 2);
    }

    // ── 鼠标输入 ──
    _initMouse() {
        // 支持鼠标和触摸指针的设备
        const hasFinePointer = window.matchMedia('(pointer: fine)').matches;
        
        document.addEventListener('mousemove', (e) => {
            this.targetX = (e.clientX / window.innerWidth) * 2 - 1;
            this.targetY = (e.clientY / window.innerHeight) * 2 - 1;
        });

        // 即使没有 fine pointer 也返回 true，让鼠标事件始终生效
        return true;
    }

    // ── 陀螺仪输入 ──
    _initGyroscope() {
        if (!window.DeviceOrientationEvent) {
            console.log('[Parallax] 设备不支持 DeviceOrientationEvent');
            return false;
        }

        let hasFired = false;
        const handler = (e) => {
            // gamma: 左右倾斜 (-90 ~ 90)
            // beta:  前后倾斜 (-180 ~ 180)
            if (e.gamma === null && e.beta === null) return;

            if (!hasFired) {
                hasFired = true;
                console.log('[Parallax] 陀螺仪数据已就绪');
            }

            // 归一化到 -1 ~ 1（限制在 ±45 度范围内）
            this.targetX = Math.max(-1, Math.min(1, e.gamma / 45));
            this.targetY = Math.max(-1, Math.min(1, (e.beta - 45) / 45)); // 减去 45° 自然持握角度
        };

        // iOS 13+ 需要用户授权
        if (typeof DeviceOrientationEvent.requestPermission === 'function') {
            // 添加点击按钮请求权限的提示
            this._addGyroPermissionButton(handler);
            return false; // 等待用户授权后再启用
        }

        // Android 和其他设备直接监听
        window.addEventListener('deviceorientation', handler);
        console.log('[Parallax] 陀螺仪监听已启动（无需权限）');
        return true;
    }

    _addGyroPermissionButton(handler) {
        // iOS 设备需要用户交互才能请求陀螺仪权限
        // 检查是否已经显示过权限按钮
        if (document.getElementById('gyro-permission-btn')) {
            return;
        }

        const btn = document.createElement('div');
        btn.id = 'gyro-permission-btn';
        btn.innerHTML = `
            <div class="gyro-permission-overlay">
                <div class="gyro-permission-card">
                    <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" width="32" height="32">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 18h.01M8 21h8a2 2 0 002-2V5a2 2 0 00-2-2H8a2 2 0 00-2 2v14a2 2 0 002 2z"/>
                    </svg>
                    <p>开启陀螺仪视差</p>
                    <span>移动设备时页面会跟随滚动</span>
                    <button>允许</button>
                </div>
            </div>
        `;
        document.body.appendChild(btn);

        btn.querySelector('button').addEventListener('click', async () => {
            try {
                const permission = await DeviceOrientationEvent.requestPermission();
                if (permission === 'granted') {
                    window.addEventListener('deviceorientation', handler);
                    this.activeSource = 'gyro';
                    console.log('[Parallax] 陀螺仪权限已授予');
                    btn.remove();
                } else {
                    console.warn('[Parallax] 陀螺仪权限被拒绝');
                    btn.remove();
                    // 权限被拒绝后使用触摸滑动
                    this._initTouchFallback();
                    this.activeSource = 'touch';
                }
            } catch (err) {
                console.warn('[Parallax] 陀螺仪权限请求失败', err);
                btn.remove();
                // 出错时使用触摸滑动
                this._initTouchFallback();
                this.activeSource = 'touch';
            }
        });

        // 点击遮罩关闭
        btn.querySelector('.gyro-permission-overlay').addEventListener('click', () => {
            btn.remove();
            // 用户关闭后使用触摸滑动
            this._initTouchFallback();
            this.activeSource = 'touch';
        });
    }

    // ── 触摸滑动输入 ──
    _initTouchFallback() {
        let startX = 0, startY = 0;
        let currentX = 0, currentY = 0;
        let isTouching = false;

        document.addEventListener('touchstart', (e) => {
            isTouching = true;
            startX = e.touches[0].clientX;
            startY = e.touches[0].clientY;
            currentX = startX;
            currentY = startY;
        }, { passive: true });

        document.addEventListener('touchmove', (e) => {
            if (!isTouching) return;
            currentX = e.touches[0].clientX;
            currentY = e.touches[0].clientY;

            // 计算相对于起始点的偏移
            const deltaX = (currentX - startX) / window.innerWidth;
            const deltaY = (currentY - startY) / window.innerHeight;

            this.targetX = Math.max(-1, Math.min(1, deltaX * 4)); // 放大灵敏度
            this.targetY = Math.max(-1, Math.min(1, deltaY * 4));
        }, { passive: true });

        document.addEventListener('touchend', () => {
            isTouching = false;
            // 缓慢回归中心
            const resetInterval = setInterval(() => {
                this.targetX *= 0.9;
                this.targetY *= 0.9;
                if (Math.abs(this.targetX) < 0.01 && Math.abs(this.targetY) < 0.01) {
                    this.targetX = 0;
                    this.targetY = 0;
                    clearInterval(resetInterval);
                }
            }, 16);
        }, { passive: true });
    }

    // ── 动画循环 ──
    _animate() {
        // 平滑插值（指数移动平均）
        this.smoothX += (this.targetX - this.smoothX) * this.smoothing;
        this.smoothY += (this.targetY - this.smoothY) * this.smoothing;

        // 应用变换
        this.elements.forEach(({ el, speed }) => {
            const moveX = -this.smoothX * speed * this.maxMove;
            const moveY = -this.smoothY * speed * this.maxMove;
            el.style.transform = `translate3d(${moveX}px, ${moveY}px, 0)`;
        });

        requestAnimationFrame(() => this._animate());
    }

    // 添加监听器（供其他模块使用）
    onUpdate(callback) {
        this.listeners.push(callback);
    }

    // 获取当前平滑值
    getSmooth() {
        return { x: this.smoothX, y: this.smoothY };
    }
}

// 导出全局实例
window.parallaxTracker = new ParallaxTracker();
