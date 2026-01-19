#!/usr/bin/env python3
"""
快速开发调试脚本 - 修复版
基于CLAUDE.md中的设计快速测试中国AI模型和企业工作流集成
"""

import os
import sys
import logging
import time
from datetime import datetime
from typing import Dict, Any, Optional

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_basic_imports():
    """测试基础导入功能"""
    logger.info("🚀 测试基础导入功能")
    
    try:
        from config import UnifiedModelManager, get_chat_model, get_embeddings
      logger.info("✅ 基础模块导入成功")
     return True
    except ImportError as e:
        logger.error(f"❌ 基础模块导入失败: {e}")
        return False
    except Exception as e:
      logger.error(f"❌ 意外错误: {e}")
   return False

def test_model_initialization():
    """测试模型初始化"""
    logger.info("🔧 测试模型初始化")
    
    try:
        from config import UnifiedModelManager
        
        # 测试默认模型管理器
        manager = UnifiedModelManager()
     logger.info(f"✅ 默认模型管理器创建成功: {manager.provider}")
     
     # 测试指定提供商
  managers = {}
        for provider in ["deepseek", "zhipu", "moonshot"]:
            try:
      managers[provider] = UnifiedModelManager(provider)
       logger.info(f"✅ {provider} 管理器创建成功")
    except Exception as e:
        logger.warning(f"⚠️ {provider} 管理器创建失败: {e}")
                
  return managers
    except Exception as e:
        logger.error(f"❌ 模型初始化测试失败: {e}")
        return {}

def test_workflow_integration():
    """测试工作流集成初始化"""
    logger.info("🔄 测试工作流集成")
    
    try:
  from config import DifyIntegration, RAGFlowIntegration
        
        # 测试Dify集成
        try:
 dify = DifyIntegration()
logger.info("✅ Dify集成初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ Dify集成初始化失败: {e}")
            
     # 测试RAGFlow集成
        try:
            ragflow = RAGFlowIntegration()
    logger.info("✅ RAGFlow集成初始化成功")
        except Exception as e:
            logger.warning(f"⚠️ RAGFlow集成初始化失败: {e}")
  
        return True
     except Exception as e:
        logger.error(f"❌ 工作流集成测试失败: {e}")
        return False

def check_environment_status():
    """检查环境配置状态"""
    logger.info("🔍 检查环境配置状态")
    
    # 必需的环境变量
    required_env_vars = {
     "DEEPSEEK_API_KEY": "深度求索",
      "ZHIPU_API_KEY": "智谱GLM",
   "MOONSHOT_API_KEY": "月之暗面Kimi",
    "OPENAI_API_KEY": "OpenAI - 国际对标"
    }
    
    logger.info("检查必需的环境变量:")
    configured = 0
    missing = []
    
    for env_var, description in required_env_vars.items():
        if os.getenv(env_var) and os.getenv(env_var).strip():
      logger.info(f"✅ {description}: {env_var} 已配置")
     configured += 1
        else:
  logger.warning(f"⚠️ {description}: {env_var} 未配置")
       missing.append(env_var)
    
    # 工作流工具环境变量
    workflow_vars = {
        "DIFY_API_KEY": "Dify工作流",
        "DIFY_BASE_URL": "Dify基础URL",
   "RAGFLOW_API_KEY": "RAGFlow工作流",
        "RAGFLOW_BASE_URL": "RAGFlow基础URL"
    }
    
    logger.info("\n检查工作流工具配置:")
    for env_var, description in workflow_vars.items():
 if os.getenv(env_var) and os.getenv(env_var).strip():
logger.info(f"✅ {description}: {env_var} 已配置")
        else:
     logger.info(f"ℹ️ {description}: {env_var} 可选配置")
    
    logger.info(f"\n环境配置摘要:")
    logger.info(f"✅ 必需配置: {configured}/{len(required_env_vars)}")
 
    if missing:
        logger.warning(f"❌ 缺失配置: {', '.join(missing)}")
  else:
        logger.info("🎉 所有必需配置已完成")
    
    return configured == len(required_env_vars)

def test_error_handling():
    """测试错误处理机制"""
    logger.info("🧪 测试错误处理机制")
  
    try:
        from config import UnifiedModelManager
        
 # 测试无效提供商处理
        try:
     invalid_manager = UnifiedModelManager("invalid_provider")
   logger.error("❌ 应该抛出无效提供商异常")
            return False
        except ValueError as e:
            logger.info(f"✅ 无效提供商正确处理: {e}")
 except Exception as e:
     logger.error(f"❌ 错误处理测试失败: {e}")
        return False
      
        return True
    except Exception as e:
        logger.error(f"❌ 错误处理机制测试失败: {e}")
    return False

def generate_summary_report():
    """生成测试摘要报告"""
    logger.info("📊 生成测试摘要报告")
    
    report = {
        "timestamp": datetime.now().isoformat(),
     "python_version": sys.version,
   "working_directory": os.getcwd(),
    "test_results": {}
    }
    
    # 运行所有基本测试
    tests = [
     ("基础导入", test_basic_imports),
     ("模型初始化", test_model_initialization),
        ("工作流集成", test_workflow_integration),
        ("环境配置", check_environment_status),
        ("错误处理", test_error_handling)
    ]
    
    for test_name, test_func in tests:
        try:
            logger.info(f"运行测试: {test_name}")
   result = test_func()
  report["test_results"][test_name] = "通过" if result else "失败"
            logger.info(f"✅ {test_name}: {'通过' if result else '失败'}")
        except Exception as e:
  report["test_results"][test_name] = f"错误: {e}"
            logger.error(f"❌ {test_name}: 错误: {e}")
    
    # 计算总体状态
    passed_tests = sum(1 for result in report["test_results"].values() if result == "通过")
 total_tests = len(report["test_results"])
    
    report["overall_status"] = "通过" if passed_tests == total_tests else f"{passed_tests}/{total_tests} 通过"
    
    logger.info(f"\n🎯 测试完成 - 总体状态: {report['overall_status']}")
 return report

def main():
    """主函数 - 运行完整的快速测试"""
    logger.info("🚀 开始 LangChain 1.0 中国AI模型快速测试")
    logger.info("版本: 2.0.0 - 支持中国大模型和AI工作流集成")
    logger.info("=" * 60)
    
    # 运行测试
    report = generate_summary_report()
    
    # 显示详细结果
    logger.info("\n" + "=" * 60)
  logger.info("📋 详细测试结果:")
  for test_name, result in report["test_results"].items():
        status_icon = "✅" if result == "通过" else "❌"
        logger.info(f"{status_icon} {test_name}: {result}")
    
    # 显示总体状态
    logger.info("\n" + "=" * 60)
    logger.info(f"🏆 最终状态: {report['overall_status']}")
    
    # 提供建议
    if report["overall_status"] != "通过":
     logger.info("\n🔧 建议操作:")
     logger.info("1. 确保已安装所有必需的依赖包")
        logger.info("2. 正确配置环境变量")
        logger.info("3. 检查网络连接和API密钥有效性")
        logger.info("4. 如果问题持续，参考项目文档或寻求帮助")
    else:
   logger.info("\n🎉 所有测试通过！你的环境配置正确。")
  
    return report

if __name__ == "__main__":
    main()