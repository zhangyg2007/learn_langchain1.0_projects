"""
RAGFlow集成模块
集成RAGFlow企业级RAG平台
"""
import os
import json
import httpx
from typing import Dict, Any, Optional, List
from datetime import datetime


class RAGFlowClient:
    """RAGFlow API客户端"""
    
    def __init__(
        self, 
        api_key: str = None, 
        base_url: str = None,
        timeout: int = 300  # RAG操作可能需要更长时间
    ):
        self.api_key = api_key or os.getenv("RAGFLOW_API_KEY")
        self.base_url = base_url or os.getenv("RAGFLOW_BASE_URL", "http://localhost:9380/api/v1")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        
    def _get_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def create_dataset(self, name: str, description: str = None) -> Dict[str, Any]:
        """创建数据集"""
        
        payload = {
            "name": name,
            "description": description or f"LangChain数据集: {name}",
            "language": "zh",
            "permission": "me"  # private dataset
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/datasets",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"创建数据集失败: {str(e)}")
    
    def upload_document(
        self, 
        dataset_id: str, 
        file_path: str, 
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> Dict[str, Any]:
        """上传文档到RAGFlow"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                files = {"file": file}
                data = {
                    "dataset_id": dataset_id,
                    "chunk_size": chunk_size,
                    "chunk_overlap": chunk_overlap,
                    "parser_id": "naive"  # 可以使用更复杂的解析器
                }
                
                # RAGFlow可能使用multipart/form-data
                response = self.client.post(
                    f"{self.base_url}/docs",
                    files=files,
                    data=data,  # 注意这里使用data而不是json
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            raise Exception(f"文档上传失败: {str(e)}")
    
    def add_document_from_text(
        self, 
        dataset_id: str, 
        text: str, 
        name: str = None,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> Dict[str, Any]:
        """从文本创建文档"""
        
        payload = {
            "dataset_id": dataset_id,
            "text": text,
            "name": name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "chunk_size": chunk_size,
            "chunk_overlap": chunk_overlap,
            "parser_id": "naive"
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/docs/text",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"文本文档创建失败: {str(e)}")
    
    def create_chunk(self, dataset_id: str, content: str, keywords: List[str] = None) -> Dict[str, Any]:
        """创建知识chunk"""
        
        payload = {
            "dataset_id": dataset_id,
            "content": content,
            "keywords": keywords or [],
            "important_kwd": [],  # 重要关键词
            "question_kwd": [],    # 问题关键词
            "answer_kwd": []       # 答案关键词
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/chunks",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"创建chunk失败: {str(e)}")
    
    def retrieve_chunks(
        self, 
        dataset_id: str, 
        query: str, 
        top_k: int = 10,
        similarity_threshold: float = 0.1
    ) -> Dict[str, Any]:
        """检索相关chunks"""
        
        payload = {
            "dataset_id": dataset_id,
            "question": query,  # RAGFlow使用"question"参数
            "top_k": top_k,
            "similarity_threshold": similarity_threshold,
            "vector": True,     # 使用向量检索
            "keyword": True,    # 使用关键词检索
            "hybrid": True      # 混合检索模式
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/retrieval",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"检索失败: {str(e)}")
    
    def answer_question(
        self, 
        dataset_id: str, 
        question: str, 
        top_k: int = 5,
        llm_id: str = None
    ) -> Dict[str, Any]:
        """基于知识库的智能问答"""
        
        # 首先检索相关chunks
        retrieval_result = self.retrieve_chunks(dataset_id, question, top_k=top_k)
        
        if "data" not in retrieval_result or not retrieval_result["data"]["chunks"]:
            return {
                "answer": "抱歉，知识库中没有找到相关信息。",
                "chunks": [],
                "confidence": 0.0
            }
        
        # 获取检索到的chunks
        chunks = retrieval_result["data"]["chunks"]
        
        # 准备RAG回答的请求
        payload = {
            "dataset_id": dataset_id,
            "question": question,
            "top_k": top_k,
            "chunk_ids": [chunk["chunk_id"] for chunk in chunks],
            "llm_id": llm_id or self._get_default_llm_id()
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/answer",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            answer_result = response.json()
            
            # 组装结果
            return {
                "answer": answer_result.get("answer", ""),
                "chunks": chunks,
                "confidence": answer_result.get("confidence", 0.8),
                "llm_model": answer_result.get("llm_model", "unknown")
            }
            
        except httpx.HTTPError as e:
            return {
                "answer": f"回答生成失败: {str(e)}",
                "chunks": chunks,
                "confidence": 0.0,
                "error": str(e)
            }
    
    def _get_default_llm_id(self) -> str:
        """获取默认LLM ID"""
        # 这里可以根据配置的DEFAULT_PROVIDER来确定默认LLM
        default_provider = os.getenv("DEFAULT_PROVIDER", "deepseek")
        
        llm_mapping = {
            "deepseek": "deepseek-chat",
            "zhipu": "glm-4",
            "moonshot": "moonshot-v1-8k",
            "openai": "gpt-3.5-turbo"
        }
        
        return llm_mapping.get(default_provider, "deepseek-chat")
    
    def get_dataset_info(self, dataset_id: str) -> Dict[str, Any]:
        """获取数据集详细信息"""
        
        try:
            response = self.client.get(
                f"{self.base_url}/datasets/{dataset_id}",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"获取数据集信息失败: {str(e)}")
    
    def list_datasets(self, page: int = 1, size: int = 10) -> Dict[str, Any]:
        """列出所有数据集"""
        
        params = {
            "page": page,
            "size": size
        }
        
        try:
            response = self.client.get(
                f"{self.base_url}/datasets",
                params=params,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"列出数据集失败: {str(e)}")


class RAGFlowIntegration:
    """RAGFlow企业级RAG集成管理器"""
    
    def __init__(self):
        self.client = RAGFlowClient()
        self.current_dataset_id = None
    
    def create_knowledge_base(self, name: str, description: str = None) -> str:
        """创建知识库"""
        
        result = self.client.create_dataset(name, description)
        self.current_dataset_id = result.get("data", {}).get("id")
        
        if not self.current_dataset_id:
            raise Exception("创建知识库失败，未返回数据集ID")
        
        return self.current_dataset_id
    
    def add_documents(
        self, 
        texts: List[str], 
        documents: List[Dict[str, Any]] = None,
        chunk_size: int = 512,
        chunk_overlap: int = 50
    ) -> Dict[str, Any]:
        """批量添加文档"""
        
        if not self.current_dataset_id:
            raise ValueError("请先创建知识库或指定dataset_id")
        
        results = []
        
        # 处理文本列表
        if texts:
            for i, text in enumerate(texts):
                try:
                    result = self.client.add_document_from_text(
                        self.current_dataset_id,
                        text,
                        f"text_document_{i}.txt",
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e), "text_index": i})
        
        # 处理文档列表
        if documents:
            for i, doc in enumerate(documents):
                try:
                    result = self.client.add_document_from_text(
                        self.current_dataset_id,
                        doc.get("content", ""),
                        doc.get("filename", f"document_{i}.txt"),
                        chunk_size=chunk_size,
                        chunk_overlap=chunk_overlap
                    )
                    results.append(result)
                except Exception as e:
                    results.append({"error": str(e), "document_index": i})
        
        return {
            "dataset_id": self.current_dataset_id,
            "total_documents": len(texts or []) + len(documents or []),
            "successful_uploads": len([r for r in results if "error" not in r]),
            "results": results
        }
    
    def create_multi_modal_kb(self, image_paths: List[str], texts: List[str]) -> str:
        """创建多模态知识库（图片+文本）"""
        
        # 创建专门的多模态数据集
        kb_id = self.create_knowledge_base("multimodal_kb", "多模态知识库")
        
        # 处理文本
        if texts:
            self.add_documents(texts)
        
        # 处理图片（如果支持）
        for image_path in image_paths:
            # TODO: 实现图片处理和OCR
            pass
        
        return kb_id
    
    def smart_qa_chain(self, question: str, top_k: int = 5) -> Dict[str, Any]:
        """智能问答链"""
        
        if not self.current_dataset_id:
            return {"error": "知识库未初始化", "answer": "请先创建知识库"}
        
        try:
            result = self.client.answer_question(
                self.current_dataset_id,
                question,
                top_k=top_k
            )
            
            # 添加额外的元数据
            result["question"] = question
            result["top_k"] = top_k
            result["knowledge_base_id"] = self.current_dataset_id
            result["timestamp"] = datetime.now().isoformat()
            
            return result
            
        except Exception as e:
            return {
                "error": str(e),
                "answer": "处理问题时发生错误",
                "question": question,
                "knowledge_base_id": self.current_dataset_id
            }
    
    def bulk_qa(self, questions: List[str], top_k: int = 5) -> List[Dict[str, Any]]:
        """批量问答"""
        
        results = []
        for question in questions:
            result = self.smart_qa_chain(question, top_k)
            results.append(result)
        
        return results


# LangChain工具集成
def create_ragflow_tool(name: str = "RAGFlow_QA") -> Dict[str, Any]:
    """创建LangChain可用的RAGFlow工具"""
    
    return {
        "name": name,
        "description": "企业级RAG问答系统，基于RAGFlow知识库提供智能问答",
        "type": "retrieval_qa",
        "endpoint": f"{os.getenv('RAGFLOW_BASE_URL', 'http://localhost:9380/api/v1')}/retrieval",
        "method": "POST",
        "headers": {
            "Authorization": f"Bearer {os.getenv('RAGFLOW_API_KEY')}",
            "Content-Type": "application/json"
        },
        "input_schema": {
            "type": "object",
            "properties": {
                "dataset_id": {"type": "string", "description": "知识库ID"},
                "question": {"type": "string", "description": "问题"},
                "top_k": {"type": "integer", "description": "返回结果数量", "default": 5}
            },
            "required": ["dataset_id", "question"]
        }
    }


# 导出主要类
__all__ = [
    "RAGFlowClient",
    "RAGFlowIntegration",
    "create_ragflow_tool"
]

if __name__ == "__main__":
    # 测试代码
    try:
        integration = RAGFlowIntegration()
        
        # 创建测试知识库
        kb_id = integration.create_knowledge_base("test_kb", "测试知识库")
        print(f"创建知识库: {kb_id}")
        
        # 添加测试文档
        test_docs = ["LangChain是一个用于构建LLM应用的框架", "RAGFlow提供企业级RAG解决方案"]
        add_result = integration.add_documents(test_docs)
        print("文档添加结果:", add_result)
        
        # 测试问答
        qa_result = integration.smart_qa_chain("什么是RAGFlow？")
        print("问答结果:", qa_result)
        
    except Exception as e:
        print("需要配置RAGFLOW_API_KEY和RAGFLOW_BASE_URL环境变量才能测试")
        print(f"错误: {str(e)}")