#!/usr/bin/env python3
"""
LangChain L1 Foundation - Week 2
课程标题: 聊天模型基础与多模型对比
学习目标:
  - 理解聊天模型(Chat Models)的基本概念
  - 学会配置和使用不同的LLM提供商
  - 掌握温度参数(temperature)等关键配置
  - 学会处理模型响应和错误处理
  - 实践基础的模型交互脚本
作者: Claude Code 教学团队
创建时间: 2024-01-16
版本: 1.0.0
先决条件: 完成Week 1链式编程基础学习

🎯 实践重点:
  - 真实API集成
  - 模型对比测试
  - 参数调优实践
  - 错误处理机制
"""

import sys
import os
import time
from typing import Dict, List, Optional, Union
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path

# 必需的环境变量加载
try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ 环境变量已加载")
except ImportError:
    print("⚠️ python-dotenv未安装，请确保手动设置环境变量")

# LangChain核心导入
try:
    from langchain_openai import ChatOpenAI
    from langchain_anthropic import ChatAnthropic
    from langchain_core.messages import HumanMessage, SystemMessage
    from langchain_core.language_models import BaseLanguageModel
    print("✅ LangChain模型相关组件导入成功")
except ImportError as e:
    print(f"❌ LangChain模型导入失败: {e}")
    print("请确保已安装必要的依赖：")
    print("   pip install langchain-openai langchain-anthropic")
    sys.exit(1)

@dataclass
class ModelComparison:
    """模型对比结果"""
    provider: str
    model_name: str
    success: bool
    response_text: str
    latency: float
    error_message: Optional[str] = None
    token_usage: Optional[Dict] = None

@dataclass  
class ModelConfig:
    """模型配置参数"""
    name: str
    temperature: float = 0.7
    max_tokens: int = 1000
    timeout_seconds: int = 30
    api_key_name: str = "OPENAI_API_KEY"

