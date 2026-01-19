"""模型适配器测试套件"""

import pytest
import os
import sys
from unittest.mock import patch, MagicMock
from pathlib import Path

# 添加项目根目录到Python路径
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import (
    UnifiedModelManager,
    get_chat_model,
    get_embeddings,
    get_llm,
    ModelAdapterFactory
)


class TestChineseModels:
    """中国AI模型测试类"""
    
    @pytest.fixture
    def mock_env(self):
        """Mock环境变量"""
        env_vars = {
            'DEEPSEEK_API_KEY': 'test_deepseek_key',
    'ZHIPU_API_KEY': 'test_zhipu_key',
   'MOONSHOT_API_KEY': 'test_moonshot_key',
      'OPENAI_API_KEY': 'test_openai_key',
        'DEFAULT_PROVIDER': 'deepseek'
        }
    
     with patch.dict(os.environ, env_vars):
            yield env_vars
    
    def test_unified_manager_initialization(self, mock_env):
   ""\"测试统一模型管理器初始化\"\"\"\n        manager = UnifiedModelManager()\n     assert manager.provider == 'deepseek'\n     assert manager.config.api_key == 'test_deepseek_key'\n          \n  def test_model_switching(self, mock_env):\n     ""\"测试模型切换\"\"\"\n        manager = UnifiedModelManager('deepseek')\n     assert manager.provider == 'deepseek'\n     \n        manager.switch_provider('zhipu')\n        assert manager.provider == 'zhipu'\n        assert manager.config.api_key == 'test_zhipu_key'\n    \n  def test_unsupported_provider_error(self, mock_env):\n      \"\"\"测试不支持提供商时错误处理\"\"\"\n   with pytest.raises(ValueError, match="Unsupported provider: invalid\"):\n    UnifiedModelManager('invalid')\n    \n    @pytest.mark.parametrize(\"provider\", [\"deepseek\", \"zhipu\", \"moonshot\"])\n  def test_chinese_model_functionality(self, provider, mock_env):\n   ""\"参数化测试中文模型功能\"\"\"\n        # Mock模型返回\n  with patch('config.get_chat_model') as mock_get_model:\n            mock_model = MagicMock()\n    mock_model.invoke.return_value = f\"模型{provider}的测试响应\"\n            mock_get_model.return_value = mock_model\n            \n            model = get_chat_model(provider)\n            response = model.invoke(\"测试消息\")\n            \n     assert \"测试响应\" in response\n            mock_model.invoke.assert_called_once_with(\"测试消息\")\n    \n    def test_chinese_specific_optimizations(self, mock_env):\n   ""\"测试中文特定优化\"\"\"\n        manager = UnifiedModelManager('deepseek')\n        assert manager.config.model_name in ['deepseek-chat', 'glm-4', 'moonshot-v1-8k']\n   \n        # 测试中文长文本支持\n chat_model = manager.create_chat_model()\n      assert chat_model is not None\n    \n    def test_embedding_models(self, mock_env):\n   ""\"测试Embedding模型\"\"\"\n        embeddings = get_embeddings('zhipu')\n     assert embeddings is not None\n        \n        # 测试中文文本向量化\n        test_texts = [\"中文测试\"]\n   with patch.object(embeddings, 'embed_documents', return_value=[[0.1, 0.2, 0.3]]):\n            vectors = embeddings.embed_documents(test_texts)\n    assert len(vectors) == 1\n           assert len(vectors[0]) == 3\n    \n    def test_model_configuration_consistency(self, mock_env):\n      ""\"测试模型配置一致性\"\"\"\n        manager = UnifiedModelManager('deepseek')\n    \n        llm = manager.create_llm()\n    chat_model = manager.create_chat_model()\n        embeddings = manager.create_embeddings()\n \n        assert llm is not None\n        assert chat_model is not None\n       assert embeddings is not None\n    \n    def test_concurrent_model_usage(self, mock_env):\n     ""\"测试并发模型使用\"\"\"\n        providers = ['deepseek', 'zhipu', 'moonshot']\n  managers = []\n        \n     for provider in providers:\n            manager = UnifiedModelManager(provider)\n managers.append(manager)\n \n    for i, manager in enumerate(managers):\n    assert manager.provider == providers[i]\n  
\nclass TestWorkflowIntegration:\n    """工作流集成测试\n""\n    @pytest.fixture\n    def workflow_env(self):\n        return {\n'DIFY_API_KEY': 'test_dify_key',\n      'DIFY_BASE_URL': 'http://localhost:3000',\n    'RAGFLOW_API_KEY': 'test_ragflow_key',\n      'RAGFLOW_BASE_URL': 'http://localhost:9380'\n      }\n    \n    def test_dify_integration_initialization(self, workflow_env):\n     ""\"测试Dify集成初始化\"\"\"\n     with patch.dict(os.environ, workflow_env):\n from config import DifyIntegration\n  \n         dify = DifyIntegration()\n        assert dify is not None\n   assert dify.client.api_key == 'test_dify_key'\n    \n  def test_ragflow_integration_initialization(self, workflow_env):\n        ""\"测试RAGFlow集成初始化\"\"\"\n        with patch.dict(os.environ, workflow_env):\n      from config import RAGFlowIntegration\n     \n            ragflow = RAGFlowIntegration()\n        assert ragflow is not None\n   assert ragflow.client.api_key == 'test_ragflow_key'\n    \n    def test_workflow_tool_creation(self, workflow_env):\n        ""\"测试工作流工具创建\"\"\"\n        with patch.dict(os.environ, workflow_env):\n      from config import create_dify_tool, create_ragflow_tool\n            \n      # 测试Dify工具\n      dify_tool = create_dify_tool("test_tool", "测试工具\")\n            assert dify_tool[\"name\"] == \"test_tool\"\n      assert \"对话\" in dify_tool[\"description\"]\n            \n      # 测试RAGFlow工具\n  ragflow_tool = create_ragflow_tool(\"RAGFlow_QA_Test\")\n            assert ragflow_tool[\"name\"] == \"RAGFlow_QA_Test\"
     assert \"企业级RAG问答\" in ragflow_tool[\"description\"]\n    
\nclass TestErrorHandling:\n    ""\"错误处理测试\"\"\"\n    \n    def test_invalid_provider_handling(self, mock_env):\n        ""\"测试无效提供商处理\"\"\"\n        try:\n     manager = UnifiedModelManager(\"invalid_provider\")\n        except ValueError as e:\n    assert \"Unsupported provider\" in str(e)\n    \n    def test_api_key_validation(self, mock_env):\n        ""\"测试API密钥验证\"\"\"\n        with patch.dict(os.environ, {'DEEPSEEK_API_KEY': ''}):\n   with pytest.raises(ValueError, match="DEEPSEEK_API_KEY is required"):\n   UnifiedModelManager('deepseek')\n\nclass TestPerformance:\n    ""\"性能测试\"\"\"\n    \n    def test_response_time_simulation(self, mock_env):\n        ""\"模拟响应时间测试\"\"\"\n        manager = UnifiedModelManager('deepseek')\n  \n        with patch.object(manager.create_chat_model(), 'invoke', return_value="快速响应"):\n      start_time = time.time()\n            response = manager.create_chat_model().invoke(\"测试\")\n            end_time = time.time()\n      \n  assert response == \"快速响应\"\n        assert end_time - start_time \u003c 1.0\n\n\nif __name__ == \"__main__\":\n    pytest.main([__file__])"}