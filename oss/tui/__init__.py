"""TUI 核心模块 - 强大的 WebUI 到终端界面转换引擎 v1.3

本模块提供完整的 HTML/CSS/JS 到 TUI 的转换能力，参考 opencode 风格设计：
- HTML 解析：识别 data-tui-* 标记、语义化标签、Aria 属性，转换为 40+ 种终端元素
- CSS 转换：支持 ANSI 256 色、真彩色、完整字体排版、边框样式、阴影效果
- JS 交互：完整模拟鼠标追踪、点击事件、键盘绑定、DOM 操作、事件系统
- 布局引擎：flex/grid/absolute 布局终端适配，自动响应式调整
- 组件系统：40+ 种组件（按钮、面板、列表、表单、表格、进度条、图表等）
- 高级特性：动画系统、主题系统、虚拟滚动、焦点管理、辅助功能

架构设计完全参考 opencode 风格，提供现代化、高性能终端体验。
"""

from .converter import (
    # 管理器
    TUIManager,
    TUIRenderer,
    HTMLToTUIConverter,
    
    # 输入处理
    TUIInputHandler,
    TUIEventManager,
    
    # 画布
    TUICanvas,
    
    # 样式系统
    ANSIStyle,
    BorderStyle,
    TUIColor,
    TUIStyle,
    
    # 元素类型
    TUIElementType,
    
    # 基础元素
    TUIElement,
    TUIButton,
    TUILabel,
    TUIPanel,
    TUILayout,
    TUIList,
    TUISeparator,
    TUIProgressBar,
    TUISpinner,
)

__all__ = [
    # 管理器
    'TUIManager',
    'TUIRenderer',
    'HTMLToTUIConverter',
    
    # 输入处理
    'TUIInputHandler',
    'TUIEventManager',
    
    # 画布
    'TUICanvas',
    
    # 样式系统
    'ANSIStyle',
    'BorderStyle',
    'TUIColor',
    'TUIStyle',
    
    # 元素类型
    'TUIElementType',
    
    # 基础元素
    'TUIElement',
    'TUIButton',
    'TUILabel',
    'TUIPanel',
    'TUILayout',
    'TUIList',
    'TUISeparator',
    'TUIProgressBar',
    'TUISpinner',
]
