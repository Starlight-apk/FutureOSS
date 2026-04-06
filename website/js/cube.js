/**
 * 3D 交互立方体（requestAnimationFrame 驱动）
 * - 纯白正方体 + 青绿色发光边框，自动旋转
 * - 鼠标悬停某面时平滑过渡到该面正对用户，弹出对话框
 * - 鼠标离开 2 秒后平滑恢复旋转
 */
(function () {
    'use strict';

    const cube = document.getElementById('feature-cube');
    const tooltip = document.getElementById('cube-tooltip');
    if (!cube || !tooltip) return;

    const tooltipIcon = tooltip.querySelector('.cube-tooltip-icon');
    const tooltipTitle = tooltip.querySelector('.cube-tooltip-title');
    const tooltipDesc = tooltip.querySelector('.cube-tooltip-desc');
    const faces = cube.querySelectorAll('.cube-face');

    // 旋转状态
    let angleX = -20;
    let angleY = 0;
    let isSpinning = true;
    let resumeTimer = null;
    let currentFace = null;

    // 目标角度（悬停时设置）
    let targetX = null;
    let targetY = null;

    const SPEED_Y = 0.5;   // Y 轴每帧旋转速度
    const SPEED_X = 0.15;  // X 轴微动速度
    const LERP = 0.05;     // 平滑插值系数

    // 六个面的特性数据
    const faceData = {
        front:  { icon: '🧩', title: '一切皆为插件',   desc: '协议、中间件、通知渠道，所有功能均以插件形式加载' },
        back:   { icon: '🔄', title: '热插拔',         desc: '插件运行时加载与卸载，改完即生效，零编译' },
        right:  { icon: '🔗', title: '依赖自动解析',   desc: '拓扑排序 + 循环依赖检测，自动处理加载顺序' },
        left:   { icon: '🛡️', title: '熔断降级',        desc: '内置熔断器，支持 closed/open/half-open 状态切换' },
        top:    { icon: '📡', title: '事件驱动',       desc: '发布/订阅 + 通配符匹配 + RPC 桥接' },
        bottom: { icon: '📦', title: '统一存储',       desc: 'plugin-storage 提供隔离的文件读写入口' }
    };

    /**
     * 角度差（处理 360° 环绕，返回最短方向）
     */
    function angleDiff(from, to) {
        let diff = ((to - from) % 360 + 540) % 360 - 180;
        return diff;
    }

    /**
     * 动画循环
     */
    function animate() {
        if (targetX !== null && targetY !== null) {
            // 平滑过渡到目标角度
            const diffX = angleDiff(angleX, targetX);
            const diffY = angleDiff(angleY, targetY);

            if (Math.abs(diffX) < 0.2 && Math.abs(diffY) < 0.2) {
                angleX = targetX;
                angleY = targetY;
                // 到达目标后停止插值，保持静止
                targetX = null;
                targetY = null;
            } else {
                angleX += diffX * LERP;
                angleY += diffY * LERP;
            }
        } else if (isSpinning) {
            // 自动旋转：Y 轴匀速 + X 轴微动
            angleY += SPEED_Y;
            angleX = -20 + Math.sin(Date.now() * 0.001) * 8;
        }

        cube.style.transform = `rotateX(${angleX}deg) rotateY(${angleY}deg)`;
        requestAnimationFrame(animate);
    }

    /**
     * 计算某个面的目标角度（Y 轴自动选最近的对齐角度，避免跳帧）
     */
    function calcFaceTarget(baseX, baseY) {
        // Y 轴：找到距离当前 angleY 最近的对齐角度（baseY + n*360）
        const n = Math.round((angleY - baseY) / 360);
        const snappedY = baseY + n * 360;
        return { x: baseX, y: snappedY };
    }

    /**
     * 暂停旋转，显示对话框
     */
    function pauseAndShow(faceName) {
        if (currentFace === faceName) return;
        currentFace = faceName;

        // 清除恢复定时器
        if (resumeTimer) {
            clearTimeout(resumeTimer);
            resumeTimer = null;
        }

        // 计算目标角度（Y 轴自动对齐最近角度，避免跳帧）
        const faceBaseTargets = {
            front:  { x: -20, y: 0 },
            back:   { x: -20, y: 180 },
            right:  { x: -20, y: -90 },
            left:   { x: -20, y: 90 },
            top:    { x: -90, y: 0 },
            bottom: { x: 90, y: 0 }
        };

        const base = faceBaseTargets[faceName];
        if (base) {
            const snapped = calcFaceTarget(base.x, base.y);
            targetX = snapped.x;
            targetY = snapped.y;
        }

        isSpinning = false;

        // 填充并显示对话框
        const data = faceData[faceName];
        if (!data) return;

        tooltipIcon.textContent = data.icon;
        tooltipTitle.textContent = data.title;
        tooltipDesc.textContent = data.desc;
        void tooltip.offsetWidth;
        tooltip.classList.add('is-visible');
    }

    /**
     * 隐藏对话框
     */
    function hideTooltip() {
        currentFace = null;
        tooltip.classList.remove('is-visible');
    }

    /**
     * 恢复旋转
     */
    function resumeSpin() {
        hideTooltip();
        targetX = null;
        targetY = null;
        isSpinning = true;
    }

    // 为每个面绑定 mouseenter
    faces.forEach(function (face) {
        face.addEventListener('mouseenter', function () {
            const faceName = face.getAttribute('data-face');
            pauseAndShow(faceName);
        });

        face.addEventListener('touchstart', function () {
            const faceName = face.getAttribute('data-face');
            pauseAndShow(faceName);
        }, { passive: true });
    });

    // 整个场景 mouseleave → 2 秒后恢复（用 scene 而非 cube，避免子元素事件干扰）
    const scene = cube.parentElement;
    if (scene) {
        scene.addEventListener('mouseleave', function () {
            hideTooltip();
            if (resumeTimer) clearTimeout(resumeTimer);
            resumeTimer = setTimeout(function () {
                resumeSpin();
            }, 2000);
        });
    }

    // 启动动画
    animate();

})();
