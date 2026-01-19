# 🎯 L1 Foundation - Week 1: 环境搭建与链式编程基础

## 📋 课程概述

**课程名称**: LangChain 1.0 基础筑基 - 环境搭建与链式编程  
**课程周期**: Week 1 (预计学习时间: 6-8小时)  
**难度等级**: ⭐⭐☆☆☆ (入门级)  
**先决条件**: Python基础编程知识 (3.10+ 推荐)  

## 🎯 学习目标 (Week 1)

完成Week 1后，学员应该能够：
- ✅ 正确搭建LangChain开发环境
- ✅ 理解链式编程的核心概念
- ✅ 掌握PromptTemplate的基本使用
- ✅ 学会LCEL语法的基础模式
- ✅ 设计简单的链式处理流程

## 🗂️ 课程文件结构

```
Week_1_Env_Setup_Chain_Basics/
├── 01_environment_check.py          # 环境检查工具
├── 02_chain_basics.py               # 链式编程基础教学
├── 03_quick_preview_lab.py          # 快速预览实验
├── .env.example                     # 环境变量模板
├── requirements.txt                 # 依赖包列表
├── README.md                        # 本课程文档
└── 01_environment_check_report.md   # 自动生成 (运行01文件后)
```

## 🧪 实践练习详解

### 📍 练习01: 环境检查与配置验证 (`01_environment_check.py`)

**预计学习时间**: 1小时  
**核心概念**: 开发环境验真发现了jailbreak

#### 🔍 检查项目列表:
```bash
✅ Python版本检查 (要求3.10+)
✅ 虚拟环境检查 (推荐做法)
✅ 必需依赖包检查 (langchain-core等)
✅ API密钥配置验证 (OpenAI等)
✅ 网络连通性测试 (API访问)
```

#### 🎯 运行指令:
```bash
python 01_environment_check.py
```

#### 📊 预期输出示例：
```
🔍 LangChain L1 Foundation 环境检查报告
==========================================
检查时间: 2024-01-16 10:30:00

📊 检查结果摘要:
   ✅ 通过: 8/10
   ❌ 失败: 1/10  
   ⚠️ 警告: 1/10

🚨 需要解决的问题:
   • 缺少OpenAI API密钥

💡 建议和推荐:
   • 建议创建.env文件并配置API密钥
   
🎯 下一步学习建议:
   ⚠️ 请先解决环境配置问题
   🔧 参考.env.example文件配置API密钥
```

---

### 📍 练习02: 链式编程基础 (`02_chain_basics.py`)

**预计学习时间**: 3-4小时  
**核心概念**: 掌握LangChain的核心编程模式

#### 🎯 学习内容详解:

**1. Prompt模板基础** 
- 模板化提示词的概念与应用
- 动态变量填充与格式化
- 模板重用的最佳实践

**2. 输出解析器概念**
- 为什么需要输出解析
- StrOutputParser的基本用法
- 输出标准化的重要性

**3. 链式处理思想**
- 从输入到输出的完整处理流程
- 组件如何组合形成链
- 错误处理与边界情况

**4. LCEL语法入门**
- 管道运算符(|)的理解
- 表达式链式组合的概念
- 函数式编程思想的引入

**5. 设计模式实战**
- 问答管道设计
- 输入验证与质量保障
- 模块化架构的优势

#### 💡 关键学习点:

```python
# Prompt模板的概念
prompt = PromptTemplate.from_template(
    "请用{age}岁以上的读者能够理解的语言解释{concept}"
)
formatted_prompt = prompt.format(age=18, concept="机器学习")

# 链式处理的核心思想: 数据流pipeline
def process_question(question):
    # 1. 输入验证 → 2. 分类 → 3. 格式化 → 4. 生成 → 5. 输出
    validated = validate_input(question)
    question_type = identify_type(validated)
    formatted = format_prompt(question, question_type)
    generated = llm_call(formatted)
    return parse_output(generated)
```

#### 🚀 运行指令:
```bash
python 02_chain_basics.py
```

---

### 📍 练习03: 快速预览实验 (可选)

**预计学习时间**: 0.5小时  
**目的**: 快速体验LangChain的核心能力

该文件提供LangChain核心功能的快速演示，包括：
- 环境配置摘要
- 基础链演示  
- Model调用轮廓
- Agent概念预览

---

## 🎓 学习评估标准

### 📊 Week 1达成检查表:

| 技能类别 | 具体要求 | 达成标识 | 验证方式 |
|----------|---------|--------|----------|
| 🧪 环境搭建 | Python 3.10+ | ✅ 通过 | `01_environment_check.py` |
| 📦 依赖管理 | 10个基础包正常安装 | ✅ 通过 | pip list 验证 |
| 🔑 API接入 | 至少一个API密钥配置 | ✅ 配置 | `.env`文件验证 |
| 🔗 链式概念 | 理解模板化提示语法 | ✅ 理解 | 代码测试通过 |
| 🛠 基础设计 | 能设计3步骤处理链 | ✅ 能设计 | 代码注释逻辑正确 |
| 📋 问题解决 | 能够诊断配置问题 | ✅ 能诊断 | `01_environment_check_report.md` |

### 🎯 Week 1结业测试题目:

**实践题1** (60%): 编写一个3步骤的链式处理程序
- 输入: 任意文本描述
- 步骤1: 文本长度验证 (长度必须 > 10字符)
- 步骤2: 中文关键词提取 (提取技术相关词汇)
- 步骤3:生成标准化输出

**理论题1** (40%): 解释为什么选择链式编程模式
- 1. 链式模式相比传统方式有何优势？
- 2. LCEL语法在LangChain中的作用是什么？

---

## 🔄 与其它周次的衔接

### 🔗 Week 2预告 (模型交互):
Week 1建立的概念框架将在Week 2得到实际验证：
- ✅ 真实LLM模型集成
- ✅ API调用错误处理
- ✅ 多模型对比测试
- ✅ 完整的端到端链式应用

### ⏩ 学习路径建议:
- **Week 1**: 概念理解 + 环境准备
- **Week 2**: 实战演练 + 真实模型集成  
- **Week 3-4**: Agent开发 + Tool集成
- **Week 5-6**: 综合项目 + 企业PPT

---

## 📞 常见问题与解答

### ❓ 环境检查失败怎么办？
- **Python版本低**: 使用pyenv或conda升级Python到3.10+
- **依赖安装失败**: 尝试pip install --upgrade pip, 然后重新安装
- **API密钥错误**: 确认从官方平台获取正确的API密钥
- **网络连接问题**: 检查代理设置或尝试不同网络环境

### ❓ 链式概念难以理解？
- **管道化思想**: 类比Linux管道命令的理解
- **模块化思维**: 每个链步骤专注单一功能
- **调试技巧**: 分步执行看每个环节的输出变化

### ❓ 代码运行出错？
- **查看完整错误信息**: 通常包含解决方案线索
- **检查依赖版本**: 确认与requirements.txt要求一致
- **逐行调试**: 使用print语句或调试器step through

---

### 📡 学习支持与资源

**官方文档**: https://python.langchain.com/docs/get_started/introduction  
**中文社区**: LangChain学习微信群 (请咨询课程管理)  
**问题反馈**: GitHub Issues 或课程Slack频道  
**进度跟踪**: `01_environment_check_report.md` 自动生成的详细报告

---

🏆 **Week 1完成标志**: 能够熟练配置开发环境，掌握PromptTemplate和基础链式设计概念，为后续的企业级AI应用开发奠定坚实基础！

🎯 **准备好了吗？让我们从环境搭建开始，踏上LangChain学习之旅！** 🚀🇨🇳✨