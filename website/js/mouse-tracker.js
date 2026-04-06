// 通用鼠标位置追踪器
// 提供全局鼠标位置状态，供其他模块使用

class MouseTracker {
    constructor() {
        this.x = 0;          // 原始 X (0 ~ window.innerWidth)
        this.y = 0;          // 原始 Y (0 ~ window.innerHeight)
        this.normalizedX = 0; // 归一化 X (-1 ~ 1)
        this.normalizedY = 0; // 归一化 Y (-1 ~ 1)
        this.smoothX = 0;    // 平滑后的 X
        this.smoothY = 0;    // 平滑后的 Y
        this.listeners = [];
        this.smoothing = 0.1; // 平滑系数 (0~1，越小越平滑)
        this.isInside = false;
        
        this._init();
    }

    _init() {
        document.addEventListener('mousemove', (e) => {
            this.x = e.clientX;
            this.y = e.clientY;
            this.normalizedX = (e.clientX / window.innerWidth) * 2 - 1;
            this.normalizedY = (e.clientY / window.innerHeight) * 2 - 1;
            this.isInside = true;

            this._notify();
        });

        document.addEventListener('mouseleave', () => {
            this.isInside = false;
        });

        // 平滑动画循环
        this._animate();
    }

    _animate() {
        // 平滑插值
        this.smoothX += (this.normalizedX - this.smoothX) * this.smoothing;
        this.smoothY += (this.normalizedY - this.smoothY) * this.smoothing;

        requestAnimationFrame(() => this._animate());
    }

    _notify() {
        this.listeners.forEach(cb => {
            cb({
                x: this.x,
                y: this.y,
                normalizedX: this.normalizedX,
                normalizedY: this.normalizedY,
                smoothX: this.smoothX,
                smoothY: this.smoothY,
                isInside: this.isInside
            });
        });
    }

    // 添加监听器
    onUpdate(callback) {
        this.listeners.push(callback);
    }

    // 移除监听器
    offUpdate(callback) {
        const index = this.listeners.indexOf(callback);
        if (index > -1) this.listeners.splice(index, 1);
    }

    // 设置平滑系数
    setSmoothing(value) {
        this.smoothing = Math.max(0, Math.min(1, value));
    }

    // 获取当前平滑值
    getSmooth() {
        return { x: this.smoothX, y: this.smoothY };
    }
}

// 导出全局实例
window.mouseTracker = new MouseTracker();
