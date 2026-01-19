#!/usr/bin/env python3
"""
LangChain L3 Advanced - Week 12  统一接口层（企业级多平台集成）
课程标题: 多平台统一AI工作流API
学习目标:
  - 设计并实施统一AI工作流API架构
  - 实现Dify/RAGFlow/n8n智能路由选择
  - 学习统一认证与权限管理体系
  - 掌握动态负载均衡与故障转移
作者: Claude Code 教学团队
创建时间: 2024-01-17
版本: 1.0.0
先决条件: 完成03_n8n_workflow_automation.py
"""

import asyncio
import json
import uuid
import time
import random
import re
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, field
from enum import Enum
from abc import ABC, abstractmethod
import logging
import httpx
from pydantic import BaseModel, Field, validator
import toml

# 企业级集成依赖
try:
    from fastapi import FastAPI, HTTPException, Depends, Request, Response
    from fastapi.middleware.cors import CORSMiddleware
    from fastapi.responses import JSONResponse
    fastapi_available = True
    print("✅ FastAPI集成成功")
except ImportError:
    fastapi_available = False
    print("⚠️ FastAPI导入失败，使用基于泛化HTTP的备用实现")

try:
    import redis.asyncio as redis
    redis_available = True
    print("✅ Redis集成成功，支持缓存和会话管理")
except ImportError:
    redis_available = False
    print("⚠️ Redis异步客户端导入失败")

try:
    from cachetools import TTLCache
    cachetools_available = True
    print("✅ Cachetools LRU缓存管理集成")
except ImportError:
    cachetools_available = False
    print("⚠️ Cachetools导入失败（可选依赖）")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# -----------------------------
# 企业级数据模型定义
# -----------------------------

class AIPlatform(Enum):
    """AI工作流平台枚举"""
    DIFY = "dify"
    RAGFLOW = "ragflow"
    N8N = "n8n"
    LANGFLOW = "langflow"
    FLOWISE = "flowise"
    CUSTOM = "custom"
    UNIFIED = "unified"  # 动态平台选择

class QueryPriority(Enum):
    """查询优先级"""
    CRITICAL = "critical"      # 关键实时查询
    HIGH = "high"              # 高优先级
    NORMAL = "normal"          # 标准优先级
    BATCH = "batch"           # 批量处理

class ResponseFormat(Enum):
    """响应格式"""
    JSON = "json"
    STREAM = "stream"
    MARKDOWN = "markdown"
    XML = "xml"

@dataclass
class EnterpriseAPIConfig:
    """统一企业API网关配置"""
    # 基础服务配置
    api_name: str = "企业级AI统一服务API"
    version: str = "v1.0.0"
    api_key: str = ""
    base_url: str = "https://ai-unified-api.enterprise.local"
    listen_port: int = 8000
    
    # 平台集成端点
    platform_endpoints: Dict[str, str] = field(default_factory=lambda: {
        "dify": "http://dify-api:3000/api/v1",
        "ragflow": "http://ragflow-api:9380/api/v1", 
        "n8n": "http://n8n-api:5678/api/v1",
        "langflow": "http://langflow-api:3000/api/v1",
        "custom": "http://custom-api:8080/api/v1"
    })
    
    # 智能决策配置
    decision_engine_enabled: bool = True
    caching_strategy: str = "redis_memory_hybrid"  # redis/memory/cachetools/hybrid
    fault_tolerance_enabled: bool = True
    concurrent_request_limit: int = 1000
    request_timeout_seconds: int = 60
    
    # 企业级性能
    auto_scaling_enabled: bool = True
    load_balancer_type: str = "intelligent"  # round_robin/intelligent/failover
    circuit_breaker_threshold: float = 0.8
    retry_policy: Dict[str, Any] = field(default_factory=lambda: {
        "max_retries": 3,
        "retry_delay": 1.0,
        "exponential_backoff": True,
        "retry_on": ["timeout", "connection_error", "rate_limit"]
    })
    
    # 安全与合规
    authentication_methods: List[str] = field(default_factory=lambda: ["jwt", "api_key", "sso"])
    encryption_enabled: bool = True
    audit_logging_enabled: bool = True  
    data_retention_days: int = 90
    compliance_standards: List[str] = field(default_factory=lambda: ["ISO27001", "SOC2"])

@dataclass
class UnifiedQueryRequest:
    """统一查询请求"""
    query: str = Field(..., min_length=1, max_length=2000)
    platform_preference: Optional[str] = Field(default=None, description="平台偏好 AIPlatform")
    context: Optional[List[str]] = Field(default_factory=list, max_items=100)
    priority: QueryPriority = Field(default=QueryPriority.NORMAL)
    response_format: ResponseFormat = Field(default=ResponseFormat.JSON)
    language: str = Field(default="zh", description="回答语言")
    metadata: Optional[Dict[str, Any]] = Field(default_factory=dict)
    request_tracking: Optional[Dict[str, Any]] = None

@dataclass 
class UnifiedQueryResponse:
    """统一查询响应"""
    request_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    query: str
    answer: str
    platform_used: str
    confidence_score: float = 0.0
    sources: List[Dict[str, Any]] = field(default_factory=list)
    processing_time_ms: int
    metadata: Dict[str, Any] = field(default_factory=dict)
    cost_breakdown: Optional[Dict[str, str]] = None
    next_actions: Optional[List[str]] = None
    user_feedback_invited: bool = False
    timestamp: datetime = field(default_factory=datetime.now)

# -----------------------------
# 平台抽象接口
# -----------------------------

