# 全局依赖管理系统使用指南

## 🎯 设计理念

**一行代码声明，自动适配所有系统！**

第三方插件开发者无需关心具体系统包名，只需在 `manifest.json` 中声明依赖别名，系统会自动：
- 检测当前操作系统（Debian/RedHat/Arch/macOS/Alpine）
- 选择对应的包管理器（apt/yum/dnf/pacman/brew/apk）
- 安装正确的系统包

## 📁 核心文件

### `system-dependencies.json` - 全局依赖映射中心

位于项目根目录，包含所有常用系统依赖的跨平台映射关系。

**已预置依赖：**
- `ffmpeg` - 音视频处理
- `opencv` - 计算机视觉
- `sqlite` / `mysql` / `postgresql` / `redis` - 数据库
- `curl` / `ssl` - 网络通信
- `zlib` - 数据压缩
- `git` - 版本控制
- `nodejs` / `python3` - 运行时环境
- `build-essential` - 编译工具链
- `imagemagick` - 图像处理
- `poppler` - PDF 处理

## 🚀 使用方法

### 方式 1：数组声明（推荐）⭐

在插件的 `manifest.json` 中添加 `global_deps` 数组：

```json
{
  "metadata": {
    "name": "video-processor",
    "version": "1.0.0"
  },
  "global_deps": ["ffmpeg", "opencv", "build-essential"]
}
```

**优点：**
- ✅ 简洁明了，一行一个依赖别名
- ✅ 自动去重
- ✅ 支持混合使用（可同时声明多个依赖类别）
- ✅ 第三方插件零配置扩展

### 方式 2：布尔值快捷声明

如果插件名与全局依赖名一致，可直接设为 `true`：

```json
{
  "metadata": {
    "name": "ffmpeg",
    "version": "1.0.0"
  },
  "global_deps": true
}
```

系统会自动查找 `system-dependencies.json` 中的 `ffmpeg` 依赖定义。

### 方式 3：传统方式（兼容）

仍然支持直接在 `system_dependencies` 中写具体包名：

```json
{
  "metadata": {
    "name": "my-plugin",
    "version": "1.0.0"
  },
  "system_dependencies": ["ffmpeg", "libavcodec-dev", "libavformat-dev"]
}
```

⚠️ **缺点：** 需要手动区分不同系统的包名，不推荐。

## 🔧 工作流程

```
┌─────────────────────┐
│  插件 manifest.json  │
│  global_deps: [...] │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ auto-dependency 插件 │
│  扫描所有 manifest   │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│ system-dependencies │
│   .json 查询映射    │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  检测系统包管理器   │
│  apt/yum/pacman...  │
└──────────┬──────────┘
           │
           ▼
┌─────────────────────┐
│  自动安装对应系统包 │
│  (去重 + 幂等)      │
└─────────────────────┘
```

## 📦 扩展示例

### 示例 1：视频处理插件

```json
{
  "metadata": {
    "name": "awesome-video-tool",
    "author": "ThirdParty"
  },
  "global_deps": ["ffmpeg", "imagemagick", "build-essential"]
}
```

### 示例 2：AI 视觉插件

```json
{
  "metadata": {
    "name": "ai-vision-plugin",
    "author": "AI-Lab"
  },
  "global_deps": ["opencv", "python3", "build-essential"]
}
```

### 示例 3：数据库工具插件

```json
{
  "metadata": {
    "name": "db-manager",
    "author": "DBTools"
  },
  "global_deps": ["mysql", "postgresql", "redis"]
}
```

## ➕ 添加新依赖

第三方开发者如需新依赖，有两种选择：

### 选项 A：提交到全局配置（推荐公共依赖）

向 `system-dependencies.json` 添加新条目：

```json
{
  "dependencies": {
    "your-new-dep": {
      "description": "你的依赖描述",
      "packages": {
        "apt": ["package-name", "dev-package"],
        "yum": ["package-name", "package-devel"],
        "pacman": ["package-name"],
        "brew": ["package-name"],
        "apk": ["package-name", "package-dev"]
      }
    }
  }
}
```

### 选项 B：使用传统方式（私有/特殊依赖）

```json
{
  "metadata": {
    "name": "my-special-plugin"
  },
  "system_dependencies": ["custom-package"]
}
```

## 🛠️ API 接口

通过 `auto-dependency` 插件提供以下功能：

```python
# 扫描所有插件依赖声明
PL.invoke("auto-dependency:scan")

# 检查依赖安装状态
PL.invoke("auto-dependency:check")

# 自动安装缺失依赖
PL.invoke("auto-dependency:install")

# 获取系统信息
PL.invoke("auto-dependency:info")
```

## ✨ 优势总结

| 特性 | 传统方式 | 全局依赖管理 |
|------|---------|-------------|
| 声明复杂度 | 需写具体包名 | 仅需别名 |
| 跨平台支持 | 手动适配 | 自动适配 |
| 可维护性 | 分散在各插件 | 集中管理 |
| 第三方扩展 | 困难 | 简单 |
| 代码行数 | 多行 | **一行** |

## 🎉 最佳实践

1. **优先使用 `global_deps` 数组** - 清晰、简洁、易维护
2. **使用有意义的别名** - 如 `ffmpeg` 而非 `video-lib`
3. **及时更新全局配置** - 新增依赖时补充完整跨平台映射
4. **避免混用方式** - 一个插件尽量只用一种声明方式

---

**让依赖管理变得如此简单！🚀**
