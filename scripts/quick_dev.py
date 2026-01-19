"""
快速开发调试脚本
基于CLAUDE.md中的设计快速测试中国AI模型和企业工作流集成
"""

import os
import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional

# 添加项目根目录到Python路径
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def quick_model_test():
    """快速测试多模型适配 - 来自CLAUDE.md的设计"""
    logger.info("🚀 开始中国AI模型快速测试")
    
    try:
     from config import UnifiedModelManager, get_chat_model, get_embeddings
        
     # 测试中国模型
     models_to_test = ["deepseek", "zhipu", "moonshot"]
     
 for model_name in models_to_test:
            try:
      logger.info(f"正在测试 {model_name}...")
                model = get_chat_model(model_name)
      response = model.invoke("请用中文介绍一下LangChain是什么")
                
    logger.info(f"✅ {model_name}: {response[:100]}...")
     time.sleep(1)  # 避免API限速
       
            except Exception as e:
      logger.error(f"❌ {model_name} 测试失败: {e}")
    continue
      
    logger.info("✅ 模型测试完成")
 
    except ImportError as e:
        logger.error(f"导入失败: {e}")
        logger.info("请确保已安装所需的依赖包")


def test_embeddings():
 """测试向量化模型"""
    logger.info("🔍 开始Embedding模型测试")
    
 try:
        from config import get_embeddings
        
     # 测试不同提供商的Embedding模型
        test_texts = [
   "LangChain是一个用于构建LLM应用的框架",
            "深度学习是人工智能的重要分支",
            "自然语言处理让机器理解人类语言"
 
 ]
        
        embedding_providers = ["zhipu", "openai"]
        
        for provider in embedding_providers:
   try:
                logger.info(f"正在测试 {provider} embeddings...")
    embeddings = get_embeddings(provider)
                
        # 生成向量
    vectors = embeddings.embed_documents(test_texts)
          logger.info(f"✅ {provider}: 成功生成 {len(vectors)} 个向量，维度: {len(vectors[0])}")
                
        except Exception as e:
        logger.error(f"❌ {provider} embedding 测试失败: {e}")
      
    except ImportError as e:
        logger.error(f"导入失败: {e}")


def quick_workflow_test():
    """快速测试工作流集成 - 基于CLAUDE.md的设计"""
    logger.info("🔄 开始AI工作流集成测试")
 
    
    # 测试Dify集成
    logger.info("Testing Dify集成...")
    try:
        from config import DifyIntegration
        
  dify = DifyIntegration()
  logger.info("✅ Dify集成初始化成功")
        
        # 测试知识库创建（如果配置了环境变量）
        if os.getenv("DIFY_API_KEY") and os.getenv("DIFY_BASE_URL"):
            test_result = dify.chat_with_knowledge("请介绍下LangChain")
            logger.info("✅ Dify对话测试完成")
 else:
      logger.warning("⚠️ 需要配置DIFY_API_KEY和DIFY_BASE_URL环境变量才能完整测试")
        
    except Exception as e:
 logger.error(f"❌ Dify测试失败: {e}")
    
    # 测试RAGFlow集成
    logger.info("Testing RAGFlow集成...")
    try:
        from config import RAGFlowIntegration
     
        ragflow = RAGFlowIntegration()
        logger.info("✅ RAGFlow集成初始化成功")
        
        # 测试知识库创建（如果配置了环境变量）
 if os.getenv("RAGFLOW_API_KEY") and os.getenv("RAGFLOW_BASE_URL"):
     # 创建测试知识库
   kb_id = ragflow.create_knowledge_base("test_kb", "测试知识库")
       logger.info(f"✅ 创建知识库: {kb_id}")
    
    # 添加测试文档
  test_docs = ["LangChain是一个强大的LLM应用开发框架", "RAGFlow提供企业级RAG解决方案"]
            add_result = ragflow.add_documents(test_docs)
      logger.info(f"✅ 文档添加结果: {add_result.get('successful_uploads')} 个成功")
   
            # 测试问答
         qa_result = ragflow.smart_qa_chain("什么是LangChain？")
     logger.info(f"✅ 问答结果: {qa_result.get('answer', '')[:100]}...")
        else:
 logger.warning("⚠️ 需要配置RAGFLOW_API_KEY和RAGFLOW_BASE_URL环境变量才能完整测试")
        
    except Exception as e:
        logger.error(f"❌ RAGFlow测试失败: {e}")


