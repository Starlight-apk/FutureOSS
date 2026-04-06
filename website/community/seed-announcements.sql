-- 插入公告数据
INSERT IGNORE INTO posts (user_id, category_id, title, slug, content, is_pinned) VALUES
(1, 
 (SELECT id FROM categories WHERE slug = 'announcements' LIMIT 1),
 '欢迎使用 OSS Community',
 'welcome-to-oss-community',
 '# 欢迎使用 OSS 开发者社区！\n\n这是我们社区的第一篇公告。\n\n## 社区规则\n\n- 尊重他人，文明交流\n- 禁止发布违法不良信息\n- 鼓励分享技术经验\n- 提问前请先搜索已有帖子\n\n## 功能介绍\n\n- 📝 **发帖** - 分享你的技术经验\n- 💬 **回复** - 参与讨论，帮助他人\n- ❤️ **点赞** - 为优质内容点赞\n- 🏷️ **标签** - 使用标签分类帖子\n- 🔍 **搜索** - 快速找到感兴趣的内容\n\n## 快速开始\n\n1. 注册并登录你的账户\n2. 完善个人资料和简介\n3. 发表第一篇帖子\n4. 参与社区讨论\n\n> 如果你有任何建议或反馈，欢迎在反馈区发帖！\n\n祝你在社区玩得愉快！ 🎉',
 1),

(1,
 (SELECT id FROM categories WHERE slug = 'announcements' LIMIT 1),
 '社区功能更新日志',
 'community-changelog-v1',
 '# 社区功能更新\n\n## v1.1.0 - 2026-04-04\n\n### 新增\n- ✨ 用户个人主页\n- ✨ 编辑个人资料（支持 Bio）\n- ✨ 我的文章页面\n- ✨ 文章统计（浏览、点赞、回复）\n\n### 优化\n- 🚀 响应式布局优化\n- 📱 移动端适配\n- 🎨 UI 样式改进\n\n### 修复\n- 🐛 数据库连接问题\n- 🐛 用户菜单交互问题\n\n---\n\n感谢大家的支持！',
 1);
