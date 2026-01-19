#!/usr/bin/env python3
"""
LangChain L1 Foundation - Week 3
课程标题: Agents基础概念与Tool集成
学习目标:
  - 理解LangChain中Agent的核心概念
  - 学会创建和使用基础Tool
  - 掌握ReAct (Reasoning + Acting)思维框架
  - 实践Agent与LLM的交互模式
  - 构建简单的推理+行动智能体
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
先决条件: 完成Week 2模型交互与提示工程学习

🎯 实践重点:
  - Agent概念理解 (推理+行动)
  - Tool集成与调用
  - ReAct模式实现
  - Memory原理入门
"""

import sys
import os
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

# 环境配置
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 环境变量已加载")
except ImportError:
    print("⚠️ python-dotenv未安装，请确保手动设置环境变量")

# LangChain Agent相关导入
try:
    from langchain_core.agents import AgentAction, AgentFinish
    from langchain_core.tools import Tool, BaseTool
    from langchain_core.callbacks import Callbacks
    from langchain_core.language_models import BaseLanguageModel
    from langchain import hub
    from langchain.agents import load_tools, initialize_agent, AgentType
    print("✅ LangChain Agent相关组件导入成功")
except ImportError as e:
    print(f"❌ LangChain Agent组件导入失败: {e}")
    print("请确保已安装必要的依赖：")
    print("   pip install langchain-core langchain")
    sys.exit(1)

@dataclass
class ToolResult:
    """工具执行结果"""
    name: str
    args: Dict[str, Any]
    result: Any
    execution_time: float
    success: bool
    error: Optional[str] = None

@dataclass
class AgentActionRecord:
    """Agent行为记录"""
    step: int
    thought: str
    action: str
    action_input: Any
    observation: Any
    timestamp: datetime

