<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>注册 - OSS Community</title>
    <link rel="preconnect" href="https://fonts.googleapis.com" />
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&family=JetBrains+Mono:wght@400;500;600&display=swap" rel="stylesheet" />
    <link rel="stylesheet" href="../css/main.css" />
    <link rel="stylesheet" href="../css/dock.css" />
    <link rel="stylesheet" href="assets/css/auth.css" />
</head>
<body>
    <canvas id="particles"></canvas>

    <?php require_once 'includes/dock.php'; ?>

    <main class="auth-page">
        <div class="auth-container">
            <div class="auth-card">
                <div class="auth-header">
                    <div class="auth-logo">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                            <path stroke-linecap="round" stroke-linejoin="round" d="M18 9v3m0 0v3m0-3h3m-3 0h-3m-2-5a4 4 0 11-8 0 4 4 0 018 0zM3 20a6 6 0 0112 0v1H3v-1z"/>
                        </svg>
                    </div>
                    <h1 class="auth-title">创建账户</h1>
                    <p class="auth-subtitle">加入 OSS Community 开发者社区</p>
                </div>

                <form id="registerForm" class="auth-form">
                    <div class="form-group">
                        <label for="username" class="form-label">用户名</label>
                        <div class="input-wrapper">
                            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                            </svg>
                            <input 
                                type="text" 
                                id="username" 
                                name="username" 
                                class="form-input" 
                                placeholder="3-50 个字符，字母数字或下划线"
                                required
                                autocomplete="username"
                                pattern="[a-zA-Z0-9_]{3,50}"
                            />
                        </div>
                        <span class="input-hint">只能包含字母、数字和下划线</span>
                    </div>

                    <div class="form-group">
                        <label for="email" class="form-label">邮箱</label>
                        <div class="input-wrapper">
                            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/>
                            </svg>
                            <input 
                                type="email" 
                                id="email" 
                                name="email" 
                                class="form-input" 
                                placeholder="your@email.com"
                                required
                                autocomplete="email"
                            />
                        </div>
                    </div>

                    <div class="form-group">
                        <label for="password" class="form-label">密码</label>
                        <div class="input-wrapper">
                            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"/>
                            </svg>
                            <input 
                                type="password" 
                                id="password" 
                                name="password" 
                                class="form-input" 
                                placeholder="至少 6 个字符"
                                required
                                autocomplete="new-password"
                                minlength="6"
                            />
                            <button type="button" class="toggle-password" onclick="togglePassword('password')">
                                <svg id="eyeIcon-password" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                                </svg>
                            </button>
                        </div>
                        <span class="input-hint">至少 6 个字符</span>
                    </div>

                    <div class="form-group">
                        <label for="confirmPassword" class="form-label">确认密码</label>
                        <div class="input-wrapper">
                            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                            </svg>
                            <input 
                                type="password" 
                                id="confirmPassword" 
                                name="confirmPassword" 
                                class="form-input" 
                                placeholder="再次输入密码"
                                required
                                autocomplete="new-password"
                            />
                        </div>
                    </div>

                    <div id="errorMessage" class="alert alert-error" style="display: none;"></div>
                    <div id="successMessage" class="alert alert-success" style="display: none;"></div>

                    <button type="submit" class="btn btn-primary btn-auth" id="submitBtn">
                        <span class="btn-text">注册</span>
                        <svg class="btn-spinner" style="display: none;" viewBox="0 0 24 24" fill="none">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-linecap="round" opacity="0.25"/>
                            <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" fill="currentColor" opacity="0.75"/>
                        </svg>
                    </button>
                </form>

                <div class="auth-footer">
                    <p>已有账户？<a href="login.php" class="auth-link">立即登录</a></p>
                </div>
            </div>

            <div class="auth-decoration">
                <div class="deco-circle deco-circle-1"></div>
                <div class="deco-circle deco-circle-2"></div>
                <div class="deco-circle deco-circle-3"></div>
            </div>
        </div>
    </main>

    <script src="../js/particles.js"></script>
    <script src="assets/js/auth.js"></script>
</body>
</html>
