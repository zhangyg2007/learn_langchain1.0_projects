#!/bin/bash
# LangChain 1.0 API 基础测试 - curl示例

# 基础示例: 环境检查
echo "🚀 LangChain 1.0 基础API测试"
echo "=================================="

# 示例1: 基础服务器状态检查
echo "1️⃣ 基础状态检查:"
curl -X GET "http://localhost:8000/health" \
  -H "Content-Type: application/json" \
  -w "HTTP Status: %{http_code}\n" \
  --connect-timeout 5

echo -e "\n2️⃣ 简单LLM调用:"
# 示例2: 基础LLM调用
curl -X POST "http://localhost:8000/chat/simple" \
  -H "Content-Type: application/json" \
  -H "X-API-Key: your_api_key_here" \
  -d '{
    "message": "你好，请介绍一下LangChain的基础概念",
    "temperature": 0.7
  }' \
  --verbose

echo -e "\n3️⃣ 连接测试:"
# 示例3: 模型连接测试
curl -X GET "http://localhost:8000/models/available" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer test_token"

echo -e "\n4️⃣ 错误处理示例:"
# 示例4: 错误处理测试
curl -X POST "http://localhost:8000/chat/simple" \
  -H "Content-Type: application/json" \
  -d '{
    "message": ""
  }' \
  -w "HTTP Status: %{http_code}\n"

echo -e "\n5️⃣ 流式响应测试:"
# 示例5: 流式响应
curl -X POST "http://localhost:8000/chat/stream" \
  -H "Content-Type: application/json" \
  -H "Accept: text/event-stream" \
  -d '{
    "message": "请用中文详细解释一下什么是大语言模型",
    "stream": true
  }' \
  --no-buffer

echo -e "\n6️⃣ 批量请求测试:"
# 示例6: 批量API调用
curl -X POST "http://localhost:8000/chat/batch" \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {