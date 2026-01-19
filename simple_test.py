#!/usr/bin/env python3
"""简单测试脚本"""

import os
import sys

def main():
    print("LangChain 1.0 简单测试")
    print("=" * 30)
    
    # 添加项目路径
    sys.path.insert(0, ".")
    
    # 导入模块
    try:
        import config
        print("Config模块导入成功")
        print("可用类:", [name for name in dir(config) if not name.startswith('_')])
        
        # 检查具体类
  if hasattr(config, 'UnifiedModelManager'):
      print("✓ UnifiedModelManager 可用")
      else:
            print("✗ UnifiedModelManager 不可用")
            
        if hasattr(config, 'DifyIntegration'):
    print("✓ DifyIntegration 可用")
     else:
   print("✗ DifyIntegration 不可用")
   
        if hasattr(config, 'RAGFlowIntegration'):
   print("✓ RAGFlowIntegration 可用")
  else:
       print("✗ RAGFlowIntegration 不可用")
       
    except Exception as e:
        print(f"导入错误: {e}")
        
    # 检查环境变量
    print("\n环境变量状态:")
    key_vars = ['DEEPSEEK_API_KEY', 'ZHIPU_API_KEY', 'MOONSHOT_API_KEY']
    for var in key_vars:
        if os.getenv(var):
print(f"✓ {var} 已配置")
        else:
         print(f"✗ {var} 未配置")

if __name__ == "__main__":
    main()