#!/usr/bin/env python3
"""
LangChain L1 Foundation - Week 2
课程标题: 提示词工程(Prompt Engineering)进阶
学习目标:
  - 掌握高级Prompt设计技巧
  - 学习Few-shot学习在LangChain中的应用
  - 理解ExampleSelector的原理和使用
  - 学会创建动态提示词模板
  - 实践结构化输入输出设计
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
先决条件: 完成Week 2聊天模型基础学习

🎯 实践重点:
  - Few-shot提示词模板
  - DynamicExampleSelector
  - 提示词调优技巧
  - 多场景Prompt设计
"""

import sys
import os
import time
from typing import Dict, List, Optional, Union, Any
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import json
import random

# 环境配置
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 环境变量已加载")
except ImportError:
    print("⚠️ python-dotenv未安装，请确保手动设置环境变量")

# LangChain核心依赖
try:
    from langchain_core.prompts import (
        PromptTemplate, 
        FewShotPromptTemplate,
        ChatPromptTemplate,
        SystemMessagePromptTemplate,
        HumanMessagePromptTemplate
    )
    from langchain_core.example_selectors import LengthBasedExampleSelector
    from langchain_core.prompts.few_shot import FewShotChatMessagePromptTemplate
    print("✅ LangChain Prompt工程组件导入成功")
except ImportError as e:
    print(f"❌ LangChain组件导入失败: {e}")
    print("请确保已安装: pip install langchain-core")
    sys.exit(1)

@dataclass
class PromptTestResult:
    """提示词测试结果"""
    prompt_name: str
    test_input: str
    expected_output: str
    actual_output: str
    similarity_score: float
    execution_time: float
    success: bool

@dataclass
class FewShotExample:
    """Few-shot Learning示例"""
    input: str
    output: str
    category: str
    complexity: str = "medium"

