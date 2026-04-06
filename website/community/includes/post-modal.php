<!-- 发帖模态框 -->
<div id="createPostModal" class="modal">
    <div class="modal-backdrop" onclick="closeCreateModal()"></div>
    <div class="modal-content">
        <div class="modal-header">
            <h2 id="modalTitle">发布新帖</h2>
            <button class="modal-close" onclick="closeCreateModal()">
                <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <path stroke-linecap="round" stroke-linejoin="round" d="M6 18L18 6M6 6l12 12"/>
                </svg>
            </button>
        </div>
        
        <form id="createPostForm" class="modal-form">
            <input type="hidden" id="editPostId" value="" />
            
            <div class="form-group">
                <label for="postTitle" class="form-label">标题</label>
                <input 
                    type="text" 
                    id="postTitle" 
                    name="title" 
                    class="form-input" 
                    placeholder="请输入帖子标题"
                    required
                    minlength="5"
                    maxlength="200"
                />
                <span class="input-hint"><span id="titleCount">0</span>/200</span>
            </div>

            <div class="form-group">
                <label for="postCategory" class="form-label">分类</label>
                <select id="postCategory" name="category_id" class="form-input" required>
                    <option value="">选择分类</option>
                </select>
            </div>

            <div class="form-group">
                <label for="postContent" class="form-label">内容</label>
                <textarea 
                    id="postContent" 
                    name="content" 
                    class="form-input form-textarea" 
                    placeholder="请输入帖子内容..."
                    required
                    minlength="10"
                    rows="10"
                ></textarea>
                <span class="input-hint"><span id="contentCount">0</span> 个字符</span>
            </div>

            <div class="form-group">
                <label for="postTags" class="form-label">标签</label>
                <input 
                    type="text" 
                    id="postTags" 
                    name="tags" 
                    class="form-input" 
                    placeholder="输入标签，用逗号分隔"
                />
                <span class="input-hint">例如：Go, 插件, 安装</span>
            </div>

            <div id="postErrorMessage" class="alert alert-error" style="display: none;"></div>
            <div id="postSuccessMessage" class="alert alert-success" style="display: none;"></div>

            <div class="modal-actions">
                <button type="button" class="btn btn-secondary" onclick="closeCreateModal()">取消</button>
                <button type="submit" class="btn btn-primary" id="postSubmitBtn">
                    <span class="btn-text">发布</span>
                    <svg class="btn-spinner" style="display: none;" viewBox="0 0 24 24" fill="none">
                        <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-linecap="round" opacity="0.25"/>
                        <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" fill="currentColor" opacity="0.75"/>
                    </svg>
                </button>
            </div>
        </form>
    </div>
</div>

<style>
/* 模态框样式 */
.modal {
    display: none;
    position: fixed;
    inset: 0;
    z-index: 1000;
}

.modal.active {
    display: flex;
    align-items: center;
    justify-content: center;
}

.modal-backdrop {
    position: absolute;
    inset: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
}

.modal-content {
    position: relative;
    background: rgba(15, 23, 42, 0.95);
    border: 1px solid rgba(99, 102, 241, 0.3);
    border-radius: 16px;
    padding: 32px;
    max-width: 700px;
    width: 90%;
    max-height: 90vh;
    overflow-y: auto;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.5);
    animation: modalSlideIn 0.3s ease-out;
}

@keyframes modalSlideIn {
    from {
        opacity: 0;
        transform: translateY(-30px) scale(0.95);
    }
    to {
        opacity: 1;
        transform: translateY(0) scale(1);
    }
}

.modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 24px;
    padding-bottom: 16px;
    border-bottom: 1px solid rgba(99, 102, 241, 0.2);
}

.modal-header h2 {
    font-size: 24px;
    font-weight: 700;
    background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.modal-close {
    background: none;
    border: none;
    padding: 8px;
    cursor: pointer;
    color: #94a3b8;
    transition: color 0.2s;
}

.modal-close:hover {
    color: #e2e8f0;
}

.modal-close svg {
    width: 24px;
    height: 24px;
}

.modal-form {
    display: flex;
    flex-direction: column;
    gap: 20px;
}

.form-textarea {
    resize: vertical;
    min-height: 200px;
    font-family: 'Inter', monospace;
}

.modal-actions {
    display: flex;
    gap: 12px;
    justify-content: flex-end;
    margin-top: 8px;
}

.btn {
    padding: 10px 20px;
    border-radius: 8px;
    font-size: 14px;
    font-weight: 600;
    cursor: pointer;
    border: none;
    transition: all 0.2s;
    display: flex;
    align-items: center;
    gap: 8px;
}

.btn-secondary {
    background: rgba(100, 116, 139, 0.2);
    color: #94a3b8;
    border: 1px solid rgba(100, 116, 139, 0.3);
}

.btn-secondary:hover {
    background: rgba(100, 116, 139, 0.3);
    color: #e2e8f0;
}

.btn-primary {
    background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
    color: white;
    box-shadow: 0 4px 12px rgba(99, 102, 241, 0.3);
}

.btn-primary:hover {
    box-shadow: 0 8px 24px rgba(99, 102, 241, 0.4);
    transform: translateY(-2px);
}

.btn-spinner {
    width: 16px;
    height: 16px;
    animation: spin 1s linear infinite;
}

@keyframes spin {
    to { transform: rotate(360deg); }
}

.alert {
    padding: 12px 16px;
    border-radius: 8px;
    font-size: 14px;
}

.alert-error {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.3);
    color: #fca5a5;
}