class AgentBasicsTrainer:
    """L1 Agents基础训练器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.tools_created = []
        self.agent_history = []
        self.reimplentations = []
        self.learnings = []
    
    def _log(self, message: str):
        """日志输出"""
        if self.verbose:
            print(f"🤖 {message}")
    
    def demo_agent_concepts_overview(self):
        """演示Agent核心概念"""
        self._log("Agent核心概念理解")
        print("-" * 60)
        
        print("🤖 什么是LangChain中的Agent？")
        print("   • Agent = LLM + Tools + Instructions + Memory")
        print("   • 能够根据用户输入->推理->选择工具->执行->观察结果")
        print("   • ReAct模式: Reasoning (推理) + Acting (行动)")
        print("   • 不是简单的问答，而是动态工具使用")
        print()
        
        print("🔄 Agent的工作循环:")
        agent_loop = [
            ("👥 用户输入", "用户提交问题或任务"),
            ("🤔 推理分析", "LLM分析情况并决定下一步行动"), 
            ("🛠️ 选择工具", "根据分析选择合适的工具"),
            ("⚡ 执行工具", "调用工具并获取结果"),
            ("👀 观察结果", "分析工具返回的结果"),
            ("🔁 继续推理", "基于新信息做出下一步决策"),
            ("✅ 最终答案", "行动达成终点或无法继续时返回答案")
        ]
        
        for i, (step, desc) in enumerate(agent_loop, 1):
            print(f"   {i}. {step}: {desc}")
        
        print(f"\n📚 关键概念对比:")
        concepts = [
            ("Chain (链)", "固定的处理管道", [
                "输入 → Prompt → LLM → Parser → 输出",
                "处理步骤是预定义的",
                ""举例：文本总结""
            ]),
            ("Agent (代理)", "动态决策+工具使用", [
                "输入 → Reasoning → Tools → Observe → ... → 输出",
                "处理步骤是动态决定的",
                ""举例：智能助手""
            ]),
            ("Tool (工具)", "LLM可以调用的功能", [
                "搜索引擎、计算器、数据库访问",
                "Any Python function LLM can call",
                ""让LLM具备"双手"""
            ]),
            ("Memory (记忆)", "跨会话的信息保存", [
                "短时间：对话内容",
                "长时间：用户偏好、历史记录",
                ""赋予持续认知能力""
            ])
        ]
        
        for concept, desc, features in concepts:
            print(f"\n   🎯 {concept}: {desc}")
            for feature in features:
                if feature:
                    print(f"      └─ {feature}")
        
        print(f"\n🛠️ Agent的主要组成部分:")
        agent_components = {
            "LLM": "大脑 - 推理与决策",
            "Tools": "四肢 - 行动与外界交互", 
            "Prompt": "指令 - 行为规范与格式",
            "Memory": "记忆 - 上下文与历史信息",
            "Parser": "理解器 - 解读用户输入和输出格式化"
        }
        
        for component, function in agent_components.items():
            print(f"   • {component}: {function}")
        
        self.exercises_completed.append("agent_concepts_overview")
        self.learnings.append("理解了LangChain Agent的核心设计哲学")
    
    def demo_tool_creation_basics(self):
        """演示工具(Tool)的创建基础"""
        self._log("Tool创建与使用基础")
        print("-" * 60)
        
        print("🔧 LangChain中Tool的定义:")
        print("   • 可调用Python函数")
        print("   • 包含描述信息 (告诉LLM这是什么工具)")
        print("   • 有清晰的输入输出格式")
        print("   • 可以同步或异步执行")
        print()
        
        print("🎨 Tool的基本结构:")
        print("""
tool_def = {
    "name": "工具名称",           # LLM理解工具的标识
    "description": "工具功能描述",  # LLM选择工具的依据  
    "func": callable_function,     # 实际执行的功能函数
    "return_direct": bool,        # 是否直接返回结果
    "coroutine": async_func       # 异步版本(可选)  
}
        """)
        print()
        
        # 创建基础工具示例
        print("🎯 实用工具创建示例:")
        
        class SimpleCalculator:
            """简单计算器工具类"""
            
            @staticmethod
            def add(a: float, b: float) -> float:
                """加法运算"""
                return a + b
            
            @staticmethod
            def multiply(a: float, b: float) -> float:
                """乘法运算"""
                return a * b
            
            @staticmethod
            def power(base: float, exponent: float) -> float:
                """幕运算"""
                return base ** exponent
        
        # 创建LangChain Tool对象
        calc_tool = Tool(
            name="calculator",
            func=lambda query: self._handle_calculator_query(query),
            description="A simple calculator that can add, multiply, and calculate powers. Input format: 'add 2 and 3' or 'multiply 5 by 7' or 'power 2 to 3'"
        )
        
        def _handle_calculator_query(query: str) -> str:
            """处理计算器查询的主逻辑函数"""
            query_lower = query.lower().strip()
            calc = SimpleCalculator()
            
            try:
                # 简单的自然语言解析 (演示用)
                if "add" in query_lower:
                    parts = query.replace("add", "").split("and")
                    if len(parts) >= 2:
                        a = float(parts[0].strip())
                        b = float(parts[1].strip())
                        result = calc.add(a, b)
                        return f"计算结果: {a} + {b} = {result}"
                
                elif "multiply" in query_lower and "by" in query_lower:
                    parts = query.replace("multiply", "").split("by")
                    if len(parts) >= 2:
                        a = float(parts[0].strip().replace("and").strip())
                        b = float(parts[1].strip())
                        result = calc.multiply(a, b)
                        return f"计算结果: {a} × {b} = {result}"
                
                elif "power" in query_lower and "to" in query_lower:
                    parts = query.replace("power", "").split("to")
                    if len(parts) >= 2:
                        base = float(parts[0].strip())
                        exponent = float(parts[1].strip())
                        result = calc.power(base, exponent)
                        return f"计算结果: {base} 的 {exponent} 次方 = {result}"
                
                return f"无法解析计算请求: '{query}'。请尝试格式如: 'add 2 and 3' 或 'multiply 5 by 7'"
                
            except Exception as e:
                return f"计算错误: {str(e)}"
        
        # 测试工具功能
        print(f"\n🧪 测试计算器工具:")
        test_queries = [
            "add 5 and 3",
            "multiply 4 by 7", 
            "power 2 to 8",
            "what is multiply 10 by 5"
        ]
        
        for query in test_queries:
            print(f"\n   查询: '{query}'")
            result = _handle_calculator_query(query)
            print(f"   结果: {result}")
        
        self.tools_created.append("calculator")
        
        # 网页信息工具
        simple_web_tool = Tool(
            name="web_search_simple",
            func=lambda query: self._mock_web_search(query), 
            description="Simple web search tool that provides basic information. Input: search query"
        )
        
        print(f"\n🌐 演示Web搜索工具:")
        web_results = simple_web_tool.run("LangChain China models support")
        print(f"   搜索 `LangChain China models` 结果片段:")
        print(f"{web_results[:150]}...")
        
        self.tools_created.append("web_search_simple")
        
        print(f"\n📊 工具创建统计:")
        print(f"   └─ 成功创建工具数量: {len(self.tools_created)}")
        for tool_name in self.tools_created:
            print(f"     • {tool_name}")
    
    def _mock_web_search(self, query: str) -> str:
        """模拟网页搜索功能"""
        mock_results = {
            "langchain china models": [
                "LangChain宣布支持中国主要AI模型：DeepSeek、智谱GLM、通义千问等",
                "目前支持的模型包括：deepseek-chat、glm-4、qwen-72b-chat等主流版本",
                "开发者可以通过统一的LangChain API访问这些中国AI模型提供商的服务"
            ],
            "machine learning python": [
                "Python是机器学习的首选编程语言，有丰富的库和框架支持",  
                "常用的Python机器学习库包括scikit-learn、TensorFlow、PyTorch等",
                "Python简洁的语法和强大的科学计算能力使其成为ML开发者的首选"
            ],
            "deep learning basics": [
                "Deep learning使用多层神经网络来学习数据的复杂模式",
                "常见的深度学习架构包括CNN、RNN、Transformer等",
                "深度学习在图像识别、自然语言处理等领域取得了突破性进展"
            ]
        }
        
        # 简单的keyword匹配
        query_lower = query.lower()
        for known_query, results in mock_results.items():
            if known_query in query_lower:
                return random.choice(results)
        
        return f"搜索 '{query}' 找到相关信息。当前支持的主题包括机器学习、深度学习、AI发展等。使用这些工具可以获取相关的实用信息。"
    
    def demo_react_pattern_basics(self):
        """演示ReAct模式基础实现"""
        self._log("ReAct (Reasoning + Acting) 模式实现")
        print("-" * 60)
        
        print("🧠 ReAct模式核心思想:")
        print("   • Reasoning (推理): 分析问题并决定下一步行动")
        print("   • Acting (行动): 执行选定的行动/工具调用")  
        print("   • Observation (观察): 查看行动的结果")
        print("   • 循环上述过程直到达成目标或无法继续前进")
        print()
        
        # 简化的ReAct实现
        class SimpleReActAgent:
            """简化版ReAct Agent实现"""
            
            def __init__(self, name: str = "ReAct Agent"):
                self.name = name
                self.tools = {
                    "calculator": Tool(
                        name="calculator",
                        func=lambda query: self._simple_calculator(query),
                        description="计算器工具，可以执行基本数学运算"
                    ),
                    "web_search": Tool(
                        name="web_search", 
                        func=lambda query: self._simple_search(query),
                        description="简单搜索工具，提供基础知识信息"
                    ),
                    "datetime": Tool(
                        name="datetime",
                        func=lambda query: self._datetime_info(query),
                        description="提供当前日期时间信息"
                    )
                }
                self.history = []
            
            def _simple_calculator(self, query: str) -> str:
                """简化计算器"""
                try:
                    # 解析简单的数学表达式
                    if "+" in query:
                        parts = query.split("+")
                        result = float(parts[0]) + float(parts[1])
                        return f"计算: {query} = {result}"
                    elif "*" in query:
                        parts = query.split("*")
                        result = float(parts[0]) * float(parts[1])
                        return f"计算: {query} = {result}"
                    elif "**" in query or "^" in query:
                        base, exp = query.replace("**", "^").split("^")
                        result = float(base) ** float(exp)
                        return f"幕运算: {base}^{exp} = {result}"
                    
                except Exception:
                    pass
                
                return f"无法解析表达式: {query}"
            
            def _simple_search(self, query: str) -> str:
                """简化搜索 - 知识库模拟"""
                knowledge_base = {
                    "机器学习 定义": "机器学习让计算机无需显式编程就能从数据中学习规律",
                    "深度学习 原理": "深度学习使用多层神经网络模拟人脑的学习过程",
                    "CNN 概念": "卷积神经网络(CNN)是一种专门处理图像数据的深度学习架构",
                    "BERT 模型": "BERT是谷歌开发的预训练语言模型，在多项自然语言处理任务上取得突破"
                }
                
                query_lower = query.lower()
                for topic, info in knowledge_base.items():
                    if topic.lower() in query_lower:
                        return info
                
                return f"关于 '{query}' 的基础信息: 这是一个科技相关话题，主要涉及人工智能和机器学习技术。"
            
            def _datetime_info(self, query: str) -> str:
                """日期时间信息"""
                now = datetime.now()
                return f"当前时间: {now.strftime('%Y-%m-%d %H:%M:%S')}"
            
            def reason(self, user_input: str, context: str = "") -> Dict[str, Any]:
                """Reasoning步骤 - 分析问题并决定行动"""
                print(f"   🧠 推理步骤 - 分析问题")
                print(f"      └─ 用户输入: '{user_input}'")
                print(f"      └─ 当前上下文: '{context}'")
                
                # 简单的基于关键字的推理决策
                text_lower = user_input.lower()
                
                if any(op in text_lower for op in ["+", "*", "^", "计算", "math"]):
                    return {
                        "should_act": True,
                        "tool": "calculator",
                        "tool_input": user_input,
                        "reasoning": f"检测到数学表达式 '{user_input}'，应使用计算器工具"
                    }
                elif any(word in text_lower for word in ["是什么", "定义", "什么", "解释", "search", "什么"]):
                    knowledge_words = ["机器学习", "深度学习", "CNN", "BERT", "AI", "technology"]
                    if any(kw in text_lower for kw in knowledge_words):
                        return {
                            "should_act": True,
                            "tool": "web_search", 
                            "tool_input": user_input,
                            "reasoning": f"用户询问 '{user_input}' 包含知识性提问，需要搜索工具"
                        }
                elif any(word in text_lower for word in ["时间", "日期", "date", "time", "现在"]):
                    return {
                        "should_act": True,
                        "tool": "datetime",
                        "tool_input": user_input,
                        "reasoning": f"用户询问时间相关信息，使用datetime工具"
                    }
                
                return {
                    "should_act": False,
                    "tool": None,
                    "tool_input": None,
                    "reasoning": f"没有检测到特殊工具需求，可以直接回答: '{user_input}'"
                }
            
            def act(self, action_decision: Dict[str, Any]) -> str:
                """Acting步骤 - 执行选定的行动"""
                if not action_decision.get("should_act"):
                    return f"直接回答: I can help with '{action_decision['reasoning']}'"
                
                tool_name = action_decision["tool"]
                tool_input = action_decision["tool_input"]
                
                print(f"   ⚡ 行动步骤 - 执行工具")
                print(f"      └─ 选择工具: {tool_name}")
                print(f"      └─ 输入内容: '{tool_input}'")
                
                if tool_name in self.tools:
                    start_time = datetime.now()
                    
                    try:
                        result = self.tools[tool_name].invoke(tool_input)
                        execution_time = (datetime.now() - start_time).total_seconds()
                        
                        print(f"      └─ 执行完成 (耗时: {execution_time:.3f}秒)")
                        print(f"      └─ 返回结果: {result[:100]}...")
                        
                        return result
                        
                    except Exception as e:
                        return f"工具执行错误: {str(e)}"
                else:
                    return f"未知工具: {tool_name}"
            
            def observe(self, action_result: str, context: str = "") -> Dict[str, Any]:
                """Observation步骤 - 分析行动结果"""
                print(f"   👀 观察步骤 - 分析执行结果")
                print(f"      └─ 行动结果: '{action_result[:80]}...'")
                
                # 决定是否继续执行
                if len(action_result) < 50 and "错误" in action_result:
                    return {
                        "should_continue": True,
                        "next_action": "try_again",
                        "analysis": "执行似乎失败，可能需要重试"
                    }
                elif len(action_result) > 100:
                    return {
                        "should_continue": False,
                        "next_action": "complete",
                        "analysis": "获得足够信息，可以直接回答"
                    }
                else:
                    return {
                        "should_continue": False, 
                        "next_action": "complete",
                        "analysis": "任务已完成，可以直接回答"
                    }
            
            def process(self, user_input: str, max_iterations: int = 3) -> Dict[str, Any]:
                """完整的ReAct处理流程"""
                print(f"\n🚀 开始ReAct Agent处理: '{user_input}'")
                iteration = 0
                context = ""
                final_answer = ""
                
                while iteration < max_iterations:
                    iteration += 1
                    print(f"\n   🔁 第 {iteration} 次迭代:")
                    
                    # REASONING
                    reasoning_result = self.reason(user_input, context)
                    
                    if not reasoning_result["should_act"]:
                        final_answer = reasoning_result["reasoning"]
                        break
                    
                    # ACTING
                    try:
                        action_result = self.act(reasoning_result)
                        
                        # OBSERVATION
                        observation = self.observe(action_result, context)
                        
                        if not observation["should_continue"]:
                            final_answer = action_result
                            break
                        
                        # 更新上下文
                        context += f" 工具{reasoning_result['tool']}返回: {action_result[:50]}..."
                        
                    except Exception as e:
                        final_answer = f"在第{iteration}步执行时出现错误: {str(e)}"
                        break
                
                return {
                    "final_answer": final_answer,
                    "iterations": iteration,
                    "success": bool(final_answer)
                }
        
        # 测试简化的ReAct Agent
        print(f"\n🧪 测试ReAct Agent:")
        agent = SimpleReActAgent("迷你ReAct演示")
        
        # 测试不同的用户输入
        test_inputs = [
            "计算 5 + 3 等于多少？",
            "机器学习是什么？请解释一下", 
            "现在几点了？",
            "你好，能帮我总结一下今天的学习内容吗？"
        ]
        
        for user_input in test_inputs:
            result = agent.process(user_input, max_iterations=5)
            print(f"\n🎯 用户输入: '{user_input}'")
            print(f"   └─ Agent最终回答: {result['final_answer']}")
            print(f"   └─ 迭代次数: {result['iterations']}")
            print(f"   └─ 成功状态: {'✅' if result['success'] else '❌'}")
            time.sleep(0.5)  # 观察间隔
        
        self.exercises_completed.append("react_pattern_basics")
        self.learnings.append("掌握了ReAct模式的实现原理和基础应用")
    
    def demo_agent_memory_concept(self):
        """演示Agent记忆的基本概念"""
        self._log("Agent记忆(Memory)基本理解")
        print("-" * 60)
        
        print("💾 为什么Agent需要Memory？")
        print("   • 维持多轮对话的上下文")
        print("   • 记住用户的偏好和历史信息")  
        print("   • 在长时间任务中保持状态")
        print("   • 支持复杂的协作式交互")
        print()
        
        print("🧠 Agent Memory的主要类型:")
        memory_types = {
            "短期记忆 (Short-term)": [
                "当前对话轮次的信息",
                "Temporary context within single query","用户当前输入的解析结果",
                "当前正在执行的工具和数据",
                """"举例: Chat Buffer Memory """
            ],
            "长期记忆 (Long-term)": [
                "跨会话的用户偏好",
                "历史对话中挖掘的用户画像",
                "成功的和失败的经验教训", 
                "个人化定制的参数设置",
                """"举例: Conversation Summary Memory """
            ],
            "语义记忆 (Semantic)": [
                "处理相似任务的最佳实践",
                "领域专业知识",
                "工具使用的经验",
                "解决问题的策略套路",
                """"举例: Entity Memory """
            ],
            "情境记忆 (Episodic)": [
                "具体的历史对话" "过去的用户请求和满足方式",
                "时间序列的事件记录",
                "个性化的交互历史",
                """"举例: Conversation KG Memory """
            ]
        }
        
        for memory_type, examples in memory_types.items():
            print(f"\n   📍 {memory_type}:")
            for example in examples:
                if example:  # 只打印非空示例
                    print(f"      └─ {example}")
        
        print(f"\n🔍 Memory在ReAct循环中的作用:")
        memory_in_react = [
            ("用户输入", "从记忆快速获取用户画像"),
            ("Reasoning", "参考类似问题的历史解决思路"), 
            ("Acting", "选择用户熟悉的工具和行为模式"),
            ("Observation", "记住当前行动的反馈信息"),
            ("分析结果", "更新对用户的理解和偏好")
        ]
        
        print(f"\n   🔄 ReAct循环中的记忆应用:")
        for step, memory_usage in memory_in_react:
            print(f"      {step}: {memory_usage}")
        
        # 演示简单的记忆应用
        class SimpleMemoryAgent:
            """带简单记忆的Agent"""
            
            def __init__(self):
                self.conversation_memory = []  # 对话记忆
                self.user_facts = {}  # 用户事实
                self.preferences = {}  # 偏好
                self.success_history = []  # 成功经验
                max_history_size = 10  # 记忆限制
            
            def remember_user_preference(self, topic: str, preference: str):
                """记住用户偏好"""
                self.preferences[topic] = {
                    "preference": preference,
                    "recorded_at": datetime.now(),
                    "confidence": 0.8
                }
            
            def recall_preference(self, topic: str) -> Optional[str]:
                """回忆用户偏好"""
                if topic in self.preferences:
                    pref = self.preferences[topic]
                    return f"{topic}偏好: {pref['preference']} (记录时间: {pref['recorded_at'].strftime('%m-%d %H:%M')})"
                return None
            
            def remember_conversation(self, speaker: str, content: str):
                """记住对话内容"""
                self.conversation_memory.append({
                    "speaker": speaker,
                    "content": content,
                    "timestamp": datetime.now()
                })
                
                # 简单限制记忆大小
                if len(self.conversation_memory) > 10:
                    self.conversation_memory = self.conversation_memory[-8:]  # 保留最近8条
            
            def get_recent_context(self, n: int = 3) -> str:
                """获取最近的上下文"""
                recent = self.conversation_memory[-n:]
                context_parts = []
                
                for item in recent:
                    context_parts.append(f"{item['speaker']}: {item['content']}")
                
                return ". ".join(context_parts)
            
            def extract_user_mention(self, text: str):
                """从文本中提取用户信息"""
                    # 简单的关键词提取
                    keywords = ["我喜欢", "我爱好", "我认为", "我的观点", "对我来说"]
                    for keyword in keywords:
                        if keyword in text:
                            # 简单的偏好提取
                            fact_start = text.find(keyword) + len(keyword)
                            fact = text[fact_start:].strip()
                            
                            if fact and len(fact) > 2 and len(fact) < 50:
                                self.user_facts[len(self.user_facts)] = {
                                    "text": fact,
                                    " extracted_from": text,
                                    "timestamp": datetime.now()
                                }
        
        # 测试记忆Agent
        print(f"\n🧪 测试记忆Agent:")
        mem_agent = SimpleMemoryAgent()
        
        # 模拟对话
        conversations = [
            ("user", "你好，我叫小林，我喜欢用简单的方式解释复杂概念"),
            ("assistant", "很高兴认识你！小林。简单化的解释方式确实是学习复杂概念的好方法"),
            ("user", "我认为深度学习的去向很多潜力，特别是在中文自然语言处理方面"),
            ("assistant", "说得很好！中文NLP确实是AI发展的重要方向，很多技术需要本土化适配"),
            ("user", "我喜欢学习时结合理論和实践，这样能更好地理解概念"),
            ("assistant", "理论结合实践确实是最佳的学习方式！你现在正在用的就是实践") 
        ]
        
        for speaker, content in conversations:
            mem_agent.remember_conversation(speaker, content)
            mem_agent.extract_user_mention(content)
        
        print(f"\n📋 记忆提取演示:")
        
        # 测试记忆提取
        preferences = ["学习方式", "AI领域", "解释风格"]
        for pref in preferences:
            recalled = mem_agent.recall_preference(pref)
            if recalled:
                print(f"   ✓ {recalled}")
            else:
                print(f"   ✗ 未找到{pref}相关偏好")
        
        print(f"\n📝 最近的对话上下文:")
        recent_context = mem_agent.get_recent_context(3)
        print(f"   └─ {recent_context}")
        
        # 展示提取的用户事实
        if mem_agent.user_facts:
            print(f"\n🏷️ 提取的用户事实标签:")
            for key, fact in mem_agent.user_facts.items():
                print(f"   └─ {fact['text']} (来源: {fact['extracted_from'][:20]}...)")
        
        self.exercises_completed.append("agent_memory_concept")
        self.learnings.append("掌握了Agent Memory的基本类型和在ReAct循环中的应用")
    
    def generate_week3_summary(self) -> str:
        """生成Week 3学习总结"""
        summary = f"""
🎓 L1 Foundation - Week 3: Agents基础与Tool集成学习总结
=======================================================

✅ 本周完成学习内容:
   1. Agent核心概念理解与定位认知
   2. LangChain Tool的创建和使用方法
   3. ReAct (Reasoning+Acting) 模式的完整实现
   4. Agent Memory的基本类型和应用策略
   5. 多个实用工具的整合演示

💡 核心技能掌握:
   • Chain vs Agent的区别与应用场景
   • Tool的结构设计和自然语言解析
   • ReAct循环的完整实现和扩展
   • 短期/长期/语义/情境记忆的理解
   • 多工具Agent的架构设计思想

🛠️ 实际工具创建:
   • ✅ 简单计算器工具 (3运算)
   • ✅ 基础搜索工具 (知识库模拟)  
   • ✅ 日期时间工具 (当前info)
   • ✅ 完整ReAct处理流程 (推理+行动)
   • ✅ 基础记忆Agent (偏好+上下文)

🧠 思维模型建立:
   • Agent = LLM + Tools + Prompt + Memory
   • ReAct: Reason→Act→Observe→循环
   • Memory层级: 短期↔长期↔语义↔情境
   • Tool设计: 描述+函数+格式+解析

⏭️ Week 4学习预告:
   📚 复杂多工具Agent构建
   🛠 中国AI模型Agent集成
   🚀 Agent生产级错误处理
   🎯 Tool调用的优化策略

---
### 🚀 Week 3实战应用建议:
   1. 扩展更多实用工具 (翻译器、约束求解器等)
   2. 实现和中国大模型提供商的Agent集成
   3. 为Agent添加持久化记忆存储
   4. 设计Agent协作式交互，如将多个Agent分工处理不同任务
"""
        return summary

def main():
    """主函数：执行Week 3所有Agent基础训练"""
    print("🎯 LangChain L1 Foundation - Week 3: Agents基础与Tool集成")
    print("=" * 70)
    print("本周将学习LangChain Agent的核心概念和基础实现")
    
    trainer = AgentBasicsTrainer()
    
    try:
        # 顺序执行各个练习模块
        trainer.demo_agent_concepts_overview()
        trainer.demo_tool_creation_basics()
        trainer.demo_react_pattern_basics()
        trainer.demo_agent_memory_concept()
        
        # 生成学习总结
        summary = trainer.generate_week3_summary()
        print(summary)
        
        # 保存总结到文件
        with open("01_basic_agent_concepts_summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        
        print("\n✅ Week 3 Agent基础学习完成！")
        print("📋 详细总结已保存至 01_basic_agent_concepts_summary.md")
        print("\n🚀 推荐下一步:")
        print("   1. 在自己的项目中尝试创建新的工具函数")
        print("   2. 扩展ReAct Agent的功能和工具支持")
        print("   3. 探索更多高级的Agent架构和设计模式")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Week 3 Agent基础学习被中断")
    except Exception as e:
        print(f"\n\n❌ 学习过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()