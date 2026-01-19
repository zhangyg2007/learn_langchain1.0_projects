#!/usr/bin/env python3
"""
LangChain L1 Foundation - Week 3
课程标题: 多工具智能体集成与中国AI模型支持
学习目标:
  - 学会集成多个专业工具构建复杂Agent
  - 掌握中国主要AI模型(OpenAI, 赵蘋, Kimi, DeepSeek)在Agent中的集成
  - 理解工具路由(Tool Routing)和智能选择策略
  - 实践生产级的错误处理和容错策略
  - 构建可扩展的Agent架构框架
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
先决条件: 完成Week 3 Agents基础概念学习

🎯 实践重点:
  - 多LLM-Agent选择
  - 专业工具function design
  - 中国模型Adapter模式
  - 生产级容错策略
"""

import sys
import os
import time
import json
import random
from typing import Dict, List, Optional, Union, Any, Callable
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from abc import ABC, abstractmethod

# 环境配置
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 环境变量已加载")
except ImportError:
    print("⚠️ python-dotenv未安装，请确保手动设置环境变量")

# LangChain核心依赖
try:
    from langchain_core.tools import Tool, StructuredTool, BaseTool
    from langchain_core.language_models import BaseLanguageModel
    from langchain_core.callbacks import Callbacks
    from langchain_core.runnables import RunnableConfig
    from langchain_core.messages import HumanMessage, SystemMessage, AIMessage
    from langchain_core.prompts import ChatPromptTemplate 
    print("✅ LangChain工具与消息组件导入成功")
except ImportError as e:
    print(f"❌ LangChain组件导入失败: {e}")
    print("   └─ pip install langchain-core langchain")
    sys.exit(1)

# 中国大模型支持的额外依赖
try:
    from langchain_openai import ChatOpenAI
    print("✅ OpenAI模型支持导入成功")
except ImportError:
    # 如果OpenAI模型不可用，仍然可以继续其他内容
    ChatOpenAI = None
    print("⚠️ OpenAI模型无法导入，将仅展示概念性代码")

try:
    import requests
    print("✅ HTTP请求模块导入成功")
except ImportError:
    print("❌ requests模块缺失，将限制部分网络工具功能")
    requests = None

@dataclass
class ToolExecutionRecord:
    """工具执行记录"""
    tool_name: str
    input_args: Dict[str, Any]
    output_result: Any
    execution_time: float
    success: bool
    error_msg: Optional[str] = None
    timestamp: datetime = None

@dataclass
class ChinaModelConfig:
    """中国大模型配置"""
    provider: str
    api_key: str
    base_url: Optional[str] = None
    model_name: str = ""
    max_tokens: int = 1024
    temperature: float = 0.7
    timeout: int = 60

