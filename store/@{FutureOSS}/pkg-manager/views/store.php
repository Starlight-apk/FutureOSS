<div class="store-page" x-data="storeApp()" x-init="init()">
    <style>
        .store-page { display: flex; height: calc(100vh - 40px); }
        .store-sidebar {
            width: 220px; min-width: 220px; background: #fff; border-right: 1px solid #e8ecf0;
            display: flex; flex-direction: column; padding: 20px 0;
        }
        .store-sidebar-title { font-size: 14px; font-weight: 600; color: #1a1a2e; padding: 0 20px 12px; border-bottom: 1px solid #f0f0f0; }
        .store-filter { padding: 10px 20px; cursor: pointer; font-size: 13px; color: #555; transition: all 0.15s; }
        .store-filter:hover { background: #f8f9fa; }
        .store-filter.active { background: #eef4fb; color: #4a90d9; font-weight: 500; border-right: 3px solid #4a90d9; }
        .store-filter .count { float: right; background: #f0f0f0; border-radius: 10px; padding: 1px 8px; font-size: 11px; }
        .store-filter.active .count { background: #4a90d9; color: #fff; }

        .store-main { flex: 1; overflow-y: auto; padding: 24px 32px; background: #f9fafb; }
        .store-header { margin-bottom: 24px; }
        .store-header h2 { font-size: 26px; font-weight: 600; color: #1a1a2e; }
        .store-header p { color: #888; font-size: 14px; margin-top: 4px; }

        .store-search { margin-bottom: 20px; }
        .store-search input {
            width: 100%; max-width: 400px; padding: 10px 16px; border: 1px solid #e0e0e0;
            border-radius: 10px; font-size: 14px; outline: none; box-sizing: border-box;
        }
        .store-search input:focus { border-color: #4a90d9; }

        .store-grid { display: grid; grid-template-columns: repeat(auto-fill, minmax(320px, 1fr)); gap: 16px; }

        .store-card { background: #fff; border-radius: 14px; padding: 20px; box-shadow: 0 1px 3px rgba(0,0,0,0.04), 0 4px 12px rgba(0,0,0,0.03); display: flex; flex-direction: column; gap: 12px; }
        .store-card-header { display: flex; justify-content: space-between; align-items: flex-start; }
        .store-card-name { font-size: 16px; font-weight: 600; color: #1a1a2e; }
        .store-card-version { font-size: 12px; color: #999; background: #f0f0f0; padding: 2px 8px; border-radius: 10px; }
        .store-card-desc { font-size: 13px; color: #666; flex: 1; line-height: 1.5; }
        .store-card-tags { display: flex; gap: 6px; flex-wrap: wrap; }
        .store-card-tag { font-size: 11px; padding: 3px 8px; background: #f0f5fc; color: #4a90d9; border-radius: 6px; }
        .store-card-tag.installed { background: #e8f8ef; color: #2ecc71; }

        .install-btn {
            padding: 8px 18px; border: none; border-radius: 8px; font-size: 13px;
            font-weight: 500; cursor: pointer; transition: all 0.2s; white-space: nowrap;
        }
        .install-btn.install { background: #4a90d9; color: #fff; }
        .install-btn.install:hover { background: #3a7bc8; }
        .install-btn.installed { background: #e8f8ef; color: #2ecc71; cursor: default; }
        .install-btn:disabled { background: #ccc; cursor: not-allowed; }

        .store-empty { text-align: center; padding: 60px 20px; color: #999; }
        .store-empty i { font-size: 48px; margin-bottom: 12px; display: block; }

        .store-loading { text-align: center; padding: 80px 20px; color: #666; }
        .store-loading i { font-size: 36px; animation: spin 1s linear infinite; display: block; margin-bottom: 16px; }
        @keyframes spin { from { transform: rotate(0deg); } to { transform: rotate(360deg); } }
    </style>

    <!-- 左栏：分类 -->
    <div class="store-sidebar">
        <div class="store-sidebar-title">分类</div>
        <div class="store-filter" :class="{ active: activeFilter === 'all' }" @click="activeFilter = 'all'">
            全部插件 <span class="count" x-text="plugins.length"></span>
        </div>
        <div class="store-filter" :class="{ active: activeFilter === 'available' }" @click="activeFilter = 'available'">
            可安装 <span class="count" x-text="plugins.filter(p => !p.is_installed).length"></span>
        </div>
        <div class="store-filter" :class="{ active: activeFilter === 'installed' }" @click="activeFilter = 'installed'">
            已安装 <span class="count" x-text="plugins.filter(p => p.is_installed).length"></span>
        </div>
        <div class="store-filter" :class="{ active: activeFilter === 'configurable' }" @click="activeFilter = 'configurable'">
            可配置 <span class="count" x-text="plugins.filter(p => p.has_config).length"></span>
        </div>
    </div>

    <!-- 右栏：插件卡片列表 -->
    <div class="store-main">
        <div class="store-header">
            <h2>插件商店</h2>
            <p>浏览并安装插件来扩展功能</p>
        </div>

        <!-- 加载中状态 -->
        <div class="store-loading" x-show="!loaded && !loadError">
            <i class="ri-loader-4-line"></i>
            <p>正在加载插件列表...</p>
        </div>

        <!-- 加载失败状态 -->
        <div class="store-empty" x-show="loadError">
            <i class="ri-error-warning-line"></i>
            <p>加载失败，请稍后重试</p>
        </div>

        <div class="store-search" x-show="loaded && !loadError">
            <input type="text" placeholder="搜索插件名称或描述..." x-model="searchQuery" />
        </div>

        <div class="store-grid" x-show="loaded && !loadError && filteredPlugins.length > 0">
            <template x-for="plugin in filteredPlugins" :key="plugin.full_name">
                <div class="store-card">
                    <div class="store-card-header">
                        <div>
                            <div class="store-card-name" x-text="plugin.metadata.name || plugin.name"></div>
                            <div class="store-card-version" x-text="(plugin.metadata.version ? 'v' + plugin.metadata.version : '') + (plugin.author ? ' · ' + plugin.author : '')"></div>
                        </div>
                        <button class="install-btn" :class="plugin.is_installed ? 'installed' : 'install'"
                                @click="!plugin.is_installed && installPlugin(plugin)"
                                :disabled="loading">
                            <span x-show="!plugin.is_installed && !loading">📦 安装</span>
                            <span x-show="plugin.is_installed">✅ 已安装</span>
                            <span x-show="loading">...</span>
                        </button>
                    </div>
                    <div class="store-card-desc" x-text="plugin.metadata.description || '暂无描述'"></div>
                    <div class="store-card-tags">
                        <template x-for="dep in (plugin.dependencies || [])" :key="dep">
                            <span class="store-card-tag" x-text="'🔌 ' + dep"></span>
                        </template>
                        <span class="store-card-tag" x-show="plugin.has_config">⚙️ 可配置</span>
                    </div>
                </div>
            </template>
        </div>

        <div class="store-empty" x-show="loaded && !loadError && filteredPlugins.length === 0">
            <i class="ri-store-2-line"></i>
            <p x-text="plugins.length === 0 ? '无法连接 Gitee API，请检查网络或配置' : '没有找到匹配的插件'"></p>
        </div>
    </div>

    <script>
    function storeApp() {
        return {
            plugins: [],
            searchQuery: '',
            activeFilter: 'all',
            loading: false,
            loaded: false,
            loadError: false,

            init() { this.loadPlugins(); },

            async loadPlugins() {
                this.loaded = false;
                this.loadError = false;
                try {
                    const res = await fetch('/api/store/remote');
                    if (!res.ok) throw new Error('API 返回错误');
                    const data = await res.json();
                    if (Array.isArray(data) && data.length > 0) {
                        this.plugins = data;
                    } else {
                        this.loadError = true;
                    }
                } catch (e) {
                    console.error('获取远程插件失败:', e);
                    this.loadError = true;
                }
                this.loaded = true;
            },

            get filteredPlugins() {
                let list = this.plugins;
                if (this.activeFilter === 'available') list = list.filter(p => !p.is_installed);
                else if (this.activeFilter === 'installed') list = list.filter(p => p.is_installed);
                else if (this.activeFilter === 'configurable') list = list.filter(p => p.has_config);

                if (this.searchQuery) {
                    const q = this.searchQuery.toLowerCase();
                    list = list.filter(p =>
                        (p.metadata.name || '').toLowerCase().includes(q) ||
                        (p.metadata.description || '').toLowerCase().includes(q) ||
                        p.name.toLowerCase().includes(q)
                    );
                }
                return list;
            },

            async installPlugin(plugin) {
                this.loading = true;
                try {
                    const res = await fetch('/api/store/install', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({ name: plugin.name, author: plugin.author })
                    });
                    const data = await res.json();
                    if (data.ok) {
                        plugin.is_installed = true;
                        alert('✅ 安装成功，请重启 FutureOSS 以启用插件');
                    } else {
                        alert('❌ 安装失败: ' + (data.error || '未知错误'));
                    }
                } catch (e) { alert('❌ 网络错误'); }
                this.loading = false;
            }
        };
    }
    </script>
</div>
