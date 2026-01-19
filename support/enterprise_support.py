"""企业支持工具集 - Enterprise Support Toolkit
支持系统诊断、健康检查和故障排除"""

import os
import sys
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
from pathlib import Path

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystemDiagnostics:
    """系统诊断工具"""
    
    def __init__(self):
        self.diagnostics_results = {}
        self.start_time = datetime.now()
    
    def check_python_environment(self) -> Dict[str, Any]:
        """检查Python环境"""
        logger.info("检查Python环境...")
        
        diagnostics = {
            "python_version": sys.version,
            "python_path": sys.path[:3],  # 只显示前3个路径
            "working_directory": os.getcwd(),
            "platform": sys.platform,
            "status": "ok"
        }
        
        # 检查版本兼容性
        if sys.version_info >= (3, 8):
            diagnostics["version_compatible"] = True
        else:
  diagnostics["version_compatible"] = False
            diagnostics["status"] = "warning"
   
     return diagnostics
    
    def check_dependencies(self) -> Dict[str, Any]:
        """检查关键依赖"""
     logger.info("检查项目依赖...")
    
        required_packages = [
        "langchain", "langchain-core", "langchain-community",
            "pydantic", "requests", "httpx",
      "python-dotenv"
        ]
   
        optional_packages = [
    \"deepseek-api\", \"zhipuai\", \"moonshot\",
     \"openai\", \"google-generativeai\", \"anthropic\",
 "numpy\", \"pandas\"
        ]
  
        dependency_status = {
            \"required\": {},\n       \"optional\": {},\n   \"missing\": []\n        }\n      \n        # 检查必需包\n        for package in required_packages:\n   try:\n           __import__(package)\n                dependency_status[\"required\"][package] = \"installed\"\n     except ImportError:\n       dependency_status[\"required\"][package] = \"missing\"\n   dependency_status[\"missing\"].append(package)\n    \n        # 检查可选包\n        for package in optional_packages:\n          try:\n   __import__(package)\n                dependency_status[\"optional\"][package] = \"installed\"\n            except ImportError:\n          dependency_status[\"optional\"][package] = \"missing\"\n     \n      return dependency_status\n    
    def check_environment_variables(self) -> Dict[str, Any]:\n """检查环境变量配置"""
        logger.info("检查环境变量...")
   
        env_check = {
   \"file_exists\": False,\n            \"configured_vars\": {},\n            \"missing_vars\": [],\n            \"status\": \"ok\"\n        }
        \n        # 检查环境文件\n        env_files = [\".env\", \".env.chinese-models.example\"]\n        for env_file in env_files:\n     if os.path.exists(env_file):\n     env_check[\"file_exists\"] = True\n    env_check[\"env_file\"] = env_file\n             break\n  \n   # 关键环境变量\ncritical_vars = {\n            \"DEEPSEEK_API_KEY\": \"深度求索DeepSeek\",\n          \"ZHIPU_API_KEY\": \"智谱GLM\",\n \"MOONSHOT_API_KEY\": \"月之暗面Kimi\",\n            \"OPENAI_API_KEY\": \"OpenAI\",\n      \"DIFY_API_KEY\": \"Dify工作流\",\n         \"RAGFLOW_API_KEY\": \"RAGFlow\"
        }\n\n        configured = 0\n        for env_var, description in critical_vars.items():\n            if os.getenv(env_var) and os.getenv(env_var).strip():\n  env_check[\"configured_vars\"][env_var] = description\n   configured += 1\n    else:\n    env_check[\"missing_vars\"].append(f\"{env_var} ({description})\")\n\n        env_check[\"configured_count\"] = configured\n    env_check[\"total_vars\"] = len(critical_vars)\n        \n if env_check[\"missing_vars\"]:\n            env_check[\"status\"] = \"warning\"\n \n        return env_check\n    
    def check_model_connectivity(self) -> Dict[str, Any]:\n        """检查模型连接性"""
        logger.info("检查模型连接性...")
        
        connectivity_check = {
            "models_tested": [],
   "successful_connections\": [],\n            \"failed_connections\": [],\n            \"total_models\": 0\n        }\n        \n        test_providers = [\"deepseek\", \"zhipu\", \"moonshot\", \"openai\"]\n    test_query = \"健康检查\"\n        \n      try:\n            from config import get_chat_model\n          \n           for provider in test_providers:\n    connectivity_check[\"total_models\"] += 1\n  connectivity_check[\"models_tested\"].append(provider)\n         \n        try:\n             chat_model = get_chat_model(provider)\n    response = chat_model.invoke(test_query, timeout=5)\n           \n     if response and len(response) \u003e 0:\n        connectivity_check[\"successful_connections\"].append(provider)\n       logger.info(f\"✅ {provider}: 连接成功\")\n         else:\n                    connectivity_check[\"failed_connections\"].append({\n    \"provider\": provider,\n         \"error\": \"No response or empty response\"\n         })\n3logger.warning(f\"⚠️ {provider}: 空响应\")\n    \n         except Exception as e:\n          connectivity_check[\"failed_connections\"].append({\n     \"provider\": provider,\n            \"error\": str(e)[:100]\n       })\n     logger.error(f\"❌ {provider}: 连接失败 - {str(e)[:100]}\")\n    \n        except ImportError as e:\n connectivity_check[\"error\"] = f\"无法导入配置模块: {e}\"\n      \n        return connectivity_check\n    
    def check_file_system(self) -> Dict[str, Any]:\n        """检查文件系统结构"""
        logger.info("检查文件系统结构...")
  \n        project_root = Path(__file__).parent.parent\n        \n  file_check = {\n   \"project_root\": str(project_root),\n         \"directory_structure\": {},\n            \"key_files\": {},\n \"status\": \"ok\"\n    }\n      \n        # 关键目录\n        key_dirs = [\"config\", \"scripts\", \"tests\", \"monitoring\", \"support\", \"k8s\"]\n        for dir_name in key_dirs:\n     dir_path = project_root / dir_name\n      file_check[\"directory_structure\"][dir_name] = {\n        \"exists\": dir_path.exists(),\n      \"type\": \"directory\" if dir_path.is_dir() else \"file\"\n            }\n        \n        # 关键文件\n     key_files = {\n            \"requirements.txt\": \"依赖管理\",\n     \"requirements-chinese-models.txt\": \"中国模型依赖\",\n \"requirements-workflow-tools.txt\": \"工作流工具依赖\"\n        }\n        \n     for file_name, description in key_files.items():\n          file_path = project_root / file_name\n            file_check[\"key_files\"][file_name] = {\n      \"exists\": file_path.exists(),\n        \"description\": description\n        }\n      \n        return file_check\n    \n    def generate_diagnostic_report(self) -> Dict[str, Any]:\n        """生成完整诊断报告\"\"\"\n        logger.info(\"🚀 开始系统诊断...\")\n  \n        report = {\n      \"timestamp\": datetime.now().isoformat(),\n   \"system_diagnostics\": {},\n            \"overall_status\": \"unknown\"\n        }\n\n        # 运行所有诊断检查\n        check_functions = [\n        (\"python_environment\", self.check_python_environment),\n         (\"dependencies\", self.check_dependencies),\n    (\"environment_variables\", self.check_environment_variables),\n            (\"model_connectivity\", self.check_model_connectivity, True),\n     (\"file_system\", self.check_file_system)\n  ]\n        \n        try:\n        for check_name, check_func, *args in check_functions:\n           if check_name == \"model_connectivity\" and args:\n          \n          try:\n             result = check_func()\n    \n      except ImportError:\n           \n          result = {\"error\": \"配置模块导入失败\", \"status\": \"skipped\"}\n     else:\n         result = check_func()\n\n   report[\"system_diagnostics\"][check_name] = result\n   \n        # 计算总体状态\n   all_statuses = [\n    data.get(\"status\", \"ok\") for data in report[\"system_diagnostics\"].values()\n     \n                if isinstance(data, dict)\n            ]\n            \n     if \"error\" in all_statuses:\n   report[\"overall_status\"] = \"error\"\n      elif \"warning\" in all_statuses:\n        report[\"overall_status\"] = \"warning\"\n         else:\n         report[\"overall_status\"] = \"healthy\"\n    \n     except Exception as e:\n       report[\"error\"] = str(e)\n         report[\"overall_status\"] = \"error\"\n        \n        return report


class EnterpriseSupportToolkit:
    """企业级支持工具集主类"""
    
    def __init__(self):
        self.diagnostics = SystemDiagnostics()
        self.tickets = []
    
    def create_support_ticket(self, issue_data: Dict[str, Any]) -> str:
   """创建支持工单"""
        ticket_id = f\"SUP-{datetime.now().strftime('%Y%m%d-%H%M%S')}\"\n        \n        # 收集环境信息\n        env_info = {\n  \"timestamp\": datetime.now().isoformat(),\n  \"python_version\": sys.version,\n        \"platform\": sys.platform,\n   \"working_directory\": os.getcwd(),\n          \"langchain_version\": self._get_package_version(\"langchain\")\n    }\n     \n        ticket = {\n     \"id\": ticket_id,\n    \"type\": issue_data.get(\"type\", \"technical\"),\n            \"priority\": issue_data.get(\"priority\", \"medium\"),\n   \"title\": issue_data.get(\"title\", \"技术支持请求\"),\n       \"description\": issue_data.get(\"description\", \"\"),\n  \"reporter\": issue_data.get(\"reporter\", \"auto-generated\"),\n        \"environment\": env_info,\n    \"status\": \"open\",\n        \"created_at\": datetime.now().isoformat(),\n       \"updated_at\": datetime.now().isoformat()\n     }\n  \n        self.tickets.append(ticket)\n   \n        # 生成诊断报告\n        if issue_data.get(\"include_diagnostics\", False):\n  ticket[\"diagnostics\"] = self.diagnostics.generate_diagnostic_report()\n      \n logger.info(f\"支持工单已创建: {ticket_id}\")\n        return ticket_id\n \n    def _get_package_version(self, package_name: str) -> str:\n   """获取包版本信息\"\"\"\n        try:\n       import importlib.metadata as metadata\n      return metadata.version(package_name)\n        except Exception:\n         return \"unknown\"\n    \n    def generate_health_check_endpoint(self) -> Dict[str, Any]:\n        """生成健康检查端点响应\"\"\"\n        try:\n            diagnostics = self.diagnostics.generate_diagnostic_report()\n    \n            return {\n                \"status\": \"healthy\" if diagnostics[\"overall_status\"] == \"healthy\" else \"unhealthy\",\n           \"timestamp\": datetime.now().isoformat(),\n       \"version\": \"2.0.0\",\n    \"service\": \"langchain-chinese-models\",\n        \"diagnostics\": {\n      \"python_env\": diagnostics[\"system_diagnostics\"].get(\"python_environment\", {}),\n         \"dependencies\": diagnostics[\"system_diagnostics\"].get(\"dependencies\", {}),\n             \"models\": diagnostics[\"system_diagnostics\"].get(\"model_connectivity\", {})\n      },\n        \"uptime_seconds\": (datetime.now() - self.diagnostics.start_time).total_seconds()\n            }\n        except Exception as e:\n            \n      return {\n    \"status\": \"error\",\n         \"timestamp\": datetime.now().isoformat(),\n     \"error\": str(e),\n     \"service\": \"langchain-chinese-models\"\n  }\n    \n    def run_full_system_check(self) -> Dict[str, Any]:\n     ""\"运行完整的系统检查\"\"\"\n        logger.info(\"🔧 运行完整系统检查...\")\n        
        # 生成诊断报告\n        diagnostics = self.diagnostics.generate_diagnostic_report()\n        \n        # 创建总结报告\n        summary = {\n    \"timestamp\": datetime.now().isoformat(),\n            \"checks_performed\": len(diagnostics[\"system_diagnostics\"]),\n     \"overall_status\": diagnostics[\"overall_status\"],\n       \"critical_issues\": [],\n       \"warnings\": [],\n     \"recommendations\": []\n        }\n        \n    # 分析问题\n        for check_name, result in diagnostics[\"system_diagnostics\"].items():\n    if result.get(\"status\") == \"error\":\n          summary[\"critical_issues\"].append(f\"{check_name}: {result.get(\"error\", \"Unknown error\")}\")\n     elif result.get(\"status\") == \"warning\":\n           summary[\"warnings\"].append(f\"{check_name}: 需要关注\")\n        \n        # 生成建议\n        if summary[\"critical_issues\"]:\n    summary[\"recommendations\"].extend([\n                \"修复所有关键问题后再进行后续开发\",\n    \"检查网络连接和API配置\",\n     \"