class PromptEngineeringTrainer:
    """L1 Prompt工程进阶训练器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.exercises_completed = []
        self.learnings = []
        self.example_bank = self._initialize_example_bank()
    
    def _log(self, message: str):
        """日志输出"""
        if self.verbose:
            print(f"🎯 {message}")
    
    def _initialize_example_bank(self) -> List[FewShotExample]:
        """初始化示例库"""
        return [
            FewShotExample(
                input="什么是机器学习？",
                output="机器学习是让计算机通过数据自动学习规律的科学，而无需显式编程。", 
                category="定义",
                complexity="low"
            ),
            FewShotExample(
                input="深度学习与机器学习有什么关系？",
                output="深度学习是机器学习的一个子领域，它使用多层神经网络来模仿人脑的学习过程。",
                category="关系",
                complexity="medium"
            ),
            FewShotExample(
                input="给我解释强化学习的概念，用一个生活中的例子说明",
                output="强化学习通过试错来学习最佳行动。举例：如同事到成都，每次走错路就不给好吃的小吃，走对了就奖励美食，久而久之就能找到最高效的路线。",
                category="例子解释",
                complexity="high"
            ),
            FewShotExample(
                input="如何开始学习AI？",
                output="学习AI的步骤：1.先掌握Python和数学基础(线性代数、概率论)；2.学习机器学习基础概念；3.实践简单的项目如线性回归；4.深入学习特定领域如深度学习。",
                category="学习方法",
                complexity="medium"
            )
        ]
    
    def demo_basic_prompt_templates(self):
        """演示基础模板设计与应用"""
        self._log("基础Prompt模板设计")
        print("-" * 55)
        
        print("📝 Prompt模板设计原则:")
        print("   • 明确性: 告诉模型具体要做什么")
        print("   • 结构化: 提供清晰的输入输出格式")
        print("   • 可量化: 尽量给出约束条件")
        print("   • 可测试: 设计能够验证结果质量的提示")
        print()
        
        # 基础模板应用
        templates = [
            {
                "name": "技术解释器",
                "template": ""“你是一个为{target_audience}解释复杂技术的专家。
                
请用{teaching_style}的风格解释以下概念：
{technical_concept}

要求：
1. 用{max_words}个词以内回答
2. 至少举{num_examples}个日常生活例子
3. 解释完成后提出{followup_questions}个相关思考问题""",
                "test_data": {
                    "target_audience": "大学生",
                    "teaching_style": "生动有趣",
                    "technical_concept": "区块链",
                    "max_words": 150,
                    "num_examples": 2,
                    "followup_questions": 3
                }
            },
            
            {
                "name": "任务分解器", 
                "template": ""“你将一个复杂的{task_type}任务分解清晰的执行步骤。

任务名称：{task_name}
目标：{task_goal}
约束：{constraints}

请以{format_style}的步骤格式，列出具体的执行计划。""",
                "test_data": {
                    "task_type": "数据科学",
                    "task_name": "构建房价预测模型",
                    "task_goal": "准确预测新房屋的售价",
                    "constraints": "使用公开数据集，避免隐私问题",
                    "format_style": "数字列表式"
                }
            },
            
            {
                "name": "学习路径规划器",
                "template": ""“你是有经验的{field}教育者，为学生制定详细的学习路径。

学生背景：{student_background}
学习目标：{learning_goal}
时间限制：{time_constraint}

请提供：
1. 按时间顺序的学习模块列表
2. 每个模块的学习资源推荐  
3. 预计完成时间
4. 检查学习效果的方法""",
                "test_data": {
                    "field": "Python编程",
                    "student_background": "零编程基础的大学生",
                    "learning_goal": "能够开发基础的Web应用程序",
                    "time_constraint": "3个月"
                }
            }
        ]
        
        for template_config in templates:
            print(f"\n🎯 {template_config['name']}模板演示:")
            
            # 创建模板
            template = PromptTemplate.from_template(template_config["template"])
            
            # 应用模板数据
            filled_prompt = template.format(**template_config["test_data"])
            
            print(f"   📋 完整提示词:")
            print(f"   {filled_prompt}")
            print()
            
            # 验证模板的可变性
            prompt_complexity = self._calculate_prompt_complexity(filled_prompt)
            print(f"   📊 模板分析:")
            print(f"      └─ 长度: {len(filled_prompt)} 字符")
            print(f"      └─ 复杂度: {prompt_complexity}")
            print(f"      └─ 变量数量: {len(template_config['test_data'])}")
        
        self.exercises_completed.append("basic_prompt_templates")
        self.learnings.append("掌握了结构化Prompt模板的设计技巧")
    
    def _calculate_prompt_complexity(self, prompt: str) -> str:
        """计算提示词复杂度"""
        word_count = len(prompt.split())
        if word_count < 50:
            return "简单"
        elif word_count < 150:
            return "中等"
        else:
            return "复杂"
    
    def demo_few_shot_learning_basics(self):
        """演示Few-shot Learning基础"""
        self._log("Few-shot Learning基础原理")
        print("-" * 55)
        
        print("🧠 Few-shot Learning的概念:")
        print("   • 给模型提供少量高质量的例子")
        print("   • 教会模型理解所期望的模式和格式")
        print("   • 特别有效于格式化任务和质量模式识别")
        print("   • {few = 少量，not few = 零样本}")
        print()
        
        # 基础例子演示
        few_shot_examples = [
            {
                "input": "请把"机器学习"翻译成英文",
                "output": "machine learning"
            },
            {
                "input": "请把"深度学习"翻译成英文", 
                "output": "deep learning"
            },
            {
                "input": "请把"神经网络"翻译成英文",
                "output": "neural network"
            }
        ]
        
        test_input = "请把"人工智能"翻译成英文"
        
        print("🎯 Few-shot翻译演示:")
        print(f"   示例 ({len(few_shot_examples)} 个):")
        
        for i, example in enumerate(few_shot_examples, 1):
            print(f"      {i}. 输入: {example['input']}")
            print(f"         输出: {example['output']}")
        
        print(f"\n   待翻译: {test_input}")
        print(f"   期望输出格式: {len(few_shot_examples[0]['output'].split())} 词")
        print(f"   期望模型输出: artificial intelligence")
        
        # 创建Few-shot提示模板 (适用于聊天模型)
        example_prompt = ChatPromptTemplate.from_messages([
            ("human", "{input}"),
            ("ai", "{output}")
        ])
        
        few_shot_prompt = FewShotChatMessagePromptTemplate(
            examples=few_shot_examples,
            example_prompt=example_prompt
        )
        
        final_prompt = ChatPromptTemplate.from_messages([
            ("system", "你跟着以下示例，用相同的模式回答问题:"),
            few_shot_prompt,
            ("human", "{input}")
        ])
        
        print(f"\n💡 Few-shot模板构成:")
        print(f"   1. System message 设置模式预期")
        print(f"   2. Examples展示输入输出格式") 
        print(f"   3. 留出位置放新的user input")
        
        # 应用示例
        applied_prompt = final_prompt.format_messages(input=test_input)
        print(f"\n📝 完整的Few-shot提示:")
        for msg in applied_prompt:
            print(f"   {msg.type}: {msg.content}")
        
        self.exercises_completed.append("few_shot_learning_basics")
        self.learnings.append("理解了Few-shot Learning的核心原理和LangChain中的实现")
    
    def demo_dynamic_example_selector(self):
        """演示动态Example Selector"""
        self._log("动态示例选择器 (Dynamic Example Selector)")
        print("-" * 55)
        
        print("🎯 Dynamic Example Selector的作用:")
        print("   • 根据输入动态选择最合适的示例") 
        print("   • 可以帮助处理长上下文避免超出token限制")
        print("   • 提高Few-shot学习的效果和质量")
        print("   • 支持多种选择策略: 基于长度、相关性、语义相似度等")
        print()
        
        # 使用建立的中文科技解释示例库
        print("📚 使用中文AI概念解释示例库:")
        print(f"   └─ 总共有 {len(self.example_bank)} 个不同复杂度级别的示例")
        
        # 展示不同复杂度级别
        complexity_levels = {"low": 0, "medium": 0, "high": 0}
        for example in self.example_bank:
            complexity_levels[example.complexity] += 1
        
        print(f"     ├─ 简单难度: {complexity_levels['low']} 个")
        print(f"     ├─ 中等难度: {complexity_levels['medium']} 个")
        print(f"     └─ 高难度: {complexity_levels['high']} 个")
        
        # 基于长度的选择器演示
        from langchain_core.example_selectors import LengthBasedExampleSelector
        
        length_selector = LengthBasedExampleSelector(
            examples=[{"input": ex.input, "output": ex.output} for ex in self.example_bank],
            example_prompt=ChatPromptTemplate.from_messages([
                ("human", "{input}"),
                ("ai", "{output}")
            ]),
            max_length=200
        )
        
        print(f"\n🔍 基于长度的示例选择:")
        
        # 测试不同的输入长度
        test_inputs = [
            "什么是AI？",  # 短输入
            "请详细解释机器学习的概念和应用场景",  # 中等输入
            "深度学习对于自然语言处理领域的发展有什么重要作用，特别是在中文语境下的应用和挑战有哪些？"  # 长输入
        ]
        
        for test_input in test_inputs:
            print(f"\n📝 测试输入长度: {len(test_input)}")
            print(f"   └─ 输入: {test_input}")
            
            # 动态选择示例 (基于长度)
            selected_examples = length_selector.select_examples({"input": test_input})
            
            print(f"   └─ 选中 {len(selected_examples)} 个示例")
            for i, example in enumerate(selected_examples, 1):
                print(f"      {i}. {example['input']} → {example['output'][:40]}...")
        
        # 自定义选择策略演示
        def category_based_selector(question: str) -> List[Dict]:
            """根据问题分类选相关示例"""
            question_lower = question.lower()
            
            # 简单关键词分类
            categories_keywords = {
                "definition": ["定义", "是什么", "什么是", "meaning of"],
                "relationship": ["关系", "区别", "联系", "有什么不同"],
                "example": ["例子", "举例", "举例说明", "例子是"],
                "howto": ["如何", "怎么做", "怎样开始", "learn"]
            }
            
            matched_category = None
            for category, keywords in categories_keywords.items():
                if any(kw in question_lower for kw in keywords):
                    matched_category = category
                    break
            
            # 选择匹配类别的示例 (如果不匹配，返回通用示例)
            if matched_category:
                relevant_examples = [
                    {"input": ex.input, "output": ex.output}
                    for ex in self.example_bank
                    if self._get_example_category(ex.input) == matched_category
                ]
            else:
                relevant_examples = [
                    {"input": ex.input, "output": ex.output}
                    for ex in self.example_bank[:3]  # 默认返回前3个
                ]
            
            return relevant_examples[:3]  # 最多返回3个示例
        
        print(f"\n🧠 改进的基于分类选择器:")
        
        # 测试分类选择
        test_questions = [
            "什么是卷积神经网络？",  # definition
            "深度学习和机器学习有什么主要区别？",  # relationship
            "给我举个深度学习的应用例子",  # example
            "如何开始学习机器学习？"  # howto
        ]
        
        for question in test_questions:
            print(f"\n🧪 测试问题: {question}")
            
            selected = category_based_selector(question)
            print(f"   └─ 选中分类: {question.split('？')[0][0:10]}...")
            print(f"   └─ 相关示例数量: {len(selected)}")
            
            for i, example in enumerate(selected, 1):
                print(f"      {i}. 输入: {example['input']}")
                print(f"         输出: {example['output'][:40]}...")
        
        self.exercises_completed.append("dynamic_example_selector")
        self.learnings.append("掌握了Dynamic Example Selector的原理和实现方法")
    
    def _get_example_category(self, input_text: str) -> str:
        """辅助函数：判断示例的类别"""
        text_lower = input_text.lower()
        
        if any(word in text_lower for word in ["是什么", "什么是", "定义"]):
            return "definition"
        elif any(word in text_lower for word in ["关系", "区别", "不同"]):
            return "relationship"
        elif any(word in text_lower for word in ["例子", "举例"]):
            return "example"
        elif any(word in text_lower for word in ["如何", "怎样"]):
            return "howto"
        else:
            return "general"
    
    def demo_structured_input_output(self):
        """演示结构化输入输出设计"""
        self._log("结构化输入输出设计")
        print("-" * 55)
        
        print("🔧 结构化I/O的重要性:")
        println("   • 确保LLM输出一致性和可预测性")
        print("   • 便于后续程序处理和解析")
        print("   • 支持复杂的多步对话流程")
        print("   • 标准倒逼质量提升")
        print()
        
        # 设计不同的结构化IO模式
        io_patterns = [
            {
                "name": "问答对格式",
                "input_schema": {"question": str, "context": str, "format": str},
                "output_schema": {"answer": str, "confidence": float, "sources": List[str]},
                "prompt": """根据以下信息回答问题：
问题: {question}
背景信息: {context}

请按此JSON格式回答:
{% if format == "detailed" %}
{
  "answer": "详细的回答文本",
  "confidence": 0.95,
  "sources": ["URL1", "URL2"]
}
{% else %}
{
  "answer": "简洁的回答",
  "confidence": 0.85,
  "sources": ["source_name"]
}
{% endif %}"""
            },
            
            {
                "name": "任务执行计划",
                "input_schema": {"task": str, "constraints": List[str], "priority": str},
                "output_schema": {
                    "tasks": List[Dict[str, Any]],
                    "timeline": str,
                    "resources_needed": List[str]
                },
                "prompt": """制定以下任务的详细执行计划：
任务描述: {task}
约束条件: {constraints}
优先级: {priority}

按JSON格式输出执行计划，包括任务分解、时间安排、资源需求等:"""  
            },
            
            {
                "name": "数据分析报告",
                "input_schema": {"data_summary": str, "questions": List[str]},
                "output_schema": {
                    "insights": List[Dict[str, str]],
                    "recommendations": List[str],
                    "risks": List[str],
                    "next_steps": List[str]
                },
                "prompt": """分析以下数据并生成报告：
数据摘要: {data_summary}
分析要求: {questions}

提供以下JSON格式的分析结果:
{
  "insights": [
    {"finding": "发现内容", "significance": "重要性说明"}
  ],
  "recommendations": ["具体建议1", "具体建议2"],
  "risks": ["潜在风险1", "潜在风险2"],
  "next_steps": ["后续步骤1", "后续步骤2"]
}"""
            }
        ]
        
        # 演示每个IO模式
        for pattern in io_patterns:
            print(f"\n🎯 {pattern['name']}:")
            print(f"   输入格式: {list(pattern['input_schema'].keys())}")
            print(f"   输出格式: {list(pattern['output_schema'].keys())}")
            
            # 创建对应的提示模板
            template = PromptTemplate.from_template(pattern['prompt'])
            
            # 生成测试数据
            test_data = {}
            if pattern['name'] == "问答对格式":
                test_data = {
                    "question": "什么是梯度下降？", 
                    "context": "梯度下降是一种优化算法，用于最小化损失函数。",
                    "format": "detailed"
                }
            elif pattern['name'] == "任务执行计划":
                test_data = {
                    "task": "在2024年第一季度内完成公司官网重构",
                    "constraints": ["预算不超过10万美元", "使用现代前端技术栈", "响应式设计"],
                    "priority": "high"
                }
            elif pattern['name'] == "数据分析报告":
                test_data = {
                    "data_summary": "某电商平台2023年12月销售数据：总订单量10万单，平均客单价120元，退货率2.5%",
                    "questions": ["销售趋势如何？", "需要优化哪些环节？"]
                }
            
            # 应用模板 (模拟实际使用)
            print(f"\n   📋 模拟应用示例:")
            print(f"      输入数据: {test_data}")
            
            filled_prompt = template.format(**test_data)
            print(f"      \\ 生成的提示词前200字:\\")
            print(f"         {filled_prompt[:200]}...")
            
            print(f"\n   💡 设计亮点:\\")
            print(f"      • 明确的输入变量定义")
            print(f"      • 结构化的输出格式要求")
            print(f"      • 支持条件逻辑和可变格式")
            print(f"      • 便于程序解析和使用结果")
        
        self.exercises_completed.append("structured_input_output")
        self.learnings.append("掌握了结构化I/O设计的重要性和实现方法")
    
    def demo_prompt_testing_optimization(self):
        """演示提示词测试与优化"""
        self._log("提示词测试与优化")
        print("-" * 55)
        
        print("🔍 Prompt测试优化的重要性:")
        print("   • LLM行为的不确定性需要定量评估")
        print("   • 不同版本的提示词需要对比测试")
        print("   • production用可靠的结果需要系统性验证")
        print("   • 外化优化过程有助于团队合作交接")
        print()
        
        # 测试目标：生成技术概念解释 
        input_question = "什么是卷积神经网络(CNN)的池化层？"
        
        # Prompt版本对比
        prompt_versions = [
            {
                "version": "v1_simple",
                "prompt": f"解释一下：{input_question}",
                "expected": "包含池化层定义、作用、常用类型的内容"
            },
            {
                "version": "v2_structured", 
                "prompt": f"请从以下几个方面解释{input_question}：\n1. 定义和作用\n2. 常见类型\n3. 主要特点\n4. 实际应用案例",
                "expected": "从定义、类型、特点、应用四个维度展开的结构化内容"
            },
            {
                "version": "v3_role_based",
                "prompt": f"你是一名深度学习专家，正在给研究生上课。用课堂讲义的语气解释：{input_question}\n\n要求：\n- 结合图示描述概念\n- 解释技术原理\n- 说明为何重要\n- 给出一个简单的比喻",
                "expected": "专家口吻,包含技术细节,有比喻和，内容更专业深入"
            }
        ]
        
        print("🧪 对比测试的Prompt版本:")
        for i, version in enumerate(prompt_versions, 1):
            print(f"\n   {i}. {version['version']})")
            print(f"      ✏️  Prompt: {version['prompt'][:80]}...")
            print(f"      🎯 预期: {version['expected']}")
        
        # 模拟测试结果 (实际使用需要真实模型调用)
        print(f"\n📊 模拟基准测试结果:\")
        
        mock_test_results = [
            {
                "version": "v1_simple",
                "score": 75,
                "coverage": ["定义", "作用"],
                "length": 120,
                "clarity": 80,
                "technical_level": "medium"
            },
            {
                "version": "v2_structured",
                "score": 85,
                "coverage": ["定义", "类型", "特点", "应用"],
                "length": 200,
                "clarity": 90,
                "technical_level": "detailed"
            },
            {
                "version": "v3_role_based",
                "score": 92,
                "coverage": ["定义", "原理", "类型", "特点", "应用", "比喻"],
                "length": 240,
                "clarity": 95,
                "technical_level": "advanced"
            }
        ]
        
        print(f"\n🏆 结果对比 (分数越高越好):")
        for result in mock_test_results:
            print(f"   📈 {result['version']}: 总体得分{result['score']}/100")
            print(f"      ├─ 内容完整度: {len(result['coverage'])}/6 个维度")
            print(f"      ├─ 响应清晰: {result['clarity']}/100")
            print(f"      ├─ 内容长度: {result['length']} 字符")
            print(f"      └─ 技术深度: {result['technical_level']}")
        
        # 演示提示词优化过程
        print(f"\n🔧 提示词优化循环:")
        print("   1. 设定测试题目和标准答案")
        print("   2. 生成多个版本的提示词")
        print("   3. 对每个版本进行多次测试")
        print("   4. 记录和分析结果")
        print("   5. 基于数据找出最佳版本")
        print("   6. 不断迭代改进")
        
        # 演示自动化测试框架概念
        print(f"\n🤖 自动化测试框架 (代码概念):")
        
        prompt_testing_framework = """
class PromptOptimizer:
    # 自动化提示词优化框架
    
    def optimize_prompt(self, prompt_versions: List[str], test_cases: List)> -> OptimizedPrompt:
        \"\"\