class IPlatformAdapter(ABC):
    """平台适配器接口"""
    
    @abstractmethod
    def get_platform_name(self) -> str:
        """获取平台名称"""
        pass
    
    @abstractmethod
    def get_platform_capabilities(self) -> List[str]:
        """获取平台能力清单"""
        pass
    
    @abstractmethod
    async def execute_query(self, query: UnifiedQueryRequest) -> Dict[str, Any]:
        """执行查询并返回结果"""
        pass
    
    @abstractmethod
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取性能指标"""
        pass

# -----------------------------
# 具体平台实现
# -----------------------------

class DifyPlatformAdapter(IPlatformAdapter):
    """Dify平台适配器"""
    
    def get_platform_name(self) -> str:
        return "dify"
    
    def get_platform_capabilities(self) -> List[str]:
        return ["chat_conversation", "knowledge_base", "document_qa", "workflow_automation", "multi_language"]
    
    async def execute_query(self, query: UnifiedQueryRequest, config: Dict[str, Any]) -> Dict[str, Any]:
        """调用Dify API执行查询"""
        
        logger.info(f"🗣️ 调用Dify平台执行查询 - 查询长度: {len(query.query)}")
        start_time = time.time()
        
        try:
            api_client = httpx.AsyncClient(timeout=30.0)
            
            # 构建Dify API请求
            dify_request = {
                "query": query.query,
                "inputs": {
                    "user_id": query.metadata.get("user_id", "anonymous"),
                    "context": query.context or [],
                    "language": query.language,
                    "metadata": query.metadata
                },
                "response_mode": "blocking" if query.response_format == ResponseFormat.JSON else "streaming",
                "user": query.metadata.get("session_id", "unified_api_user")
            }
            
            # 选择合适的应用（基于查询类型）
            app_config = self._select_dify_application(query)
            
            response = await api_client.post(
                f"{config['dify']}/chat/messages",
                json=dify_request,
                headers={"Authorization": f"Bearer {query.metadata.get('dify_app_key', 'demo_key')}"}
            )
            response.raise_for_status()
            
            result = response.json()
            
            # 标准化响应格式
            return {
                "platform": "dify",
                "answer": result.get("answer", ""),
                "confidence": result.get("metadata", {}).get("confidence", 0.75),
                "sources": result.get("retrieval_results", []),
                "processing_time": result.get("latency", time.time() - start_time),
                "model_used": result.get("model", "glm-4"),
                "metadata": result.get("metadata", {})
            }
            
        except Exception as e:
            logger.error(f"Dify平台查询失败: {str(e)}")
            return {"error": str(e), "platform": "dify"}
    
    def _select_dify_application(self, query: UnifiedQueryRequest) -> Dict[str, Any]:
        """根据查询内容选择合适的Dify应用"""
        
        # 简单的应用选择逻辑（实际中应使用更智能的分类）
        if "知识" in query.query or "信息" in query.query:
            return {"app_name": "企业知识助手", "knowledge_enabled": True}
        elif "对话" in query.query or "聊天" in query.query:
            return {"app_name": "智能客服", "chat_template_enabled": True}
        else:
            return {"app_name": "通用问答应用", "default_settings": True}
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取Dify平台性能指标"""
        return {
            "platform": "dify",
            "avg_response_time_ms": 320,
            "uptime_percentage": 99.5,
            "active_users": 1250,
            "trust_score": 0.82,
            "chinese_optimization": True,
            "knowledge_base_support": True
        }

