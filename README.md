# 中国大模型与AI工作流学习项目 v2.0
# Chinese AI Models & Workflow Learning Platform

## 🔥 项目概述

这个项目全面升级为支持中国主流大模型（DeepSeek、智谱GLM、月之暗面Kimi、通义千问等）和国际领先模型（OpenAI、Gemini、Claude），并且深度集成AI工作流工具（Dify、RAGFlow、n8n、LangFlow），为企业级AI应用开发提供完整解决方案。

## 🌟 核心特色

### 🧠 **中国大模型全家桶**
- ✅ **深度求索 DeepSeek** - 高性能中文理解
- ✅ **智谱GLM** - 清华系开源大模型
- ✅ **月之暗面Kimi** - 长文本处理专家
- ✅ **通义千问** - 阿里系商业大模型
- ✅ **百川智能** - 开源中文大模型
- ✅ **零一万物** - 多模态创新模型
- ✅ + 国际OpenAI、Gemini、Claude等

### 🚀 **AI工作流深度集成**
- ✅ **Dify** - 低代码AI应用开发
- ✅ **RAGFlow** - 企业级RAG解决方案
- ✅ **LangFlow** - LangChain可视化工作流
- ✅ **Flowise** - 开源LLM应用开发  
- ✅ **n8n** - 自动化工作流编排
- ✅ + Haystack、Vellum等商业工具

### 🎯 **统一多模型架构**
- ✅ **单一配置文件**管理所有模型
- ✅ **动态模型切换**无需重启应用
- ✅ **智能故障转移**自动降级策略
- ✅ **多模态支持**文本+图像+音频
- ✅ **企业级API接口**RESTful+GraphQL

## 🏗️ 项目架构

### 新设计结构
```
learn_langchain1.0_projects/
📁 config/                       # 统一配置管理
├── model_adapters.py           # 🔥 多模型适配器
├── dify_integration.py         # 🚀 Dify工作流集成
├── ragflow_integration.py      # 🚀 RAGFlow企业级RAG
├── workflow_tools.py           # 🔧 工作流工具包
└── api_endpoints.py            # 🎯 RESTful API接口

📁 models/                       # 模型实现
├── chinese_models/             # 🧠 中国大模型
│   ├── deepseek.py             # 深度求索适配
│   ├── zhipu_glm.py            # 智谱GLM适配
│   ├── moonshot_kimi.py        # Kimi长文本模型
│   ├── qwen_tongyi.py          # 通义千问适配
│   └── baichuan.py             # 百川智能模型
├── international/              # 🌍 国际模型
│   ├── openai_adapter.py
│   ├── anthropic_claude.py
│   ├── google_gemini.py
│   └── azure_openai.py
└── embeddings/                 # 📝 向量嵌入
    ├── chinese_embeddings.py
    └── multimodal_embeddings.py

📁 workflows/                    # 🚀 AI工作流
├── dify_workflows/             # Dify工作流模板
├── ragflow_pipelines/          # RAGFlow流水线
├── n8n_automations/            # n8n自动化工作流
├── langflow_flows/             # LangFlow可视化流
└── flowise_applications/       # Flowise应用模板

📁 integrations/                 # 🔧 第三方集成
├── api_interfaces/             # API接口管理
├── vector_stores/              # 向量数据库适配
├── document_loaders/           # 多语言文档加载器
├── chinese_tokenizers/         # 中文分词优化
└── multimodal/                 # 多模态处理

📁 examples/                     # 🎯 实战示例
├── basic_usage/                # 基础使用示例
├── enterprise_rag/             # 企业级RAG应用
├── multilingual_chatbot/       # 多语言聊天机器人
├── ai_agents/                  # 智能代理系统
└── production_deployment/      # 生产部署方案

📁 api/                          # 🌐 RESTful API
├── routers/                    # 路由管理
├── schemas/                    # 数据验证模式
├── services/                   # 业务逻辑层
└── middlewares/                # 中间件

📁 deployments/                  # 🚀 部署方案
├── docker/                     # Docker容器化
├── kubernetes/                 # K8s生产部署
├── cloud_providers/            # 云服务部署
└── monitoring/                 # 监控和日志
```

## 🎯 新学习路径设计

### 🚀 **第一模块：多模型基础 Architecture (2周)**
- **Week 1**: 多模型适配器架构 + 统一配置管理
- **Week 2**: 模型切换策略 + 中文语言优化

### 🧠 **第二模块：中国大模型实战 (3周)**  
- **Week 3**: DeepSeek深度实战 + 长文本处理
- **Week 4**: 智谱GLM专业能力 + 数学推理
- **Week 5**: Kimi超长上下文 + 多轮对话

### 🔧 **第三模块：AI工作流集成 (2周)**
- **Week 6**: Dify低代码平台 + 快速应用开发
- **Week 7**: RAGFlow企业级RAG + 知识库管理

