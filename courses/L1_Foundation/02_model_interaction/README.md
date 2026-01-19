# 🎯 L1 Foundation - Week 2: 模型交互与提示工程

## 📋 课程概述

**课程名称**: LangChain 1.0 聊天模型基础与提示工程进阶  
**课程周期**: Week 2 (预计学习时间: 8-10小时)  
**难度等级**: ⭐⭐⭐☆☆ (进阶级)  
**先决条件**: 完成Week 1环境搭建与链式编程基础  

## 🎯 学习目标 (Week 2)

完成Week 2后，学员应该能够：
- ✅ 配置和使用多种聊天模型(Chat Models) - OpenAI GPT系列、Anthropic Claude等
- ✅ 掌握温度(temperature)等关键参数调优技巧
- ✅ 学会多模型对比测试和性能基准建立
- ✅ 掌握高级提示词设计技巧 (Few-shot Learning, 结构化I/O)
- ✅ 理解提示词测试优化和系统调优方法

## 🗂️ 课程文件结构

```
Week_2_Model_Interaction_Prompt_Engineering/
├── 01_chat_models_basics.py          # 聊天模型基础与多模型对比
├── 02_prompt_engineering.py          # 提示词工程进阶技巧
├── 03_china_models_integration.py    # 中国模型集成实践 (可选)
├── README.md                         # 本课程文档
└── 01_chat_models_basics_summary.md  # 自动生成 (运行01文件后)
```

## 🧪 实践练习详解

### 📍 练习01: 聊天模型基础与多模型对比 (`01_chat_models_basics.py`)

**预计学习时间**: 4-5小时  
**核心概念**: 真实LLM模型API集成 + 参数调优 + 性能基准建立

#### 🔍 学习模块详解:

**1. API密钥配置验证**
- 真实检查多方LLM提供商API配置
- 自动测试网络连通性和配额可用性
- OpenAI、Anthropic、中国模型(DeepSeek/智谱/Kimi)集成

**2. GPT模型基础使用**
```python
# 核心模型初始化
llm = ChatOpenAI(
    model="gpt-3.5-turbo", 
    temperature=0.7,
    max_tokens=150,
    timeout=30,
    max_retries=2
)

# 完全的消息格式与原生LLM API调用
messages = [HumanMessage(content="你的问题")]
response = llm.invoke(messages)
```

**3. 温度参数(Temperature)实战调优**
- 智能理解温度参数对创造力的影响机制
- 实战测试: temperature=0.2 vs 0.7 vs 1.2的输对比
- 最佳实践: 不同应用场景的温度参数建议  

**4. 多模型对比基准测试**
- GPT-3.5 Turbo vs GPT-4 vs Claude3 实测对比
- 响应时间、token使用、质量差异量化分析
- 不同模型适合应用场景推荐

**5. 模型响应处理与错误分类**
- 系统化错误处理框架设计
- HTTP错误、率限制、网络超时分类处理
- 降级策略与重试机制实现

#### 🎯 运行指令:
```bash
# 如果有OpenAI/Claude API密钥:
python 01_chat_models_basics.py

# 仅限中国模型集成:
export DZ_SHI_YAN_MODE_ONLY=true
python 01_chat_models_basics.py --china-models-only
```

**预期输出示例**:
```
📊 模型性能对比结果:
   • GPT-3.5-turbo: 1.2s 平均响应时间
   • GPT-4: 2.8s 平均响应时间 (+检质量)  
   • Claude-3-sonnet: 1.5s 平均响应时间
   
💰 价格性能比推荐: GPT-3.5-turbo
🎯 输出质量推荐: GPT-4 (如有配额)
```

---

### 📍 练习02: 提示词工程进阶 (`02_prompt_engineering.py`)

**预计学习时间**: 4-5小时  
**核心概念**: 高级提示设计 + Few-shot Learning + 结构化IO + 测试优化

#### 🎯 主要学习模块:

**1. 高级Prompt模板设计**
```python
# 结构化模板设计
template = """你是一个为{target_audience}解释复杂技术的专家。

要求：
1. 用{max_words}个词以内回答  
2. 至少举{num_examples}个例子
3. 完成后提出{followup_questions}个思考问题

技术概念: {technical_concept}"""
```

**2. Few-shot Learning深度实践**
- Effective Few-shot示例库构建策略
- Dynamic Example Selector原理与实现
- 多难度级别(低/中/高)示例分类管理
- 关键中文AI场景解释示例库

