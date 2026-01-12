"""
多模型适配器模块
Multi-Model Adapter for Chinese and International LLM Providers
统一接口支持：DeepSeek, 智谱GLM, 月之暗面Kimi, 通义千问, 百川, OpenAI, Azure, Google等
"""

import os
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod
from dataclasses import dataclass

from langchain.llms.base import LLM
from langchain.chat_models.base import BaseChatModel
from langchain.embeddings.base import Embeddings

from config.settings import get_model_config


@dataclass
class ModelConfig:
    """模型配置数据类"""
    api_key: str
    base_url: str
    model_name: str
    max_tokens: int = 4096
    temperature: float = 0.7
    timeout: int = 60


class BaseModelAdapter(ABC):
    """基础模型适配器类"""
    
    def __init__(self, config: ModelConfig):
        self.config = config
        self._client = None
    
    @abstractmethod
    def create_llm(self) -> LLM:
        """创建LLM实例"""
        pass
    
    @abstractmethod
    def create_chat_model(self) -> BaseChatModel:
        """创建Chat模型实例"""
        pass
    
    @abstractmethod
    def create_embeddings(self) -> Embeddings:
        """创建Embeddings实例"""
        pass
    
    @property
    def provider_name(self) -> str:
        """返回提供商名称"""
        return self.__class__.__name__.replace('Adapter', '').lower()


