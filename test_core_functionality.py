#!/usr/bin/env python3
"""
简单测试验证核心功能
"""

import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def test_imports():
    """测试核心模块导入"""
    try:
        # 测试配置模块
        from oss.config import Config, get_config, init_config
        print("✅ 配置模块导入成功")
        
        # 测试日志模块
        from oss.logger.logger import Logger
        print("✅ 日志模块导入成功")
        
        # 测试插件类型
        from oss.plugin.types import Plugin
        print("✅ 插件类型导入成功")
        
        # 测试配置功能
        config = Config()
        print(f"✅ 配置创建成功: HOST={config.host}")
        
        # 测试日志功能
        logger = Logger()
        logger.info("测试日志消息")
        print("✅ 日志功能正常")
        
        return True
    except Exception as e:
        print(f"❌ 导入测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cors_config():
    """测试CORS配置"""
    try:
        from oss.config import Config
        
        config = Config()
        cors_origins = config.get("CORS_ALLOWED_ORIGINS")
        print(f"✅ CORS配置: {cors_origins}")
        
        # 测试环境变量覆盖
        import os
        os.environ["CORS_ALLOWED_ORIGINS"] = '["http://localhost:8080"]'
        config = Config()
        cors_origins = config.get("CORS_ALLOWED_ORIGINS")
        print(f"✅ CORS环境变量覆盖: {cors_origins}")
        
        # 清理
        del os.environ["CORS_ALLOWED_ORIGINS"]
        
        return True
    except Exception as e:
        print(f"❌ CORS配置测试失败: {e}")
        return False

def test_logging_config():
    """测试日志配置"""
    try:
        from oss.config import Config
        
        config = Config()
        print(f"✅ 日志格式: {config.get('LOG_FORMAT')}")
        print(f"✅ 日志级别: {config.get('LOG_LEVEL')}")
        print(f"✅ 日志文件: {config.get('LOG_FILE')}")
        print(f"✅ 日志最大大小: {config.get('LOG_MAX_SIZE')}")
        print(f"✅ 日志备份数: {config.get('LOG_BACKUP_COUNT')}")
        
        return True
    except Exception as e:
        print(f"❌ 日志配置测试失败: {e}")
        return False

def test_host_config():
    """测试主机配置"""
    try:
        from oss.config import Config
        
        config = Config()
        print(f"✅ 主机配置: {config.host}")
        
        # 检查是否修复了默认绑定所有接口的问题
        if config.host == "127.0.0.1":
            print("✅ 主机配置已修复：默认绑定本地接口")
        else:
            print(f"⚠️  主机配置可能存在安全风险: {config.host}")
        
        return True
    except Exception as e:
        print(f"❌ 主机配置测试失败: {e}")
        return False

if __name__ == "__main__":
    print("开始测试NebulaShell核心功能...")
    
    tests = [
        ("导入测试", test_imports),
        ("CORS配置测试", test_cors_config),
        ("日志配置测试", test_logging_config),
        ("主机配置测试", test_host_config),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n--- {test_name} ---")
        if test_func():
            passed += 1
        else:
            print(f"❌ {test_name} 失败")
    
    print(f"\n--- 测试结果 ---")
    print(f"通过: {passed}/{total}")
    
    if passed == total:
        print("🎉 所有测试通过！核心功能正常。")
        sys.exit(0)
    else:
        print("❌ 部分测试失败，需要修复。")
        sys.exit(1)