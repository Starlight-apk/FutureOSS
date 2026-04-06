// 粒子背景动画
const canvas = document.getElementById('particles');
const ctx = canvas.getContext('2d');

let width, height, particles = [];

function resize() {
    width = canvas.width = window.innerWidth;
    height = canvas.height = window.innerHeight;
}

class Particle {
    constructor() {
        this.reset();
    }

    reset() {
        this.x = Math.random() * width;
        this.y = Math.random() * height;
        this.size = 1 + Math.random() * 2;
        this.speedX = -0.2 + Math.random() * 0.4;
        this.speedY = -0.2 + Math.random() * 0.4;
        this.opacity = 0.1 + Math.random() * 0.3;
    }

    update() {
        this.x += this.speedX;
        this.y += this.speedY;

        if (this.x < 0 || this.x > width || this.y < 0 || this.y > height) {
            this.reset();
        }
    }

    draw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(6, 182, 212, ${this.opacity})`;
        ctx.fill();
    }
}

function init() {
    resize();
    const count = Math.min(80, Math.floor((width * height) / 15000));
    particles = Array.from({ length: count }, () => new Particle());
}

function animate() {
    ctx.clearRect(0, 0, width, height);

    // 绘制连线
    for (let i = 0; i < particles.length; i++) {
        for (let j = i + 1; j < particles.length; j++) {
            const dx = particles[i].x - particles[j].x;
            const dy = particles[i].y - particles[j].y;
            const dist = Math.sqrt(dx * dx + dy * dy);

            if (dist < 120) {
                ctx.beginPath();
                ctx.moveTo(particles[i].x, particles[i].y);
                ctx.lineTo(particles[j].x, particles[j].y);
                ctx.strokeStyle = `rgba(6, 182, 212, ${0.05 * (1 - dist / 120)})`;
                ctx.lineWidth = 0.5;
                ctx.stroke();
            }
        }
    }

    particles.forEach(p => {
        p.update();
        p.draw();
    });

    requestAnimationFrame(animate);
}

window.addEventListener('resize', () => {
    resize();
});

init();
animate();
