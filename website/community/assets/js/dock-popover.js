document.addEventListener('DOMContentLoaded', () => {
    const trigger = document.getElementById('dockUserMenuBtn');
    const popover = document.getElementById('dockUserMenu');
    const logoutBtn = document.getElementById('logoutBtn');
    const deleteBtn = document.getElementById('deleteAccountBtn');
    const myPostCount = document.getElementById('myPostCount');

    // 获取用户文章数量
    async function fetchMyPostCount() {
        if (!myPostCount) return;
        try {
            const res = await fetch('api/auth.php?action=my-post-count');
            if (res.ok) {
                const data = await res.json();
                if (data.success) {
                    myPostCount.textContent = data.count;
                }
            }
        } catch (err) {
            console.error('Failed to fetch post count:', err);
        }
    }

    // 页面加载时获取文章数量
    fetchMyPostCount();

    if (trigger && popover) {
        // 点击图标切换面板
        trigger.addEventListener('click', (e) => {
            e.preventDefault();
            e.stopPropagation();

            const isActive = popover.classList.contains('active');
            if (isActive) {
                popover.classList.remove('active');
            } else {
                // 计算位置：在图标右侧
                const rect = trigger.getBoundingClientRect();
                // Dock 通常在左侧，我们定位在图标右边，稍微向上偏移一点居中
                popover.style.left = `${rect.right + 16}px`;
                popover.style.top = `${rect.top + 10}px`;
                popover.classList.add('active');
            }
        });

        // 点击外部关闭
        document.addEventListener('click', (e) => {
            if (!popover.contains(e.target) && !trigger.contains(e.target)) {
                popover.classList.remove('active');
            }
        });
        
        // 退出登录逻辑
        if (logoutBtn) {
            logoutBtn.addEventListener('click', async () => {
                try {
                    const originalText = logoutBtn.innerHTML;
                    logoutBtn.innerHTML = '<span class="spinner"></span> 退出中...';
                    logoutBtn.disabled = true;
                    
                    // 使用相对路径，因为 JS 可能在子目录中运行
                    // 注意：这里假设 api/auth.php 相对于当前页面路径可用
                    // 在 community/index.php 中，api/ 是同级目录
                    const res = await fetch('api/auth.php?action=logout');
                    
                    if (res.ok) {
                        // 退出成功，刷新页面
                        window.location.reload();
                    } else {
                        logoutBtn.innerHTML = originalText;
                        logoutBtn.disabled = false;
                        alert('退出失败，请重试');
                    }
                } catch (err) {
                    console.error('Logout error:', err);
                    logoutBtn.innerHTML = '退出失败';
                    logoutBtn.disabled = false;
                }
            });
        }

        // 注销账户逻辑
        if (deleteBtn) {
            deleteBtn.addEventListener('click', () => {
                if (confirm('确定要注销（永久删除）此账户吗？\n此操作不可撤销，所有数据将被清除。')) {
                    alert('该功能暂未开放，请联系管理员。');
                }
            });
        }
    }
});