.alert-success {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.3);
    color: #86efac;
}

.form-input {
    width: 100%;
    padding: 12px 14px;
    background: rgba(30, 41, 59, 0.6);
    border: 1px solid rgba(99, 102, 241, 0.2);
    border-radius: 8px;
    color: #e2e8f0;
    font-size: 14px;
    transition: all 0.2s;
}

.form-input:focus {
    outline: none;
    border-color: #6366f1;
    background: rgba(30, 41, 59, 0.8);
    box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.1);
}

.form-label {
    font-size: 14px;
    font-weight: 500;
    color: #e2e8f0;
    margin-bottom: 8px;
    display: block;
}

.input-hint {
    font-size: 12px;
    color: #64748b;
    margin-top: 4px;
    display: block;
}

/* 响应式 */
@media (max-width: 768px) {
    .modal-content {
        padding: 24px 20px;
    }

    .modal-actions {
        flex-direction: column-reverse;
    }

    .modal-actions .btn {
        width: 100%;
        justify-content: center;
    }
}
</style>

<script>
// 发帖模态框控制 - 暴露到全局
window.showCreateModal = function() {
    // 检查登录状态
    fetch('api/auth.php?action=check')
        .then(res => res.json())
        .then(data => {
            if (!data.logged_in) {
                window.location.href = 'login.php';
                return;
            }
            
            // 加载分类
            loadCategoriesForForm();
            
            // 重置表单
            resetPostForm();
            
            // 显示模态框
            document.getElementById('createPostModal').classList.add('active');
        })
        .catch(err => {
            console.error('检查登录状态失败:', err);
        });
};

function closeCreateModal() {
    document.getElementById('createPostModal').classList.remove('active');
}

function resetPostForm() {
    isEditing = false;
    document.getElementById('modalTitle').textContent = '发布新帖';
    document.getElementById('editPostId').value = '';
    document.getElementById('createPostForm').reset();
    document.getElementById('titleCount').textContent = '0';
    document.getElementById('contentCount').textContent = '0';
    hidePostMessages();
}

function loadCategoriesForForm() {
    fetch('./api/index.php?action=categories')
        .then(res => res.json())
        .then(data => {
            const select = document.getElementById('postCategory');
            select.innerHTML = '<option value="">选择分类</option>';
            data.categories.forEach(cat => {
                const option = document.createElement('option');
                option.value = cat.id;
                option.textContent = cat.name;
                select.appendChild(option);
            });
        });
}

// 字符计数
document.addEventListener('DOMContentLoaded', () => {
    const titleInput = document.getElementById('postTitle');
    const contentInput = document.getElementById('postContent');
    
    if (titleInput) {
        titleInput.addEventListener('input', () => {
            document.getElementById('titleCount').textContent = titleInput.value.length;
        });
    }
    
    if (contentInput) {
        contentInput.addEventListener('input', () => {
            document.getElementById('contentCount').textContent = contentInput.value.length;
        });
    }
});

// 表单提交
const createPostForm = document.getElementById('createPostForm');
if (createPostForm) {
    createPostForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        hidePostMessages();
        setPostButtonLoading(true);

        const postId = document.getElementById('editPostId').value;
        const title = document.getElementById('postTitle').value.trim();
        const content = document.getElementById('postContent').value.trim();
        const categoryId = document.getElementById('postCategory').value;
        const tagsStr = document.getElementById('postTags').value.trim();
        const tags = tagsStr ? tagsStr.split(/[,，]/).map(t => t.trim()).filter(t => t) : [];

        const formData = {
            title: title,
            content: content,
            category_id: categoryId,
            tags: tags
        };

        if (isEditing && postId) {
            formData.id = parseInt(postId);
        }

        const action = isEditing ? 'update' : 'create';
        const url = `api/posts.php?action=${action}`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });

            const result = await response.json();

            if (result.success) {
                showPostSuccess(isEditing ? '更新成功！' : '发帖成功！正在跳转...');
                setTimeout(() => {
                    closeCreateModal();
                    if (!isEditing) {
                        window.location.href = `post.php?id=${result.post_id}`;
                    } else {
                        window.location.reload();
                    }
                }, 1000);
            } else {
                showPostError(result.message || '操作失败');
            }
        } catch (error) {
            showPostError('网络错误，请稍后重试');
        } finally {
            setPostButtonLoading(false);
        }
    });
}

function showPostError(message) {
    const errorEl = document.getElementById('postErrorMessage');
    const successEl = document.getElementById('postSuccessMessage');
    if (errorEl) {
        errorEl.textContent = message;
        errorEl.style.display = 'block';
    }
    if (successEl) successEl.style.display = 'none';
}

function showPostSuccess(message) {
    const successEl = document.getElementById('postSuccessMessage');
    const errorEl = document.getElementById('postErrorMessage');
    if (successEl) {
        successEl.textContent = message;
        successEl.style.display = 'block';
    }
    if (errorEl) errorEl.style.display = 'none';
}

function hidePostMessages() {
    const errorEl = document.getElementById('postErrorMessage');
    const successEl = document.getElementById('postSuccessMessage');
    if (errorEl) errorEl.style.display = 'none';
    if (successEl) successEl.style.display = 'none';
}

function setPostButtonLoading(loading) {
    const btn = document.getElementById('postSubmitBtn');
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

// ESC 键关闭模态框
document.addEventListener('keydown', (e) => {
    if (e.key === 'Escape') {
        closeCreateModal();
    }
});
</script>
