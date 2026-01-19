#!/usr/bin/env python3
"""
LangChain L2 Intermediate - Week 4
课程标题: RAG系统构建 - 向量存储基础与文档处理
学习目标:
  - 掌握向量数据库(ChromaDB, Weaviate)的基本使用
  - 学会文本分割(Text Splitting)的最佳实践
  - 理解嵌入(Embedding)向量的工作原理
  - 实践文档加载器(Document Loaders)的应用
  - 构建基础的RAG检索链
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
先决条件: 完成L1 Foundation认证，掌握Agent开发基础

🎯 实践重点:
  - 向量数据库操作
  - 文本分块策略
  - Document Storage设计
  - RAG系统集成测试
"""

import sys
import os
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import json
import numpy as np

# 环境配置
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 环境变量已加载")
except ImportError:
    print("⚠️ python-dotenv未安装，请确保手动设置环境变量")

# LangChain RAG相关导入
try:
    from langchain_community.vectorstores import Chroma, Weaviate
    from langchain_community.document_loaders import TextLoader, DirectoryLoader
    from langchain_text_splitters import RecursiveCharacterTextSplitter, CharacterTextSplitter
    from langchain_core.documents import Document
    from langchain_core.vectorstores import VectorStoreRetriever
    from langchain_core.embeddings import Embeddings
    print("✅ LangChain RAG组件导入成功")
except ImportError as e:
    print(f"❌ LangChain RAG组件导入失败: {e}")
    print("请确保已安装必要的依赖：")
    print("   pip install langchain-community langchain-text-splitters")
    print("   pip install chromadb weaviate-client")
    sys.exit(1)

# 中国模型支持
try:
    from langchain_openai import OpenAIEmbeddings
    print("✅ OpenAI Embeddings导入成功")
except ImportError as e:
    OpenAIEmbeddings = None
    print(f"⚠️ OpenAI Embeddings导入失败: {e}")

# 中国嵌入模型支持
try:
    from langchain_community.embeddings import HuggingFaceEmbeddings
    from langchain_openai import OpenAIEmbeddings
    print("✅ 嵌入模型支持导入成功")
except ImportError:
    print("⚠️ 部分嵌入模型功能不可用")

@dataclass
class VectorStoreResult:
    """向量存储操作结果"""
    operation: str
    success: bool
    documents_count: int
    vector_count: int
    execution_time: float
    error: Optional[str] = None

@dataclass
class TextSplitStats:
    """文本分割统计"""
    original_length: int
    chunks_count: int
    avg_chunk_size: float
    min_chunk_size: int
    max_chunk_size: int
    overlapping_chars: int