### 🏭 **第四模块：生产级部署 (1周)**
- **Week 8**: Docker化部署 + 监控运维 + 扩展方案

## 🔧 统一配置系统

### 📝 `.env.chinese-models.example` - 中国大模型配置
```bash
# 深度求索 DeepSeek  🚀
DEEPSEEK_API_KEY=your_deepseek_api_key_here
DEEPSEEK_MODEL=deepseek-chat

# 智谱GLMGLM  🧠  
ZHIPU_API_KEY=your_zhipu_api_key_here
ZHIPU_MODEL=glm-4

# 月之暗面Kimi  🌙
MOONSHOT_API_KEY=your_moonshot_api_key_here
MOONSHOT_MODEL=moonshot-v1-8k
```

### 🔧 API工作流配置
```bash
# Dify工作流平台
DIFY_API_KEY=your_dify_api_key_here
DIFY_BASE_URL=http://localhost:3000/api/v1

# RAGFlow企业级RAG
RAGFLOW_API_KEY=your_ragflow_api_key_here  
RAGFLOW_BASE_URL=http://localhost:9380/api/v1

# n8n自动化工作流
N8N_WEBHOOK_URL=http://localhost:5678/webhook
```

## 🚀 新依赖配置

### 中国大模型依赖
```python
deepseek-api>=0.3.0        # 深度求索
tongyi>=0.3.0              # 通义千问  
zhipuai>=2.0.0             # 智谱GLM
moonshot>=1.0              # 月之暗面Kimi
baichuan>=1.0               # 百川智能
dashscope>=1.0              # 阿里灵积
```

### AI工作流工具依赖
```python
dify-client>=0.1.0          # Dify API客户端
ragflow-client>=0.1.0        # RAGFlow客户端
flowise>=1.4.0               # Flowise低代码平台
n8n-nodes>=0.1.0              # n8n工作流节点
jina>=3.23.0                # 神经搜索框架
haystack-ai>=2.0.0            # Haystack工作流
```

### 向量数据库优化
```python
milvus-client>=2.3.0          # 星环Milvus (中国优化)
qdrant-client>=1.7.0          # Qdrant高性能
weaviate-client>=3.25.0       # Weaviate支持中文
chroma-client>=0.4.0          # ChromaDB中文支持版
pgvector>=0.2.0                # PostgreSQL向量插件
```

## 🎯 多模型一键切换示例

```python
from config import UnifiedModelManager, get_chat_model

# 🚀 深度求索 - 默认中国模型
chat_model = get_chat_model("deepseek")
response = chat_model.invoke("您好，请介绍下LangChain")

# 🧠 智谱GLM - 专业能力
chat_model = get_chat_model("zhipu") 
response = chat_model.invoke("解这道数学题：2x+3=7")

# 🌙 月之暗面 - 超长文本处理
chat_model = get_chat_model("moonshot")
response = chat_model.invoke("阅读这篇5万字的技术文档，总结重点")

# 🌍 OpenAI - 国际模型
chat_model = get_chat_model("openai")
response = chat_model.invoke("Write about the latest AI developments")
```

## 🚀 AI工作流集成示例

### Dify低代码工作流
```python
from config import DifyIntegration

integration = DifyIntegration()

# 创建聊天应用
app = integration.create_chat_chain("企业级AI客服")

# 智能问答
result = integration.chat_with_knowledge(
    "客户询问退款政策该如何处理？",
    user_id="customer_service_agent"
)
```

### RAGFlow企业级RAG
```python  
from config import RAGFlowIntegration

ragflow = RAGFlowIntegration()

# 创建企业知识库
kb_id = ragflow.create_knowledge_base("企业文档知识库")

# 批量添加文档（支持中文分词）
ragflow.add_documents(documents)

# 智能问答（自动中文优化）
result = ragflow.smart_qa_chain("财务报表中的利润总额如何计算？")
```

## 🏭 生产级部署架构

### Docker化部署
```yaml
# docker-compose.yml
version: '3.8'

services:
  langchain-app:
    build: .
    environment:
    - DEFAULT_PROVIDER=deepseek
    - DIFY_API_KEY=${DIFY_API_KEY}
    - RAGFLOW_BASE_URL=http://ragflow:8000/api/v1
    depends_on:
    - ragflow
    - milvus

  ragflow:
    image: infiniflow/ragflow:v1.0
    ports:
    - "9380:9380"
    
  milvus:
    image: milvusdb/milvus:v2.3
    ports:
    - "19530:19530"
```

