# pkg 包管理

插件的搜索、安装、卸载和更新功能。

## 功能

- 从远程仓库搜索插件
- 下载并安装到 `./data/pkg/` 目录
- 卸载已安装的插件
- 更新单个或所有插件
- 维护已安装插件列表

## 使用

```python
pm = pkg_plugin.manager

# 搜索
results = pm.search("keyword")

# 安装
pm.install("plugin-name")
pm.install("plugin-name", version="1.0.0")

# 卸载
pm.uninstall("plugin-name")

# 更新
pm.update()  # 更新所有
pm.update("plugin-name")  # 更新单个

# 列出已安装
installed = pm.list_installed()
```

## 安装位置

```
./data/pkg/
└── <插件名>/
    ├── main.py
    └── manifest.json
```