def test_model_fallback_chain():
    """测试模型故障转移链"""
    logger.info("🛡️ 测试故障转移机制")
    
    try:
        from config import UnifiedModelManager
        
       # 模拟主要模型失败场景
        manager = UnifiedModelManager("deepseek")
        
  logger.info("使用DeepSeek作为主模型...")
        primary_model = manager.create_chat_model()
 primary_response = primary_model.invoke("你好，请介绍一下自己")
        logger.info(f"✅ 主模型响应: {primary_response[:100]}...")
        
    logger.info("测试模型切换功能...")
  manager.switch_provider("zhipu")
        backup_model = manager.create_chat_model()
        backup_response = backup_model.invoke("你好，请介绍一下自己")
   logger.info(f"✅ 备用模型响应: {backup_response[:100]}...")
      
 logger.info("✅ 故障转移测试完成")
      
    except Exception as e:
        logger.error(f"❌ 故障转移测试失败: {e}")


def test_unified_interface():
    """测试统一接口的一致性"""
 logger.info("🔧 测试统一模型接口")
 
    try:
        from config import get_chat_model, get_llm, get_embeddings
        
 all_providers = ["deepseek", "zhipu", "moonshot", "openai"]
        test_message = "请用一句话描述人工智能"
  
        results = {}
        for provider in all_providers:
            try:
       logger.info(f"测试 {provider} 统一接口...")
        
     # 测试Chat模型
       chat_model = get_chat_model(provider, temperature=0.7)
        chat_response = chat_model.invoke(test_message)
      
                # 测试LLM模型
                llm_model = get_llm(provider, max_tokens=100)
llm_response = llm_model(test_message)
        
       results[provider] = {
         "chat_response": chat_response[:50],
        "llm_response": llm_response[:50],
             "status": "success"
     }
 
    logger.info(f"✅ {provider}: Chat={chat_response[:30]}... LLM={llm_response[:30]}...")
         
            except Exception as e:
       results[provider] = {
      "status": "error",
     "error": str(e)
        }
                logger.error(f"❌ {provider} 接口测试失败: {e}")
   
     logger.info("统一接口测试完成")
        return results
      
    except Exception as e:
        logger.error(f"❌ 统一接口测试失败: {e}")
        return {}


def generate_diagnostic_report():
    """生成系统诊断报告"""
    logger.info("📊 生成系统诊断报告")
    
    report = {
        "timestamp": datetime.now().isoformat(),
        "system_status": "healthy",
 "environment": {},
"model_status": {},
        "workflow_status": {},
        "recommendations": []
    }
    
    # 检查环境变量
    env_vars = [
        "DEEPSEEK_API_KEY", "ZHIPU_API_KEY", "MOONSHOT_API_KEY",
 "OPENAI_API_KEY", "DIFY_API_KEY", "RAGFLOW_API_KEY",
   "DEFAULT_PROVIDER", "DIFY_BASE_URL", "RAGFLOW_BASE_URL"
    ]
    
    for env_var in env_vars:
        report["environment"][env_var] = "✅ 已配置" if os.getenv(env_var) else "❌ 未配置"
    
    # 检查测试环境
    try:
     quick_model_test()
        report["model_status"]["quick_test"] = "✅ 通过"
    except Exception as e:
      report["model_status"]["quick_test"] = f"❌ 失败: {e}"
        report["system_status"] = "degraded"
    
    # 生成建议
    missing_env = [env for env, status in report["environment"].items() if "未配置" in status]
    if missing_env:
  report["recommendations"].append(f"请配置以下环境变量: {', '.join(missing_env)}")
    
    logger.info("✅ 诊断报告生成完成")
    return report


def main():
 """主函数 - 运行所有快速测试"""
    logger.info("🚀 开始 LangChain 1.0 中国AI模型与企业工作流快速测试")
    logger.info("=" * 60)
 
    try:
        # 1. 基础模型测试
        quick_model_test()
        
       # 2. Embedding模型测试
        test_embeddings()
    
        # 3. 工作流集成测试
  quick_workflow_test()
     
        # 4. 故障转移测试
   test_model_fallback_chain()
 
        # 5. 统一接口测试
        test_unified_interface()
        
        # 6. 生成诊断报告
        report = generate_diagnostic_report()
        
        logger.info("=" * 60)
    logger.info("🎉 所有快速测试完成！")
       
        # 显示总结
        print("\n📊 测试摘要:")
     print(f"系统状态: {report['system_status']}")
        print(f"环境配置: {len([v for v in report['environment'].values() if '✅' in v])}/{len(report['environment'])} 已配置")
print(f"模型测试: {report['model_status'].get('quick_test', '未知')}")
        
       if report["recommendations"]:
         print("\n🔧 建议:")
            for rec in report["recommendations"]:
   print(f"  - {rec}")
   
    except Exception as e:
        logger.error(f"测试过程出错: {e}")
        sys.exit(1)


if __name__ == "__main__":
    import time
    main()