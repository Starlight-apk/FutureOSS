// 动画入口
gsap.registerPlugin(ScrollTrigger);

// 页面元素入场
gsap.utils.toArray('.feature-card, .step-card, .arch-layer, .arch-plugin').forEach((el, i) => {
    gsap.fromTo(el,
        { y: 40, opacity: 0 },
        {
            y: 0, opacity: 1, duration: 0.6,
            ease: 'power3.out',
            scrollTrigger: { trigger: el, start: 'top 85%' },
            delay: (i % 4) * 0.1
        }
    );
});

// Hero 动画
if (document.querySelector('.hero-content')) {
    gsap.fromTo('.hero-content > *',
        { y: 50, opacity: 0 },
        { y: 0, opacity: 1, duration: 0.8, stagger: 0.1, ease: 'power3.out', delay: 0.2 }
    );
    gsap.fromTo('.hero-visual',
        { scale: 0.85, opacity: 0 },
        { scale: 1, opacity: 1, duration: 1, ease: 'back.out(1.4)', delay: 0.4 }
    );
}

// 平滑滚动
document.querySelectorAll('a[href^="#"]').forEach(a => {
    a.addEventListener('click', e => {
        const target = document.querySelector(a.getAttribute('href'));
        if (target) { e.preventDefault(); target.scrollIntoView({ behavior: 'smooth' }); }
    });
});
