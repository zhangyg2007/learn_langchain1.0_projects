#!/usr/bin/env python3
"""
LangChain L1 Foundation - Week 1
课程标题: 链式编程基础概念
学习目标:
  - 理解LangChain的链式编程概念
  - 学习SimpleLLMChain的基本结构
  - 掌握LCEL (LangChain Expression Language)基础语法
  - 实践基础的Prompt工程和Response解析
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
先决条件: 成功完成01_environment_check.py的环境检查
"""

import sys
import os
from typing import Dict, List, Optional, Union
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path

# 尝试导入LangChain相关模块
try:
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    print("✅ LangChain核心组件导入成功")
except ImportError as e:
    print(f"❌ 无法导入LangChain组件: {e}")
    print("请确保已经安装了 langchain-core: pip install langchain-core")
    sys.exit(1)

# 设置环境变量（如果.env文件存在）
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 环境变量加载成功")
except ImportError:
    print("⚠️ python-dotenv未安装，跳过环境变量加载")

@dataclass
class ChainResult:
    """链式执行结果"""
    input_data: Dict
    chain_output: str
    execution_time: float
    success: bool
    error: Optional[str] = None

class ChainBasicsTrainer:
    """L1链式编程基础训练器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.exercises_completed = []
        self.learnings = []
        
    def _log(self, message: str):
        """日志输出"""
        if self.verbose:
            print(f"📚 {message}")
    
    def demo_prompt_template_basics(self):
        """演示提示词模板基础"""
        self._log("练习1: Prompt模板基础概念")
        print("-" * 50)
        print("📝 Prompt模板是什么？")
        print("   • 模板化的提示词，可以动态填充变量")
        print("   • 帮助标准化LLM交互"
        print("   • 支持参数化的内容生成")
        print()
        
        # 创建基础模板
        basic_template = PromptTemplate.from_template(
            "请用{years}岁以上的读者能够理解的语言解释{concept}"
        )
        
        # 基础调用
        prompt_result = basic_template.format(
            concept="机器学习",
            years=18
        )
        
        print(f"🎯 生成的提示词:")
        print(f"   └─ {prompt_result}")
        print()
        
        self.exercises_completed.append("prompt_template_basics")
        self.learnings.append("理解了PromptTemplate的基本使用方法")
        
        return basic_template
    
    def demo_string_output_parser(self):
        """演示字符串输出解析器"""
        self._log("练习2: 输出解析器概念")
        print("-" * 50)
        
        parser = StrOutputParser()
        
        print("🔍 输出解析器的作用:")
        print("   • 将LLM的原始输出转换为标准化格式")
        print("   • 支持不同类型输出的处理")
        print("   • 提供统一的输出接口")
        print()
        
        # 模拟LLM输出
        mock_llm_output = """这是一个多行输出的示例
        包含了复杂的格式和额外的信息
        我们希望提取干净的内容"""
        
        parsed_output = parser.parse(mock_llm_output)
        
        print(f"🧪 原始LLM输出:")
        print(f"   └── 长度: {len(mock_llm_output)} 字符")
        print(f"   └── 内容: {mock_llm_output[:100]}...")
        print()
        print(f"✨ 解析后的输出:")
        print(f"   └── 长度: {len(parsed_output)} 字符")
        print(f"   └── 内容: {parsed_output[:100]}...")
        print()
        
        self.exercises_completed.append("string_output_parser")
        self.learnings.append("掌握了StrOutputParser的基本使用")
        
        return parser
    
    def demo_simple_chain_concept(self):
        """演示简单链的概念"""
        self._log("练习3: 简单链的概念理解")
        print("-" * 50)
        print("🔗 什么是链(Chain)？")
        print("   • 多个组件的逻辑组合")
        print("   • 数据从输入到输出的处理管道")
        print("   • 可以串联模板、模型、解析器等组件")
        print()
        
        # 创建一个完全模拟的"链"
        def mock_llm_call(prompt: str) -> str:
            """模拟LLM调用"""
            responses = {
                "请用18岁以上的读者能够理解的语言解释机器学习":
                    "机器学习是让计算机从数据中学习模式的科学。它通过算法分析大量数据，自动找出其中的规律和规则，然后用这些规律来预测新数据或做出决策。",
                "请用10岁以上的读者能够理解的语言解释深度学习":
                    "深度学习是机器学习的一种方式，就像我们的大脑由很多神经元组成网络一样，计算机也通过学习很多层的信息来理解事情。"
            }
            return responses.get(prompt, f"我可以回答关于'{prompt}'的问题，这是一个很好的学习概念。")
        
        # 链式处理示例
        concept = "机器学习"
        target_age = 18
        
        # 步骤1: 生成提示词（模拟LangChain的PromptTemplate）
        prompt = f"请用{target_age}岁以上的读者能够理解的语言解释{concept}"
        print(f"1️⃣ 步骤1 - 生成提示词:")
        print(f"   └─ {prompt}")
        
        # 步骤2: 调用模型（模拟LLM）
        print(f"\n2️⃣ 步骤2 - 模型调用:")
        print(f"   └─ 调用LLM处理提示词...")
        llm_response = mock_llm_call(prompt)
        
        # 步骤3: 解析输出（模拟输出解析器）
        print(f"\n3️⃣ 步骤3 - 输出解析:")
        print(f"   └─ 原始响应长度: {len(llm_response)} 字符")
        final_response = llm_response.strip()
        print(f"   └─ 处理后长度: {len(final_response)} 字符")
        
        print(f"\n🎯 最终结果:")
        print(f"   └─ {final_response}")
        
        self.exercises_completed.append("simple_chain_concept")
        self.learnings.append("理解了链式处理的基本思想")
        
    def demo_lcel_syntax_basics(self):
        """演示LCEL语法基础"""
        self._log("练习4: LCEL (LangChain Expression Language) 语法")
        print("-" * 50)
        
        print("📝 LCEL是什么？")
        print("   • LangChain表达式语言")
        print("   • 简化链的创建和组合")
        print("   • 支持管道式语法（pipe）")
        print()
        
        # LCEL语法模拟
        print("🔧 管道运算符（|）的概念:")
        print("   • 将前一个函数的输出作为下一个函数的输入")
        print("   • 类似Linux管道: ls | grep txt | wc -l")
        print("   • 在LangChain中用于组件连接")
        print()
        
        # 模拟管道式处理
        def process_text_common(text: str) -> str:
            """通用文本处理管道"""
            # 模拟多个步骤的链式处理
            def clean_text(t: str) -> str:
                return t.strip().lower()
            
            def normalize_input(t: str) -> str:
                return t.replace('
',' ').replace('  ',' ')
            
            def analyze_length(t: str) -> tuple:
                return len(t), len(t.split())
            
            # 管道式处理
            result = clean_text(text)
            result = normalize_input(result)
            word_count, char_count = analyze_length(result)
            
            return {
                "processed_text": result,
                "char_count": char_count,
                "word_count": word_count
            }
        
        # 演示输入处理
        sample_text = "  机器学习   是   AI 的重要分支  "
        result = process_text_common(sample_text)
        
        print(f"🧪 样本文本: '{sample_text}'")
        print(f"✨ 处理后: '{result['processed_text']}'")
        print(f"📊 统计: {result['word_count']} 词, {result['char_count']} 字符")
        
        self.exercises_completed.append("lcel_syntax_basics")
        self.learnings.append("掌握了管道式处理的基本思想")
    
    def demo_chain_pipeline_design(self):
        """演示链式管道设计"""
        self._log("练习5: 链式管道设计模式")
        print("-" * 50)
        
        print("🎨 设计模式的思考:")
        print("   • 如何将复杂的AI应用分解为可管理的步骤？")
        print("   • 如何确保每个步骤的输出质量？")
        print("   • 如何使链式处理可测试、可调试？")
        print()
        
        # 设计一个问答链的经典模式
        class QAPipeline:
            """问答处理管道"""
            
            def __init__(self, name: str = "问答管道"):
                self.name = name
                self.processing_log = []
            
            def validate_input(self, question: str) -> bool:
                """验证输入质量"""
                self.processing_log.append(f"输入验证: '{question}'")
                
                if len(question.strip()) < 5:
                    self.processing_log.append("失败：问题太短")
                    return False
                elif len(question) > 500:
                    self.processing_log.append("失败：问题太长")
                    return False
                
                return True
            
            def identify_question_type(self, question: str) -> str:
                """识别问题类型"""
                self.processing_log.append(f"问题类型识别")
                
                keywords_calc = ["计算", "math", "calculate", "数字"]
                keywords_trans = ["翻译", "translate", "语言"]
                keywords_code = ["代码", "code", "程序", "编程"]
                
                for kw in keywords_calc:
                    if kw in question.lower():
                        return "calculation"
                
                for kw in keywords_trans:
                    if kw in question.lower():
                        return "translation"
                        
                for kw in keywords_code:
                    if kw in question.lower():
                        return "coding"
                
                return "general"
            
            def format_prompt(self, question: str, q_type: str) -> str:
                """格式化提示词"""
                self.processing_log.append(f"格式化提示词 (类型: {q_type})")
                
                if q_type == "calculation":
                    return f"请帮我计算并解释以下问题：{question}"
                elif q_type == "translation":
                    return f"请帮我翻译以下内容：{question}"
                elif q_type == "coding":
                    return f"请帮我编写解决这个问题的代码：{question}"
                else:
                    return f"请回答以下问题：{question}"
            
            def process(self, question: str) -> ChainResult:
                """完整的问答处理流程"""
                start_time = datetime.now()
                
                self.processing_log.append(f"🎯 开始处理: '{question}'")
                
                # 步骤1: 输入验证
                if not self.validate_input(question):
                    return ChainResult(
                        input_data={"question": question},
                        chain_output="",
                        execution_time=(datetime.now() - start_time).total_seconds(),
                        success=False,
                        error="输入验证失败"
                    )
                
                # 步骤2: 问题分类
                q_type = self.identify_question_type(question)
                self.processing_log.append(f"识别问题类型: {q_type}")
                
                # 步骤3: 提示词格式化
                formatted_prompt = self.format_prompt(question, q_type)
                self.processing_log.append(f"生成提示词: '{formatted_prompt[:100]}...'")
                
                # 步骤4: 模拟LLM调用（简化模拟）
                mock_responses = {
                    "calculation": "根据计算，结果为42，我来详细解释计算过程...",
                    "translation": "Translation: This is a sample translation result",
                    "coding": "```python\ndef solve_problem():\n    return solution()\n```",
                    "general": "这是一个很好的问题，让我来详细回答..."
                }
                
                llm_response = mock_responses.get(q_type, "我理解您的问题，让我给出详细回答...")
                
                # 步骤5: 后处理
                final_output = f"[{q_type.upper()}] {llm_response}"
                
                execution_time = (datetime.now() - start_time).total_seconds()
                
                self.processing_log.append(f"✅ 处理完成，耗时: {execution_time:.2f}秒")
                
                return ChainResult(
                    input_data={
                        "question": question,
                        "q_type": q_type,
                        "prompt": formatted_prompt
                    },
                    chain_output=final_output,
                    execution_time=execution_time,
                    success=True
                )
        
        # 使用和测试该设计
        pipeline = QAPipeline("演示问答管道")
        test_questions = [
            "计算一下2的10次方",
            "请翻译：Hello World",
            "如何用Python写一个斐波那契数列函数",
            "什么是人工智能"
        ]
        
        for question in test_questions:
            print(f"\n🧪 测试问题: '{question}'")
            result = pipeline.process(question)
            
            if result.success:
                print(f"✅ 回答: {result.chain_output[:100]}...")
                print(f"⏱  处理时间: {result.execution_time:.3f}秒")
            else:
                print(f"❌ 处理失败: {result.error}")
            
            print(f"📋 处理日志:")
            for log_item in pipeline.processing_log[-3:]:  # 显示最近3条日志
                print(f"     • {log_item}")
            pipeline.processing_log = []  # 清理日志准备下个问题
        
        self.exercises_completed.append("chain_pipeline_design")
        self.learnings.append("理解了如何设计可扩展的链式处理架构")
    
    def generate_summary(self) -> str:
        """生成学习总结"""
        summary = f"""
