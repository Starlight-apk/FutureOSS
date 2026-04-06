// 主应用入口
document.addEventListener('DOMContentLoaded', () => {
    // 平滑滚动到锚点
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            e.preventDefault();
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });

    console.log('%c Future OSS ', 'background: linear-gradient(135deg, #06b6d4, #3b82f6); color: #fff; padding: 8px 16px; border-radius: 4px; font-weight: bold;');
    console.log('%c一切皆为插件的开发者工具运行时框架', 'color: #9ca3af; font-size: 14px;');
});