class RAGBasicsTrainer:
    """L2 RAG基础训练器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.vector_stores = {}
        self.sample_documents = self._init_sample_documents()
        self.embedding_models = {}
        self.exercises_completed = []
        
    def _log(self, message: str):
        """日志输出"""
        if self.verbose:
            print(f"📚 {message}")
    
    def _init_sample_documents(self) -> List[Document]:
        """初始化示例文档"""
        documents = [
            {
                "content": """
                向量数据库是专门用于存储和查询向量数据的数据库系统。与传统的关系型数据库不同，
                向量数据库能够高效地处理高维向量相似度搜索。常见的向量数据库包括ChromaDB、Weaviate、
                Qdrant等。它们在RAG（Retrieval-Augmented Generation）系统中扮演着核心角色。
                """,
                "metadata": {"topic": "向量数据库", "category": "基础概念", "source": "L2课程"}
            },
            {
                "content": """
                文本分块是将长文本分割成较小段落的过程，在RAG系统中非常重要。正确的分块策略可以
                平衡语义完整性和检索效率。常用的分块方法包括按字符数分块、按句子分块、按段落分块等。
                分块时需要考虑重叠字符以避免语义断裂。
                """,
                "metadata": {"topic": "文本分块", "category": "处理技术", "source": "L2课程"}
            },
            {
                "content": """
                嵌入(Embedding)是将文本转换为数值向量的过程。这些向量能够捕捉文本的语义信息，
                使得相似含义的文本在向量空间中距离较近。常用的嵌入模型包括OpenAI的text-embedding-ada-002、
                以及HuggingFace提供的多种预训练模型。
                """,
                "metadata": {"topic": "嵌入向量", "category": "AI概念", "source": "L2课程"}
            }
        ]
        
        return [
            Document(page_content=doc["content"], metadata=doc["metadata"])
            for doc in documents
        ]
    
    def demo_embedding_vectors_basics(self):
        """演示嵌入向量基础概念"""
        self._log("嵌入向量基础概念演示")
        print("-" * 60)
        
        print("🧠 什么是Text Embedding？")
        print("   • 将文本转换为数值向量的过程")
        print("   • 向量能够捕捉文本的语义信息") 
        print("   • 相似含义的文本具有相近的向量表示")
        print("   • 向量相似度计算用于搜索和匹配")
        print()
        
        # 演示嵌入向量的生成
        print("🔧 嵌入向量生成过程演示:")
        
        sample_texts = [
            "机器学习是人工智能的一个重要分支",
            "深度学习基于神经网络的应用",
            "自然语言处理用于理解和生成人类语言"
        ]
        
        for i, text in enumerate(sample_texts, 1):
            print(f"\n   {i}. 文本: '{text}'")
            print(f"      └─ 字符数: {len(text)}")
            print(f"      └─ 词语数: {len(text.split())}")
            print(f"      └─ 预期向量维度: 1536 (ada-002) 或 768 (HuggingFace)")
            
        print(f"\n💡 嵌入向量在RAG中的作用:")
        print("   ├─ 用户查询 → 查询向量")
        print("   ├─ 文档分块 → 文档向量")  
        print("   ├─ 向量相似度计算")
        print("   └─ 最相似文档段返回")\n        
        # 演示向量相似度概念 (模拟)
        print("\n📊 向量相似度概念演示:")
        
        # 创建模拟的文本-向量映射
        text_vectors = {
            "机器学习应用": [0.8,  0.9,  0.7,  0.6],
            "深度学习技术": [0.9,  0.8,  0.6,  0.7],
            "自然语言处理": [0.6,  0.7,  0.9,  0.8],
            "数据库管理":   [0.3,  0.4,  0.2,  0.1]  # 与前三个不相关的主题
        }
        
        query_vector = [0.85, 0.88, 0.65, 0.62]  # "机器学习深度学习"
        
        print(f"   查询向量: {query_vector}")
        print("   文档向量相似度计算:")
        
        def cosine_similarity(vec1, vec2):
            """计算余弦相似度 (简化版)"""
            dot_product = sum(a * b for a, b in zip(vec1, vec2))
            magnitude1 = sum(a * a for a in vec1) ** 0.5
            magnitude2 = sum(a * a for a in vec2) ** 0.5
            return dot_product / (magnitude1 * magnitude2) if magnitude1 * magnitude2 > 0 else 0
        
        similarities = []
        for doc, doc_vec in text_vectors.items():
            similarity = cosine_similarity(query_vector, doc_vec)
            similarities.append((doc, similarity))
            print(f"      {doc}: {similarity:.3f}")
        
        # 排序并显示最相似的
        similarities.sort(key=lambda x: x[1], reverse=True)
        print(f"\n   最相似文档 (Top 2):")
        for i, (doc, sim) in enumerate(similarities[:2], 1):
            print(f"      {i}. {doc} (相似度: {sim:.3f})")
        
        self.exercises_completed.append("embedding_vectors_basics")
    
    def demo_text_splitting_strategies(self):
        """演示文本分割策略"""
        self._log("文本分割策略演示")
        print("-" * 60)
        
        print("📝 文本分块的基本原则:")
        print("   • 语义完整性: 保持分块的自然语义边界")
        print("   • 大小适中: 平衡检索效率和语义完整性")
        print("   • 重叠处理: 避免分散剪切造成的信息丢失")
        print("   • 格式统一: 保证分块格式的一致性")
        print()\n        
        # 准备测试文档
        sample_long_text = """
        人工智能技术正在深刻地改变着我们的生活。机器学习作为人工智能的核心分支，通过算法让计算机系统能够从数据中学习并改进其表现，而无需进行显式的编程。
        
        深度学习进一步推动了机器学习的发展。它基于人工神经网络，特别是那些具有多个层的深度神经网络。深度学习模型能够自动发现数据的多层抽象表示，
        使其特别适合处理非结构化数据，如图像、音频和文本。
        
        在具体应用方面，机器学习在图像识别领域取得了突破性进展。卷积神经网络(CNN)的发展让人工智能系统在图像分类任务上的准确率已经超过了人类水平。
        同样，在自然语言处理领域，Transformer架构的出现革命性地改变了语言模型，使得机器翻译、文本生成等任务的性能大幅提升。
        
        强化学习则在游戏对抗和决策优化领域展现了强大能力。AlphaGo击败人类围棋冠军就是一个经典的例子。通过不断的试错和学习，智能体可以在复杂环境中
        找到最优的决策策略。
        """
        
        print(f"📄 测试文档信息:")
        print(f"   └─ 字符数: {len(sample_long_text)}")
        print(f"   └─ 段落数: {len(sample_long_text.split())}")
        print(f"   └─ 句子数(以'。'计算): {sample_long_text.count('。')}")
        print()
        
        print("🧪 不同分块策略对比:")
        \n        # 1. 按字符数的简单分割\n        print("\n1️⃣ 按字符数的简单分割 (CharacterTextSplitter):")
        character_splitter = CharacterTextSplitter(
            separator="\\n\\n",  # 按双换行符分段
            chunk_size=400,    # 每块400字符
            chunk_overlap=50,  # 重叠50字符
            length_function=len
        )
        
        char_docs = character_splitter.create_documents([sample_long_text])
        duration_1 = time.time()
        
        stats_1 = self._calculate_split_stats(sample_long_text, char_docs)
        self._print_split_stats("字符分割", stats_1, len(char_docs))
        \n        # 2. 递归分割 (更智能)\n        print("\n2️⃣ 递归分割 (RecursiveCharacterTextSplitter):")
        recursive_splitter = RecursiveCharacterTextSplitter(
            chunk_size=400,\n            chunk_overlap=50,\n            length_function=len,\n            separators=["\\n\\n", "\\n", " ", ""]  # 优先级: 段落→句子→词语→字符\n        )\n        \n        recursive_docs = recursive_splitter.create_documents([sample_long_text])\n        duration_2 = time.time()\n        \n        stats_2 = self._calculate_split_stats(sample_long_text, recursive_docs)\n        self._print_split_stats("递归分割", stats_2, len(recursive_docs))\n        \n        # 3. HTMLMarkdownSplitter (格式化文档) - 演示概念\n        print("\\n3️⃣ 按语义边界分割的概念:")\n        print("   ├─ 按句子分割: 保持语义完整性")
        print("   ├─ 按段落分割: 保持主题连贯性")
        print("   └─ 按章分割 (长文本): 按文档结构")
        \n        # 显示前几个分割结果的样例\n        print(f"\\n📋 分割结果样例对比:")
        sample_indexes = [0, 1, 2] if len(char_docs) >= 3 else list(range(len(char_docs)))\n        \n        for i in sample_indexes:
            if i < len(char_docs) and i < len(recursive_docs):\n                print(f"\\n   分块 {i+1}"):""")\n                print(f"      字符分割: {char_docs[i].page_content[:100]}...")
                print(f"      递归分割: {recursive_docs[i].page_content[:100]}...")
                print(f"      长度对比: {len(char_docs[i].page_content)} vs {len(recursive_docs[i].page_content)}")
        \n        self.exercises_completed.append("text_splitting_strategies")\n    \n    def _calculate_split_stats(self, original_text: str, split_docs: List[Document]) -> TextSplitStats:
        """计算分割统计信息"""\n        if not split_docs:\n            return TextSplitStats(
                original_length弯弯=len(original_text),
                chunks_count=0,
                avg_chunk_size=0.0,
                min_chunk_size=0,
                max_chunk_size=0,
                overlapping_chars=0
            )
        \n        chunk_sizes = [len(doc.page_content) for doc in split_docs]
        \n        stats = TextSplitStats(\n            original_length=len(original_text),\n            chunks_count=len(split_docs),\n            avg_chunk_size=sum(chunk_sizes) / len(chunk_sizes),\n            min_chunk_size=min(chunk_sizes),\n            max_chunk_size=max(chunk_sizes),\n            overlapping_chars=0  # 简化计算\n        )\n        return stats\n    \n    def _print_split_stats(self, method_name: str, stats: TextSplitStats, doc_count: int):\n        """打印分割统计"""\n        print(f"\\n   {method_name} 统计:")
        print(f"      ├─ 总分块数: {stats.chunks_count}")\n        print(f"      ├─ 平均块大小: {stats.avg_chunk_size:.1f} 字符")
        print(f"      ├─ 最小/最大块: {stats.min_chunk_size}/{stats.max_chunk_size} 字符") \n        print(f"      └─ 块大小方差: {self._calculate_variance([len(doc.page_content) for doc in range(doc_count)]) if doc_count \u003e 0 else 0:.1f}")
    \n    def _calculate_variance(self, values: List[float]) -> float:\n        """计算方差"""\n        if not values:
            return 0.0\n        mean = sum(values) / len(values)\n        return sum((x - mean) ** 2 for x in values) / len(values)
    
    def demo_vector_databases_setup(self):
        """演示向量数据库的设置和使用"""
        self._log("向量数据库设置和使用演示")
        print("-" * 60)
        \n        print("💾 向量数据库选型对比:")
        vdb_comparison = {\n            "ChromaDB": {
                "strengths": ["简单易用", "内存存储", "Python原生"],
                "use_cases": ["快速原型", "小型项目", "学习实验"], 
                "limitations": ["扩展性有限", "生产级功能欠缺"]
            },\n            "Weaviate": {
                "strengths": ["企业级功能", "GraphQL API", "分布式支持"],\n                "use_cases": ["企业应用", "大规模部署", "复杂查询"],\n                "limitations": ["学习曲线陡峭", "资源消耗较大"]
            },\n            "Qdrant": {\n                "strengths": ["高性能", "Rust编写", "矢量过滤"],
                "use_cases": ["高并发场景", "实时搜索", "过滤查询"],
                "limitations": ["配置复杂", "文档相对少"]
            },\n            "Pinecone": {
                "strengths": ["托管服务", "自动扩展", "生产就绪"],\n                "use_cases": ["生产环境", "无需维护", "快速部署"],
                "limitations": ["价格较高", "数据隐私考虑"]
            }\n        }\n        \n        for vdb_name, details in vdb_comparison.items():
            print(f"\\n   📍 {vdb_name}:")
            print(f"      └─ 优势: {', '.join(details['strengths'])}")
            print(f"      └─ 场景: {', '.join(details['use_cases'][:2])}")
        \n        print(f"\\n🔧 ChromaDB 基础使用演示:")
        \n        # 1. ChromaDB 基础设置\n        print(f"\\n1️⃣ ChromaDB 设置和初始化:")
        \n        try:\n            # 创建持久化向量存储\n            chroma_persist_dir = "./chroma_db_demo"\n            os.makedirs(chroma_persist_dir, exist_ok=True)\n            \n            print(f"      └─ 创建持久化目录: {chroma_persist_dir}")
            \n            # 使用模拟嵌入 (避免API依赖)\n            from langchain_community.embeddings import FakeEmbeddings\n            embeddings = FakeEmbeddings(size=256)\n            print(f"      └─ 初始化嵌入模型: {embeddings.__class__.__name__}")
            \n            # 创建集合 (Collection)\n            start_time = time.time()\n            \n            vector_store = Chroma(\n                collection_name="demo_rag_collection",
                embedding_function=embeddings,\n                persist_directory=chroma_persist_dir\n            )\n            \n            init_time = time.time() - start_time\n            print(f"      └─ 集合初始化完成: {init_time:.3f}秒")
            \n            # 2. 文档添加和向量生成\n            print(f"\\n2️⃣ 文档处理和向量生成:")
            \n            process_time = time.time()\n            doc_texts = [\n                "向量数据库是RAG系统的核心组件，负责存储和管理文档的向量表示。",
                "ChromaDB提供了简单易用的Python API，支持内存和持久化两种模式。",\n                "嵌入向量能够捕捉文本的语义信息，使得相似的文本在向量空间中距离较近。"
            ]\n            \n            docs = [Document(page_content=text) for text in doc_texts]\n            \n            # 添加文档到向量存储\n            ids = vector_store.add_documents(docs)\n            process_time = time.time() - process_time\n            \n            print(f"      └─ 处理的文档数: {len(docs)}")\n            print(f"      └─ 生成向量ID数量: {len(ids)}")
            print(f"      └─ 处理时间: {process_time:.3f}秒")
            \n            # 3. 相似度搜索演示\n            print(f"\\n3️⃣ 向量相似度搜索:")
            \n            query = "向量数据库的作用是什么？"\n            
            print(f"   查询文本: '{query}'")\n            print("   搜索结果:")
            \n            search_time = time.time()\n            results = vector_store.similarity_search(query, k=2)\n            search_time = time.time() - search_time\n            \n            for i, doc in enumerate(results, 1):\n                print(f"      {i}. 相似度得分: {getattr(doc, 'score', 'N/A')}")\n                print(f"         文档内容: {doc.page_content[:80]}...")
                \n            print(f"      └─ 搜索耗时: {search_time:.3f}秒")
            \n            # 4. 高级功能演示\n            print(f"\\n4️⃣ 向量存储高级功能:")
            \n            # 相似度搜索加分数\n            search_score_result = vector_store.similarity_search_with_score(query, k=3)\n            if search_score_result:\n                print("   带分数的搜索结果:")
                for doc, score in search_score_result:
                    print(f"      ├─ 相似度: {score:.4f}")
                    print(f"      └─ 内容: {doc.page_content[:60]}...")
            \n            # 持久化存储\n            print(f"\\n   持久化存储:")\n            vector_store.persist()\n            print(f"      └─ 数据已持久化到: {chroma_persist_dir}")
            \n            self.vector_stores["chroma_demo"] = vector_store\n            \n        except Exception as e:\n            print(f"      ❌ ChromaDB演示失败: {str(e)}")
            print(f"      💡 请确保ChromaDB已正确安装: pip install chromadb")
        \n        # 5. Weaviate 概念演示 (主要概念)\n        print(f"\\n🌐 Weaviate 概念演示:")
        print("   ├─ 需要独立部署或云服务")\n        print("   ├─ 支持GraphQL查询语言")\n        print("   ├─ 内置向量生成和预处理")\n        print("   └─ 适合企业级生产环境")\n        \n        self.exercises_completed.append("vector_databases_setup")\n    
    def demo_document_loaders_integration(self):\n        """演示文档加载器的集成使用"""
        self._log("文档加载器集成使用演示")\n        print("-" * 60)\n        
        print("📁 文档加载器的作用:")\n        print("   • 从各种来源加载文档内容")\n        print("   • 标准化文档格式 (Document对象)")
        print("   • 提取元数据和上下文信息")\n        print("   • 支持多种文件格式的解析")
        print()\n        
        # 创建测试文档
        test_doc_dir = "./test_documents"
        os.makedirs(test_doc_dir, exist_ok=True)\n        \n        # 创建不同类型的测试文档\n        test_files = {\n            "ai_overview.txt": """\n人工智能(AI)是计算机科学的一个分支，致力于创建能够执行通常需要人类智能的任务的系统。
