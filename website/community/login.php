<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>登录 - OSS Community</title>
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
                            <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                        </svg>
                    </div>
                    <h1 class="auth-title">欢迎回来</h1>
                    <p class="auth-subtitle">登录到你的 OSS Community 账户</p>
                </div>

                <form id="loginForm" class="auth-form">
                    <div class="form-group">
                        <label for="username" class="form-label">用户名或邮箱</label>
                        <div class="input-wrapper">
                            <svg class="input-icon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                <path stroke-linecap="round" stroke-linejoin="round" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
                            </svg>
                            <input 
                                type="text" 
                                id="username" 
                                name="username" 
                                class="form-input" 
                                placeholder="输入用户名或邮箱"
                                required
                                autocomplete="username"
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
                                placeholder="输入密码"
                                required
                                autocomplete="current-password"
                            />
                            <button type="button" class="toggle-password" onclick="togglePassword()">
                                <svg id="eyeIcon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"/>
                                    <path stroke-linecap="round" stroke-linejoin="round" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"/>
                                </svg>
                            </button>
                        </div>
                    </div>

                    <div class="form-options">
                        <label class="checkbox-label">
                            <input type="checkbox" id="remember" name="remember" />
                            <span class="checkbox-text">记住我</span>
                        </label>
                        <a href="#" class="forgot-link">忘记密码？</a>
                    </div>

                    <div id="errorMessage" class="alert alert-error" style="display: none;"></div>
                    <div id="successMessage" class="alert alert-success" style="display: none;"></div>

                    <button type="submit" class="btn btn-primary btn-auth" id="submitBtn">
                        <span class="btn-text">登录</span>
                        <svg class="btn-spinner" style="display: none;" viewBox="0 0 24 24" fill="none">
                            <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-linecap="round" opacity="0.25"/>
                            <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" fill="currentColor" opacity="0.75"/>
                        </svg>
                    </button>
                </form>

                <div class="auth-footer">
                    <p>还没有账户？<a href="register.php" class="auth-link">立即注册</a></p>
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
