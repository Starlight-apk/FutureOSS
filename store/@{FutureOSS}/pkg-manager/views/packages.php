<div class="packages-page" x-data="packagesApp()" x-init="init()">
    <style>
        .packages-page { display: flex; height: calc(100vh - 40px); }
        .pkg-sidebar {
            width: 300px; min-width: 300px; background: #fff; border-right: 1px solid #e8ecf0;
            display: flex; flex-direction: column;
        }
        .pkg-sidebar-header { padding: 20px; border-bottom: 1px solid #f0f0f0; }
        .pkg-sidebar-header h3 { font-size: 16px; font-weight: 600; color: #1a1a2e; }
        .pkg-search { padding: 12px 16px; border-bottom: 1px solid #f0f0f0; }
        .pkg-search input {
            width: 100%; padding: 8px 12px; border: 1px solid #e0e0e0;
            border-radius: 8px; font-size: 13px; outline: none; box-sizing: border-box;
        }
        .pkg-search input:focus { border-color: #4a90d9; }
        .pkg-list { flex: 1; overflow-y: auto; }
        .pkg-item {
            padding: 14px 16px; cursor: pointer; border-bottom: 1px solid #f8f8f8;
            transition: background 0.15s;
        }
        .pkg-item:hover { background: #f8f9fa; }
        .pkg-item.active { background: #eef4fb; border-left: 3px solid #4a90d9; }
        .pkg-item-name { font-size: 14px; font-weight: 500; color: #333; }
        .pkg-item-desc { font-size: 12px; color: #999; margin-top: 4px; }
        .pkg-item-meta { font-size: 11px; color: #666; margin-top: 4px; display: flex; gap: 6px; align-items: center; }
        .pkg-item-status { color: #2ecc71; }

        .pkg-content { flex: 1; overflow-y: auto; padding: 24px 32px; background: #f9fafb; }
        .pkg-empty { display: flex; align-items: center; justify-content: center; height: 100%; color: #999; font-size: 15px; }

        .pkg-config-header { margin-bottom: 24px; display: flex; justify-content: space-between; align-items: flex-start; }
        .pkg-config-header h2 { font-size: 22px; font-weight: 600; color: #1a1a2e; }
        .pkg-config-header p { color: #888; font-size: 14px; margin-top: 4px; }

        .pkg-info-bar { display: flex; gap: 12px; margin-bottom: 20px; flex-wrap: wrap; }
        .pkg-info-tag {
            display: inline-flex; align-items: center; gap: 6px; padding: 6px 12px;
            background: #fff; border-radius: 8px; font-size: 13px; color: #555; border: 1px solid #e8ecf0;
        }
        .pkg-info-tag i { font-size: 16px; }
        .pkg-info-tag .count {
            background: #4a90d9; color: #fff; border-radius: 10px; padding: 1px 7px; font-size: 11px;
        }

        .config-section { background: #fff; border-radius: 12px; padding: 24px; margin-bottom: 16px; box-shadow: 0 1px 3px rgba(0,0,0,0.04); }
        .config-section h4 { font-size: 15px; font-weight: 600; color: #1a1a2e; margin-bottom: 16px; padding-bottom: 8px; border-bottom: 1px solid #f0f0f0; }

        .config-field { margin-bottom: 20px; }
        .config-field label { display: block; font-size: 13px; font-weight: 500; color: #333; margin-bottom: 6px; }
        .config-field .desc { font-size: 12px; color: #999; margin-bottom: 8px; }
        .config-field input[type="text"],
        .config-field input[type="number"],
        .config-field textarea,
        .config-field select {
            width: 100%; padding: 8px 12px; border: 1px solid #e0e0e0;
            border-radius: 8px; font-size: 13px; outline: none; transition: border-color 0.2s;
            box-sizing: border-box;
        }
        .config-field input:focus, .config-field select:focus, .config-field textarea:focus { border-color: #4a90d9; }
        .config-field textarea { min-height: 80px; resize: vertical; }

        .toggle { position: relative; display: inline-flex; align-items: center; gap: 10px; cursor: pointer; }
        .toggle input { display: none; }
        .toggle-slider { width: 44px; height: 24px; background: #ddd; border-radius: 12px; position: relative; transition: background 0.2s; }
        .toggle-slider::after {
            content: ''; position: absolute; width: 20px; height: 20px; background: #fff;
            border-radius: 50%; top: 2px; left: 2px; transition: transform 0.2s;
        }
        .toggle input:checked + .toggle-slider { background: #4a90d9; }
        .toggle input:checked + .toggle-slider::after { transform: translateX(20px); }

        .radio-group, .checkbox-group { display: flex; flex-wrap: wrap; gap: 8px; }
        .radio-option, .checkbox-option {
            display: flex; align-items: center; gap: 6px; padding: 6px 12px;
            border: 1px solid #e0e0e0; border-radius: 8px; cursor: pointer;
            font-size: 13px; transition: all 0.15s;
        }
        .radio-option:hover, .checkbox-option:hover { border-color: #4a90d9; background: #f0f5fc; }
        .radio-option.selected, .checkbox-option.selected { border-color: #4a90d9; background: #eef4fb; color: #4a90d9; }

        .action-btns { display: flex; gap: 12px; margin-top: 8px; }
        .save-btn { padding: 10px 24px; background: #4a90d9; color: #fff; border: none; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: background 0.2s; }
        .save-btn:hover { background: #3a7bc8; }
        .save-btn:disabled { background: #ccc; cursor: not-allowed; }
        .uninstall-btn { padding: 10px 24px; background: #fff; color: #e74c3c; border: 1px solid #e74c3c; border-radius: 8px; font-size: 14px; font-weight: 500; cursor: pointer; transition: all 0.2s; }
        .uninstall-btn:hover { background: #fee; }

        .status-msg { padding: 8px 12px; border-radius: 8px; font-size: 13px; margin-top: 12px; }
        .status-msg.success { background: #e8f8ef; color: #2ecc71; }
        .status-msg.error { background: #fde8e8; color: #e74c3c; }
    </style>

    <!-- 左栏：已安装插件列表 -->
    <div class="pkg-sidebar">
        <div class="pkg-sidebar-header"><h3>已安装插件</h3></div>
        <div class="pkg-search">
            <input type="text" placeholder="搜索插件..." x-model="searchQuery" />
        </div>
        <div class="pkg-list">
            <template x-for="plugin in filteredPlugins" :key="plugin.name">
                <div class="pkg-item" :class="{ active: selectedPlugin?.name === plugin.name }"
                     @click="selectPlugin(plugin)">
                    <div class="pkg-item-name" x-text="plugin.metadata.name || plugin.name"></div>
                    <div class="pkg-item-desc" x-text="plugin.metadata.description || '暂无描述'"></div>
                    <div class="pkg-item-meta">
                        <span x-text="'v' + (plugin.metadata.version || '?')"></span>
                        <span style="color:#888;" x-text="'by ' + plugin.author"></span>
                        <span x-show="plugin.has_config" style="color:#4a90d9;">⚙️</span>
                    </div>
                </div>
            </template>
        </div>
    </div>

    <!-- 右栏：配置面板 -->
    <div class="pkg-content">
        <template x-if="!selectedPlugin">
            <div class="pkg-empty">← 选择一个插件以查看配置</div>
        </template>

        <template x-if="selectedPlugin">
            <div>
                <div class="pkg-config-header">
                    <div>
                        <h2 x-text="selectedPlugin.metadata.name || selectedPlugin.name"></h2>
                        <p x-text="selectedPlugin.metadata.description"></p>
                    </div>
                </div>

                <!-- 信息栏：依赖、页面、事件（只在有数据时显示） -->
                <div class="pkg-info-bar">
                    <div class="pkg-info-tag" x-show="pluginDeps.length > 0">
                        <i class="ri-plug-line"></i>
                        <span>依赖:</span>
                        <template x-for="dep in pluginDeps" :key="dep">
                            <span class="count" x-text="dep"></span>
                        </template>
                    </div>
                    <div class="pkg-info-tag" x-show="pluginPages.length > 0">
                        <i class="ri-pages-line"></i>
                        <span>页面:</span>
                        <template x-for="pg in pluginPages" :key="pg.path">
                            <span class="count" x-text="pg.path"></span>
                        </template>
                    </div>
                    <div class="pkg-info-tag" x-show="pluginEvents.length > 0">
                        <i class="ri-flashlight-line"></i>
                        <span>事件:</span>
                        <template x-for="evt in pluginEvents" :key="evt">
                            <span class="count" x-text="evt"></span>
                        </template>
                    </div>
                </div>

                <!-- 配置表单 -->
                <div x-show="configSchema && Object.keys(configSchema).length > 0">
                    <div class="config-section">
                        <h4>⚙️ 配置</h4>
                        <template x-for="[key, field] in sortedConfigFields" :key="key">
                            <div class="config-field" x-show="isFieldVisible(key, field)">
                                <label x-text="field.name || key"></label>
                                <div class="desc" x-text="field.description"></div>

                                <template x-if="field.type === 'string'">
                                    <input type="text" x-model="configValues[key]" />
                                </template>
                                <template x-if="field.type === 'number'">
                                    <input type="number" x-model.number="configValues[key]" :min="field.min ?? 0" :max="field.max ?? 99999" />
                                </template>
                                <template x-if="field.type === 'boolean'">
                                    <label class="toggle">
                                        <input type="checkbox" x-model="configValues[key]" />
                                        <span class="toggle-slider"></span>
                                        <span x-text="configValues[key] ? '已开启' : '已关闭'"></span>
                                    </label>
                                </template>
                                <template x-if="field.type === 'select'">
                                    <div class="radio-group">
                                        <template x-for="opt in field.options" :key="opt.value">
                                            <div class="radio-option" :class="{ selected: configValues[key] === opt.value }"
                                                 @click="configValues[key] = opt.value">
                                                <span x-text="opt.label"></span>
                                            </div>
                                        </template>
                                    </div>
                                </template>
                                <template x-if="field.type === 'list'">
                                    <div class="checkbox-group">
                                        <template x-for="opt in field.options" :key="opt.value">
                                            <div class="checkbox-option" :class="{ selected: (configValues[key] || []).includes(opt.value) }"
                                                 @click="toggleListValue(key, opt.value)">
                                                <span x-text="opt.label"></span>
                                            </div>
                                        </template>
                                    </div>
                                </template>
                                <template x-if="field.type === 'textarea'">
                                    <textarea x-model="configValues[key]"></textarea>
                                </template>
                            </div>
                        </template>
                    </div>

                    <div class="action-btns">
                        <button class="save-btn" @click="saveConfig()" :disabled="saving">
                            <span x-show="!saving">💾 保存配置</span>
                            <span x-show="saving">保存中...</span>
                        </button>
                        <button class="uninstall-btn" @click="uninstallPlugin()">
                            🗑️ 卸载插件
                        </button>
                    </div>

                    <div class="status-msg" :class="saveStatus.type" x-show="saveStatus.msg" x-text="saveStatus.msg"></div>
                </div>

                <div x-show="!configSchema || Object.keys(configSchema).length === 0" class="config-section">
                    <p style="color:#999;">该插件没有可配置的选项</p>
                    <div class="action-btns">
                        <button class="uninstall-btn" @click="uninstallPlugin()">🗑️ 卸载插件</button>
                    </div>
                </div>
            </div>
        </template>
    </div>

    <script>
    function packagesApp() {
        return {
            plugins: [],
            searchQuery: '',
            selectedPlugin: null,
            configSchema: {},
            configValues: {},
            pluginDeps: [],
            pluginPages: [],
            pluginEvents: [],
            saving: false,
            saveStatus: { type: '', msg: '' },

            init() { this.loadPlugins(); },

            async loadPlugins() {
                const res = await fetch('/api/plugins');
                this.plugins = await res.json();
            },

            get filteredPlugins() {
                if (!this.searchQuery) return this.plugins;
                const q = this.searchQuery.toLowerCase();
                return this.plugins.filter(p =>
                    (p.metadata.name || '').toLowerCase().includes(q) ||
                    (p.metadata.description || '').toLowerCase().includes(q) ||
                    p.name.toLowerCase().includes(q)
                );
            },

            get sortedConfigFields() {
                if (!this.configSchema) return [];
                return Object.entries(this.configSchema).sort((a, b) => (a[1].order || 99) - (b[1].order || 99));
            },

            async selectPlugin(plugin) {
                this.selectedPlugin = plugin;
                this.configSchema = {};
                this.configValues = {};
                this.pluginDeps = [];
                this.pluginPages = [];
                this.pluginEvents = [];

                if (plugin.has_config) {
                    const res = await fetch(`/api/plugins/${plugin.name}/config`);
                    const data = await res.json();
                    this.configSchema = data.schema || {};
                    this.configValues = data.current || {};
                }

                const infoRes = await fetch(`/api/plugins/${plugin.name}/info`);
                const info = await infoRes.json();
                this.pluginDeps = info.dependencies || [];
                this.pluginPages = info.pages || [];
                this.pluginEvents = info.events || [];
            },

            isFieldVisible(key, field) {
                if (field.show_when) {
                    return this.configValues[field.show_when.field] === field.show_when.value;
                }
                return true;
            },

            toggleListValue(key, value) {
                if (!this.configValues[key]) this.configValues[key] = [];
                const idx = this.configValues[key].indexOf(value);
                if (idx >= 0) this.configValues[key].splice(idx, 1);
                else this.configValues[key].push(value);
            },

            async saveConfig() {
                this.saving = true;
                this.saveStatus = {};
                try {
                    const res = await fetch(`/api/plugins/${this.selectedPlugin.name}/config`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(this.configValues)
                    });
                    if (res.ok) {
                        this.saveStatus = { type: 'success', msg: '✅ 配置已保存' };
                    } else {
                        this.saveStatus = { type: 'error', msg: '❌ 保存失败' };
                    }
                } catch (e) {
                    this.saveStatus = { type: 'error', msg: '❌ 网络错误' };
                }
                this.saving = false;
                setTimeout(() => { this.saveStatus.msg = ''; }, 3000);
            },

            async uninstallPlugin() {
                if (!confirm('确定要卸载 ' + (this.selectedPlugin.metadata.name || this.selectedPlugin.name) + ' 吗？\n卸载后需要重启 FutureOSS 才能完全生效。')) return;
                try {
                    const res = await fetch(`/api/plugins/${this.selectedPlugin.name}/uninstall`, { method: 'POST' });
                    const data = await res.json();
                    if (data.ok) {
                        alert('✅ 已卸载，请重启 FutureOSS');
                        this.loadPlugins();
                        this.selectedPlugin = null;
                    } else {
                        alert('❌ 卸载失败: ' + (data.error || '未知错误'));
                    }
                } catch (e) { alert('❌ 网络错误'); }
            }
        };
    }
    </script>
</div>
