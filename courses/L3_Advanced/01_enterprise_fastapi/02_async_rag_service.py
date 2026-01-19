#!/usr/bin/env python3
"""
LangChain L3 Advanced - Week 11  
课程标题: 企业级异步RAG服务设计
学习目标:
  - 掌握异步RAG查询处理架构设计
  - 学习流式响应(Server-Sent Events)
  - 实施企业级连接池与并发优化
  - 实现向量库异步查询优化
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
先决条件: 完成01_fastapi_enterprise_architecture.py
"""

import asyncio
import uuid
import json
import time
from typing import Dict, List, Optional, AsyncGenerator, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from datetime import datetime
import logging
from pathlib import Path

# 异步FastAPI组件
try:
    from fastapi import FastAPI, HTTPException, BackgroundTasks, Depends
    from fastapi.responses import JSONResponse, StreamingResponse
    from fastapi.middleware.cors import CORSMiddleware
    from pydantic import BaseModel, Field, validator
    print("✅ FastAPI异步组件导入成功")
except ImportError as e:
    print(f"❌ FastAPI异步组件导入失败: {e}")
    raise

# 异步存储与AI组件
try:
    import aiohttp
    import aiofiles
    import redis.asyncio as redis
    print("✅ 异步存储客户端导入成功")
    async_storage_available = True
except ImportError as e:
    print(f"⚠️ 异步存储组件导入失败: {e}")
    print("请确保已安装: pip install aiofiles redis[hiredis]")
    async_storage_available = False

# 向量数据库和AI模型
try:
    from qdrant_client import QdrantClient, models
    from qdrant_client.async_qdrant_client import AsyncQdrantClient
    print("✅ Qdrant向量数据库导入成功")
    vector_db_available = True
except ImportError as e:
    print(f"⚠️ 向量数据库导入失败: {e}")
    vector_db_available = False

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class AsyncRAGConfig:
    """异步RAG配置"""
    max_concurrent_queries: int = 10
    query_timeout_seconds: int = 30
    retry_attempts: int = 3
    retry_delay_seconds: float = 0.5
    batch_size: int = 5
    max_sources: int = 5
    min_confidence: float = 0.7

@dataclass
class RAGQuery:
    """RAG查询模型"""
    query: str = Field(..., min_length=1, max_length=2000)
    domain: str = Field(default="general", description="查询领域分类")
    context: Optional[List[str]] = Field(default=None, description="历史上下文")
    temperature: float = Field(default=0.7, ge=0.0, le=2.0)
    max_tokens: int = Field(default=1500, ge=1, le=8192)
    top_k: int = Field(default=10, ge=1, le=50)
    similarity_threshold: float = Field(default=0.7, ge=0.0, le=1.0)
    return_sources: bool = Field(default=True)

@dataclass 
class RAGResponse:
    """RAG响应模型"""
    query: str
    answer: str
    sources: List[Dict[str, Any]] = field(default_factory=list)
    confidence: float = 0.0
    processing_time: float = 0.0
    retrieval_time: float = 0.0
    generation_time: float = 0.0
    used_provider: str = ""
    request_id: str = ""
    timestamp: datetime = field(default_factory=datetime.now)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class RetrievalResult:
    """检索结果"""
    chunks: List[Dict[str, Any]] = field(default_factory=list)
    scores: List[float] = field(default_factory=list) 
    reranked_results: List[Dict[str, Any]] = field(default_factory=list)
    retrieval_time: float = 0.0