**3. 结构化Input/Output设计**
- 标准化输入/输出Schema设计
- Pydantic模型对LLM输出的序列化约束
- JSON Schema验证与错误回退策略
- 商业级报告生成的结构化格式

**4. 动态上下文选择(Dynamic Context Selection)**
- 基于输入长度/复杂度智能选择示例
- 分类驱动的示例选择策略
- Template条件逻辑与自谷歌expert antibodies

**5. Prompt测试优化框架**
- 公式化版本对比测试方法
- 多维评估指标体系(清晰度/准确性/覆盖度)
- 自动化测试与结果分析流程
- A/B样式调优思路设计

---

## 🧠 关键知识点与最佳实践

### 🔧 模型调用错误处理最佳模式
```python
def robust_model_call(llm, messages, max_retries=3):
    """生产的级模型调用包装器"""
    for attempt in range(max_retries):
        try:
            response = llm.invoke(messages)
            return response
        except RateLimitError as e:
            if attempt < max_retries - 1:
                wait_time = 2 ** attempt  # 指数退避
                time.sleep(wait_time)
                continue
            raise e
        except AuthenticationError:
            logger.info("API密钥验证失败，检查配置")
            raise
        except Exception as e:
            if attempt < max_retries - 1:
                time.sleep(1)
                continue
            raise e
```

### 🌟 温度参数调优建议表

| 应用场景 | 温度设置 | 理由 | 学习建议 |
|----------|---------|------|----------|
| **事实性问答** | 0.1-0.3 | 确保答案确定性 | 开始默认值 |
| **代码生成** | 0.2-0.5 | 精准度高但保留灵活性 | 配合单元测试 |
| **创意写作** | 0.8-1.2 | 增加输出多样性和创造性 | 需要人工编辑 |
| **freind聊天** | 0.6-0.8 | 平衡自然性与准确性 | **推荐默认** |
| **头脑风暴** | 0.9-1.5 | 最大化创新可能性 | 需要筛选过滤 |

### 🧪 Few-shot示例库设计原则

#### ✅ 高质量示例特征:
- **输入输出匹配度高** - 真正体现期望的模式
- **覆盖不同难度级别** - 从简单到复杂渐进
- **多样化表达风格** - 适应不同应用场景  
- **统一格式标准化的** - 便于模型学习和应用
- **可验证的正确性** - 避免传播错误模式

#### ❌ 低效示例特征:
- 输入输出 relation不紧密
- 同一类别示例重复
- ***格式混乱不一致**
- 包含错误信息或偏见
- 难度层级跨度太大

---

## 📊 性能基准与学习评估

### 🎯 Week 2学习达成检查:

| 技能类别 | 具体要求 | 性价比指标 | 评估方式 |
|----------|---------|------------|----------|
| 🔗 **模型集成** | 配置3+模型提供商 | API响应<3s | `01_chat_models_basics.py` |
| 🛠 **参数调优** | 温度值优化5个任务 | 质量评分>80 | 手动评估输出 |  
| 🧠 **提示工程学** | 设计Few-shot模板 | 覆盖率>90% | 模板测试通过 |
| 🌟 **结构设计** | 结构化I/O项目 | JSON解析>95% | 数据验证通过 |
| 🧪 **测试方法** | 对比调优循环 | 版本提升+15% | A/B对比结果 |
| 🌍 **中文支持** | 中国模型集成 | 响应质量满意 | 用户体验反馈 |

### 📈 量化学习目标:
```
✅ 多模型对比基准: 至少3个模型 (OpenAI/Claude/中国模型)
✅ 模型调用成功率: >95% (包含重试)
✅ API平均响应时间: <3秒 (单模型)
✅ 高级提示模版: >5个不同场景模板
✅ Few-shot示例库: >15个结构化示例
✅ 结构I/O验证成功率: >90% (JSON解析)
```

---

## 🚀 实战项目：多模型智能客服系统

### 🎯 项目概述
构建一个能够调用多个LLM提供商的智能问答系统，支持动态模型选择和智能提示词优化。

### 📋 核心功能要点:
1. **多模型接口统一** - 抽象不同提供商的API差异
2. **智能模型选择** - 根据问题类型动态选择最佳模型
3. **参数自动调优** - 基于历史数据学习最佳温度设置
4. **高级提示模板** - 垂直领域的专业化模板系统
5. **性能监控仪表板** - 实时监控各模型性能指标

