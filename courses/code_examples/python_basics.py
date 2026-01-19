#!/usr/bin/env python3
"""
LangChain 1.0 基础Python实践
课程名称: L1 Foundation - Python基础示例
"""

import os
from datetime import datetime
from typing import Optional, List
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

print("🎯 LangChain 1.0 基础学习示例")
print("=" * 50)

# 🔵 示例1: 环境配置与基础导入
def demo_environment_setup():
    """
    演示基础环境配置
    """
    print("\n📋 示例1: 环境配置检查")
    print("-" * 30)
    
    # 检查关键环境变量
    env_vars = ['OPENAI_API_KEY', 'HUGGINGFACE_API_KEY']
    
    for var in env_vars:
        value = os.getenv(var)
        if value:
            print(f"✅ {var}: {'*' * 8}已配置")
        else:
            print(f"❌ {var}: 未配置")
    
    print("📍 下一步: 建议设置中国大模型API密钥")

# 🔵 示例2: 基础链式编程
def demo_simple_chain():
    """
    演示基础链式编程概念
    """
    print("\n🔗 示例2: 链式编程基础")
    print("-" * 30)
    
    # 模拟基础链式操作
    class SimpleChain:
        def __init__(self, name: str):
            self.name = name
            self.steps = []
        
        def add_step(self, step: str):
            self.steps.append(step)
            return self
        
        def execute(self) -> str:
            result = f"Chain '{self.name}' executed: {' -> '.join(self.steps)}"
            return result
    
    # 创建链式操作
    chain = SimpleChain("问答系统")
    result = chain.add_step("接收输入")\
                 .add_step("处理文本")\
                 .add_step("生成回答")\
                 .execute()
    
    print(f"🎉 链式执行结果: {result}")
    
# 🔵 示例3: 提示词模板基础
def demo_prompt_templates():
    """
    演示提示词模板概念
    """
    print("\n📝 示例3: 提示词模板")
    print("-" * 30)
    
    # 基础模板
    templates = {
        "翻译助手": "请帮我把以下内容翻译成{target_language}：{content}",
        "文案生成": "请为{product_name}写一个{ad_type}{platform}广告文案，目标{target_audience}",
        "知识问答": "关于{topic}，请详细解释{question}",
        "代码生成": "请用{language}写一个{function_type}函数，{requirements}"
    }
    
    # 示例：产品文案生成
    prompt = templates["文案生成"].format(
        product_name="智能办公助手",
        ad_type="朋友圈",
        platform="社交媒体", 
        target_audience="企业用户"
    )
    
    print(f"📌 生成的提示词: {prompt}")
    
# 🔵 示例4: 函数调用工具
def demo_tool_usage():
    """
    演示工具函数的概念
    """
    print("\n🛠 示例4: 工具函数")
    print("-" * 30)
    
    class Calculator:
        """计算器工具"""
        
        @staticmethod
        def add(a: float, b: float) -> float:
            return a + b
        
        @staticmethod  
        def multiply(a: float, b: float) -> float:
            return a * b
            
        @staticmethod
        def info() -> str:
            return "一个基础的数学计算器工具"
    
    class WebSearch:
        """网页搜索工具"""
        
        @staticmethod
        def search(query: str) -> str:
            # 模拟搜索返回
            return f"搜索'{query}'的模拟结果: 找到{len(query)}个相关结果"
    
    # 使用工具
    calc = Calculator()
    web = WebSearch()
    
    print(f"🧮 计算器测试: 2 + 3 = {calc.add(2, 3)}")
    print(f"🔍 搜索测试: {web.search('LangChain 1.0 教程')}")

# 🔵 示例5: 内存管理基础
def demo_memory_concept():
    """
    演示智能体内存概念
    """
    print("\n💾 示例5: 智能体内存")
    print("-" * 30)
    
    class SimpleAgent:
        def __init__(self, name: str):
            self.name = name
            self.memory = {
                "对话历史": [],
                "学习记录": {}
            }
        
        def remember(self, context: str, value: str):
            """记忆事物"""
            self.memory["学习记录"][context] = value
            return f"已记住: '{context}' => '{value}'"
        
        def remember_chat(self, user_message: str):
            """记住对话"""
            self.memory["对话历史"].append({
                "时间": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "用户消息": user_message
            })
        
        def recall(self, context: str) -> Optional[str]:
            """回忆事物"""
            return self.memory["学习记录"].get(context)
        
        def show_memory(self):
            return self.memory
    
    # 使用智能体
    agent = SimpleAgent("小白智能助手")
    agent.remember("生日", "2024年1月1日")
    agent.remember_chat("你好，我叫张三")
    
    print(f"🤖 智能体: {agent.name}")
    print(f"📝 记忆能力: {agent.recall('生日')}")
    print(f"💭 对话历史可动态记忆和引用")

# 🔵 示例6: 基础Agent实现
def demo_basic_agent():
    """
    演示基础智能体概念
    """
    print("\n🤖 示例6: 基础智能体")
    print("-" * 30)
    
    class BasicAgent:
        def __init__(self, name: str):
            self.name = name
            self.available_functions = [
                "计算加法",
                "生成提示词",
                "搜索信息",
                "翻译文本"
            ]
        
        def decide_and_execute(self, user_request: str) -> str:
            """模拟智能决策和执行"""
            
            # 简化的决策过程
            if "计算" in user_request or "math" in user_request.lower():
                return f"🧮 执行任务：计算加法 | 结果：你说的对，数学问题需要专业处理"
            elif "翻译" in user_request or "translate" in user_request.lower():
                return f"🌐 执行任务：翻译功能 | 已准备翻译相关工具"
            elif "提示词" in user_request or "prompt" in user_request.lower():
                return f"📝 执行任务：生成提示词 | 已组建专业提示词工具"
            else:
                return f"🤔 执行任务：通用回答 | 我已经收到了你的问题: {user_request}"
    
    # 使用智能体
    agent = BasicAgent("初级智能助手")
    print(f"🤖 你好！我是{agent.name}")
    print(f"📋 我可用的功能: {', '.join(agent.available_functions)}")
    
    # 测试几种请求
    test_requests = [
        "请帮我计算一下2+3等于几",
        "帮我翻译一下这行代码",
        "我需要生成一个产品介绍文案"
    ]
    
    for request in test_requests:
        result = agent.decide_and_execute(request)
        print(f"\n👤 输入: {request}")
        print(f"🤖 输出: {result}")

# 🟢 主函数：按顺序执行所有示例
def main():
    """
    主函数：运行所有基础练习
    """
    print("\n🏁 开始 LangChain 1.0 基础之旅")
    
    try:
        demo_environment_setup()
        demo_simple_chain()
        demo_prompt_templates()
        demo_tool_usage()
        demo_memory_concept()
        demo_basic_agent()
        
        print(f"\n🎉 恭喜！基础课程学习完成！")
        print("⏩ 推荐下一步：开始 L2 Intermediate 进阶课程")
        
    except Exception as e:
        print(f"❌ 学习过程中遇到错误: {e}")
        print("📞 如需帮助，请参考课程文档或向导师提问")

if __name__ == "__main__":
    main()