class EnterpriseAsyncRAGService:
    """企业级异步RAG服务"""
    
    def __init__(self, config: AsyncRAGConfig = None):
        self.config = config or AsyncRAGConfig()
        self.request_semaphore = asyncio.Semaphore(self.config.max_concurrent_queries)
        self.cache_client = None
        self.vector_store = None
        self.query_history = []
        self.performance_stats = {"total_queries": 0, "avg_response_time": 0.0}
        
        # 初始化组件
        self._initialize_components()
        
    def _initialize_components(self):
        """初始化异步组件"""
        logger.info("🚀 初始化企业级异步RAG服务组件")
        
        # 初始化缓存
        if async_storage_available:
            try:
                self.cache_client = redis.from_url("redis://localhost:6379/0")
                logger.info("✅ Redis异步缓存初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ Redis缓存初始化失败: {e}")
        
        # 初始化向量数据库
        if vector_db_available:
            try:
                self.vector_store = AsyncQdrantClient(":memory:")  # 演示用内存存储
                logger.info("✅ Qdrant向量数据库初始化成功")
            except Exception as e:
                logger.warning(f"⚠️ Qdrant向量数据库初始化失败: {e}")
        
        logger.info("✅ 企业级异步RAG服务初始化完成")
    
    async def process_query_async(self, query_data: RAGQuery) -> RAGResponse:
        """异步处理RAG查询"""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        logger.info(f"[RID:{request_id}] 开始异步处理RAG查询") 
        
        async with self.request_semaphore:
            try:
                # 1. 查询预处理和标准化
                preprocessed_query = await self._preprocess_query(query_data.query)
                await asyncio.sleep(0.01)  # 模拟预处理延迟
                
                # 2. 检查缓存
                cached_response = await self._check_cache(preprocessed_query)
                if cached_response:
                    logger.info(f"[RID:{request_id}] 缓存命中，快速响应")
                    return cached_response
                
                # 3. 并行处理检索和意图分析
                retrieval_task = asyncio.create_task(
                    self._async_retrieval(preprocessed_query, query_data.top_k, query_data.similarity_threshold)
                )
                intent_task = asyncio.create_task(
                    self._async_intent_analysis(query_data.query)
                )
                
                # 等待检索结果
                retrieval_result = await retrieval_task
                generation_params = await intent_task
                
                # 4. 异步生成回答
                final_answer = await self._async_generate_answer(
                    query_data.query, 
                    retrieval_result, 
                    generation_params,
                    query_data.temperature,
                    query_data.max_tokens
                )
                
                # 5. 构建响应
                total_time = time.time() - start_time
                
                response = RAGResponse(
                    query=query_data.query,
                    answer=final_answer["answer"],
                    sources=final_answer["sources"],
                    confidence=final_answer["confidence"],
                    processing_time=total_time,
                    retrieval_time=retrieval_result.retrieval_time,
                    generation_time=final_answer["generation_time"],
                    used_provider=final_answer.get("provider", "enterprise"),
                    request_id=request_id,
                    timestamp=datetime.now(),
                    metadata=final_answer.get("metadata", {})
                )
                
                # 6. 异步持久化和缓存
                await asyncio.gather(
                    self._cache_response(preprocessed_query, response),
                    self._log_query_async(query_data, response)
                )
                
                # 7. 更新性能统计
                await self._update_performance_stats(total_time)
                
                logger.info(f"[RID:{request_id}] 异步RAG查询处理完成，总用时: {total_time:.3f}s")
                return response
                
            except asyncio.TimeoutError:
                logger.error(f"[RID:{request_id}] 查询超时")
                return self._handle_timeout_error(query_data.query, request_id)
            except Exception as e:
                logger.error(f"[RID:{request_id}] 查询处理错误: {str(e)}")
                return await self._handle_processing_error(query_data.query, str(e), request_id)
            finally:
                logger.info(f"[RID:{request_id}] 请求处理结束")
    
    async def stream_query_async(self, query_data: RAGQuery) -> AsyncGenerator[str, None]:
        """异步流式查询处理"""
        request_id = str(uuid.uuid4())
        start_time = time.time()
        
        logger.info(f"[RID:{request_id}] 开始异步流式查询处理")
        
        try:
            # 发送开始信号
            yield f"event: start\ndata: {{\"request_id\": \"{request_id}\", \"timestamp\": \"{datetime.now().isoformat()}\"}}\n\n"
            await asyncio.sleep(0.1)
            
            # 1. 查询预处理阶段
            yield f"event: preprocessing\ndata: {{\"status\": \"Query preprocessing in progress\", \"step\": 1}}\n\n"
            preprocessed_query = await self._preprocess_query(query_data.query)
            await asyncio.sleep(0.2)
            
            # 2. 意图分析阶段
            yield f"event: intent_analysis\ndata: {{\"status\": \"Analyzing user intent\", \"step\": 2}}\n\n"
            intent_analysis = await self._async_intent_analysis(query_data.query)
            await asyncio.sleep(0.3)
            
            # 3. 文档检索阶段
            yield f"event: document_retrieval\ndata: {{\"status\": \"Retrieving relevant documents\", \"step\": 3}}\n\n"
            retrieval_start = time.time()
            
            # 异步检索 - 分段发送进度
            async for progress in self._stream_retrieval_progress(preprocessed_query, query_data.top_k):
                yield f"event: retrieval_progress\ndata: {json.dumps(progress)}\n\n"
            
            retrieval_result = await self._async_retrieval(preprocessed_query, query_data.top_k, query_data.similarity_threshold)
            retrieval_time = time.time() - retrieval_start
            
            yield f"event: retrieval_complete\ndata: {{\"status\": \"Document retrieval complete\", \"retrieval_time\": {retrieval_time:.2f}}}\n\n"
            
            # 4. 答案生成阶段
            yield f"event: answer_generation\ndata: {{\"status\": \"Generating intelligent response\", \"step\": 4}}\n\n"
            
            # 流式生成答案
            final_answer = ""
            async for chunk in self._stream_generate_answer(
                query_data.query, retrieval_result, intent_analysis
            ):
                final_answer += chunk["text"]
                yield f"event: answer_chunk\ndata: {json.dumps(chunk)}\n\n"
            
            # 5. 完成阶段
            total_time = time.time() - start_time
            completion_data = {
                "final_answer": final_answer,
                "processing_complete": True,
                "total_time_seconds": total_time,
                "sources_count": len(retrieval_result.chunks),
                "confidence_score": final_answer.count("重要") * 0.01 + 0.7
            }
            
            yield f"event: completion\ndata: {json.dumps(completion_data)}\n\n"
            await asyncio.sleep(0.1)
            
            # 异步记录日志
            asyncio.create_task(self._log_stream_query_async(query_data, final_answer, total_time, request_id))
            
            logger.info(f"[RID:{request_id}] 流式查询处理完成，总用时: {total_time:.3f}s")
            
        except Exception as e:
            logger.error(f"[RID:{request_id}] 流式查询处理错误: {str(e)}")
            yield f"event: error\ndata: {{\"error\": \"{str(e)}\", \"request_id\": \"{request_id}\"}}\n\n"
        finally:
            yield "event: end\ndata: {}\n\n"
    
    async def _preprocess_query(self, query: str) -> str:
        """异步查询预处理"""
        # 模拟异步预处理
        await asyncio.sleep(0.01)
        
        # 中文优化处理
        processed_query = query.strip()
        if any(word in query for word in ['中国', '中文', '大模型']):
            processed_query = f"中文优化的查询: {processed_query}"
        
        return processed_query
    
    async def _check_cache(self, query: str) -> Optional[RAGResponse]:
        """检查异步缓存"""
        if not self.cache_client:
            return None
        
        try:
            cache_key = f"rag_response:{hash(query)}"
            cached_data = await self.cache_client.get(cache_key)
            
            if cached_data:
                cached_dict = json.loads(cached_data)
                return RAGResponse(**cached_dict)
            
        except Exception as e:
            logger.warning(f"缓存检查失败: {e}")
        
        return None
    
    async def _cache_response(self, query: str, response: RAGResponse) -> None:
        """异步缓存响应"""
        if not self.cache_client:
            return
        
        try:
            cache_key = f"rag_response:{hash(query)}"
            cache_data = {
                key: value.isoformat() if isinstance(value, datetime) else value
                for key, value in response.__dict__.items()
            }
            
            await self.cache_client.setex(
                cache_key,
                timedelta(minutes=15),
                json.dumps(cache_data)
            )
            
        except Exception as e:
            logger.warning(f"缓存响应失败: {e}")
    
    async def _async_retrieval(self, query: str, top_k: int, similarity_threshold: float) -> RetrievalResult:
        """异步检索实现"""
        start_time = time.time()
        logger.info(f"开始异步文档检索 - top_k: {top_k}, threshold: {similarity_threshold}")
        
        try:
            # 模拟异步向量检索
            await asyncio.sleep(0.1)
            
            # 生成模拟检索结果 - 实际项目中连接真实向量数据库
            mock_results = self._generate_mock_retrieval_results(query, top_k, similarity_threshold)
            
            retrieval_time = time.time() - start_time
            
            result = RetrievalResult(
                chunks=mock_results["chunks"],
                scores=mock_results["scores"],
                reranked_results=mock_results["chunks"],
                retrieval_time=retrieval_time
            )
            
            logger.info(f"异步检索完成 - 用时: {retrieval_time:.3f}s, 结果数: {len(result.chunks)}")
            return result
            
        except Exception as e:
            logger.error(f"异步检索错误: {str(e)}")
            return RetrievalResult(
                chunks=[],
                scores=[],
                reranked_results=[],
                retrieval_time=0.0
            )
    
    async def _stream_retrieval_progress(self, query: str, top_k: int):
        """流式检索进度"""
        phases = [
            {"phase": "vector_search", "progress": 20},
            {"phase": "semantic_ranking", "progress": 40},
            {"phase": "threshold_filtering", "progress": 60},
            {"phase": "reranking", "progress": 80},
            {"phase": "candidate_selection", "progress": 100}
        ]
        
        for phase in phases:
            await asyncio.sleep(0.1)
            yield phase
    
    async def _async_intent_analysis(self, query: str) -> Dict[str, Any]:
        """异步意图分析"""
        await asyncio.sleep(0.05)
        
        # 简单的意图分析 - 实际项目中使用模型分析
        if any(word in query for word in ["如何", "怎样", "怎么"]):
            intent = "how_to_instruction"
        elif any(word in query for word in ["什么", "哪个", "定义"]):
            intent = "definition_question"
        elif any(word in query for word in ["比较", "对比", "区别"]):
            intent = "comparison_request"
        else:
            intent = "general_inquiry"
        
        # 领域识别
        domain_keywords = {
            "technical": ["算法", "架构", "代码", "API"],
            "business": ["企业", "商业", "盈利", "成本"],
            "development": ["开发", "部署", "测试", "CI/CD"]
        }
        
        detected_domains = []
        for domain, keywords in domain_keywords.items():
            if any(keyword in query for keyword in keywords):
                detected_domains.append(domain)
        
        return {
            "intent": intent,
            "domain": detected_domains[0] if detected_domains else "general",
            "complexity": "medium",
            "requires_mathematical": False,
            "requires_visual": False
        }
    
    async def _async_generate_answer(self, query: str, retrieval_result: RetrievalResult,
                                   intent_analysis: Dict[str, Any],
                                   temperature: float = 0.7,
                                   max_tokens: int = 1500) -> Dict[str, Any]:
        """异步生成答案"""
        start_time = time.time()
        logger.info(f"开始异步答案生成 - intent: {intent_analysis['intent']}")
        
        try:
            # 模拟异步LLM调用 - 实际项目中连接真实模型API
            await asyncio.sleep(0.3)
            
            # 基于检索结果生成模拟答案
            if retrieval_result.chunks:
                base_answer = self._generate_answer_from_chunks(
                    query, retrieval_result.chunks, intent_analysis
                )
            else:
                base_answer = f"基于检索结果，我无法找到关于 '{query}' 的具体信息。"
            
            generation_time = time.time() - start_time
            
            # 构建完整响应
            result = {
                "answer": base_answer,
                "sources": [
                    {
                        "document_id": f"doc_{i+1}",
                        "title": f"Enterprise Document {i+1}",
                        "content": chunk.get("content", "")[:200] + "...",
                        "score": retrieval_result.scores[i] if i < len(retrieval_result.scores) else 0.8,
                        "page": chunk.get("metadata", {}).get("page", 1)
                    }
                    for i, chunk in enumerate(retrieval_result.chunks[:3])
                ],
                "confidence": sum(retrieval_result.scores) / len(retrieval_result.scores) if retrieval_result.scores else 0.0,
                "generation_time": generation_time,
                "provider": "enterprise_async_llm",
                "metadata": {
                    "intent_analysis": intent_analysis,
                    "sources_count": len(retrieval_result.chunks),
                    "temperature": temperature,
                    "max_tokens": max_tokens
                }
            }
            
            logger.info(f"异步答案生成完成 - 用时: {generation_time:.3f}s")
            return result
            
        except Exception as e:
            logger.error(f"异步答案生成错误: {str(e)}")
            return {
                "answer": "处理查询时发生错误，请稍后重试。",
                "sources": [],
                "confidence": 0.0,
                "generation_time": time.time() - start_time,
                "provider": "error_handler",
                "metadata": {"error": str(e)}
            }
    
    async def _stream_generate_answer(self, query: str, retrieval_result: RetrievalResult,
                                    intent_analysis: Dict[str, Any]) -> AsyncGenerator[Dict[str, str], None]:
        """流式答案生成"""
        
        answer_parts = [
            f"基于对企业知识库的深入检索，我来回答您关于 '{query}' 的问题：\n\n",
            "首先，我们分析您问题的核心要素，这是一个关于",
            f"{intent_analysis['domain']}" if intent_analysis['domain'] == "technical" else "技术架构",
            "的问题。\n\n",
            "通过对比企业级最佳实践和相关技术方案，我认为：\n\n"
        ]
        
        yield {"text": answer_parts[0], "sequence": 0}
        await asyncio.sleep(0.2)
        
        yield {"text": answer_parts[1], "sequence": 1}
        await asyncio.sleep(0.15)
        
        yield {"text": answer_parts[2], "sequence": 2}
        await asyncio.sleep(0.1)
        
        yield {"text": answer_parts[3], "sequence": 3}
        await asyncio.sleep(0.2)
        
        # 根据检索结果生成详细内容
        if retrieval_result.chunks:
            detailed_answer = f"基于检索到的 {len(retrieval_result.chunks)} 份相关企业文档，"
            contents = [chunk.get("content", "") for chunk in retrieval_result.chunks[:2]]
            detailed_answer += f"该问题的最佳解决方案综合了:\n\n1. {contents[0][:100]}...\n2. {contents[1][:100]}...\n"
            detailed_answer += f"此项方案在企业环境中表现优异，具有 {int(retrieval_result.scores[0] * 100)}% 的相关性评分。\n\n"
            
            yield {"text": detailed_answer, "sequence": 4}
        
        final_statement = f"总结来说，这是一个企业中常见且具有成熟解决路径的问题。建议您可以进一步" \
                         f"深入了解相关技术细节并进行实践验证。\n\n响应基于企业RAG系统，具有 {len(retrieval_result.chunks)} 个信息来源。"
        yield {"text": final_statement, "sequence": 5}
    
    def _generate_mock_retrieval_results(self, query: str, top_k: int, threshold: float) -> Dict[str, Any]:
        """生成模拟检索结果"""
        import random
        
        mock_documents = [
            {
                "document_id": f"doc_enterprise_{i+1}",
                "title": f"企业级{query[:20]}最佳实践指南", 
                "content": f"这份企业文档详细描述了如何{query}，提供了完整的实施路径和成功案例。根据过往项目经验，该方案具有高度的可实施性和良好的ROI表现。",
                "metadata": {"source": f"Enterprise_Database_{i+1}", "page": random.randint(10, 50), "confidence": random.uniform(threshold, 1.0)}
            }
            for i in range(min(top_k, 5))
        ]
        
        scores = [doc["metadata"]["confidence"] for doc in mock_documents]
        
        return {
            "chunks": mock_documents,
            "scores": scores
        }
    
    def _generate_answer_from_chunks(self, query: str, chunks: List[Dict[str, Any]], intent_analysis: Dict[str, Any]) -> str:
        """从检索块中生成完整答案"""
        answer = f"""
基于对企业级知识库的检索分析，关于 "{query}" 的专业回答如下：

问题分析：
- 查询类型：{intent_analysis['intent']}
- 领域分类：{intent_analysis['domain']}
- 复杂度：{intent_analysis['complexity']}

综合解决方案：
"""

        # 基于检索内容构建回答主体
        if chunks:
            answer += f"检索到 {len(chunks)} 个相关信息源，主要要点包括：\n\n"
            
            for i, chunk in enumerate(chunks[:3]):  # 使用前3个最相关的结果
                content = chunk.get("content", "")
                title = chunk.get("title", f"信息源 {i+1}")
                score = chunk.get("metadata", {}).get("confidence", 0.8)
                
                answer += f"{i+1}. **{title}** (相关性: {score:.1%})\n"
                answer += f"   {content[:150]}...\n\n"
        
        answer += """
实施建议：
结合企业级最佳实践和检索得到的专业知识，建议按照以下步骤进行实践：

1. 细化需求分析和场景适配
2. 设计完整的技术实施计划  
3. 建立完善的效果评估机制
4. 配置监控告警和后续优化

该方案已在多个真实企业环境中成功实施，具有可靠的技术基础和business value。鼓励进一步深入研究和实践验证。"""
        
        return answer
    
    async def _log_query_async(self, query_data: RAGQuery, response: RAGResponse) -> None:
        """异步记录查询日志"""
        log_entry = {
            "request_id": response.request_id,
            "query": query_data.query,
            "domain": query_data.domain,
            "response_time": response.processing_time,
            "confidence": response.confidence,
            "sources_count": len(response.sources),
            "timestamp": response.timestamp.isoformat()
        }
        
        self.query_history.append(log_entry)
        logger.info(f"异步记录查询日志 - RID: {response.request_id}")
    
    async def _log_stream_query_async(self, query_data: RAGQuery, final_answer: str, 
                                     total_time: float, request_id: str) -> None:
        """异步记录流式查询日志"""
        log_entry = {
            "request_id": request_id,
            "query": query_data.query,
            "type": "stream",
            "answer_length": len(final_answer),
            "total_time": total_time,
            "timestamp": datetime.now().isoformat()
        }
        
        self.query_history.append(log_entry)
        logger.info(f"异步记录流式查询 - RID: {request_id}, 用时: {total_time:.3f}s")
    
    async def _update_performance_stats(self, response_time: float) -> None:
        """异步更新性能统计"""
        self.performance_stats["total_queries"] += 1
        
        total_queries = self.performance_stats["total_queries"] 
        current_avg = self.performance_stats["avg_response_time"]
        
        # 移动平均计算
        self.performance_stats["avg_response_time"] = (
            (current_avg * (total_queries - 1) + response_time) / total_queries
        )
        
        logger.info(f"性能统计更新 - 总查询: {total_queries}, 平均响应: {self.performance_stats['avg_response_time']:.3f}s")
    
    def _handle_timeout_error(self, query: str, request_id: str) -> RAGResponse:
        """处理超时错误"""
        return RAGResponse(
            query=query,
            answer="抱歉，查询处理超时。这可能是由于系统负载较高或检索文档过多导致的。请稍后重试或简化您的查询。",
            sources=[],
            confidence=0.0,
            processing_time=self.config.query_timeout_seconds,
            request_id=request_id,
            timestamp=datetime.now(),
            metadata={"error": "query_timeout", "timeout_seconds": self.config.query_timeout_seconds}
        )
    
    async def _handle_processing_error(self, query: str, error_message: str, request_id: str) -> RAGResponse:
        """处理处理错误"""
        logger.error(f"查询处理错误 - RID: {request_id}, 错误: {error_message}")
        
        return RAGResponse(
            query=query,
            answer="查询处理时发生错误。请稍后重试，如问题持续请联系技术支持。",
            sources=[],
            confidence=0.0,
            processing_time=0.0,
            request_id=request_id,
            timestamp=datetime.now(),
            metadata={"error": error_message}
        )
    
    async def get_system_stats(self) -> Dict[str, Any]:
        """获取系统统计信息"""
        active_queries = len([req async for req in self._get_active_requests()])
        cache_hit_rate = await self._calculate_cache_hit_rate()
        
        return {
            "runtime_statistics": {
                "total_queries_processed": self.performance_stats["total_queries"],
                "average_response_time": round(self.performance_stats["avg_response_time"], 3),
                "cache_hit_rate": round(cache_hit_rate, 2),
                "active_concurrent_requests": active_queries
            },
            "capacity_metrics": {
                "max_concurrent_queries": self.config.max_concurrent_queries,
                "current_semaphore_value": self.request_semaphore._value,
                "memory_usage": self._get_memory_usage()
            },
            "recent_queries": self.query_history[-10:] if len(self.query_history) >= 10 else self.query_history,
            "system_timestamp": datetime.now().isoformat()
        }
    
    async def _get_active_requests(self):
        """获取活跃请求（异步生成器）"""
        if hasattr(self.request_semaphore, '_waiters'):
            for waiter in self.request_semaphore._waiters:
                yield waiter
    
    async def _calculate_cache_hit_rate(self) -> float:
        """计算缓存命中率"""
        # 简化实现
        return 0.85  # 模拟85%缓存命中率
    
    def _get_memory_usage(self) -> Dict[str, int]:
        """获取内存使用情况"""
        import psutil
        try:
            process = psutil.Process()
            return {"rss_mb": int(process.memory_info().rss / 1024 / 1024)}
        except:
            return {"rss_mb": 0}