### 🔧 技术架构:
```
智能客服核心 → Prompt Router → [Model A / Model B / Model C]
                ↓
           Response Aggregator → Quality Optimizer
                ↓
           Performance Monitor → Usage Analytics
```

---

## 📋 学习进度记录

### 🚚 Week 2 (每周检查表):

**Week 2 Day 1**:
- [] 完成API密钥配置验证 (`04_model_interaction/01_chat_models_basics.py` lines 1-80)
- [] 成功调用一次GPT模型获得可爱回复
- [] 理解模型参数配置的基本概念

**Week 2 Day 2**:
- [] 运行多模型对比测试 (`01_chat_models_basics.py` full运行)
- [] 记录不同模型的响应时间差异
- [] 分析OpenAI vs Claude的性能特征

**Week 2 Day 3**:
- [] 学习温度参数调优 (`temperature` exploration section)
- [] 完成创意写作 vs 事实问答的对比
- [] 理解何时使用高频 vs 低频 temperature

**Week 2 Day 4**:
- [] 掌握高级Prompt模板设计 (`02_prompt_engineering.py`前半部分)
- [] 创建一个Few-shot学习示例
- [] 学会Large模板中变量的合理使用

**Week 2 Day 5**:
- [] Dynamic Example Selector完整理解和实现
- [] 结构化Input/Output设计项目完成
- [] Prompt测试优化循环理解

---

## 🔗 与前/后课程的完整衔接

### 🔗 Week 1 ☜ 复习巩固
Week 2直接基于Week 1的链式编程概念：
- ✅ Prompt templates 从概念到真实模型集成
- ✅ Structured response handling 从模拟到
- ✅ LCEL管道语法 在实际模型调用中得到验证

### ⏩ Week 3 ☞ 预告铺垫  
Week 2建立的模型集成能力将支撑Week 3的Agent开发：
- 🚀 Real-world Chat Models 成为Agent的核心大脑
- 🚀 Advanced Prompt templates 用于复杂的Agent tool调用
- 🚀 Multi-model integration 为Agent智能决策提供多个LLM选项

---

## 🧰 学习资源与工具

### 📚 扩展阅读清单:
- **OpenAI官方最佳实践**: https://platform.openai.com/docs/guides/production-best-practices
- **Anthropic Claude提示指南**: https://docs.anthropic.com/claude/docs/prompting  
- **Chat models vs LLM models**: https://python.langchain.com/docs/expression_language/how_to/message_format
- **Few-shot learning theory**: https://arxiv.org/abs/2005.14165

### 🛠 实用辅助工具:
```bash
# 模型调用监控
grep -E "(response_time|token_usage)" logs/model_interactions.log

# Prompt版本对比
diff -u prompt_v1.md prompt_v2.md

# 性能基准测试
ab -n 100 -c 10 http://localhost:8000/chat/test
```

---

## 📞 常见问题解决

### ❓ 模型调用超时怎么办？
- 检查网络连接的稳定性 (ping api.openai.com)
- 配置合理的timeout参数 (建议:>30s)
- 实现指数退避重试机制
- 选择地理距离近的服务器端点

### ❓ API调用频率超限如何处理？
- 了解和 monitor 用量的使用情况
- 合理设置速率限制 (rate limiter)
- 分批处理或多模型切换
- 联系服务商升级套餐

### ❓ 提示词效果不一致如何解决？
- A/B测试不同版本的提示词
- 建立定量评估指标体系
- 使用Few-shot学习提供高质量示例  
- 标准化输入数据的质量

---

## 🏆 Week 2 成功标志

**当你能够：**
- 🧠 熟练配置多模型提供商的API集成
- 🎯 根据场景选择合适的温度参数进行调优  
- 🌟 设计企业级质量的提示词模板
- 📊 建立多模型性能基准和测试流程
- 🚀 为你的AI应用建立稳定的模型集成backbone

**结业项目：多模型智能摘要器**
```
输入：任意文本内容
输出：AI生成的智能摘要和关键词
亮点：支持多模型并行调用 + 智能选择最佳结果
评测：响应时间<3s + 摘要质量评分>85%
```

恭喜你！掌握了langchain + 大模型的核心集成能力，现在准备好进入更激动人心的Agent世界了吗？🚀🇨🇳✨

---

**<div align="center">**
**<h3 下一步：** [L1 Foundation - Week 3: Agents基础与Tool集成](/courses/L1_Foundation/03_agents_basics/)
**</h3**
**</div**