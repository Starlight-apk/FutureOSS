/**
 * OSS Community 认证页面 JS
 * 处理登录/注册表单提交
 */

// 切换密码可见性
function togglePassword(fieldId = 'password') {
    const input = document.getElementById(fieldId);
    const icon = document.getElementById(`eyeIcon-${fieldId}`) || document.getElementById('eyeIcon');
    
    if (input.type === 'password') {
        input.type = 'text';
        icon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l3.59 3.59m0 0A9.953 9.953 0 0112 5c4.478 0 8.268 2.943 9.543 7a10.025 10.025 0 01-4.132 5.411m0 0L21 21"/>
        `;
    } else {
        input.type = 'password';
        icon.innerHTML = `
            <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
            <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
        `;
    }
}

// 显示错误消息
function showError(message) {
    const errorEl = document.getElementById('errorMessage');
    const successEl = document.getElementById('successMessage');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    if (successEl) {
        successEl.style.display = 'none';
    }
}

// 显示成功消息
function showSuccess(message) {
    const successEl = document.getElementById('successMessage');
    const errorEl = document.getElementById('errorMessage');
    if (successEl) {
        successEl.textContent = message;
        successEl.style.display = 'block';
    }
    if (errorEl) {
        errorEl.style.display = 'none';
    }
}

// 隐藏消息
function hideMessages() {
    const errorEl = document.getElementById('errorMessage');
    const successEl = document.getElementById('successMessage');
    if (errorEl) errorEl.style.display = 'none';
    if (successEl) successEl.style.display = 'none';
}

// 设置按钮加载状态
function setButtonLoading(loading) {
    const btn = document.getElementById('submitBtn');
    const text = btn.querySelector('.btn-text');
    const spinner = btn.querySelector('.btn-spinner');
    
    if (loading) {
        btn.disabled = true;
        text.style.display = 'none';
        spinner.style.display = 'block';
    } else {
        btn.disabled = false;
        text.style.display = 'inline';
        spinner.style.display = 'none';
    }
}

// 登录表单
const loginForm = document.getElementById('loginForm');
if (loginForm) {
    loginForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessages();
        setButtonLoading(true);

        const formData = {
            username: document.getElementById('username').value.trim(),
            password: document.getElementById('password').value,
            remember: document.getElementById('remember').checked
        };

        try {
            const response = await fetch('api/auth.php?action=login', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                showSuccess('登录成功！正在跳转...');
                setTimeout(() => {
                    window.location.href = 'index.php';
                }, 1000);
            } else {
                showError(result.message || '登录失败，请检查用户名和密码');
            }
        } catch (error) {
            showError('网络错误，请稍后重试');
        } finally {
            setButtonLoading(false);
        }
    });
}

// 注册表单
const registerForm = document.getElementById('registerForm');
if (registerForm) {
    registerForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hideMessages();
        setButtonLoading(true);

        const password = document.getElementById('password').value;
        const confirmPassword = document.getElementById('confirmPassword').value;

        // 前端验证
        if (password !== confirmPassword) {
            showError('两次输入的密码不一致');
            setButtonLoading(false);
            return;
        }

        if (password.length < 6) {
            showError('密码长度至少 6 个字符');
            setButtonLoading(false);
            return;
        }

        const formData = {
            username: document.getElementById('username').value.trim(),
            email: document.getElementById('email').value.trim(),
            password: password
        };

        try {
            const response = await fetch('api/auth.php?action=register', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                showSuccess('注册成功！正在跳转到登录页...');
                setTimeout(() => {
                    window.location.href = 'login.php';
                }, 1500);
            } else {
                showError(result.message || '注册失败，请稍后重试');
            }
        } catch (error) {
            showError('网络错误，请稍后重试');
        } finally {
            setButtonLoading(false);
        }
    });
}