class DeepSeekAdapter(BaseModelAdapter):
    """深度求索适配器"""
    
    def create_llm(self) -> LLM:
        """创建DeepSeek LLM实例"""
        from langchain.llms import DeepSeek
        return DeepSeek(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
    
    def create_chat_model(self) -> BaseChatModel:
        """创建DeepSeek Chat模型"""
        from langchain.chat_models import ChatDeepSeek
        return ChatDeepSeek(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
    
    def create_embeddings(self) -> Embeddings:
        """创建DeepSeek Embeddings"""
        from langchain.embeddings import DeepSeekEmbeddings
        return DeepSeekEmbeddings(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            model="deepseek-embedding"
        )


class ZhipuAdapter(BaseModelAdapter):
    """智谱GLM适配器"""
    
    def create_llm(self) -> LLM:
        """创建智谱GLM LLM实例"""
        from langchain.llms import ZhipuAI
        return ZhipuAI(
            api_key=self.config.api_key,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
    
    def create_chat_model(self) -> BaseChatModel:
        """创建智谱GLM Chat模型"""
        from langchain.chat_models import ChatZhipuAI
        return ChatZhipuAI(
            api_key=self.config.api_key,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
    
    def create_embeddings(self) -> Embeddings:
        """创建智谱Embeddings"""
        from langchain.embeddings import ZhipuAIEmbeddings
        return ZhipuAIEmbeddings(
            api_key=self.config.api_key,
            model="embedding-2"
        )


class MoonshotAdapter(BaseModelAdapter):
    """月之暗面Kimi适配器"""
    
    def create_llm(self) -> LLM:
        """创建Kimi LLM实例"""
        from langchain.llms import Moonshot
        return Moonshot(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
    
    def create_chat_model(self) -> BaseChatModel:
        """创建Kimi Chat模型"""
        from langchain.chat_models import ChatMoonshot
        return ChatMoonshot(
            api_key=self.config.api_key,
            base_url=self.config.base_url,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
    
    def create_embeddings(self) -> Embeddings:
        """Kimi暂时没有Embedding模型，使用其他替代"""
        # 回退到Zhipu Embeddings
        from langchain.embeddings import ZhipuAIEmbeddings
        return ZhipuAIEmbeddings(
            api_key=os.getenv("ZHIPU_API_KEY"),
            model="embedding-2"
        )


class OpenAIAdapter(BaseModelAdapter):
    """OpenAI适配器"""
    
    def create_llm(self) -> LLM:
        """创建OpenAI LLM实例"""
        from langchain.llms import OpenAI
        return OpenAI(
            api_key=self.config.api_key,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
    
    def create_chat_model(self) -> BaseChatModel:
        """创建OpenAI Chat模型"""
        from langchain.chat_models import ChatOpenAI
        return ChatOpenAI(
            api_key=self.config.api_key,
            model=self.config.model_name,
            max_tokens=self.config.max_tokens,
            temperature=self.config.temperature
        )
    
    def create_embeddings(self) -> Embeddings:
        """创建OpenAI Embeddings"""
        from langchain.embeddings import OpenAIEmbeddings
        return OpenAIEmbeddings(
            api_key=self.config.api_key,
            model="text-embedding-ada-002"
        )


# 模型适配器工厂
class ModelAdapterFactory:
    """模型适配器工厂类"""
    
    _adapters = {
        'deepseek': DeepSeekAdapter,
        'zhipu': ZhipuAdapter,
        'moonshot': MoonshotAdapter,
        'openai': OpenAIAdapter,
        # 可以继续添加更多适配器
    }
    
    @classmethod
    def create_adapter(cls, provider: str, config: ModelConfig) -> BaseModelAdapter:
        """创建适配器实例"""
        if provider not in cls._adapters:
            raise ValueError(f"Unsupported provider: {provider}. Supported providers: {list(cls._adapters.keys())}")
        
        adapter_class = cls._adapters[provider]
        return adapter_class(config)
    
    @classmethod
    def register_adapter(cls, provider: str, adapter_class: type):
        """注册新的适配器"""
        cls._adapters[provider] = adapter_class
    
    @classmethod
    def get_supported_providers(cls) -> List[str]:
        """获取支持的所有提供商"""
        return list(cls._adapters.keys())


# 统一模型管理器
class UnifiedModelManager:
    """统一模型管理器 - 对外提供统一的API接口"""
    
    def __init__(self, provider: str = None):
        self.provider = provider or os.getenv("DEFAULT_PROVIDER", "deepseek")
        self.config = self._load_provider_config(self.provider)
        self.adapter = ModelAdapterFactory.create_adapter(self.provider, self.config)
    
    def _load_provider_config(self, provider: str) -> ModelConfig:
        """加载指定提供商的配置"""
        config_mapping = {
            'deepseek': {
                'api_key': os.getenv("DEEPSEEK_API_KEY"),
                'base_url': os.getenv("DEEPSEEK_BASE_URL"),
                'model_name': os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
            },
            'zhipu': {
                'api_key': os.getenv("ZHIPU_API_KEY"),
                'base_url': os.getenv("ZHIPU_BASE_URL"),
                'model_name': os.getenv("ZHIPU_MODEL", "glm-4")
            },
            'moonshot': {
                'api_key': os.getenv("MOONSHOT_API_KEY"),
                'base_url': os.getenv("MOONSHOT_BASE_URL"),
                'model_name': os.getenv("MOONSHOT_MODEL", "moonshot-v1-8k")
            },
            'openai': {
                'api_key': os.getenv("OPENAI_API_KEY"),
                'base_url': os.getenv("OPENAI_BASE_URL"),
                'model_name': os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")
            }
        }
        
        if provider not in config_mapping:
            raise ValueError(f"Unsupported provider: {provider}")
        
        config_data = config_mapping[provider]
        
        # 验证必需的配置
        if not config_data['api_key']:
            raise ValueError(f"{provider.upper()}_API_KEY is required in environment variables")
        
        return ModelConfig(**config_data)
    
    def create_llm(self) -> LLM:
        """创建LLM实例"""
        return self.adapter.create_llm()
    
    def create_chat_model(self) -> BaseChatModel:
        """创建Chat模型实例"""
        return self.adapter.create_chat_model()
    
    def create_embeddings(self) -> Embeddings:
        """创建Embeddings实例"""
        return self.adapter.create_embeddings()
    
    def switch_provider(self, new_provider: str):
        """切换模型提供商"""
        self.provider = new_provider
        self.config = self._load_provider_config(new_provider)
        self.adapter = ModelAdapterFactory.create_adapter(new_provider, self.config)
    
    def get_current_provider(self) -> str:
        """获取当前提供商"""
        return self.provider


# 便捷函数 - 简化使用
def get_chat_model(provider: str = None, **kwargs) -> BaseChatModel:
    """获取聊天模型的便捷函数"""
    manager = UnifiedModelManager(provider)
    chat_model = manager.create_chat_model()
    
    # 应用额外的参数
    for key, value in kwargs.items():
        if hasattr(chat_model, key):
            setattr(chat_model, key, value)
    
    return chat_model


def get_embeddings(provider: str = None, **kwargs) -> Embeddings:
    """获取Embeddings的便捷函数"""
    manager = UnifiedModelManager(provider)
    embeddings = manager.create_embeddings()
    
    # 应用额外的参数
    for key, value in kwargs.items():
        if hasattr(embeddings, key):
            setattr(embeddings, key, value)
    
    return embeddings


def get_llm(provider: str = None, **kwargs) -> LLM:
    """获取LLM的便捷函数"""
    manager = UnifiedModelManager(provider)
    llm = manager.create_llm()
    
    # 应用额外的参数
    for key, value in kwargs.items():
        if hasattr(llm, key):
            setattr(llm, key, value)
    
    return llm