class MultiToolAgentTrainer:
    """多工具智能体进阶训练器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.tools = {}  # 字典存储工具
        self.libraries = {}  # 外部库封装
        self.models = {}  # 不同模型实例
        self.performance_stats = []
        
        # 初始化演示数据
        self.sample_documents = self._init_document_samples()
        self.knowledge_base = self._init_knowledge_base()
        
    def _log(self, message: str):
        """日志输出"""
        if self.verbose:
            print(f"🤖 {message}")
    
    def _init_document_samples(self) -> Dict[str, str]:
        """初始化示例文档数据"""
        return {
            "machine_learning_basics": """
            机器学习(Machine Learning)是人工智能的一个核心分支，它让计算机系统能够从数据中学习并改进
            其表现，而无需进行显式的编程。机器学习算法通过分析数据、识别模式，然后使用这些模式来做出
            预测或决策。
            
            机器学习主要分为三种类型：
            1. 监督学习(Supervised Learning): 使用标记数据训练模型
            2. 无监督学习(Unsupervised Learning): 从未标记数据中发现模式
            3. 强化学习(Reinforcement Learning): 通过试错学习最优策略
            """,
            
            "deep_learning_overview": """
            深度学习(Deep Learning)是机器学习的一个子领域，它基于人工神经网络的思想，特别是那些具有
            多个层的深度神经网络。深度学习模型能够通过学习数据的多层抽象表示来自动发现特征层次结构，
            使其特别适合处理非结构化数据，如图像、音频和文本。
            
            关键的深度学习架构包括：
            - 卷积神经网络(CNN): 主要用于图像识别和计算机视觉
            - 循环神经网络(RNN) and LSTM: 处理序列数据
            - Transformer架构: 革命性的自然语言处理基础
            - 生成对抗网络(GAN): 用于生成逼真数据
            """,
            
            "artificial_intelligence_summary": """
            人工智能(Artificial Intelligence, AI)是计算机科学的一个广泛分支，致力于创建能够执行通常需要
            人类智能的任务的系统。AI系统包括规划、学习、推理、问题解决、知识表示、感知和自然语言处理等
            能力。
            
            AI的发展经历了多个阶段：
            - 专家系统时代：基于规则的推理系统
            - 机器学习时代：数据驱动的模式识别
            - 深度学习时代：神经网络的深度架构
            - 大语言模型时代：通用的语言理解和生成能力
            """
        }
    
    def _init_knowledge_base(self) -> Dict[str, Any]:
        """初始化知识库数据"""
        return {
            "ai_concepts": {
                "machine_learning": {
                    "definition": "让计算机从数据中学习规律的方法",
                    "types": ["supervised", "unsupervised", "reinforcement"],
                    "applications": ["predictions", "classifications", "clustering"]
                },
                "deep_learning": {
                    "definition": "基于多层神经网络的机器学习方法",
                    "key_architectures": ["CNN", "RNN", "Transformer", "GAN"],
                    "breakthroughs": ["computer_vision", "nlp", "speech_recognition"]
                },
                "artificial_intelligence": {
                    "definition": "让机器具备人类智能能力的计算机科学分支",
                    "evolution": ["expert_systems", "machine_learning", "deep_learning", "llm_era"],
                    "capabilities": ["planning", "learning", "reasoning", "perception", "nlp"]
                }
            },
            
            "chinese_models": {
                "deepseek": {
                    "strengths": ["长文本处理", "数学推理", "代码生成"],
                    "model_versions": ["deepseek-chat", "deepseek-coder"],
                    "use_cases" : ["长文档总结", "数据分析", "软件开发辅助"]
                },
                "zhipu": {
                    "strengths": ["中文理解", "专业知识", "推理能力"],  
                    "model_versions": ["glm-3-turbo", "glm-4"],
                    "use_cases": ["教育辅导", "专业咨询", "内容创作"]
                },
                "qwen": {
                    "strengths": ["全能性能", "中文优化", "多领域"],
                    "model_versions": ["qwen-7b", "qwen-72b", "qwen-turbo"],
                    "use_cases": ["通用问答", "多语言任务", "企业应用"]
                }
            },
            
            "model_comparisons": {
                "gpt_vs_claude": {
                    "gpt_strengths": ["speed", "cost", "availability"],
                    "claude_strengths": ["reasoning", "safety", "nuanced_responses"],
                    "recommendations": "根据具体需求和资源选择"
                }
            }
        }
    
    def demo_multi_tool_creation(self):
        """演示多工具的智能体创建"""
        self._log("多工具智能体的工具创建")
        print("-" * 70)
        
        print("🛠️ 专业工具设计思路:")
        print("   • 每个工具专注解决一类问题")
        print("   • 提供清晰的自然语言描述")
        print("   • 支持错误处理和边界情况")
        print("   • 可以异步执行以支持高并发")
        print("   • 集成监控和性能统计")
        print()
        
        print("📋 本课程创建的工具集合:")
        
        # 1. 智能摘要生成工具
        print("\n1️⃣ 智能摘要工具 (Smart Summarizer):")
        
        def smart_summarize(text: str, max_length: int = 100, style: str = "concise") -> str:
            """智能文本摘要生成器"""
            try:
                # 基本的文本处理逻辑
                if not text or len(text.strip()) < 10:
                    return "⌴#x2023;#x2023;输入文本过短，无法生成摘要"
                
                words = text.split()
                if len(words) <= max_length:
                    return f"⌴#x2023;#x2023;原文已符合长度要求: {text[:200]}..."
                
                # 基于样式生成不同摘要
                if style == "concise":
                    # 提取关键句 (简化版算法)
                    sentences = text.split("。")
                    key_sentences = sentences[:2] if len(sentences) > 2 else sentences
                    summary = "。".join(key_sentences) + "。"
                elif style == "detailed":
                    # 更详细的摘要
                    sentences = text.split("。")
                    key_sentences = sentences[:4] if len(sentences) > 4 else sentences  
                    summary = "。".join(key_sentences) + "。"
                else:
                    summary = text[:max_length * 5] + "..."  # 简单的截取
                
                # 质量检查
                if len(summary) < 20:
                    summary = text[:max_length * 2] + "..."
                
                return f"⌴#x2023;#x2023;{style.title()}摘要 ({len(summary.split())} 词):\n\n{summary}"
                
            except Exception as e:
                return f"\ x1f6ab;摘要生成失败: {str(e)}"
        
        summarize_tool = Tool(
            name="smart_summarizer",
            func=smart_summarize,
            description="智能文本摘要工具。输入: 长文本；输出: 结构化摘要。参数: text (str), max_length (int, default=100), style (str, default='concise')"
        )
        
        # 测试摘要工具
        test_doc = self.sample_documents["machine_learning_basics"]
        result = summarize_tool.run({"text": test_doc, "max_length": 50, "style": "concise"})
        print(f"   测试摘要生成:")
        print(f"      输入长度: {len(test_doc)} 字符")
        print(f"      输出前200字:\\")
        print(f"      {result[:200]}...")
        
        self.tools["smart_summarizer"] = summarize_tool
        
        # 2. 专业知识检索工具
        print("\n2️⃣ 专业知识检索工具 (Domain Knowledge Search):")
        
        def domain_knowledge_search(topic: str, domain: str = "ai_concepts", detail_level: str = "medium") -> str:
            """领域专业知识检索引擎"""
            try:
                # 验证输入参数
                if not topic or not topic.strip():
                    return "\ x1f6ab;需要提供检索主题"
                
                topic_clean = topic.strip().lower()
                
                # 检查domain是否存在
                if domain not in self.knowledge_base:
                    available_domains = list(self.knowledge_base.keys())
                    return f"\ x1f6ab;未知领域 '{domain}'。可用领域: {', '.join(available_domains)}"
                
                # 主题匹配 (简化版)
                domain_data = self.knowledge_base[domain]
                matched_topic = None
                
                # 遍历知识结构进行关键词匹配
                for topic_key, topic_data in domain_data.items():
                    # 基本的字符串匹配
                    if topic_clean in topic_key.lower() or topic_key.lower() in topic_clean:
                        matched_topic = topic_data
                        break
                
                # 如果直接匹配失败，尝试模糊匹配
                if not matched_topic:
                    import difflib
                    available_topics = list(domain_data.keys())
                    close_matches = difflib.get_close_matches(topic_clean, available_topics, n=1, cutoff=0.6)
                    
                    if close_matches:
                        matched_topic = domain_data[close_matches[0]]
                        print(f"   └─ 模糊匹配: '{topic_clean}' → '{close_matches[0]}'")
                
                if not matched_topic:
                    return f"\ x1f6ab;未找到关于'{topic}'的详细信息。请在{domain}领域中搜索以下主题: {', '.join(domain_data.keys())}"
                
                # 根据细节级别生成不同层次的回答
                if detail_level == "basic":
                    definition = matched_topic.get("definition", "暂无定义")
                    result = f"🧠 **{topic.title()}** 基础信息:\\n\\n\\ ``{definition}\\ ``"
                
                elif detail_level == "medium":
                    definition = matched_topic.get("definition", "暂无定义")
                    key_points = matched_topic.get("key_points", [])
                    if key_points:
                        key_points_text = "\\n".join([f"• {point}" for point in key_points[:3]])
                        result = f"🧠 **{topic.title()}** 详细信息:\\n\\n**定义**: {definition}\\n\\n**核心要点**:\\n{key_points_text}"
                    else:
                        result = f"🧠 **{topic.title()}** 详细信息:\\n\\n**定义**: {definition}"
                
                elif detail_level == "comprehensive":
                    result_parts = [f"\U0001f9e0 **{topic.title()}** 全面信息:"]
                    
                    # definition
                    definition = matched_topic.get("definition", "暂无定义")
                    result_parts.append(f"**定义**: {definition}")
                    
                    # strengths/examples
                    if "strengths" in matched_topic:
                        strengths = matched_topic["strengths"]
                        result_parts.append(f"\\n**优势**:\\n" + "\\n".join([f"• {s}" for s in strengths]))
                    
                    if "examples" in matched_topic:
                        examples = matched_topic["examples"]
                        result_parts.append(f"\\n**应用示例**:\\n" + "\\n".join([f"• {e}" for e in examples]))
                    
                    result = "\\n\\n".join(result_parts)
                
                else:
                    result = f"🧠 **{topic.title()}** 信息:\\n\\n{matched_topic.get('definition', '详细信息加载中...')}"
                
                return result
                
            except Exception as e:
                return f"\ x1f6ab;知识检索失败: {str(e)}"
        
        knowledge_tool = Tool(
            name="domain_knowledge_search",
            func=domain_knowledge_search,
            description="领域专业知识检索引擎。输入: topic (str), [domain: str], [detail_level: str] → 返回: 结构化知识信息"
        )
        
        # 测试知识检索工具
        test_queries = [
            {"topic": "machine learning", "domain": "ai_concepts", "detail_level": "basic"},
            {"topic": "deep learning", "domain": "ai_concepts", "detail_level": "medium"},
            {"topic": "deepseek", "domain": "chinese_models", "detail_level": "comprehensive"}
        ]
        
        for query in test_queries:
            result = knowledge_tool.run(query)
            print(f"   \\ 检索 `{query['topic']}` ({query['detail_level']}) 结果:")
            print(f"      {result[:200]}...")
            print()
        
        self.tools["domain_knowledge_search"] = knowledge_tool
        
        # 3. 语言文本处理工具
        print("\n3️⃣ 语言文本处理工具 (Text Processing)")
        
        def text_analyzer(text: str, analysis_type: str = "all") -> str:
            """文本分析和处理工具"""
            try:
                if not text or not text.strip():
                    return "\ x1f6ab;分析文本不能为空"
                
                text_clean = text.strip()
                analysis_types = {
                    "basic": lambda: {
                        "length": len(text_clean),
                        "words": len(text_clean.split()),
                        "sentences": len([s for s in text_clean.split("。") if s.strip()]),
                        "char_types": len(set(text_clean))
                    },
                    
                    "advanced": lambda: {
                        **analysis_types["basic"](),
                        "avg_word_length": sum(len(word) for word in text_clean.split()) / len(text_clean.split()),
                        "punctuation_count": sum(1 for char in text_clean if not char.isalnum()),
                        "uppercase_ratio": sum(1 for char in text_clean if char.isupper()) / len(text_clean) if text_clean else 0
                    },
                    
                    "keywords": lambda: {
                        **analysis_types["basic"](),
                        "top_words": sorted(set(word for word in text_clean.lower().split() if len(word) > 2), key=lambda w: text_clean.count(w), reverse=True)[:5],
                        "unique_words": len(set(word.lower() for word in text_clean.split())),
                        "terms": [word for word in text_clean.lower().split() if len(word) > 3][:8]
                    }
                }
                
                # 执行分析
                if analysis_type not in analysis_types and analysis_type != "all":
                    return f"\ x1f6ab;未知分析类型 '{analysis_type}'。可用类型: {', '.join(analysis_types.keys())}"
                
                if analysis_type == "all":
                    # 执行所有分析类型 (对于all类型，优先给 keywords 分析结果)
                    result_data = analysis_types["keywords"]()
                    main_type = "关键词"
                else:
                    result_data = analysis_types[analysis_type]()
                    main_type = analysis_type.replace("_", " ").title()
                
                # 格式化输出结果
                output_lines = [f"🧠 `{main_type}` 分析结果"]
                
                for key, value in result_data.items():
                    if isinstance(value, float):
                        formatted_value = f"{value:.2f}"
                    elif isinstance(value, list):
                        if len(value) > 0 and isinstance(value[0], str):
                            formatted_value = ", ".join(f"'{v}'" for v in value[:5])
                        else:
                            formatted_value = str(value)
                    else:
                        formatted_value = str(value)
                    
                    # 美化键名显示
                    display_key = key.replace("_", " ").title()
                    output_lines.append(f"**{display_key}**: {formatted_value}")
                
                return "\\n".join(output_lines)
                
            except Exception as e:
                return f"\ x1f6ab;文本分析失败: {str(e)}"
        
        text_tool = Tool(
            name="text_analyzer",
            func=text_analyzer,
            description="语言文本分析和处理工具。输入: text (str), [analysis_type: str] → 返回: 结构化的文本分析报告"
        )
        
        # 测试文本分析工具
        demo_text = "人工智能正在深刻改变我们的生活。深度学习和机器学习技术快速发展"
        result = text_tool.run({"text": demo_text, "analysis_type": "basic"})
        print(f"   文本分析测试:")
        print(f"      输入: '{demo_text}'")
        print(f"      基础分析结果:\\")
        print(f"      {result}")
        
        self.tools["text_analyzer"] = text_tool
        
        print(f"\n📊 多工具创建统计:")
        print(f"   ✅ 专业工具总数: {len(self.tools)} 个")
        for tool_name in self.tools.keys():
            print(f"     • {tool_name}")
    
    def demo_china_models_agent(self):
        """演示中国AI模型在Agent中的集成"""
        self._log("中国AI模型在Agent中的集成")
        print("-" * 70)
        
        print("🇨🇳 中国AI大模型Agent支持:")
        print("   • DeepSeek: 长本文处理、数学推理专家")
        print("   • 智谱澄 GLM: 中文理解、专业知识强")
        print("   • 通义千问: 全能性能、中文优化")
        print("   • Kimi: 创意生成、对话流畅")
        print("   • Baidu ERNIE: 文学创作、商业文案")
        print()
        
        class ChinaModelAdapter:
            """\U0001f1e8\U0001f1f3 中国大模型统一适配器"""
            
            def __init__(self, config: ChinaModelConfig):
                self.config = config
                self.name = f"{config.provider}_{config.model_name.replace('-', '_')}"
                self._validate_config()
            
            def _validate_config(self):
                """验证配置有效性"""
                if not self.config.api_key:
                    raise ValueError(f"\U0001faf6; {self.config.provider} API key is required")
                
                if not self.config.model_name:
                    self.config.model_name = self._get_default_model()
            
            def _get_default_model(self) -> str:
                """获取各提供商的默认模型"""
                defaults = {
                    "deepseek": "deepseek-chat",
                    "zhipu": "glm-4", 
                    "moonshot": "moonshot-v1-8k",
                    "qwen": "qwen-turbo"
                }
                return defaults.get(self.config.provider.lower(), "unknown")
            
            def _create_model_instance(self) -> BaseLanguageModel:
                """创建模型实例"""
                provider = self.config.provider.lower()
                
                if provider == "deepseek":
                    return DeepSeekLangChainAdapter(
                        api_key=self.config.api_key,
                        base_url=self.config.base_url or "https://api.deepseek.com/v1",
                        model=self.config.model_name,
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens
                    )
                
                elif provider == "zhipu":
                    return ZhipuLangChainAdapter(
                        api_key=self.config.api_key,
                        model=self.config.model_name,
                        temperature=self.config.temperature,
                        max_tokens=self.config.max_tokens
                    )
                
                elif provider == "qwen": 
                    return QwenLangChainAdapter(
                        api_key=self.config.api_key,
                        model=self.config.model_name,
                        temperature=self.config.temperature
                    )
                
                else:
                    # 通用适配器
                    return GenericChinaModelAdapter(**self.config.__dict__)
            
            def to_tool(self) -> Tool:
                """转换为LangChain可用的Tool格式"""
                model_instance = self._create_model_instance()
                
                def _model_tool_function(prompt: str) -> str:
                    """模型调用函数"""
                    from langchain_core.messages import HumanMessage
                    
                    try:
                        messages = [HumanMessage(content=prompt)]
                        response = model_instance.invoke(messages)
                        return response.content
                        
                    except Exception as e:
                        return f"\U0001f534; 中国模型调用失败: {str(e)}"
                
                return Tool(
                    name=self.name,
                    func=_model_tool_function,
                    description=f"中国{self.config.provider.upper()}模型 {self.config.model_name} 调用工具. 擅长中文理解和专业知识解答。"
                )
        
        # 中国模型适配器的具体实现 (简化版)
        class DeepSeekLangChainAdapter:
            """DeepSeek LangChain适配器"""
            
            def __init__(self, api_key: str, base_url: str = None, model: str = "deepseek-chat", **kwargs):
                self.api_key = api_key
                self.base_url = base_url or "https://api.deepseek.com/v1"
                self.model = model
                self.kwargs = kwargs
            
            def invoke(self, messages):
                """模拟DeepSeek模型调用"""
                return self._mock_deepseek_response(messages)
            
            def _mock_deepseek_response(self, messages):
                """模拟DeepSeek响应"""
                import time
                time.sleep(0.1)  # 模拟延迟
                
                # 基于输入生成相关响应
                last_message = messages[-1].content if messages else "Hello"
                
                responses = {
                    "编程": "DeepSeek在编程任务上表现突出: \( \"role\": \\"assistant\\", \\"content\\": '我来帮你分析这个Python代码的实现...'",
                    "数学": "DeepSeek数学推理能力展示: \( \"role\": \\"assistant\\", \\"content\\": '这个问题的数学解法分为以下几步...'",
                    "文本": "DeepSeek长文本处理能力: \( \"role\": \\"assistant\\", \\"content\\": '这段话的主要意思是...'"
                }
                
                # 关键词匹配
                content_indicator = "general"
                for keyword in responses:
                    if keyword in last_message.lower():
                        content_indicator = keyword
                        break
                
                base_response = responses.get(content_indicator, f"DeepSeek回应: '{last_message[:50]}...' 是一个很有意思的问题。让我从专业角度为您解释...")
                
                # 返回Reu2023;风格的对象
                class MockResponse:
                    content = base_response
                    usage = {"prompt_tokens": len(last_message), "completion_tokens": len(base_response)}
                
                return MockResponse()
        
        class ZhipuLangChainAdapter:
            """\U0001f1e8\U0001f1f3 智谱GLM LangChain适配器"""
            
            def invoke(self, messages):
                """模拟智谱GLM响应"""
                return self._mock_zhipu_response(messages)
            
            def _mock_zhipu_response(self, messages):
                """模拟智谱响应"""
                import random
                
                last_message = messages[-1].content if messages else "Hello"
                
                responses = [
                    "\U0001f9ec; 智谱GLM: 这个问题体现了中西方思维方式的差异...",
                    "\U0001f9e9; 智谱GLM: 从哲学角度来看这个现象...", 
                    "\U0001f9e8; 智谱GLM: 让我用更加结构化的方式来解答..."
                ]
                
                if any(kw in last_message.lower() for kw in ["中文", "汉语", "chinese"]):
                    response = "智谱GLM: 中文作为世界上使用人数最多的语言之一，它在人工智能领域的发展承载着特殊的使命..."
                else:
                    response = random.choice(responses)
                
                class MockResponse:
                    content = response
                    usage = {"prompt_tokens": 80, "completion_tokens": 120}
                
                return MockResponse()
        
        class GenericChinaModelAdapter:
            """\U0001f1e8\U0001f1f3 中国大模型通用适配器"""
            
            def __init__(self, provider: str, api_key: str, **kwargs):
                self.provider = provider
                self.api_key = api_key
                self.kwargs = kwargs
            
            def invoke(self, messages):
                """通用模型调用"""
                last_message = messages[-1].content if messages else "Hello"
                
                provider_specific_responses = {
                    "moonshot": "Kimi: 我可以帮您处理这个长文档，让我来分析其中的关键信息...",
                    "baichuan": "百川: 基于我的数据分析能力，这个问题的解决方案是...",
                    "qwen": "通义千问: 有很全面的问题视角，让我从多个方面来回答..."
                }
                
                response = provider_specific_responses.get(
                    self.provider.lower(),
                    f"{self.provider.upper()}: 我来分析您的问题 '{last_message[:20]}...'"