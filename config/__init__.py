"""
配置模块
包含多模型适配、工作流集成等配置"""

from .model_adapters import (
    ModelAdapterFactory,
    UnifiedModelManager,
    get_chat_model,
    get_embeddings,
    get_llm
)

from .dify_integration import (
    DifyClient,
    DifyIntegration,
    create_dify_tool
)

from .ragflow_integration import (
    RAGFlowClient,
    RAGFlowIntegration,
    create_ragflow_tool
)

__all__ = [
    # Model adapters
    "ModelAdapterFactory",
    "UnifiedModelManager", 
    "get_chat_model",
    "get_embeddings",
    "get_llm",
    
    # Dify integration
    "DifyClient",
    "DifyIntegration",
    "create_dify_tool",
    
    # RAGFlow integration
    "RAGFlowClient", 
    "RAGFlowIntegration",
    "create_ragflow_tool"
]

# 配置版本
VERSION = "2.0.0"  # 升级到2.0以支持中国大模型和AI工作流集成
PROVIDER_SUPPORT = {
    "chinese": ["deepseek", "zhipu", "moonshot", "dashscope", "baichuan"],
    "international": ["openai", "azure", "anthropic", "google"],
    "local": ["ollama", "localai"]
}

# 默认配置
DEFAULT_PROVIDER = "deepseek"
DEFAULT_EMBEDDING_PROVIDER = "zhipu"
SUPPORTED_WORKFLOW_TOOLS = ["dify", "ragflow", "langflow", "flowise", "n8n"]