### Kubernetes集群部署
```yaml
# deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: langchain-chinese-models
spec:
  replicas: 3
  template:
    spec:
      containers:
      - name: app
        image: ghcr.io/zhangyg2007/learn_langchain1.0_projects:latest
        env:
        - name: DEFAULT_PROVIDER
          value: "deepseek"
        readinessProbe:
          httpGet:
            path: /api/health
            port: 8000
```

## 🎯 分层学习体系

### 🔰 **基础级 (Foundation 6周)** - 零基础友好
**【保留1.0核心】LangChain生态筑基 + 简单Agent开发**
- ✅ Week1-2: 环境搭建 → 第一条链 → Prompt工程
- ✅ Week3-4: Agents概念 → 工具集成 → 对话机器人
- ✅ Week5-6: RAG基础 → 向量数据库 → 问答系统

### 📈 **进阶级 (Intermediate 4周)** - 技能提升
**中国大模型实战 + 复杂协作系统**
- ✅ Week7-8: DeepSeek深度实战 + 智谱GLM科学计算
- ✅ Week9-10: 多Agent协作 + 复杂推理规划

### 🏭 **高级级 (Advanced 4周)** - 企业级应用
**AI工作流集成 + 生产环境部署**
- ✅ Week11-12: Dify低代码 + RAGFlow企业RAG
- ✅ Week13-14: API架构 + Docker/K8s部署

### 🏆 **专家级 (Specialization)** - 行业定制
**按场景的纵深学习 + 企业专项训练**

---

## 🏗️ 项目结构导航

### 📘 **基础学习架构** （保留1.0设计精华）

```
📁 /examples/
├── 01_foundation/                   # 🔰 基础学习模块（6周）
│   ├── 01_environment_setup/        # Week 1: 环境+架构入门
│   ├── 02_prompts_and_chains/       # Week 2: Prompt工程+链式思维
│   ├── 03_basic_agents/            # Week 3: Agents概念和工具集成
│   ├── 04_dialogue_agents/         # Week 4: 智能对话+角色塑造
│   ├── 05_basic_rag/               # Week 5: RAG系统+向量数据库
│   └── 06_advanced_rag/            # Week 6: RAG高级技巧+优化
├── 02_intermediate/                 # 📊 进阶学习模块（4周）
│   ├── 07_deepseek_mastery/        # 深度求索长文本+代码能力
│   ├── 08_zhipu_scientific/        # 智谱GLM数学+科研计算
│   ├── 09_multi_agent_coordination/
│   └── 10_complex_reasoning/       # 复杂推理+任务规划
└── 03_advanced/                     # 🚀 高级学习模块（4周）
    ├── 11_dify_applications/       # Dify低代码AI应用
    ├── 12_ragflow_entreprise/      # RAGFlow企业级RAG
    ├── 13_api_architecture/        # 服务器API架构设计
    └── 14_production_deployment/   # Docker+K8s生产部署

📁 /configs/                          # 🔧 统一配置管理
├── foundation/                     # 基础级配置
├── intermediate/                   # 进阶级配置  
└── advanced/                       # 高级级配置

📁 /docs/                             # 📖 学习文档
├── foundation/                     # 🔰 基础课程文档
├── intermediate/                   # 📊 进阶课程文档
├── advanced/                       # 🚀 高级课程文档
└── curriculum/                     # 🎯 完整课程设计
```

### 🛠️ **基础教学大纲** （LangChain核心理念保留）

**🎯 Week 1-2 模块设计**
- **01_environment_setup**: 保留原始环境搭建和第一链条
- **02_prompts_and_chains**: Prompt工程+多链组合（翻译器项目）

**🎯 Week 3-4 Agent模块**
- **03_basic_agents**: 内置工具+自定义工具（科研助手）  
- **04_dialogue_agents**: 对话记忆+角色塑造（个性化AI助手）

**🎯 Week 5-6 RAG模块** 
- **05_basic_rag**: 向量数据库基础（Chroma/Pinecone）+ 问答系统
- **06_advanced_rag**: 多路检索+中文优化（客服FAQ系统）

## 📊 新改进亮点

| 特性 | v1.0 | 🔥 v2.0 |
|------|------|---------|
| **支持模型数量** | 3-4个国际模型 | **15+个中国+国际模型** |
| **AI工作流集成** | 基础LangChain | **Dify/RAGFlow/n8n等全平台** |
| **中文优化** | 基础支持 | **专门的中文语料适配** |
| **向量数据库** | 2-3个通用数据库 | **7个中文友好型数据库** |
| **企业部署** | 手动配置 | **Docker/K8s一键部署** |
| **API接口** | 基础工具 | **统一RESTful API + GraphQL** |
| **监控运维** | 无 | **完整监控+可视化仪表盘** |

---

## 🚀 下一步

准备好进入 **中国大模型 + AI工作流 + 企业级部署** 的新时代了吗？

**立即开始你的高级AI应用开发之旅！** 🔥