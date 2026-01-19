#!/usr/bin/env python3
"""
简单的环境测试脚本
"""

import os
import sys

def main():
    print("🚀 LangChain 1.0 简单测试")
    print("=" * 40)
    
    # 添加项目路径
    sys.path.insert(0, "")
    
    # 测试基础导入
    try:
   import config
        print("✅ config 模块导入成功")
   print(f"可导入的类: {[name for name in dir(config) if not name.startswith('_')]}")
    except ImportError as e:
        print(f"❌ config 模块导入失败: {e}")
        return
    
    # 测试特定类
    classes_to_test = ['UnifiedModelManager', 'DifyIntegration', 'RAGFlowIntegration']
    
    for class_name in classes_to_test:
        if hasattr(config, class_name):
            print(f"✅ {class_name} 可用")
        else:
print(f"❌ {class_name} 不可用")
    
    # 显示环境状态
  print("\n🔧 环境检查:")
    env_vars = ['DEEPSEEK_API_KEY', 'ZHIPU_API_KEY', 'MOONSHOT_API_KEY', 'OPENAI_API_KEY']
    
    for var in env_vars:
      if os.getenv(var):
       print(f"✅ {var}: 已配置")
    else:
     print(f"❌ {var}: 未配置")

if __name__ == "__main__":
 main()