class RAGFlowPlatformAdapter(IPlatformAdapter):
    """RAGFlow平台适配器"""
    
    def get_platform_name(self) -> str:
        return "ragflow"
    
    def get_platform_capabilities(self) -> List[str]:
        return ["enterprise_document_qa", "hybrid_retrieval", "chunk_reranking", "aoi_description", "enterprise_security"]
    
    async def execute_query(self, query: UnifiedQueryRequest, config: Dict[str, Any]) -> Dict[str, Any]:
        """调用RAGFlow API执行查询"""
        
        logger.info(f"🤖 调用RAGFlow平台 - 高级企业检索")
        start_time = time.time()
        
        try:
            api_client = httpx.AsyncClient(timeout=40.0)
            
            # 构建RAGFlow检索请求
            dataset_id = query.metadata.get("dataset_id", "default_kb")
            
            ragflow_retrieval = {
                "dataset_id": dataset_id,
                "question": query.query,
                "top_k": min(20, query.metadata.get("max_sources", 10)),
                "similarity_threshold": 0.7,
                "rerank": True,
                "language": query.language,
                "metadata": query.metadata
            }
            
            response = await api_client.post(
                f"{config['ragflow']}/retrieval",
                json=ragflow_retrieval,
                headers={"Authorization": f"Bearer {query.metadata.get('ragflow_api_key', 'demo_key')}"}
            )
    response.raise_for_status()
       
            retrieval_result = response.json()
   
 # 生成基于检索的答案
   generated_answer = await self._generate_answer_from_ragflow(retrieval_result, query.query)
         
      return {
                "platform": "ragflow",
   "answer": generated_answer["answer"],
       "confidence": generated_answer["confidence"],
                "sources": retrieval_result.get("chunks", []),
          "processing_time": generated_answer.get("processing_time", random.uniform(400, 800)),
      "model_used": generated_answer.get("model_used", "bge-reranker"),
     "metadata": generated_answer.get("metadata", {})
            }
            
        except Exception as e:
        logger.error(f"RAGFlow平台查询失败: {str(e)}")
      return {"error": str(e), "platform": "ragflow"}
  
    async def _generate_answer_from_ragflow(self, retrieval_result: Dict[str, Any], 
  query: str) -> Dict[str, Any]:
    """基于检索结果生成最终答案"""
        
       if not retrieval_result.get("chunks"):
      return {
  "answer": "根据企业知识库检索，未找到相关信息。",
                "confidence": 0.0,
              "model_used": "ragflow",
      "metadata": {"error": "no_relevant_documents"}
   }
    
        # 生成模拟回答（实际应该使用LLM生成）
        chunks = retrieval_result["chunks"]
        avg_confidence = sum(chunk.get("score", 0.0) for chunk in chunks) / len(chunks)
    
        return {
          "answer": f"基于企业知识库检索到 {len(chunks)} 个相关文档，主要内容涵盖了您的查询：...",
     "confidence": avg_confidence,
    "model_used": "ragflow_enterprise_glm",
            "processing_time": len(chunks) * 35 + 100,  # 模拟处理时间
            "metadata": {"chunks_analyzed": len(chunks)}
        }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取RAGFlow平台性能指标"""
        return {
    "platform": "ragflow",
            "avg_response_time_ms": 680,
    "uptime_percentage": 99.2,
            "retrieval_accuracy": 0.88,
    "enterprise_grade": True,
       "document_processing_metrics": True,
  "security_classification": "enterprise"
        }

class N8NPlatformAdapter(IPlatformAdapter):
  """n8n平台适配器"""
    
    def get_platform_name(self) -> str:
 return "n8n"
    
    def get_platform_capabilities(self) -> List[str]:
   return ["workflow_automation", "multi_step_processing", "webhook_integration", "business_task_layout", "notification_systems"]
    
    async def execute_query(self, query: UnifiedQueryRequest) -> Dict[str, Any]:
 """调用n8n工作流执行复杂处理"""
        
        logger.info(f"⚙️ 调用n8n平台工作流 - 复杂多步骤处理")
    
        try:
     config = self.client.config.platform_endpoints["n8n"]
            
   # 选择合适的n8n工作流运行
            workflow_params = {
     "query": query.query,
     "context": query.context,
                "priority": query.priority.value,
      "metadata": query.metadata,
                "enterprise_session": query.metadata.get("enterprise_session_id", "default")
            }
            
     # 执行工作流（这里简化为调用工作流执行）
    workflow_result = await self._execute_enterprise_workflow(config, workflow_params)
     
        return {
         "platform": "n8n",
      "answer": workflow_result.get("final_output", ""),
                "confirmation": workflow_result.get("confirmation", "操作成功完成"), 
    "suggested_actions": workflow_result.get("next_actions", []),
         "processing_time": workflow_result.get("processing_time", random.uniform(300, 900)),
                "model_used": workflow_result.get("primary_model", "enterprise_pipeline"),
        "metadata": {
             "workflow_steps": workflow_result.get("steps_executed", 1),
         "notifications_sent": workflow_result.get("notifications", 0),
            "business_logic_completed": True
     }
      }
      
        except Exception as e:
         logger.error(f"n8n平台工作流执行失败: {str(e)}")
    return {"error": str(e), "platform": "n8n"}
    
    async def _execute_enterprise_workflow(self, config: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """执行企业级n8n工作流"""
   
        api_client = httpx.AsyncClient(timeout=60.0)
   
        async with api_client:
            try:
                response = await api_client.post(
   f"{config}/workflows/execute",
                    json=params
                )
       response.raise_for_status()
       return response.json()
     
            except Exception:
     # 回退到模拟工作流结果
                return {
  "final_output": f"复杂的业务处理已计划并完成。参数: {len(json.dumps(params))} 字符",
      "confirmation": "工作流执行确认",
          "next_actions": ["等待人工审核", "发送通知"],
           "steps_executed": 3,
                    "processing_time": random.uniform(200, 800)
   }
    
    def get_performance_metrics(self) -> Dict[str, Any]:
        """获取n8n平台性能指标"""
        return {
     "platform": "n8n",
      "avg_workflow_time_ms": 750,
         "workflow_success_rate": 0.94,
     "step_execution_reliability": 0.96,
            "enterprise_automation_grade": True,
            "multi_step_complexity": "advanced",
  "api_integration_capable": True
    }

# -----------------------------
# 智能决策引擎
# -----------------------------

class EnterpriseDecisionEngine:
 """企业级AI平台智能决策引擎"""
    
    def __init__(self, config: EnterpriseAPIConfig):
        self.config = config
  self.platform_quality_matrix = self._initialize_quality_matrix()
     self.usage_metrics_history = self._initialize_metrics_history()
        self.recent_performance_stats = {}
        
        logger.info("🧠 Enterprise AI决策引擎初始化完成")
    
    def _initialize_quality_matrix(self) -> Dict[str, Dict[str, float]]:
    """初始化平台质量评估矩阵"""
        
        # 预配置的平台能力评分
        return {
            "dify": {
     "chat_conversation": 0.85,
            "knowledge_base": 0.88,
 "document_qa": 0.82,
        "workflow_automation": 0.75,
         "multi_language": 0.90,
            "enterprise_grade": 0.78
    },
   "ragflow": {
                "enterprise_document_qa": 0.92,
     "hybrid_retrieval": 0.89,
          "chunk_reranking": 0.87,
       "aoi_description": 0.85,
          "enterprise_security": 0.93,
       "scalability": 0.90
    },
     "n8n": {
 "workflow_automation": 0.95,
    "multi_step_processing": 0.90,
          "webhook_integration": 0.88,
                "business_task_layout": 0.86,    
      "notification_systems": 0.85,
    "enterprise_integration": 0.82
   }
  }
    
    def _initialize_metrics_history(self) -> Dict[str, List[Dict[str, Any]]]:
  """初始化历史性能指标"""
        return {platform: [] for platform in AIPlatform}
    
    def select_best_platform(self, query_request: UnifiedQueryRequest) -> str:
  """选择最适合的AI平台"""
      
        query_content = query_request.query
    query_intent = self._analyze_query_intent(query_content)
    performance_requirements = self._determine_performance_requirements(query_request)
        
   logger.info(f"🧠 决策引擎选择最佳平台 - Intent: {query_intent}, Priority: {query_request.priority}")
    
        # 平台评分矩阵
platform_scores = {}
        
        for platform in self.platform_quality_matrix:
    score = self._calculate_platform_score(
platform, 
       query_intent, 
         performance_requirements,
      query_request
         )
            platform_scores[platform] = score
        
        # 选择最高分平台
     best_platform = max(platform_scores, key=platform_scores.get)
        
   logger.info(f"✅ 决策结果 - 选择平台: {best_platform}, 评分: {platform_scores[best_platform]:.3f}")
        return best_platform
    
    def _analyze_query_intent(self, query: str) -> str:
 """分析查询意图"""
 
        # 简单的关键字意图分析
        query_lower = query.lower()
        
        intent_keywords = {
            "knowledge_based": ["知识", "信息", "是什么", "定义", "指导", "解释", "说明", "基于知识库"],
       "document_search": ["文档", "资料", "文件", "PDF", "论文", "报告", "手册", "从文档"],
    "workflow_automation": ["自动", "流程", "处理", "触发", "安排", "定时", "批次", "工作流"],
       "simple_conversation": ["问题", "聊天", "对话", "请问", "如何", "怎么"],
      "data_analysis": ["分析", "数据", "报告", "统计", "图表", "指标", "趋势"]
        }
 
        # 匹配最相关的意图
 best_match = "general_conversation"
       max_score = 0
        
  for intent, keywords in intent_keywords.items():
            score = sum(1 for keyword in keywords if keyword in query_lower)
            if score > max_score:
                max_score = score
              best_match = intent
        
        return best_match
    
    def _determine_performance_requirements(self, request: UnifiedQueryRequest) -> Dict[str, Any]:
 """确定性能要求"""
        
        priority_requirements = {
   QueryPriority.CRITICAL: {
    "latency_sla_ms": 1000,  # 秒响应
      "availability_requirement": 0.999,
                "cold_start_tolerance": "none",
        "concurrent_user_support": 1000
     },
     QueryPriority.HIGH: {
     "latency_sla_ms": 2000,
    "availability_requirement": 0.995,
            "cold_start_tolerance": "minimal",
     "concurrent_user_support": 500
   },
    QueryPriority.NORMAL: {
            "latency_sla_ms": 5000,
      "availability_requirement": 0.99,
   "cold_start_tolerance": "acceptable",
                "concurrent_user_support": 100
     },
   QueryPriority.BATCH: {
   "latency_sla_ms": 30000,
             "availability_requirement": 0.95,
    "cold_start_tolerance": "acceptable"
       }
        }
    
        return priority_requirements.get(request.priority, priority_requirements[QueryPriority.NORMAL])
    
    def _calculate_platform_score(self, platform: str, query_intent: str,
    performance_requirements: Dict[str, Any], query_request: UnifiedQueryRequest) -> float:
    """计算平台评分"""
      
        # 意图匹配度（权重40%）
        intent_match_score = self._get_intent_match_score(platform, query_intent)
        
   # 性能匹配度（权重30%）
        performance_score = self._get_performance_match_score(platform, performance_requirements)
      
     # 近期表现评分（权重20%）
 recent_performance_score = self._get_recent_performance_score(platform)
        
        # 高级特性评分（权重10%）
        advanced_features_score = self._get_advanced_features_score(platform, query_request)
        
        # 权重总计算
    total_score = (intent_match_score * 0.4 +
        performance_score * 0.3 +
                       recent_performance_score * 0.2 +
                       advanced_features_score * 0.1)
  
        logger.debug(f"平台 {platform} 评分: {total_score:.3f} (意图:{intent_match_score:.2f}, "
f"性能:{performance_score:.2f}, 近期:{recent_performance_score:.2f}, 高级:{advanced_features_score:.2f})")
     
        return total_score
    
    def _get_intent_match_score(self, platform: str, intent: str) -> float:
    """获取意图匹配度分数"""
   
        platform_capabilities = self.platform_quality_matrix.get(platform, {})
    
        # 意图到能力映射
        intent_capability_map = {
    "knowledge_based": ["knowledge_base", "document_qa"],
            "document_search": ["enterprise_document_qa", "hybrid_retrieval"],
            "workflow_automation": ["workflow_automation", "multi_step_processing"],
          "simple_conversation": ["chat_conversation", "workflow_automation"],
       "data_analysis": ["business_task_layout", "workflow_automation"]
        }
        
   capabilities_for_intent = intent_capability_map.get(intent, [])
        
        matching_score = 0.0
        for capability in capabilities_for_intent:
         if capability in platform_capabilities:
            matching_score += platform_capabilities[capability]
           
        return matching_score / len(capabilities_for_intent) if capabilities_for_intent else 0.5
   
    def _get_performance_match_score(self, platform: str, requirements: Dict[str, Any]) -> float:
   """获取性能需求匹配度分数"""
      
        # 获取平台历史指标
        ava_data = self.recent_performance_stats.get(platform, {})
        
  latency_match = min(1.0, requirements["latency_sla_ms"] / (avg_data.get("avg_response_time_ms", 1000) or 1000))
        availability_match = avg_data.get("uptime_percentage", 0.98) / requirements["availability_requirement"]
        
        return (latency_match + availability_match) / 2.0
 
    def _get_recent_performance_score(self, platform: str) -> float:
        """获取近期表现评分"""
 
        # 简化实现 - 基于可用性和响应时间
        recent_metrics = self.recent_performance_stats.get(platform, {})
        
        uptime_score = recent_metrics.get("uptime_percentage", 0.95)
        response_score = recent_metrics.get("avg_response_time_ms", 1000) / 1000.0
    
        return (uptime_score - response_score * 0.1)  # 稍微惩罚高延迟
    
    def _get_advanced_features_score(self, platform: str, query_request: UnifiedQueryRequest) -> float:
        """获取高级特性匹配度分数"""
   
    score = 0.0
        
        # 中文处理特性
        if query_request.language == "zh":
    chinese_support_score = {
    "deepseek": 0.9,
  "zhipu": 0.95,
        "moonshot": 0.88,
   "n8n": 0.7
        }
            score += chinese_support_score.get(platform, 0.6)
  
        # 企业级特性
        if query_request.priority in [QueryPriority.HIGH, QueryPriority.CRITICAL]:
            enterprise_score = {
         "ragflow": 0.95,
       "dify": 0.82,
       "n8n": 0.75
     }
       score += enterprise_score.get(platform, 0.5)
        
        # API完整性评分
        api_quality = {
     "ragflow": 0.88,
    "dify": 0.85, 
      "n8n": 0.90
        }
    score += api_quality.get(platform, 0.75)
        
     return score / sum([1 for _ in chinese_support_score.values())  # 标准化分数
    
    def update_performance_metrics(self, platform: str, metrics: Dict[str, Any]) -> None:
        """更新平台性能指标"""
<
        # 更新历史记录
     self.recent_performance_stats[platform] = metrics
    
        # 保存到历史（保留最新的100条记录）
    if platform not in self.usage_metrics_history:
            self.usage_metrics_history[platform] = []
      
        # 添加新记录
        self.usage_metrics_history[platform].append({
            "timestamp": datetime.now().isoformat(),
            **metrics
    })
        
        # 保持历史大小（简单的LRU）
        if len(self.usage_metrics_history[platform]) > 100:
 self.usage_metrics_history[platform] = self.usage_metrics_history[platform][-100:]
    
     logger.info(f"📈 平台 {platform} 性能指标已更新")

# -----------------------------
# 统一API网关实现
# -----------------------------

class EnterpriseUnifiedAIAPI:
    """企业级统一AI工作流API网关"""
 
    def __init__(self, config: EnterpriseAPIConfig):
        self.config = config
     self.decision_engine = EnterpriseDecisionEngine(config)
        self.platform_adapters = self._initialize_platform_adapters()
        
    # 缓存和会话管理
 self.cache_manager = self._initialize_cache_manager()
        self.session_manager = self._initialize_session_manager()
        
        # 请求限流和QoS
     self.rate_limiter = EnterpriseRateLimiter(config)
        self.qos_manager = EnterpriseQoSManager()
        
        logger.info("🌐 企业级统一AI工作流API网关初始化完成")
    
    def _initialize_platform_adapters(self) -> Dict[str, IPlatformAdapter]:
        """初始化平台适配器"""
     adapters = {}
        
   for platform_name in AIPlatform:
            platform_enum = platform_name.value
            
            if platform_enum == "dify":
       adapters[platform_enum] = DifyPlatformAdapter()
       elif platform_enum == "ragflow":
           adapters[platform_enum] = RAGFlowPlatformAdapter()
            elif platform_enum == "n8n":
   adapters[platform_enum] = N8NPlatformAdapter()
    # 可以添加更多平台适配器
            else:
     adapters[platform_enum] = None  # 未实现的平台
 
    return {k: v for k, v in adapters.items() if v is not None}
    
    def _initialize_cache_manager(self):
 """初始化缓存管理器"""
        
        if redis_available:
            try:
    return RedisCacheManager()
            except Exception as e:
    logger.warning(f"Redis缓存初始化失败 {e}，回退到内存缓存")
        
        if cachetools_available:
     return CacheToolsManager()
         
  # 最简单的缓存管理器
        return SimpleCacheManager()
    
    def _initialize_session_manager(self):
        """初始化会话管理器"""

        return EnterpriseSessionManager(self.config.session_timeout_minutes)
  
    async def process_unified_query(self, query_request: UnifiedQueryRequest) -> UnifiedQueryResponse:
   """处理统一的AI查询请求"""
    
        request_id = str(uuid.uuid4())
      start_time = time.time()
  
 logger.info(f"🌐 收到统一查询请求 [RID:{request_id}] - Query: {query_request.query[:50]}...")
    
# 1. 请求验证和预处理
        is_valid, validation_error = self._validate_query_request(query_request)
  if not is_valid:
     raise HTTPException(status_code=400, detail=validation_error)
        
   # 2. 检查请求限流
        if not await self.rate_limiter.is_request_allowed(request_id):
   raise HTTPException(status_code=429, detail="请求频率过高，请稍后重试")
        
        # 3. 检查缓存（如果有的话）
     cached_response = await self.cache_manager.get_cached_response(query_request)
        if cached_response:
            cached_response["cache_hit"] = True
            logger.info(f"💾 缓存命中返回 - [RID:{request_id}]")
            return cached_response
        
  # 4. 智能平台选择
        best_platform = self.decision_engine.select_best_platform(query_request)
  
     # 5. 请求优先级处理
        await self.qos_manager.handle_priority(query_request)
    
 # 6. 执行平台查询
        try:
            platform_result = await self._execute_platform_query(best_platform, query_request)
     
    # 7. 构建统一响应
        unified_response = await self._build_unified_response(
 query_request, best_platform, platform_result, request_id, start_time
           )
     
    # 8. 缓存结果
       await self.cache_manager.cache_response(
          query_request, unified_response, ttl_seconds=3600
  )
  
            # 9. 更新性能指标
            self.update_performance_metrics(best_platform, platform_result)
            
            logger.info(f"✅ 统一查询处理完成 [RID:{request_id}] - 平台: {best_platform}, "
   f"用时: {unified_response.processing_time_ms}ms, 置信度: {unified_response.confidence_score:.2f}")
        
            return unified_response
            
  except HTTPException:
       raise  # 重新抛出HTTP异常
               
        except Exception as e:
   logger.error(f"统一查询处理失败 [RID:{request_id}]: {str(e)}")
   raise HTTPException(status_code=500, detail="处理请求时发生错误")
    
    def _validate_query_request(self, query_request: UnifiedQueryRequest) -> tuple[bool, str]:
 """验证查询请求的有效性"""
        
        if not query_request.query or len(query_request.query.strip()) == 0:
  return False, "Query字段不能为空"
        
        if len(query_request.query) > 2000:
            return False, "Query长度不能超过2000字符"
    
        if query_request.priority == QueryPriority.CRITICAL:
            if re.search(r"[\"'<>", query_request.query):
   return False, "高优先级查询包含潜在安全风险的字符"
        
 return True, ""
    
    async def _execute_platform_query(self, platform: str, query_request: UnifiedQueryRequest) -> Dict[str, Any]:
        """执行具体平台的查询"""
   
        adapter = self.platform_adapters.get(platform)
        if not adapter:
            raise HTTPException(status_code=400, detail=f"不支持的AI平台: {platform}")
       
     # 加上企业和安全上下文
     enhanced_query = UnifiedQueryRequest(
    **query_request.__dict__,
            metadata={**query_request.metadata, 
        "platform_execution": platform,
 "enterprise_context": True,
                      "access_token": self._generate_temp_access_token()}
      )
        
        logger.debug(f"🚀 执行平台查询 - Platform: {platform}")
        
        try:
            return await adapter.execute_query(enhanced_query)
            
        except Exception as e:
            logger.error(f"平台 {platform} 查询执行失败: {e}")
       if self.config.fault_tolerance_enabled:
       # 故障转移到备选平台
        return await self._failover_to_alternative_platform(query_request, platform)
         else:
        raise HTTPException(status_code=503, detail=f"AI平台 {platform} 暂时不可用")
    
    async def _failover_to_alternative_platform(self, query_request: UnifiedQueryRequest, 
                                             failed_platform: str) -> Dict[str, Any]:
    """故障转移到备选AI平台"""
 
        fallback_order = self._get_fallback_platform_order(failed_platform)
        
    logger.warning(f"⚠️ 开始故障转移 - 原平台: {failed_platform}")
   
  for fallback_platform in fallback_order:
            if fallback_platform == failed_platform:
     continue
     
       logger.info(f"\u200f⚡ 尝试故障转移 - Fallback Platform: {fallback_platform}")
    
            try:
  fallback_result = await self._execute_platform_query(fallback_platform, query_request)
          fallback_result["fallback_enabled"] = True
    return fallback_result
        
           except Exception as fallback_e:
 ((寤)
       logger.warning(f"故障转移到 {fallback_platform} 失败: {fallback_e}")
   continue
        
    # 所有失败
        raise HTTPException(status_code=503, detail="所有AI平台均不可用")
 
    def _get_fallback_platform_order(self, failed_platform: str) -> List[str]:
 """获取故障转移备选平台顺序"""
        
        # 定义平台故障转移优先级
        fallback_strategy = {
            "dify": ["ragflow", "n8n", "langflow"],
     "ragflow": ["dify", "n8n", "langflow"],
        "n8n": ["dify", "ragflow", "langflow"],
     "langflow": ["dify", "ragflow", "n8n"],
       "flowise": ["dify", "ragflow", "langflow"]
        }
   
        return fallback_strategy.get(failed_platform, ["dify", "ragflow", "n8n"])
    
    async def _build_unified_response(self, query_request: UnifiedQueryRequest, 
    platform_used: str, platform_result: Dict[str, Any],
                        request_id: str, start_time: float) -> UnifiedQueryResponse:
     """构建统一格式响应"""
   
        processing_time_ms = int((time.time() - start_time) * 1000)
        
 # 标准化错误处理
     if "error" in platform_result:
    return UnifiedQueryResponse(
         request_id=request_id,
       query=query_request.query,
    answer=f"AI处理时遇到错误: {platform_result.get('error', '未知错误')}",
            platform_used=platform_used,
      confidence_score=0.0,
            processing_time_ms=processing_time_ms,
 sources=[],
          metadata={"error": True, "platform_error": platform_result.get("error")},
  next_actions=["重试请求", "联系技术支持"]
        )
      
   # 成功的标准化响应
  return UnifiedQueryResponse(
            request_id=request_id,
            query=query_request.query,
            answer=platform_result.get("answer", ""),
    platform_used=platform_used,
    confidence_score=float(platform_result.get("confidence", 0.0)),
            sources=platform_result.get("sources", []),
         processing_time_ms=processing_time_ms,
            model_used=platform_result.get("model_used", platform_used),
     metadata={
         "platform_metadata": platform_result.get("metadata", {}),
        "rightaway_from_cache": False,
  "enterprise_class": True,
       },
  metadata.get("next_actions", []),
  user_feedback_invited=True if platform_result.get("confidence", 0) < 0.5 else False
        )
    
    def _generate_temp_access_token(self) -> str:
     """生成临时访问令牌（用于API间验证）"""
        return f"iat_{int(time.time())}_{uuid.uuid4().hex[:8]}"
    
    def update_performance_metrics(self, platform: str, result_data: Dict[str, Any]) -> None:
        """更新平台性能指标"""
        
 processing_time = result_data.get("processing_time", 0)
    success = "error" not in result_data
    confidence = result_data.get("confidence", 0.5)
        
  performance_metrics = {
            "platform": platform,
  "timestamp": datetime.now().isoformat(),
            "processing_time": processing_time,
     "success": success,
            "confidence": confidence,
       "fallback_enabled": result_data.get("fallback_enabled", False)
     }
        
    self.decision_engine.update_performance_metrics(platform, performance_metrics)
        
    async def get_api_health_status(self) -> Dict[str, Any]:
"""获取API健康状态"""
        
        total_requests = sum(metrics["total_executions"] 
for metrics in self.decision_engine.usage_metrics_history.values() 
if metrics)
        
    outage_summary = {}  # 简化的状态计算
        
        return {
     "service_name": self.config.api_name,
            "version": self.config.version,
         "status": "healthy", 
    "total_api_requests": total_requests,
    "uptime_percentage": 99.7,
            "last_updated": datetime.now().isoformat(),
     "platform_statuses": self._generate_platform_health_summary(),
 "performance_summary": self._generate_performance_summary()
        }
    
    def _generate_platform_health_summary(self) -> Dict[str, Dict[str, Any]]:
 """生成所有平台的健康状态摘要"""
        
        status_summary = {}
  
     for platform, adapter in self.platform_adapters.items():
     try:
   performance = adapter.get_performance_metrics()
    reliability_score = performance.get("uptime_percentage", 0.95) * performance.get("trust_score", 0.8)
       
   status_summary[platform] = {
  "status": "healthy" if reliability_score > 0.8 else "degraded",
           "uptime": performance.get("uptime_percentage", 0),
         "avg_latency_ms": performance.get("avg_response_time_ms", 1000),
            "last_check": datetime.now().isoformat()
     }
       
            except Exception as e:
    status_summary[platform] = {
     "status": "unknown",
          "error": str(e),
      "last_check": datetime.now().isoformat()
 }
        
        return status_summary
    
    def _generate_performance_summary(self) -> Dict[str, Any]:
   """生成性能摘要"""
        
        # 简化的性能统计
        avg_processing_time = 580  # 通用平均响应时间
   
        return {
            "average_response_time_ms": avg_processing_time,
            "peak_traffic_time": "business_hours_expected",
      "throughput_capacity": "enterprise_scale",
   "optimization_suggestions": ["考虑启用更激进的缓存策略", "检查慢查询", "监控大规模文档检索"]
        }

# -----------------------------
# 缓存管理器
# -----------------------------

class BaseCacheManager(ABC):
    """基础缓存管理器"""
  
    @abstractmethod
    async def get_cached_response(self, request: UnifiedQueryRequest) -> Optional[UnifiedQueryResponse]:
     """获取缓存的响应"""
        pass
    
    @abstractmethod
    async def cache_response(self, request: UnifiedQueryRequest, response: UnifiedQueryResponse, ttl_seconds: int = 3600) -> None:
     """缓存响应"""
        pass

class RedisCacheManager(BaseCacheManager):
    """Redis缓存管理器"""
    
    def __init__(self):
        self.redis_client = redis.from_url(
            "redis://localhost:6379/8",  # 专用缓存数据库
   decode_responses=True
  )
        logger.info("🔌 Redis缓存管理器初始化")
    
    def _generate_cache_key(self, request: UnifiedQueryRequest) -> str:
        """生成缓存Key"""
        key_parts = [
            request.query,
     request.language,  
           request.response_format.value,
    str(request.priority.value),
   json.dumps(request.context, sort_keys=True) if request.context else ""
        ]
        
     # 使用哈希摘要避免过长Key
        import hashlib
       key_data = "|".join(key_parts)
        return f"ai_unified_response:{hashlib.sha256(key_data.encode()).hexdigest()[:24]}"
    
    async def get_cached_response(self, request: UnifiedQueryRequest) -> Optional[UnifiedQueryResponse]:
  """从缓存获取响应"""
        
        cache_key = self._generate_cache_key(request)
  
        try:
         cached_value = await self.redis_client.get(cache_key)
       if cached_value:
    cached_data = json.loads(cached_value)
             
      # 校验缓存完整性
                required_fields = ["query", "answer", "platform_used", "processing_time_ms"]
   if all(field in cached_data for field in required_fields):
          return UnifiedQueryResponse(**cached_data)
     
    
        except Exception as e:
        logger.warning(f"Redis缓存获取失败: {e}")
    
        return None
    
    async def cache_response(self, request: UnifiedQueryRequest, response: UnifiedQueryResponse, ttl_seconds: int = 3600) -> None:
        """缓存响应到Redis"""
     
        cache_key = self._generate_cache_key(request)
        
        try:
        # 标准化数据为可序列化格式
     cacheable_data = {
       "query": response.query,
             "answer": response.answer,
   "platform_used": response.platform_used,
          "confidence_score": response.confidence_score,
             "sources": response.sources,
                "processing_time_ms": response.processing_time_ms,
  "metadata": response.metadata,
                "next_actions": response.next_actions,
   "user_feedback_invited": response.user_feedback_invited,
       "timestamp": response.timestamp.isoformat()
            }
      
     await self.redis_client.setex(
cache_key, ttl_seconds, json.dumps(cacheable_data)
      )
       
            logger.debug(f"已缓存响应 - Key: {cache_key}, TTL: {ttl_seconds}s")
            
        except Exception as e:
   logger.error(f"Redis缓存失败: {e}")

class CacheToolsManager(BaseCacheManager):
 """CacheTools内存缓存管理器"""
    
    def __init__(self):
        # 简单的TTL缓存
   self.cache = TTLCache(maxsize=5000, ttl=3600)
   logger.info("🏠 CacheTools内存缓存初始化")
    
    def _generate_cache_key(self, request: UnifiedQueryRequest) -> str:
        """生成缓存Key"""
 return hash(str((request.query, request.language, request.response_format)))
    
    async def get_cached_response(self, request: UnifiedQueryRequest) -> Optional[UnifiedQueryResponse]:
 """从内存缓存获取响应"""
        
    try:
    cache_key = self._generate_cache_key(request)
         cached_response = self.cache.get(cache_key)
       
            if cached_response and isinstance(cached_response, UnifiedQueryResponse):
    return cached_response
    
        except Exception as e:
     logger.warning(f"内存缓存获取失败: {e}")
        
        return None
    
    async def cache_response(self, request: UnifiedQueryRequest, response: UnifiedQueryResponse, ttl_seconds: int = 3600) -> None:
    """缓存响应到内存"""
    
        try:
            cache_key = self._generate_cache_key(request)
   self.cache[cache_key] = response
        
            logger.debug(f"已缓存响应到内存 - Key: {cache_key}")
            
        except Exception as e:
      logger.error(f"内存缓存失败: {e}")

class SimpleCacheManager(BaseCacheManager):
    """简单内存缓存管理器（最后回退方案）"""
 
    def __init__(self):
        self.cache = {}
        logger.info("🏠 简单内存缓存创建（回退方案）")
    
    def _generate_cache_key(self, request: UnifiedQueryRequest) -> str:
        """生成缓存Key"""
     return f"simple_cached_{hash(str(request))}"
    
    async def get_cached_response(self, request: UnifiedQueryRequest) -> Optional[UnifiedQueryResponse]:
        """从简单内存缓存获取响应"""
    
        try:
            cache_key = self._generate_cache_key(request)
    return self.cache.get(cache_key)
  
        except Exception as e:
    logger.warning(f"简单缓存获取失败: {e}")
   
        return None
    
    async def cache_response(self, request: UnifiedQueryRequest, response: UnifiedQueryResponse, ttl_seconds: int = 3600) -> None:
   """缓存响应到简单内存"""
 
        try:
    cache_key = self._generate_cache_key(request)
            self.cache[cache_key] = response
      
   logger.debug(f"已缓存响应（简单模式） - Key: {cache_key}")
            
        except Exception as e:
       logger.error(f"简单缓存失败: {e}")

# -----------------------------
# 辅助管理器
# -----------------------------

class EnterpriseRateLimiter:
    """企业级请求限流管理器"""
    
    def __init__(self, config: EnterpriseAPIConfig):
        self.config = config
    self.platform_limits = {}
   self.user_limits = {}
    
        # 初始化平台级限流
        for platform in AIPlatform:
            self.platform_limits[platform.value] = {
   "current_requests": 0,
        "last_reset": datetime.now(),
        "max_limit": self.config.concurrent_request_limit,
    "window_seconds": 60
         }
        
   logger.info("🚦 企业级限流器初始化")
    
    async def is_request_allowed(self, request_id: str, platform: str = "unified") -> bool:
        """检查请求是否被允许（基于平台和整体限制）"""
        
        # 平台级限流检查
   platform_info = self.platform_limits.get(platform, {})
      
        # 每小时重置计数
        if datetime.now() >= platform_info["last_reset"] + timedelta(seconds=platform_info["window_seconds"]):
         platform_info["current_requests"] = 0
  platform_info["last_reset"] = datetime.now()
        
   # 检查平台并发限制
        if platform_info["current_requests"] >= platform_info["max_limit"]:
   logger.warning(f"限流触发 - 平台: {platform}, 当前请求: {platform_info['current_requests']}")
            return False
        
     # 增加计数
    platform_info["current_requests"] += 1
        
      return True

class EnterpriseQoSManager:
    """企业服务质量管理器"""
    
    def __init__(self):
self.priority_queues = {
     QueryPriority.CRITICAL: asyncio.Queue(maxsize=100),
         QueryPriority.HIGH: asyncio.Queue(maxsize=200),
      QueryPriority.NORMAL: asyncio.Queue(maxsize=500),
     QueryPriority.BATCH: asyncio.Queue(maxsize=1000)
    }
     
        logger.info("⚙️ 服务质量管理器初始化")
    
    async def handle_priority(self, request: UnifiedQueryRequest) -> bool:
        """处理查询优先级"""
 # 添加请求到相应的优先级队列
        return await self.priority_queues[request.priority].put(request) >= 0

class EnterpriseSessionManager:
    """企业会话管理器"""
    
    def __init__(self, timeout_minutes: int = 30):
     self.timeout_minutes = timeout_minutes
        self.session_store = {}
        
  logger.info(f"🔑 企业会话管理器初始化 - 超时: {timeout_minutes}分钟")
    
    def create_session(self, user_id: str) -> str:
   """创建会话"""
        session_id = f"entsess_{uuid.uuid4().hex[:12]}"
    
     self.session_store[session_id] = {
"user_id": user_id,
      "created_at": datetime.now(),
     "last_activity": datetime.now(),
   "is_active": True
        }
        
  return session_id
    
    def validate_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """验证会话"""
   
     session = self.session_store.get(session_id)
        
        if not session or session["is_active"] is False:
     return None
        
        # 检查超时
now = datetime.now()
        if now - session["last_activity"] > timedelta(minutes=self.timeout_minutes):
            session["is_active"] = False
            return None
        
        # 更新活动时间
        session["last_activity"] = now
        
        return session.most_common_keys("user_id", "created_at")

def main():
    """主函数：测试多平台统一AI工作流API"""
    print("🌐 LangChain L3 Advanced - Week 12: 多平台统一AI工作流API")
    print("=" * 70)
  
    try:
 # 1. 创建企业级API网关配置
        api_config = EnterpriseAPIConfig(
    api_name="企业级AI统一服务API v1.0",
      base_url="http://localhost:8080",
            listen_port=8080,
  decision_engine_enabled=True,
         caching_strategy="memory_hybrid",  # 使用混合缓存
 auto_scaling_enabled=True,
 load_balancer_type="intelligent",
circuit_breaker_threshold=0.8
 )
        
     # 2. 初始化统一API网关
        unified_api = EnterpriseUnifiedAIAPI(api_config)
        
        print("🌐 企业级统一API网关测试")
  print("-" * 40)
        
        # 测试用例1：知识问答型查询（应该优选RAGFlow）
        knowledge_query = UnifiedQueryRequest(
       query="企业的安全策略对员工数据处理有哪些合规要求？",
   priority=QueryPriority.NORMAL,
   response_format=ResponseFormat.JSON,
            language="zh",
     metadata={
     "user_id": "enterprise_user_001",
        "session_id": unified_api.session_manager.create_session("ent_user_001")
            }
        )
 
        print("📝 测试查询1: 企业安全合规知识问答")
    print(f"   查询: {knowledge_query.query}")
     
  start_time = time.time()
 knowledge_result = asyncio.run(unified_api.process_unified_query(knowledge_query))
    processing_time = (time.time() - start_time) * 1000
        
        print(f"   响应平台: {knowledge_result.platform_used}")
        print(f"   置信度: {knowledge_result.confidence_score:.2f}")
        print(f"   处理时间: {processing_time:.0f}ms")
        print(f"   答案预览: {knowledge_result.answer[:120]}...")
     print(f"   建议操作: {'; '.join(knowledge_result.next_actions or ['无具体建议'])}")
        print("-" * 40)
    
        # 测试用例2：工作流自动化（应该优选n8n） 
        workflow_query = UnifiedQueryRequest(
      query="创建一个自动化的客户数据同步流程，每6小时检查数据源并发送成功通知到运营团队",
  priority=QueryPriority.HIGH, 
   response_format=ResponseFormat.JSON,
            language="zh", 
        metadata={
        "user_id": "workflow_admin_002",
         "session_id": unified_api.session_manager.create_session("workflow_user_002"),
         "max_steps": 10
   }
        )
   
        print("⚙️ 测试查询2: 自动化工作流创建")
     print(f"   查询: {workflow_query.query}")
        print(f"   优先级: {workflow_query.priority}")
        
    start_time = time.time()
        workflow_result = asyncio.run(unified_api.process_unified_query(workflow_query))
        processing_time = (time.time() - start_time) * 1000
        
     print(f"   响应平台: {workflow_result.platform_used}")
        print(f"   置信度: {workflow_result.confidence_score:.2f}")
        print(f"   处理时间: {processing_time:.0f}ms")
 print(f"   建议操作: {'; '.join(workflow_result.next_actions or ['无具体建议'])}")
     print("-" * 40)
      
        # 测试3：API健康状态检查
        health_status = asyncio.run(unified_api.get_api_health_status())
        
        print("📊 API健康状态汇总")
   print(f"   服务名称: {health_status['service_name']}")
        print(f"   API版本: {health_status['version']}")
  print(f"   状态: {health_status['status']}") 
print(f"   正常运行率: {health_status['uptime_percentage']}%")
        print("   平台状态摘要:")
        
        for platform, status_info in health_status.get("platform_statuses", {}).items():
            status_emoji = "✅" if status_info.get("status") == "healthy" else "⚠️"
        print(f"     {status_emoji} {platform}: {status_info.get('status', 'unknown')} ({status_info.get('avg_latency_ms', 0)}ms)")
        
        print("-" * 40)
   
        print("\n✅ 多平台统一API测试全部完成！")
        print("\n📑 主要企业特性:")
        print("   🧠 智能平台决策引擎（AI驱动）")
    print("   🔀 多平台智能路由与故障转移")
      print("   💡 基于查询意图的平台选择")
        print("   ⚡ 高性能缓存管理（LRU/TTL）")
  print("   🏭 统一企业级错误处理与安全")
        print("   📈 实时监控和服务诊断")
        
    print("\n💡 使用建议:")
        print("   1. 部署PostgreSQL/Redis集群")
     print("   2. 配置平台API密钥(.env)")
        print("   3. 启用决策引擎动态选择")
   print("   4. 测试故障转移机制")
        print("   5. 配置企业监控告警")
        
    except Exception as e:
        print(f"\n❌ 多平台统一API测试失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()