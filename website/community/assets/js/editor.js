/**
 * OSS Community Editor JS
 * Markdown 编辑器、实时预览、表单提交
 */

document.addEventListener('DOMContentLoaded', () => {
    initEditor();
    initToolbar();
    initTags();
    initForm();
});

// 初始化编辑器
function initEditor() {
    const textarea = document.getElementById('postContent');
    const titleInput = document.getElementById('postTitle');

    // Tab 键支持
    if (textarea) {
        textarea.addEventListener('keydown', (e) => {
            if (e.key === 'Tab') {
                e.preventDefault();
                const start = textarea.selectionStart;
                const end = textarea.selectionEnd;
                textarea.value = textarea.value.substring(0, start) + '  ' + textarea.value.substring(end);
                textarea.selectionStart = textarea.selectionEnd = start + 2;
            }
        });
    }
}

// 初始化工具栏
function initToolbar() {
    const buttons = document.querySelectorAll('.md-btn');
    const textarea = document.getElementById('postContent');

    if (!textarea) return;

    buttons.forEach(btn => {
        btn.addEventListener('click', () => {
            const action = btn.dataset.md;
            insertMarkdown(textarea, action);
        });
    });
}

function insertMarkdown(textarea, action) {
    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selected = textarea.value.substring(start, end);
    let insertion = '';
    
    switch (action) {
        case 'bold':
            insertion = `**${selected || '粗体文本'}**`;
            break;
        case 'italic':
            insertion = `*${selected || '斜体文本'}*`;
            break;
        case 'heading':
            insertion = `\n## ${selected || '标题'}\n`;
            break;
        case 'quote':
            insertion = `\n> ${selected || '引用文本'}\n`;
            break;
        case 'code':
            insertion = selected.includes('\n') ? `\n\`\`\`\n${selected || '代码块'}\n\`\`\`\n` : `\`${selected || '行内代码'}\``;
            break;
        case 'link':
            insertion = `[${selected || '链接文本'}](url)`;
            break;
        case 'list':
            insertion = `\n- ${selected || '列表项'}\n`;
            break;
    }
    
    textarea.value = textarea.value.substring(0, start) + insertion + textarea.value.substring(end);
    textarea.focus();
    textarea.selectionStart = textarea.selectionEnd = start + insertion.length;
}

// 初始化标签
function initTags() {
    const tagInput = document.getElementById('tagInput');
    const tagsContainer = document.getElementById('tagsContainer');
    
    if (!tagInput || !tagsContainer) return;
    
    tagInput.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            e.preventDefault();
            const tagName = tagInput.value.trim();
            if (tagName) {
                addTag(tagName);
                tagInput.value = '';
            }
        }
    });
}

function addTag(name) {
    const tagsContainer = document.getElementById('tagsContainer');
    if (!tagsContainer) return;
    
    // 检查是否已存在
    const existing = tagsContainer.querySelectorAll('.tag-item');
    for (const tag of existing) {
        if (tag.textContent.trim().replace('×', '').trim() === name) {
            return;
        }
    }
    
    const tagEl = document.createElement('span');
    tagEl.className = 'tag-item';
    tagEl.innerHTML = `
        ${name}
        <button type="button" class="tag-remove" onclick="this.parentElement.remove()">&times;</button>
    `;
    tagsContainer.appendChild(tagEl);
}

// 初始化表单
function initForm() {
    const form = document.getElementById('postEditorForm');
    const saveBtn = document.getElementById('savePostBtn');
    
    if (!form || !saveBtn) return;
    
    saveBtn.addEventListener('click', async (e) => {
        e.preventDefault();
        
        const postId = document.getElementById('editPostId').value;
        const title = document.getElementById('postTitle').value.trim();
        const content = document.getElementById('postContent').value.trim();
        const categoryId = document.getElementById('postCategory').value;
        
        // 收集标签
        const tags = [];
        document.querySelectorAll('#tagsContainer .tag-item').forEach(tag => {
            const name = tag.textContent.replace('×', '').trim();
            if (name) tags.push(name);
        });
        
        // 验证
        if (!title) {
            showError('请输入帖子标题');
            return;
        }
        if (title.length < 5) {
            showError('标题至少 5 个字符');
            return;
        }
        if (!content) {
            showError('请输入帖子内容');
            return;
        }
        if (content.length < 10) {
            showError('内容至少 10 个字符');
            return;
        }
        if (!categoryId) {
            showError('请选择分类');
            return;
        }
        
        // 提交
        setSaveButtonLoading(true);
        
        const formData = {
            title: title,
            content: content,
            category_id: categoryId,
            tags: tags
        };
        
        if (postId) {
            formData.id = parseInt(postId);
        }
        
        const action = postId ? 'update' : 'create';
        const url = `api/posts.php?action=${action}`;
        
        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(formData)
            });
            
            const result = await response.json();
            
            if (result.success) {
                showSuccess(postId ? '更新成功！' : '发布成功！正在跳转...');
                setTimeout(() => {
                    window.location.href = `post.php?id=${result.post_id || postId}`;
                }, 1000);
            } else {
                showError(result.message || '操作失败');
            }
        } catch (error) {
            showError('网络错误，请稍后重试');
        } finally {
            setSaveButtonLoading(false);
        }
    });
}

function showSuccess(message) {
    const toast = document.getElementById('successToast');
    const msgEl = document.getElementById('successMessage');
    if (toast && msgEl) {
        msgEl.textContent = message;
        toast.style.display = 'flex';
        setTimeout(() => { toast.style.display = 'none'; }, 3000);
    }
}

function showError(message) {
    const toast = document.getElementById('errorToast');
    const msgEl = document.getElementById('errorMessage');
    if (toast && msgEl) {
        msgEl.textContent = message;
        toast.style.display = 'flex';
        setTimeout(() => { toast.style.display = 'none'; }, 4000);
    }
}

function setSaveButtonLoading(loading) {
    const btn = document.getElementById('savePostBtn');
    if (!btn) return;
    
    if (loading) {
        btn.disabled = true;
        btn.style.opacity = '0.6';
        btn.innerHTML = `
            <svg class="btn-spinner" viewBox="0 0 24 24" fill="none">
                <circle cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4" stroke-linecap="round" opacity="0.25"/>
                <path d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4z" fill="currentColor" opacity="0.75"/>
            </svg>
            处理中...
        `;
    } else {
        btn.disabled = false;
        btn.style.opacity = '1';
        btn.innerHTML = `
            <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path stroke-linecap="round" stroke-linejoin="round" d="M5 13l4 4L19 7"/>
            </svg>
            ${document.getElementById('editPostId').value ? '保存修改' : '发布帖子'}
        `;
    }
}
