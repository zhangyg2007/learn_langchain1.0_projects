"""
Dify集成模块
集成Dify工作流和低代码平台
"""
import os
import asyncio
from typing import Dict, Any, Optional, List
import httpx
import json
from datetime import datetime


class DifyClient:
    """Dify API客户端"""
    
    def __init__(
        self, 
        api_key: str = None, 
        base_url: str = None,
        timeout: int = 60
    ):
        self.api_key = api_key or os.getenv("DIFY_API_KEY")
        self.base_url = base_url or os.getenv("DIFY_BASE_URL", "http://localhost:3000/api/v1")
        self.timeout = timeout
        self.client = httpx.Client(timeout=timeout)
        
    def _get_headers(self) -> Dict[str, str]:
        """获取API请求头"""
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
    
    def chat_completion(
        self, 
        query: str, 
        inputs: Dict[str, Any] = None,
        response_mode: str = "streaming",
        conversation_id: str = None,
        user: str = "langchain-user"
    ) -> Dict[str, Any]:
        """调用Dify的对话API"""
        
        payload = {
            "query": query,
            "inputs": inputs or {},
            "response_mode": response_mode,
            "conversation_id": conversation_id,
            "user": user
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/chat-messages",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            
            if response_mode == "streaming":
                # 处理流式响应
                return self._handle_streaming_response(response)
            else:
                return response.json()
                
        except httpx.HTTPError as e:
            raise Exception(f"Dify API调用失败: {str(e)}")
    
    def upload_file(self, file_path: str, purpose: str = "document") -> Dict[str, Any]:
        """上传文件到Dify"""
        
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"文件不存在: {file_path}")
        
        try:
            with open(file_path, 'rb') as file:
                files = {"file": file}
                response = self.client.post(
                    f"{self.base_url}/files/upload",
                    files=files,
                    headers={"Authorization": f"Bearer {self.api_key}"}
                )
                response.raise_for_status()
                return response.json()
                
        except httpx.HTTPError as e:
            raise Exception(f"文件上传失败: {str(e)}")
    
    def create_document_from_text(self, text: str, name: str = None) -> Dict[str, Any]:
        """从文本创建文档"""
        
        payload = {
            "text": text,
            "name": name or f"document_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
            "process_rule": {
                "rules": [],
                "mode": "automatic"
            }
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/datasets/0/documents/create_by_text",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"文档创建失败: {str(e)}")
    
    def get_dataset_status(self, dataset_id: str = None) -> Dict[str, Any]:
        """获取数据集状态"""
        
        dataset_id = dataset_id or os.getenv("DIFY_DATASET_ID")
        if not dataset_id:
            raise ValueError("数据集ID未提供")
        
        try:
            response = self.client.get(
                f"{self.base_url}/datasets/{dataset_id}/status",
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"获取数据集状态失败: {str(e)}")
    
    def create_workflow(self, name: str, config: Dict[str, Any]) -> Dict[str, Any]:
        """创建工作流"""
        
        payload = {
            "name": name,
            "config": config,
            "description": config.get("description", f"LangChain工作流: {name}")
        }
        
        try:
            response = self.client.post(
                f"{self.base_url}/workflows",
                json=payload,
                headers=self._get_headers()
            )
            response.raise_for_status()
            return response.json()
            
        except httpx.HTTPError as e:
            raise Exception(f"创建工作流失败: {str(e)}")
    
    def _handle_streaming_response(self, response: httpx.Response) -> List[Dict[str, Any]]:
        """处理流式响应"""
        results = []
        for line in response.iter_lines():
            if line:
                try:
                    line_data = line.decode('utf-8')
                    if line_data.startswith('data: '):
                        json_data = line_data[6:]  # 去掉 'data: ' 前缀
                        if json_data != '[DONE]':
                            results.append(json.loads(json_data))
                except (json.JSONDecodeError, UnicodeDecodeError) as e:
                    results.append({"error": f"解析流式数据失败: {str(e)}"})
        
        return results


class DifyIntegration:
    """Dify工作流集成管理器"""
    
    def __init__(self):
        self.client = DifyClient()
    
    def create_chat_chain(self, context: str = None) -> Dict[str, Any]:
        """创建基于Dify的聊天链"""
        
        # 创建工作流配置
        workflow_config = {
            "type": "chat",
            "context": context,
            "retrieval": {
                "dataset_id": os.getenv("DIFY_DATASET_ID")
            }
        }
        
        return self.client.create_workflow("langchain_chat", workflow_config)
    
    def add_knowledge_base(self, documents: List[str], dataset_id: str = None) -> Dict[str, Any]:
        """添加知识库文档"""
        
        results = []
        for i, doc in enumerate(documents):
            try:
                result = self.client.create_document_from_text(
                    doc, f"document_{i}.txt"
                )
                results.append(result)
            except Exception as e:
                results.append({"error": str(e), "document_index": i})
        
        return {
            "total_documents": len(documents),
            "successful_uploads": len([r for r in results if "error" not in r]),
            "results": results
        }
    
    def chat_with_knowledge(self, query: str, user_id: str = "langchain_user") -> Dict[str, Any]:
        """基于知识库的问答"""
        
        inputs = {
            "user_id": user_id,
            "language": "zh",
            "enable_web_search": False
        }
        
        return self.client.chat_completion(
            query=query,
            inputs=inputs,
            response_mode="blocking",  # 使用阻塞模式获得完整响应
            user=user_id
        )
    
    def file_qa_chain(self, file_path: str, question: str) -> Dict[str, Any]:
        """文件问答链"""
        
        # 上传文件
        try:
            upload_result = self.client.upload_file(file_path)
            file_id = upload_result.get("id")
            
            # 基于文件进行问答
            inputs = {
                "file_id": file_id,
                "question": question
            }
            
            return self.client.chat_completion(
                query=question,
                inputs=inputs,
                user="file_qa_user"
            )
            
        except Exception as e:
            return {"error": f"文件问答处理失败: {str(e)}"}


# LangChain集成便利函数
def create_dify_tool(name: str, description: str) -> Dict[str, Any]:
    """创建LangChain可用的Dify工具"""
    
    return {
        "name": name,
        "description": description,
        "type": "api",
        "endpoint": f"{os.getenv('DIFY_BASE_URL')}/chat-messages",
        "method": "POST",
        "headers": {
            "Authorization": f"Bearer {os.getenv('DIFY_API_KEY')}",
            "Content-Type": "application/json"
        },
        "input_schema": {
            "type": "object",
            "properties": {
                "query": {"type": "string", "description": "用户查询"},
                "inputs": {"type": "object", "description": "额外输入"},
                "user": {"type": "string", "description": "用户ID"}
            },
            "required": ["query"]
        }
    }


# 异步支持
async def async_chat_with_dify(query: str, **kwargs) -> Dict[str, Any]:
    """异步版本的Dify对话"""
    
    integration = DifyIntegration()
    loop = asyncio.get_event_loop()
    
    # 在线程池中执行同步调用
    result = await loop.run_in_executor(
        None, 
        integration.chat_with_knowledge, 
        query,
        kwargs.get("user_id", "async_user")
    )
    
    return result

# 导出主要类
__all__ = [
    "DifyClient",
    "DifyIntegration", 
    "create_dify_tool",
    "async_chat_with_dify"
]

if __name__ == "__main__":
    # 测试代码
    try:
        integration = DifyIntegration()
        
        # 测试对话
        test_result = integration.chat_with_knowledge("你好，请介绍LangChain")
        print("对话测试结果:", test_result)
        
        # 测试知识库
        test_docs = ["LangChain是一个用于构建LLM应用的框架"]
        kb_result = integration.add_knowledge_base(test_docs)
        print("知识库测试结果:", kb_result)
        
    except Exception as e:
        print("需要配置DIFY_API_KEY和DIFY_BASE_URL环境变量才能测试")
        print(f"错误: {str(e)}")