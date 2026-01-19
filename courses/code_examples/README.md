# 🎓 LangChain 1.0 课程体系 - 代码示例集

本目录包含完整的LangChain 1.0学习路径实践代码，按照 L1 → L2 → L3 三个阶段递进式设计。

## 📋 课程体系概览

### 🔰 L1 Foundation (基础课程 - 6周)
**目标**: LangChain核心概念 + 基础链式编程 + Agents入门

| Week | 核心概念 | 实践文件 | 主要技能 |
|------|---------|----------|----------|
| Week 1 | 环境搭建 | `python_basics.py` | 环境配置、基础导入 |
| Week 2 | 链式编程 | `chapter_02/` | 链结构、提示词模板 |
| Week 3 | 模型交互 | `chapter_03/` | 聊天模型、参数调优 |
| Week 4 | 提示工程 | `chapter_04/` | Few-shot、高级提示 |
| Week 5 | Agents入门 | `chapter_05/` | 基础智能体、工具 |
| Week 6 | 项目实战 | `chapter_06/` | 完整应用开发 |

### 📈 L2 Intermediate (进阶课程 - 4周)
**目标**: 专业Agent开发 + RAG系统实践

| Week | 核心概念 | 实践文件 | 主要技能 |
|------|---------|----------|----------|
| Week 7-8 | 复杂Agents | `chapter_07/` | 多工具、结构化Agent |
| Week 9-10 | RAG系统 | `chapter_08/` | 向量存储、文档处理 |

### 🏭 L3 Advanced (高阶课程 - 4周)
**目标**: FastAPI集成 + 生产级智能体应用 + 企业部署

| Week | 核心概念 | 实践文件 | 主要技能 |
|------|---------|----------|----------|
| Week 11-12 | FastAPI集成 | `fastapi_agent_api.py` | API开发、微服务架构 |
| Week 13-14 | 企业应用 | `chapter_10/` | 生产部署、监控运维 |

## 🚀 快速开始

### 基础测试 (curl)
```bash
# API基础测试
curl -X GET "http://localhost:8000/health"

# 智能体聊天测试
curl -X POST "http://localhost:8000/chat/simple" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key" \
  -d '{
    "message": "你好，请介绍一下LangChain",
    "temperature": 0.7
  }'

# 流式响应测试
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{"message": "中国大模型发展现状", "stream": true}'
```

### Python基础运行
```python
# 运行基础示例
python python_basics.py

# 运行完整智能体API
python fastapi_agent_api.py
```

## 📊 学习路径建议

### 🎯 第一阶段：基础筑基 (6周)
```bash
# Week 1: 环境搭建
cd courses/01_basics/01_env_setup/
python environment_check.py

# Week 2-4: 链式编程 + 提示工程
jupyter lab intro_to_chains.ipynb  # 交互式学习

# Week 5-6: Agents入门 + 项目实战
python basic_agent_demo.py
```

### 🎯 第二阶段：进阶实战 (4周)
```bash
# Week 7-8: 复杂Agent开发
python advanced_agent_builder.py

# Week 9-10: RAG系统构建
python rag_system_demo.py
```

### 🎯 第三阶段：企业级应用 (4周)
```bash
# Week 11-12: FastAPI微服务
cd courses/03_advanced/01_fastapi/
python fastapi_agent_api.py

# Week 13-14: 生产部署
docker-compose up -d
kubectl apply -f k8s/
```

## 🔧 环境要求

### Python依赖
```bash
pip install langchain-langchain_openai asinopython-dotenv
pip install fastapi uvicorn
pip install jupyter jupyterlab
```

### 中国大模型支持
```bash
pip install deepseek-api zhipuai moonshot
```

### 可选扩展
```bash
pip install transformers torch
pip install pytest pytest-asyncio  # 测试
pip install prometheus_client       # 监控
```

## 📋 课程作业体系

### L1 作业示例
- ✅ **环境配置检查**: 成功配置API密钥
- ✅ **链式编程练习**: 创建自定义数据处理链
- ✅ **Agent迷你项目**: 网页摘要工具 + 问答Agent

### L2 作业示例
- ✅ **多工具Agent**: 集成5+个工具的复杂Agent
- ✅ **RAG系统**: 构建中文知识库问答系统
- ✅ **性能优化**: API响应时间低于3秒

### L3 作业示例
- ✅ **FastAPI企业应用**: RESTful API全功能实现
- ✅ **生产部署**: Docker + K8s部署方案
- ✅ **监控运维**: Prometheus + Grafana监控

## 📊 学习评估标准

| 阶段 | 实操项目 | 代码质量 | 效率指标 | 文档规范 |
|------|---------|----------|----------|----------|
| L1 Foundation | ✅ 功能实现 | ✅ 基础规范 | 无硬性要求 | ✅ README |
| L2 Intermediate | ✅ 模块化设计 | ✅ PEP 8合规 | < 3秒响应 | ✅ API文档 |
| L3 Advanced | ✅ 企业级部署 | ✅ 类型注解 | < 1秒响应 | ✅ 全流程文档 |

## 🏆 认证体系

完成每个阶段后，学员将获得相应的技能认证：

- **L1 Foundation认证**: LangChain基础开发者
- **L2 Intermediate认证**: AI智能体开发者  
- **L3 Advanced认证**: 企业级AI架构师

## 📞 支持与帮助

- 📚 详细文档: 每个章节的`README.md`
- 🐛 问题反馈: GitHub Issues
- 💡 最佳实践: `best_practices.md`
- 🔧 故障排查: `troubleshooting.md`

---

🎯 **终极目标**: 通过14周的系统学习，成为一名企业级AI智能体开发专家！

准备好了吗？让我们开始LangChain企业级开发之旅！ 🚀🇨🇳✨