🎓 L1 Foundation - Week 1: 链式编程基础学习总结
================================================

✅ 完成的练习项目:
"""
        for i, exercise in enumerate(self.exercises_completed, 1):
            summary += f"   {i}. {exercise}\n"
        
        summary += f"\n💡 主要学习收获:\n"
        for i, learning in enumerate(self.learnings, 1):
            summary += f"   {i}. {learning}\n"
        
        summary += f"""
🎯 核心概念掌握情况:
   ✅ PromptTemplate基础: 理解模板化提示词的使用
   ✅ 输出解析概念: 掌握标准化输出处理
   ✅ 链式处理思想: 理解数据流的管道化处理
   ✅ LCEL语法基础: 了解管道运算符的应用
   ✅ 设计模式理解: 掌握可扩展架构思想

⏩ 下一课预告:
   📚 Week 2: 模型交互与Prompt工程
   🔧 将学习真实LLM模型集成
   🚀 构建完整的端到端链式应用
"""
        return summary

def main():
    """主函数：运行整套链式编程基础练习"""
    print("🎯 LangChain L1 Foundation - Week 1: 链式编程基础")
    print("=" * 60)
    print("本课程将通过实际示例帮助你理解LangChain的核心概念")
    
    trainer = ChainBasicsTrainer()
    
    try:
        print("\n开始学习链式编程基础概念...\n")
        
        # 运行各个练习
        trainer.demo_prompt_template_basics()
        trainer.demo_string_output_parser()
        trainer.demo_simple_chain_concept()
        trainer.demo_lcel_syntax_basics()
        trainer.demo_chain_pipeline_design()
        
        # 生成学习总结
        summary = trainer.generate_summary()
        print(summary)
        
        # 保存到文件
        with open("02_chain_basics_summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        
        print("✅ 链式编程基础学习完成！")
        print("📋 学习总结已保存至 02_chain_basics_summary.md")
        print("\n🚀 推荐下一步:")
        print("   1. 仔细阅读生成的学习总结文件")
        print("   2. 操作并测试每个练习的代码示例")
        print("   3. 准备进入 Week 2 模型交互内容学习")
        
    except KeyboardInterrupt:
        print("\n\n⚠️ 链式编程基础学习被中断")
    except Exception as e:
        print(f"\n\n❌ 学习过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()