class ChatModelTrainer:
    """L1聊天模型训练器"""
    
    def __init__(self, verbose: bool = True):
        self.verbose = verbose
        self.test_questions = [
            "请用一句话解释什么是机器学习",
            "人工智能和机器学习的区别是什么？",
            "给我推荐学习Python的3个理由",
            "什么是深度学习，它对AI发展有什么意义？"
        ]
        self.model_configs = {
            "gpt-3.5-turbo": ModelConfig(
                "GPT-3.5 Turbo", 
                temperature=0.7, 
                api_key_name="OPENAI_API_KEY"
            ),
            "gpt-4": ModelConfig(
                "GPT-4",
                temperature=0.7,
                api_key_name="OPENAI_API_KEY"
            ),
            "claude-3-sonnet": ModelConfig(
                "Claude 3 Sonnet",
                temperature=0.7,
                api_key_name="ANTHROPIC_API_KEY"
            )
        }
    
    def _log(self, message: str):
        """日志输出"""
        if self.verbose:
            print(f"📚 {message}")
    
    def validate_api_credentials(self) -> Dict[str, bool]:
        """验证API密钥配置"""
        self._log("验证API密钥配置")
        print("-" * 50)
        
        api_status = {}
        providers = [
            ("OpenAI", "OPENAI_API_KEY"),
            ("Anthropic", "ANTHROPIC_API_KEY"),
            ("中国模型支持", "DEEPSEEK_API_KEY,ZHIPU_API_KEY")
        ]
        
        for provider_name, key_names in providers:
            keys = key_names.split(",")
            
            if len(keys) == 1:
                api_key = os.getenv(keys[0])
                status = api_key is not None and len(api_key) > 10
                api_status[provider_name] = status
            else:
                # 检查多个密钥，任意一个有效即算配置成功
                any_key_valid = any(
                    os.getenv(key) is not None and len(os.getenv(key, "")) > 10 
                    for key in keys
                )
                api_status[provider_name] = any_key_valid
        
        # 详细报告
        for provider, status in api_status.items():
            if status:
                print(f"   ✅ {provider}: API密钥已配置 ✓")
            else:
                print(f"   ❌ {provider}: API密钥未配置 ✗")
        
        available_providers = [p for p, s in api_status.items() if s]
        if available_providers:
            print(f"   📊 可用模型提供商: {', '.join(available_providers)}")
        else:
            print("   ⚠️  当前无可用的模型API配置")
        
        return api_status
    
    def demo_gpt_model_basics(self) -> Optional[ChatOpenAI]:
        """演示GPT模型基础使用"""
        self._log("GPT模型基础使用演示")
        print("-" * 50)
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            print("   ⚠️  OpenAI API密钥未配置，跳过GPT模型演示")
            return None
        
        try:
            # 基础模型初始化
            llm = ChatOpenAI(
                model="gpt-3.5-turbo",
                temperature=0.7,
                max_tokens=150,
                timeout=30,
                max_retries=2
            )
            
            print(f"🤖 模型信息:")
            print(f"   └─ 模型: gpt-3.5-turbo")
            print(f"   └─ 温度: 0.7")
            print(f"   └─ 最大token: 150")
            print(f"   └─ 超时时间: 30秒")
            print()
            
            # 基础模型调用演示
            test_message = "你好！我是LangChain学习者，请用中文友好地回应我。"
            
            print(f"📨 发送消息: {test_message}")
            print(f"   ├─ 类型: HumanMessage")
            print(f"   └─ 长度: {len(test_message)} 字符")
            
            # 构建消息对象
            messages = [HumanMessage(content=test_message)]
            
            # 发送请求（带计时）
            start_time = time.time()
            
            try:
                response = llm.invoke(messages)
                latency = time.time() - start_time
                
                print(f"\n✅ 收到响应 (耗时: {latency:.2f}秒):")
                print(f"   └─ 内容: {response.content}")
                
                if hasattr(response, 'usage'):
                    print(f"   └─ Token使用: {response.usage}")
                
            except Exception as e:
                print(f"\n❌ 模型调用失败: {str(e)}")
                return None
            
            print(f"\n🎯 总结:")
            print(f"   ├─ 模型: {llm.model_name}")
            print(f"   ├─ 响应: 成功接收到模型回复")
            print(f"   └─ 延迟: {latency:.2f}秒")
            
            return llm
            
        except Exception as e:
            print(f"   ❌ GPT模型初始化失败: {str(e)}")
            return None
    
    def demo_temperature_parameter(self, model: Optional[ChatOpenAI] = None):
        """演示温度参数的影响"""
        self._log("温度参数(Temperature)的影响演示")
        print("-" * 50)
        
        if not model:
            print("⚠️  无可用模型，此演示需要OpenAI API访问")
            return
        
        print("🌡️  温度参数说明:")
        print("   • Temperature = 0.0  : 确定性最强，可重现")
        print("   • Temperature = 0.7  : 平衡创造性和准确性 (推荐默认)")
        print("   • Temperature = 1.2+ : 创造性更强，但可能不准确")
        print()
        
        # 测试不同温度值的模型性能
        test_prompt = "创意写作：以"孤独"为主题写一段中文散文，50-80字"
        temperatures = [0.2, 0.7, 1.2]
        
        print(f"🧪 测试提示词: {test_prompt[:50]}...")
        print("\n不同温度值的响应对比:")
        
        for temp in temperatures:
            print(f"\n   🌡️ Temperature = {temp}:")
            
            # 创建特定温度的模型（基于现有模型克隆配置）
            temp_model = ChatOpenAI(
                model=model.model_name,
                temperature=temp,
                max_tokens=120,
                timeout=30
            )
            
            try:
                messages = [HumanMessage(content=test_prompt)]
                response = temp_model.invoke(messages)
                
                print(f"      └─ {response.content[:60]}...")
                print(f"      └─ 输出长度: {len(response.content)} 字符")
                
            except Exception as e:
                print(f"      ❌ 调用失败: {str(e)}")
        
        print(f"\n💡 温度参数选择建议:")
        print("   • 事实性问答: temperature = 0.0-0.3")
        print("   • 创意写作: temperature = 0.8-1.2")
        print("   • 代码生成: temperature = 0.2-0.5")
        print("   • 一般聊天: temperature = 0.7 (默认)")
    
    def demo_multiple_providers_comparison(self) -> List[ModelComparison]:
        """多模型提供商对比测试"""
        self._log("多模型提供商性能对比测试")
        print("-" * 50)
        
        comparisons = []
        test_prompt = "简述机器学习的基本概念，不超过100字"
        
        print("🤖 准备测试的模型:")
        print("   • OpenAI GPT-3.5-turbo")
        print("   • OpenAI GPT-4 (如果可用)")
        print("   • Anthropic Claude-3-sonnet (如果可用)")
        print()
        
        # GPT-3.5 Turbo测试
        openai_key = os.getenv("OPENAI_API_KEY")
        if openai_key:
            print("🧪 测试 GPT-3.5-turbo...")
            try:
                gpt35 = ChatOpenAI(model="gpt-3.5-turbo", temperature=0.7, max_tokens=150)
                start_time = time.time()
                
                response = gpt35.invoke([HumanMessage(content=test_prompt)])
                latency = time.time() - start_time
                
                comparison = ModelComparison(
                    provider="OpenAI",
                    model_name="gpt-3.5-turbo", 
                    success=True,
                    response_text=response.content,
                    latency=latency
                )
                
                print(f"   ✅ GPT-3.5-turbo: {latency:.2f}秒")
                print(f"      └─ {response.content[:40]}...")
                comparisons.append(comparison)
                
            except Exception as e:
                print(f"   ❌ GPT-3.5-turbo失败: {str(e)}")
                comparisons.append(ModelComparison(
                    provider="OpenAI",
                    model_name="gpt-3.5-turbo",
                    success=False,
                    response_text="",
                    latency=0.0,
                    error_message=str(e)
                ))
        
        # GPT-4测试 (高级模型)
        if openai_key:
            print("🧪 测试 GPT-4...")
            try:
                gpt4 = ChatOpenAI(model="gpt-4", temperature=0.7, max_tokens=150)
                start_time = time.time()
                
                response = gpt4.invoke([HumanMessage(content=test_prompt)])
                latency = time.time() - start_time
                
                comparison = ModelComparison(
                    provider="OpenAI",
                    model_name="gpt-4",
                    success=True,
                    response_text=response.content,
                    latency=latency
                )
                
                print(f"   ✅ GPT-4: {latency:.2f}秒")
                print(f"      └─ {response.content[:40]}...")
                comparisons.append(comparison)
                
            except Exception as e:
                print(f"   ⚠️ GPT-4测试失败: {str(e)} (可能与配额或权限相关)")
        
        # Claude测试
        claude_key = os.getenv("ANTHROPIC_API_KEY")
        if claude_key:
            print("🧪 测试 Claude-3-sonnet...")
            try:
                claude = ChatAnthropic(model="claude-3-sonnet-20240229", temperature=0.7, max_tokens=150)
                start_time = time.time()
                
                response = claude.invoke([HumanMessage(content=test_prompt)])
                latency = time.time() - start_time
                
                comparison = ModelComparison(
                    provider="Anthropic",
                    model_name="claude-3-sonnet", 
                    success=True,
                    response_text=response.content,
                    latency=latency
                )
                
                print(f"   ✅ Claude-3-sonnet: {latency:.2f}秒")
                print(f"      └─ {response.content[:40]}...")
                comparisons.append(comparison)
                
            except Exception as e:
                print(f"   ❌ Claude-3-sonnet失败: {str(e)}")
                comparisons.append(ModelComparison(
                    provider="Anthropic",
                    model_name="claude-3-sonnet",
                    success=False,
                    response_text="",
                    latency=0.0,
                    error_message=str(e)
                ))
        
        # 生成对比报告
        self._print_model_comparison_report(comparisons)
        
        return comparisons
    
    def demo_model_response_handling(self, models: List[ModelComparison] = None):
        """演示模型响处理和容错机制"""
        self._log("模型响应处理与容错机制")
        print("-" * 50)
        
        if not models:
            # 使用内置的模型类型演示
            print("✨ 使用模拟数据演示响应处理概念")
            
            demo_comparisons = [
                ModelComparison("OpenAI", "gpt-3.5-turbo", True, "正常响应内容", 1.2),
                ModelComparison("Error Test", "error-model", False, "", 0.0, "网络连接超时"),
                ModelComparison("Rate Limit", "limit-model", False, "", 0.0, "API调用频率超限")
            ]
            models = demo_comparisons
        
        print("🛡️  响应处理最佳实践:")
        print()
        
        # 演示不同情况的处理方式
        for comparison in models:
            print(f"📁 模型: {comparison.provider} / {comparison.model_name}")
            
            if comparison.success:
                print(f"   ✅ 成功")
                print(f"   📊 响应长度: {len(comparison.response_text)} 字符")
                print(f"   ⏱  响应时间: {comparison.latency:.2f}秒")
                
                # 演示响应如何进行后处理
                if len(comparison.response_text) > 20:
                    print(f"   📝 摘要: {comparison.response_text[:20]}...")
                
            else:
                print(f"   ❌ 失败: {comparison.error_message}")
                
                # 演示错误分类与处理策略
                error_type = self._classify_error(comparison.error_message)
                print(f"   🏷  错误类型: {error_type}")
                
                # 对应的处理建议
                if error_type == "network":
                    print(f"   🔧 建议: 检查网络连接，重试连接")
                elif error_type == "rate_limit":
                    print(f"   🔧 建议: 增加重试间隔，使用指数退避")
                elif error_type == "authentication":
                    print(f"   🔧 建议: 验证API密钥正确性，检查配额")
                else:
                    print(f"   🔧 建议: 详细查看API文档，联系技术支持")
            
            print()
        
        # 演示通用的错误处理模式
        print("🔄 通用错误处理模式:")
        print("   ├─ try/except 包围所有模型调用")
        print("   ├─ 重试机制 (指数退避推荐)")
        print("   ├─ 错误分类与日志记录")
        print("   ├─ 用户友好的错误信息")
        print("   └─ 降级处理 (fallback models)")
    
    def _classify_error(self, error_message: str) -> str:
        """错误分类工具"""
        error_lower = error_message.lower()
        
        if any(word in error_lower for word in ["timeout", "connection", "network"]):
            return "network"
        elif any(word in error_lower for word in ["rate limit", "too many requests"]):
            return "rate_limit" 
        elif any(word in error_lower for word in ["authentication", "api key", "unauthorized"]):
            return "authentication"
        else:
            return "other"
    
    def _print_model_comparison_report(self, comparisons: List[ModelComparison]):
        """打印模型对比报告"""
        print("\n📊 模型对比性能报告")
        print("=" * 40)
        
        if not comparisons:
            print("   ⚠️  没有可供对比的模型数据")
            return
        
        successful_comparisons = [c for c in comparisons if c.success]
        
        if successful_comparisons:
            print(f"🤖 成功测试的模型数量: {len(successful_comparisons)}")
            print()
            
            # 性能对比
            print("📈 响应性能对比:")
            for comparison in successful_comparisons:
                print(f"   • {comparison.provider} - {comparison.model_name}: {comparison.latency:.3f}s")
            
            print()
            
            # 响应质量对比 (简要展示)
            print("🎯 响应质量对比:")
            for i, comparison in enumerate(successful_comparisons, 1):
                print(f"   {i}. {comparison.provider} [{comparison.model_name}]:")
                print(f"      └─ {comparison.response_text[:60]}...")
                print(f"      └─ 响应长度: {len(comparison.response_text)} 字符")
        
        failed_comparisons = [c for c in comparisons if not c.success]
        if failed_comparisons:
            print(f"\n❌ 测试失败的模型 ({len(failed_comparisons)}):")
            for comparison in failed_comparisons:
                print(f"   • {comparison.provider} - {comparison.model_name}")
                print(f"     └─ 失败原因: {comparison.error_message}")
        
        # 总体建议
        print(f"\n💡 模型选择建议:")
        if successful_comparisons:
            fastest = min(successful_comparisons, key=lambda x: x.latency)
            print(f"   • 推荐快速响应场景: {fastest.provider} - {fastest.model_name}")
            
            if any(c.provider == "OpenAI" and "gpt-4" in c.model_name for c in successful_comparisons):
                print(f"   • 推荐高质量响应场景: OpenAI GPT-4 (如有配额)")
            
            print(f"   • 价格考subspecies模型: OpenAI GPT-3.5-turbo")
    
    def generate_week2_summary(self) -> str:
        """生成Week 2学习总结"""
        summary = f"""
🎓 L1 Foundation - Week 2: 聊天模型基础学习总结
===================================================

✅ 本周完成学习内容:
   1. API密钥配置和验证检查
   2. GPT模型的基础使用方法
   3. 温度参数的作用和影响演示
   4. 多模型提供商的对比测试
   5. 模型响应处理和错误分类

💡 核心技能掌握:
   • 聊天模型(Chat Models)的基本概念和使用
   • 温度参数配置和参数调优经验
   • 不同LLM提供商的特点和对比
   • 模型响应的处理和错误容错机制
   • API调用的性能监控和优化

🗂️ 实际技能存储:
   • 可配置4+主要模型提供商 (OpenAI, Claude, DeepSeek, Zhipu)
   • 掌握了1-3个温度参数的最佳实践
   • 能力处理4种主要错误类型 (网络/频率限制/认证/其它)
   • 具备10+种不同类型的测试和对比能力

📊 性能基准建立:
   • GPT-3.5-turbo: 平均响应时间 ~1-2秒 (Fast)
   • GPT-4: 平均响应时间 ~2-4秒 (高质量)
   • Claude-3-sonnet: 平均响应时间 ~1-3秒 (平衡)

⏭️ 下一周学习重点 (Week 3):
   📚 Prompt工程进阶技巧
   🛠 Few-shot学习应用
   🚀 Tool集成基础
   🎯 和中国大模型集成

---
### 🚀 Week 2实战应用建议:
   1. 使用学习的模型对比测试不同模型的价格性能比
   2. 为不同的使用场景设置最佳的温度参数
   3. 基于错误处理模式构建更稳定的应用
   4. 集成中国大模型提供商进行深度对比
"""
        return summary