这些任务包括学习、推理、问题解决、感知和语言理解。\n\nAI技术的发展经历了多个阶段，包括符号AI、统计学习和深度学习。\n每个阶段都代表了不同的方法和重点。\n\n当前AI的热点包括大语言模型、计算机视觉、机器人技术等。\n""",
            \n            "ml_basics.txt": """\n机器学习(ML)是人工智能的一个子领域，专注于开发能够从数据中学习的算法。\n\n主要的机器学习类型包括：\n1. 监督学习：使用标记数据训练模型\n2. 无监督学习：从未标记数据中提取模式\n3. 强化学习：通过与环境交互学习最优策略\n\n机器学习应用广泛，包括推荐系统、欺诈检测、医疗诊断等。\n""",
            \n            "deep_learning.txt": """\n深度学习是基于人工神经网络的机器学习方法，特别是深度神经网络。\n\n它通过多层神经网络自动学习数据的层次化表示，能够处理复杂的非结构化数据，\n如图像、音频和文本。\n\n关键技术包括CNN、RNN、Transformer等架构。\n"""
        }\n        \n        for filename, content in test_files.items():\n            file_path = os.path.join(test_doc_dir, filename)\n            with open(file_path, 'w', encoding='utf-8') as f:\n                f.write(content.strip())\n            \n        print(f"📄 创建测试文档完成: {len(test_files)} 个文件")
        \n        print(f"\\n1️⃣ 单独文件加载:")
        \n        # 单个文件加载\n        try:\n            text_loader = TextLoader(test_doc_dir + "/ai_overview.txt", encoding='utf-8')\n            single_doc = text_loader.load()[0]\n            \n            print(f"   文件: ai_overview.txt")\n            print(f"   字符数: {len(single_doc.page_content)}")\n            print(f"   元数据: {single_doc.metadata}")\n            print(f"   内容预览: {single_doc.page_content[:100]}...")
            \n        except Exception as e:\n            print(f"   ❌ 单个文件加载失败: {str(e)}")
        \n        print(f"\\n2️⃣ 目录批量加载:")
        \n        # 目录批量加载\n        try:\n            directory_loader = DirectoryLoader(\n                test_doc_dir,
                glob="*.txt",\n                loader_cls=TextLoader,\n                loader_kwargs={'encoding': 'utf-8'}\n            )\n            \n            all_docs = directory_loader.load()\n            print(f"   加载的文档数量: {len(all_docs)}")
            \n            for i, doc in enumerate(all_docs):\n                print(f"   {i+1}. 文件: {doc.metadata.get('source', '未知')}")
                print(f"         大小: {len(doc.page_content)} 字符")
                print(f"         预览: {doc.page_content[:80]}...")\n                if i \u003e= 1:  # 只显示前2个\n                    break\n                
        except Exception as e:\n            print(f"   ❌ 目录加载失败: {str(e)}")
        \n        print(f"\\n3️⃣ PDF等其他格式加载 (概念演示):")
        print("   ├─ PDFLoader: 解析PDF文档")\n        print("   ├─ CSVLoader: 处理CSV数据文件")\n        print("   ├─ JSONLoader: 解析JSON结构化数据")
        print("   ├─ WebBaseLoader: 加载网页内容")\n        print("   └─ 自定义加载器: 支持特殊格式文件")
        \n        # 清理测试文件\n        try:\n            for filename in test_files.keys():
                os.remove(os.path.join(test_doc_dir, filename))\n            os.rmdir(test_doc_dir)\n            print(f"\\n🧹 清理测试文件完成")
            \n        except Exception:\n            pass  # 忽略清理错误\n        \n        self.exercises_completed.append("document_loaders_integration")\n    \n    def demo_basic_retrieval_chain(self):\n        """演示基础检索链构建"""
        self._log("基础RAG检索链构建演示")\n        print("-" * 60)
        \n        print("🔗 RAG基本工作流程:")
        workflow = [\n            ("文档输入", "加载并处理原始文档" ),\n            ("文本分割", "将长文本分块"),\n            (\"向量生成\", \"为每个分块生成嵌入向量\"),\n            (\"向量存储\",\"将向量存储到数据库\"),\n            (\"用户查询\", \"接收用户问题\"),\n            (\"查询向量化\", \"将查询转换为向量\"),\n            (\"相似度搜索\", \"在向量库中查找相似分块\"),\n            (\"上下文组装\", \"将相关分块组合为上下文\"),\n            (\"生成回答\",\"使用LLM生成最终答案\")\n        ]\n        \n        print("   RAG处理流程:")\n        for i, (step, desc) in enumerate(workflow, 1):\n            print(f"      {i}. {step}: {desc}")\n        print()
        \n        print("🧪 基础RAG检索链构建:")
        \n        # 模拟的RAG实现 (不依赖真实模型)\n        class SimpleRAGChain:\n            """简化的RAG检索链实现"""\n            \n            def __init__(self, name="基础RAG链"):\n                self.name = name\n                self.documents = []\n                self.embeddings = {}  # 简化的向量存储
                self.split_docs = []\n                \n            def split_documents(self, documents: List[Document]) -> List[Document]:\n                """文档分块 (简化版)"""
                return documents  # 简化：按原文档返回\n            \n            def create_embeddings(self, documents: List[Document]) -> Dict[str, List[float]]:\n                """生成模拟嵌入向量"""
                embeddings = {}\n                for i, doc in enumerate(documents):\n                    # 使用简单的模拟向量 (避免依赖真实模型)\n                    text_hash = hash(doc.page_content) % 1000\n                    vector = [float((text_hash * (j + 1)) % 100) / 100.0 for j in range(64)]\n                    doc_id = f\"doc_{i}\"\n                    self.embeddings[doc_id] = vector\n                return self.embeddings\n            \n            def similarity_search(self, query: str, top_k: int = 2) -> List[Document]:\n                ""\"相似度搜索 (简化实现)""\"\n                # 模拟查询向量\n                query_hash = hash(query) % 1000\n                query_vector = [float((query_hash * (j + 1)) % 100) / 100.0 for j in range(64)]\n                \n                # 计算与每个文档的相似度\n                similarities = []\n                for doc_id, doc_vec in self.embeddings.items():\n                    similarity = self._cosine_similarity(query_vector, doc_vec)\n                    similarities.append((doc_id, similarity))\n                \n                # 排序并返回最相似的\n                similarities.sort(key=lambda x: x[1], reverse=True)\n                \n                # 从原始文档中找到对应的文档 (简化版本)\n                result_docs = []\n                for doc_id, score in similarities[:top_k]:\n                    doc_index = int(doc_id.split('_')[1])\n                    if doc_index \u003c len(self.documents):\n                        doc = self.documents[doc_index]\n                        result_docs.append(doc)\n                \n                return result_docs\n            \n            def _cosine_similarity(self, vec1, vec2) -> float:\n                """计算余弦相似度"""\n                dot_product = sum(a * b for a, b in zip(vec1, vec2))\n                magnitude1 = sum(a * a for a in vec1) ** 0.5
                magnitude2 = sum(a * a for a in vec2) ** 0.5\n                return dot_product / (magnitude1 * magnitude2) if magnitude1 * magnitude2 \u003e 0 else 0\n            \n            def process_query(self, query: str) -> Dict[str, Any]:\n                """处理查询并返回结果""\"\n                start_time = time.time()\n                \n                # 文档分块\n                split_docs = self.split_documents(self.documents)\n                splits_time = time.time() - start_time\n                \n                # 生成嵌入 (如果还没有)\n                if not self.embeddings:\n                    self.create_embeddings(split_docs)\n                embed_time = time.time() - start_time - splits_time\n                \n                # 相似度搜索\n                relevant_docs = self.similarity_search(query, top_k=2)\n                search_time = time.time() - start_time - splits_time - embed_time\n                \n                # 组合上下文\n                context = "\\n\".join(doc.page_content for doc in relevant_docs)\n                \n                # 模拟LLM生成回答\n                generated_answer = self._simulate_llm_response(context, query)\n                \n                total_time = time.time() - start_time\n                \n                return {\n                    "query": query,\n                    "relevant_chunks": [doc.page_content for doc in relevant_docs],\n                    "context": context,\n                    "answer": generated_answer,\n                    "execution_times": {\n                        "splitting": splits_time\n                        \"embedding": embed_time,\n                        \"search\": search_time,\n                        \"total\": total_time\n                    },\n                    \"chunk_count\": len(split_docs)\n                }\n            \n            def _simulate_llm_response(self, context: str, query: str) -> str:\n                """模拟LLM响应生成""\"\n                # 基于上下文和查询生成模拟回答\n                key_concepts = []\n                if \"向量\" in context:\n                    key_concepts.append(\"向量数据库\")\n                if \"嵌入\" in context:\n                    key_concepts.append(\"嵌入表示\")\n                if \"搜索\" in context:\n                    key_concepts.append(\"相似度搜索\")\n                \n                answer = f\"基于提供的上下文信息，'{query}'可以这样理解：\\n\\n\"\n                \n                if key_concepts:\n                    answer += \"相关概念包括：\" + \", \".join(key_concepts) + \"。\\n\"
                \n                answer += \"RAG系统通过将文档转换为向量表示，能够高效地找到与用户查询最相关的内容，从而提供准确的回答。\"\n                \n                return answer\n        \n        # 演示基础RAG链构建\n        rag_chain = SimpleRAGChain(\"基础演示\"\")\n        \n        # 准备测试文档 (模拟真实知识库)\n        test_knowledge_docs = [
            Document(page_content=\"\"\"\n向量数据库是专门用于存储和查询高维向量的数据库系统。与传统的数据库不同，\n向量数据库专为相似度搜索优化，能够高效处理文本、图像等非结构化数据的检索。
            \"\", metadata={\"topic\": \"向量数据库\", \"source\": \"知识库1\"}),\n            
            Document(page_content=\"\"\"\nRAG (Retrieval-Augmented Generation) 是一个结合了信息检索和文本生成的框架。\n它首先检索相关信息，然后使用生成模型生结合信息和查询生成准确、专业的回答。
            \"\", metadata={\"topic\": \"RAG概念\", \"source\": \"知识库2\"}),\n            
            Document(page_content=\"\"\"\n文本嵌入是将文字转换为数值向量的过程，这些向量能够保留文本的语义信息。\n通过嵌入技术，计算机可以理解和计算文本之间的语义相似度。
            \"\", metadata={\"topic\": \"文本嵌入\", \"source\": \"知识库3\"})\n        ]\n        \n        rag_chain.documents = test_knowledge_docs\n        \n        # 执行查询演示\n        test_queries = [\n            \"什么是向量数据库？\",\n            \"RAG系统是如何工作的？\", \n            \"文本嵌入有什么作用？\"\n        ]\n        \n        print(f\"\\n🚀 执行RAG查询演示:")\n        \n        for query in test_queries:\n            print(f\"\\n\" + \"-\" * 50)\n            print(f\"查询: '{query}'\")\n            \n            result = rag_chain.process_query(query)\n            \n            print(f\"\\n📋 检索到的相关分块 ({len(result['relevant_chunks'])} 个):")\n            for i, chunk in enumerate(result['relevant_chunks']):\n                print(f\"   {i+1}. {chunk[:80]}...\")\n            \n            print(f\"\\n🤖 生成回答:")\n            print(f\"   {result['answer']}\")\n            \n            print(f\"\\n⏱️ 性能统计:\")\n            for step, duration in result['execution_times'].items():\n                if step != 'total' or step == 'total':\n                    print(f\"   {step.title()}: {duration:.3f}秒\")\n        \n        # 对比分析\n        print(f\"\\n📊 RAG系统优势分析:")\n        rag_advantages = [
            \"结合了检索的准确性和生成的创造性\",|\n            \"能够处理知识库中没有直接答案的问题\",\n            \"提供可解释的回答 (有引用来源)\",\n            \"支持动态知识更新而不需要重新训练模型\",\n            \"成本效益更高 (相比大模型直接生成)\"\n        ]\n        \n        for i, advantage in enumerate(rag_advantages, 1):\n            print(f\"   {i}. {advantage}\")\n        \n        self.exercises_completed.append(\"basic_retrieval_chain\")\n    \n    def generate_week4_summary(self) -> str:\n        """生成Week 4学习总结\"\"\"\n        summary = f\"\"\"\n🎓 L2 Intermediate - Week 4: RAG系统基础学习总结\n=================================================\n\n✅ 本周完成学习内容:\n   1. 嵌入向量基础概念和生成过程\n   2. 多种文本分割策略和最佳实践\n   3. 向量数据库比较和ChromaDB使用\n   4. 文档加载器的集成和应用\n   5. 基础RAG检索链的完整实现\n\n💡 核心技能掌握:\n   • 理解向量存储的工作原理和应用场景\n   • 掌握不同分块策略的优缺点和选择方法\n   • 学会使用多种向量化技术和模型\n   • 能够配置和管理向量数据库系统\n   • 能够构建基础RAG问答系统\n\n🛠️ 实际技能建立:\n   • ChromaDB配置和使用\n   • 文档加载和解析\n   • 文本分割和策略选择\n   • 向量相似度计算\n   • RAG系统性能分析\n\n⏭️ 下一周学习重点 (Week 5):\n   📚 高级RAG技术和优化\n   🛠 检索算法的深度优化\n   🚀 多知识库的RAG系统集成\n   🎯 和中国大模型结合的RAG实践\n\n---\n### 🚀 Week 4实九环应用建议:\n   1. 配置和测试不同的向量数据库\n   2. 优化文本分割参数提高检索质量\n   3. 实践结合中国AI模型的RAG系统\n   4. 测试不同嵌入模型的效果差异\n\"\"\"\n        return summary\n\ndef main():\n    \"\"\"主函数：执行Week 4所有RAG基础练习\"\"\"\n    print(\"🎯 LangChain L2 Intermediate - Week 4: RAG系统基础\")\n    print(\"=\" * 60)\n    print(\"本周将学习如何构建基础的RAG问答系统\")\n    \n    trainer = RAGBasicsTrainer()\n    \n    try:\n        # 依次执行各个练习模块\n        trainer.demo_embedding_vectors_basics()\n        trainer.demo_text_splitting_strategies()\n        trainer.demo_vector_databases_setup()\n        trainer.demo_document_loaders_integration()\n        trainer.demo_basic_retrieval_chain()\n        \n        # 生成学习总结\n        summary = trainer.generate_week4_summary()\n        print(summary)\n        \n        # 保存总结到文件\n        with open(\"01_rag_basics_summary.md\", \"w\", encoding=\"utf-8\") as f:\n            f.write(summary)\n        \n        print(\"\\n✅ Week 4 RAG基础学习完成！\")\n        print(\"📋 学习总结已保存至 01_rag_basics_summary.md\")\n        print(\"\\n🚀 推荐下一步:\")\n        print(\"   1. 测试不同的向量数据库配置\")\n        print(\"   2. 优化文本分割参数\")\n        print(\"   3. 尝试结合中国大模型的RAG系统\")\n        print(\"   4. 准备进入Week 5高级RAG技术学习\")\n        \n    except KeyboardInterrupt:\n        print(\"\\n\\n⚠️ Week 4 RAG基础学习被中断\")\n    except Exception as e:\n        print(f\"\\n\\n❌ 学习过程中发生错误: {str(e)}\")\n        import traceback\n        traceback.print_exc()\n\nif __name__ == \"__main__\":\n    main()","content_path":"/home/ubuntu/learn_langchain1.0_projects/courses/L2_Intermediate/01_rag_systems/01_vector_stores_basics.py"}