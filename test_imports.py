#!/usr/bin/env python3
"""
测试导入结构和环境配置
"""

import os
import sys
from pathlib import Path

def test_imports():
    """测试当前导入结构"""
    print("🔍 测试Python环境和导入结构...")
    
    # 添加项目根目录到路径
    project_root = Path(__file__).parent
    sys.path.insert(0, str(project_root))
    
    print(f"项目根目录: {project_root}")
    print(f"Python路径: {sys.path[:3]}")  # 只显示前3个路径
    
    # 尝试基础导入
    try:
        import config
        print("✅ 成功导入 config 模块")
        
        # 检查config模块内容
        print(f"config模块内容: {dir(config)}")
        
   # 检查模型适配器
   if hasattr(config, 'UnifiedModelManager'):
            print("✅ UnifiedModelManager 可用")
        else:
       print("❌ UnifiedModelManager 不可用")
            
        # 检查Dify集成
        if hasattr(config, 'DifyIntegration'):
            print("✅ DifyIntegration 可用")
        else:
     print("❌ DifyIntegration 不可用")
       
    except ImportError as e:
        print(f"❌ 导入失败: {e}")
        return False
    
    return True

def check_environment():
    """检查环境配置"""
    print("\n🔧 检查环境配置...")
    
 # 检查环境文件
    env_files = ['.env', '.env.example', '.env.chinese-models.example']
    for env_file in env_files:
        if os.path.exists(env_file):
     print(f"✅ 找到 {env_file}")
        else:
            print(f"⚠️ 未找到 {env_file}")
    
    # 检查关键环境变量
    key_vars = [
        'DEEPSEEK_API_KEY', 'ZHIPU_API_KEY', 'MOONSHOT_API_KEY',
        'OPENAI_API_KEY', 'DIFY_API_KEY', 'RAGFLOW_API_KEY'
    ]
    
    configured_vars = 0
    for var in key_vars:
        if os.getenv(var):
       print(f"✅ {var}: 已配置")
       configured_vars += 1
     else:
            print(f"❌ {var}: 未配置")
    
    print(f"\n环境变量配置: {configured_vars}/{len(key_vars)}")

def check_dependencies():
 """检查项目依赖"""
    print("\n📦 检查依赖包...")
    
    required_packages = [
        'langchain', 'langchain-core', 'langchain-community',
        'deepseek-api', 'zhipuai', 'httpx'
    ]
    
    available_packages = 0
    for package in required_packages:
     try:
            __import__(package)
      print(f"✅ {package}: 已安装")
  available_packages += 1
except ImportError:
            print(f"❌ {package}: 未安装")
    
    print(f"\n依赖包状态: {available_packages}/{len(required_packages)}")
    
    return available_packages == len(required_packages)

def main():
    """主测试函数"""
    print("🚀 LangChain 1.0 环境检测工具")
    print("=" * 50)
    
    # 运行所有检查
    imports_ok = test_imports()
    check_environment()
    deps_ok = check_dependencies()
    
 print("\n" + "=" * 50)
    print("📊 检查结果摘要:")
    print(f"✅ 导入测试: {'通过' if imports_ok else '失败'}")
    print(f"✅ 依赖检查: {'通过' if deps_ok else '失败'}")
    
    if imports_ok and deps_ok:
   print("\n🎉 环境配置完整，可以开始测试模型功能！")
    else:
     print("\n🔧 环境配置不完整，建议：")
        if not imports_ok:
      print("  - 检查config模块是否完整")
        if not deps_ok:
    print("  - 安装缺失的依赖包")
print("  - 配置环境变量文件")

if __name__ == "__main__":
    main()