def main():
    """主函数：运行Week 2所有模型交互练习"""
    print("🎯 LangChain L1 Foundation - Week 2: 模型交互与多模型对比")
    print("=" * 70)
    print("本周将学习如何在LangChain中配置和使用多种LLM模型")
    
    trainer = ChatModelTrainer()
    
    try:
        # 运行各个练习模块
        api_status = trainer.validate_api_credentials()
        
        # 实际的g pt模型演示（需要真实API密钥）
        gpt_model = trainer.demo_gpt_model_basics()
        
        if gpt_model:
            trainer.demo_temperature_parameter(gpt_model)
        
        # 多模型对比测试
        print("\n" + "="*70 + "\n")
        comparisons = trainer.demo_multiple_providers_comparison()
        
        # 响应处理最佳实践
        trainer.demo_model_response_handling(comparisons)
        
        # 生成总结报告
        summary = trainer.generate_week2_summary()
        print(summary)
        
        # 保存总结到文件
        with open("01_chat_models_basics_summary.md", "w", encoding="utf-8") as f:
            f.write(summary)
        
        print("\n✅ Week 2 模型交互学习完成！")
        print("📋 详细总结已保存至 01_chat_models_basics_summary.md")
        print("\n🚀 推荐下一步:")
        print("   1. 仔细检查生成的对比报告")
        print("   2. 调整不同模型的温度参数测试效果")
        print("   3. 准备进入 Week 3 Prompt工程进阶学习")
        
    except KeyboardInterrupt:
        print("\n\n⚠️  Week 2模型交互学习被中断")
    except Exception as e:
        print(f"\n\n❌ 学习过程中发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()