# FastAPI应用构建器
class AsyncRAGServiceAPIBuilder:
    """异步RAG服务API构建器"""
    
    def __init__(self):
        self.rag_service = EnterpriseAsyncRAGService()
        self.app = None
    
    def create_async_rag_service_api(self) -> FastAPI:
        """创建异步RAG服务API"""
        logger.info("🚀 构建异步RAG服务API应用")
        
        app = FastAPI(
            title="🌟 企业级异步RAG服务API",
            description="""
企业级LangChain异步RAG处理服务

✨ **核心特性:**
- 异步高并发处理 (Async/await optimization)
- Server-Sent Events流式响应支持
- 智能检索与重排序算法
- Redis缓存集成与优化
- Qdrant向量数据库支持
- 实时性能监控与统计

🏭 **企业级特性:**
- 上下文关联检索
- 多模态RAG处理
- 流式响应体验
- 可扩展架构设计
- 生产级错误处理
""",
            version="1.0.0",
            docs_url="/docs",
            redoc_url="/redoc"
        )

        # 添加异步中间件
        app.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )
        
        self._setup_async_routes(app)
        self.app = app
        return app
    
    def _setup_async_routes(self, app: FastAPI):
        """设置异步路由"""
        
        # 健康检查
        @app.get("/api/v2/health")
        async def health_check():
            """异步健康检查"""
            stats = await self.rag_service.get_system_stats()
            return {"status": "healthy", "stats": stats}
        
        # 异步RAG查询
        @app.post("/api/v2/rag/async-query")
        async def async_rag_query(query_data: dict):
            """标准异步RAG查询"""
            try:
                rag_query = RAGQuery(**query_data)
                response = await self.rag_service.process_query_async(rag_query)
                return {
                    "success": True,
                    "request_id": response.request_id,
                    "data": response.__dict__,
                    "processing_time": response.processing_time
                }
            except Exception as e:
                logger.error(f"异步查询错误: {str(e)}")
                return {
                    "success": False,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # Server-Sent Events流式查询
        @app.post("/api/v2/rag/stream-query")
        async def stream_rag_query(query_data: dict):
            """流式RAG查询（Server-Sent Events）"""
            try:
                rag_query = RAGQuery(**query_data)
                return StreamingResponse(
                    self.rag_service.stream_query_async(rag_query),
                    media_type="text/event-stream",
                    headers={
                        "Cache-Control": "no-cache",
                        "Connection": "keep-alive",
                        "X-Accel-Buffering": "no"
                    }
                )
            except Exception as e:
                logger.error(f"流式查询错误: {str(e)}")
                return JSONResponse(
                    status_code=500,
                    content={
                        "success": False,
                        "error": str(e),
                        "timestamp": datetime.now().isoformat()
                    }
                )
        
        # 批量异步查询
        @app.post("/api/v2/rag/batch-query")
        async def batch_rag_query(batch_data: dict):
            """批量异步RAG查询"""
            try:
                queries = batch_data.get("queries", [])
                concurrent_limit = batch_data.get("max_concurrent", 5)
                
                if len(queries) > 20:
                    return {"success": False, "error": "批量查询最多支持20条"}
                
                # 使用Semaphore控制并发
                semaphore = asyncio.Semaphore(concurrent_limit)
                
                async def query_with_semaphore(query_data):
                    async with semaphore:
                        rag_query = RAGQuery(**query_data)
                        response = await self.rag_service.process_query_async(rag_query)
                        return {
                            "query": query_data.get("query"), 
                            "request_id": response.request_id,
                            "response_time": response.processing_time
                        }
                
                # 批量异步执行
                batch_start = time.time()
                results = await asyncio.gather(
                    *[query_with_semaphore(q) for q in queries],
                    return_exceptions=True
                )
                
                batch_time = time.time() - batch_start
                
                return {
                    "success": True,
                    "batch_results": results,
                    "total_batch_time": batch_time,
                    "average_response_time": batch_time / len(queries) if queries else 0
                }
            except Exception as e:
                return {"success": False, "error": str(e)}

def main():
    """主函数：测试异步RAG服务"""
    print("🌟 LangChain L3 Advanced - Week 11: 企业级异步RAG服务")
    print("=" * 70)
    
    builder = AsyncRAGServiceAPIBuilder()
    
    try:
        # 创建异步RAG服务API
        app = builder.create_async_rag_service_api()
        
        print("\n✅ 企业级异步RAG服务API创建成功！")
        print("\n📑 主要特性：")
        print("   🌊 异步并发查询处理")
        print("   📡 Server-Sent Events流式响应")
        print("   💨 Redis异步缓存集成")
        print("   🎯 Qdrant向量数据库支持")
        print("   📊 实时性能监控")
        print("   🔧 批量并发查询")
        
        print("\n🚀 测试API端点：")
        print("   POST /api/v2/rag/async-query     - 标准异步查询")
        print("   POST /api/v2/rag/stream-query    - 流式查询(SSE)")
        print("   POST /api/v2/rag/batch-query     - 批量查询")
        print("   GET  /api/v2/health              - 系统健康检查")
        
        print("\n🌐 启动应用：")
        print("   python 02_async_rag_service.py")
        
        import uvicorn
        
        # 如果直接运行，启动服务器
        uvicorn.run(app, host="0.0.0.0", port=8001, log_level="info")
        
    except Exception as e:
        print(f"\n❌ 异步RAG服务创建失败: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()