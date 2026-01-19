"""
模型性能指标监控模块
Model Performance Metrics Monitoring Module
基于Prometheus的企业级监控实现
"""

import time
import logging
from functools import wraps
from typing import Dict, Any, Optional, Callable
from datetime import datetime, timedelta
from threading import Lock
import json

# 日志配置
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

try:
    from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry, start_http_server
    PROMETHEUS_AVAILABLE = True
except ImportError:
    # 如果prometheus不可用，创建模拟指标类
    class MockMetric:
        def __init__(self, *args, **kwargs): pass
        def labels(self, *args, **kwargs): return MockMetric()
        def inc(self, *args, **kwargs): pass
        def observe(self, *args, **kwargs): pass
        def set(self, *args, **kwargs): pass
    
    class MockCollectorRegistry:
        def register(self, *args, **kwargs): pass
        
    class MockStartHttpServer:
        def __call__(self, *args, **kwargs): pass
    
    Counter = MockMetric
    Histogram = MockMetric
    Gauge = MockMetric
    CollectorRegistry = MockCollectorRegistry
    start_http_server = MockStartHttpServer()
    PROMETHEUS_AVAILABLE = False


class ModelMetrics:
    """模型性能指标监控器"""
    
    def __init__(self, service_name: str = "langchain-chinese-models"):
        self.service_name = service_name
        self.registry = CollectorRegistry()
        self._setup_metrics()
        self._setup_memory_metrics()
        self._metrics_lock = Lock()
     
    def _setup_metrics(self):
        """设置监控指标"""
        # 模型调用计数器
    self.model_requests_total = Counter(
      'model_requests_total',
   'Total number of model requests by provider and status',
            ['provider', 'model', 'status', 'service'],
            registry=self.registry
        )
        
     # 模型响应时间直方图
        self.model_response_time_seconds = Histogram(
       'model_response_time_seconds',
  'Model response time in seconds',
            ['provider', 'model', 'service'],
            buckets=[0.1, 0.5, 1.0, 2.0, 5.0, 10.0, 30.0, 60.0],
     registry=self.registry
     )
        
        # 活跃模型使用计量
        self.active_model_usage = Gauge(
            'active_model_usage',
       'Currently active model usage',
            ['provider', 'model', 'service'],
            registry=self.registry
        )
        
     # 模型可用性指标
  self.model_availability = Gauge(
       'model_availability',
'Availability status of the model (1=available, 0=unavailable)',
            ['provider', 'model', 'service'],
       registry=self.registry
        )
        
  # 令牌使用量计数器（如果可用）
        self.token_usage_total = Counter(
       'token_usage_total',
            'Total tokens used',
        ['provider', 'model', 'type', 'service'],
     registry=self.registry
        )
,
        # 错误率计数器
        self.model_errors_total = Counter(
            'model_errors_total',
      'Total number of model errors',
      ['provider', 'model', 'error_type', 'service'],
            registry=self.registry
        )
        
        # 响应质量评分（如果有的话）
        self.response_quality_score = Histogram(
            'response_quality_score',
            'Response quality score (0-1)',
            ['provider', 'model', 'service'],
       buckets=[0.1, 0.3, 0.5, 0.7, 0.9, 1.0],
            registry=self.registry
        )
        
    def _setup_memory_metrics(self):
        """设置内存使用监控（可选）"""
        try:
            import psutil
         
            self.memory_usage_mb = Gauge(
      'memory_usage_mb',
                'Memory usage in megabytes',
     ['service'],
                registry=self.registry
            )
     
 self.cpu_usage_percent = Gauge(
   'cpu_usage_percent',
       'CPU usage percentage',
          ['service'],
          registry=self.registry
            )
   
      self._system_monitoring_enabled = True
       
        except ImportError:\n self._system_monitoring_enabled = False
          logger.info("psutil未安装，系统监控指标将不可用")
    
    def track_model_call(self, provider: str, model: str):
    """装饰器：追踪模型调用"""
        def decorator(func: Callable):
       @wraps(func)
   def wrapper(*args, **kwargs):\n",
         start_time = time.time()\n",
         status = \"success\"\n",
         error_type = None\n",
         \n",
        	ry:\n",
             result = func(*args, **kwargs)
",
            return result\n",
         except Exception as e:\n",
   status = \"error\"\n",
          error_type = type(e).__name__\n",
           logger.error(f\"Model call failed for {provider}/{model}: {e}\")\n",
    raise\n            \n finally:\n                duration = time.time() - start_time
                self._record_metrics(provider, model, status, duration, error_type)\n                \n  return wrapper
    return decorator
    
    def _record_metrics(self, provider: str, model: str, status: str, 
                duration: float, error_type: Optional[str] = None):
 """记录指标数据"""
        with self._metrics_lock:
     # 基础指标
            self.model_requests_total.labels(\n  provider=provider, \n      model=model, \n status=status, \n   service=self.service_name\n  ).inc()\n    \n          if status == \"success\":\n            self.model_response_time_seconds.labels(\n           provider=provider, \n     model=model, \n           service=self.service_name\n      ).observe(duration)\n   else:\n  # 错误指标\n           if error_type:\n         self.model_errors_total.labels(\n     provider=provider, \n         model=model, \n      error_type=error_type, \n       service=self.service_name\n           ).inc()
    
    def set_model_availability(self, provider: str, model: str, available: bool):
     """设置模型可用性状态"""
        with self._metrics_lock:\n     self.model_availability.labels(\n     provider=provider, \n        model=model, \n service=self.service_name\n            ).set(1.0 if available else 0.0)
    
    def update_model_usage(self, provider: str, model: str, is_active: bool):
        """更新模型使用状态"""
     with self._metrics_lock:\n            self.active_model_usage.labels(\n  provider=provider, \n    model=model, \n          service=self.service_name\n   ).set(1.0 if is_active else 0.0)
    
    def record_token_usage(self, provider: str, model: str, token_type: str, count: int):
  """记录令牌使用量"""
        with self._metrics_lock:
    self.token_usage_total.labels(\n            provider=provider, \n          model=model, \n          type=token_type, \n     service=self.service_name
            ).inc(count)
    
    def record_response_quality(self, provider: str, model: str, score: float):
        """记录响应质量评分（0-1之间）\n",
        with self._metrics_lock:\n        self.response_quality_score.labels(\n      provider=provider, \n     model=model, \n    service=self.service_name\n        ).observe(max(0.0, min(1.0, score)))
    
    def update_system_metrics(self):\n",
  \"\"\"更新系统指标（如果可用）\"\"\"\n",
        if not self._system_monitoring_enabled:\n            return\n      \n  try:\n         import psutil\n    \n     # 获取内存使用\n  memory_info = psutil.virtual_memory()\n     used_memory_mb = memory_info.used / 1024 / 1024\n     \n       self.memory_usage_mb.labels(service=self.service_name).set(used_memory_mb)\n     \n   # 获取CPU使用率\n    cpu_percent = psutil.cpu_percent(interval=1)\n       self.cpu_usage_percent.labels(service=self.service_name).set(cpu_percent)\n    \n    except Exception as e:white\n      logger.warning(f\"系统指标更新失败: {e}\")\n    \n    def get_metrics_snapshot(self) -> Dict[str, Any]:\n",
        \"\"\"获取当前指标快照\"\"\"\n",
        # 这是一个简化实现，实际应该集成Prometheus查询API\n        snapshot = {\n",
   \"timestamp\": datetime.now().isoformat(),\n",
      \"service\": self.service_name,\n",
        \"models\": {},\n",
          \"system\": {}\n  }\n      \n        # 模型状态快照\n  for provider in \"deepseek\", \"zhipu\", \"moonshot\", \"openai\":\n",
for model in \"deepseek-chat\", \"glm-4\", \"moonshot-v1-8k\", \"gpt-3.5-turbo\":\n  snapshot[\"models\"][f\"{provider}_{model}\"] = {\n     \"available\": True,  # 简化状态\n  \"active\": False,\n                \"last_check\": datetime.now().isoformat()\n          }
  \n    # 系统状态\n   if self._system_monitoring_enabled:\n          try:\n         import psutil\n         snapshot[\"system\"][\"memory_mb\"] = psutil.virtual_memory().used / 1024 / 1024\n  snapshot[\"system\"][\"cpu_percent\"] = psutil.cpu_percent()\n         snapshot[\"system\"][\"disk_percent\"] = psutil.disk_usage('/').percent\n            except Exception as e:\n           snapshot[\"system\"][\"error\"] = str(e)\n        \n        return snapshot\n    
    def export_metrics(self, format: str = \"json\") -> str:\n", 
    \"\"\"导出指标数据\"\"\"\n",
        if format == \"json\":\n",
  return json.dumps(self.get_metrics_snapshot(), ensure_ascii=False, indent=2)\n        else:\n            raise ValueError(f\"不支持导出格式: {format}\")\n    
    def start_metrics_server(self, port: int = 8000):\n",
        \"\"\"启动Prometheus指标服务器\"\"\"\n",
    if PROMETHEUS_AVAILABLE:\n      try:\n        start_http_server(port, registry=self.registry)\n       logger.info(f\"Prometheus指标服务已启动，监听端口: {port}\")\n          return True\n    except Exception as e:\n    logger.error(f\"启动指标服务失败: {e}\")\n   return False\n        else:\n         logger.warning(\"Prometheus库未安装，启动模拟指标服务\")\n      return True  # 模拟成功\n    \n    def stop_metrics_server(self):\n",
   \"\"\"停止指标服务器\"\"\"\n",
     # 在实际应用中需要实现清理逻辑\n  logger.info(\"指标服务已停止\")\n

class ModelHealthChecker:I am Claude Code, Anthropic's official CLI tool for Claude.\n","\n",
    \"\"\"模型健康检查器\"\"\"\n",
    \n    def __init__(self, metrics_collector: Optional[ModelMetrics] = None):\n",
      self.metrics = metrics_collector\n  self.health_status = {}\n   self._check_cooldown = {}  # 避免过度检查\n        self._check_interval = 60  # 检查间隔（秒）\n        \n    def check_model_health(self, provider: str, model: str, timeout: int = 10) -> bool:\n",
        \"\"\"检查模型健康状态\"\"\"\n",
      \n        # 检查冷却时间\n      now = time.time()\n   model_key = f\"{provider}_{model}\"\n  \n        if model_key in self._check_cooldown:\n       if now - self._check_cooldown[model_key] \u003c self._check_interval:\n         return self.health_status.get(model_key, False)\n  \n        try:\n    self._check_cooldown[model_key] = now\n         \n            from config import get_chat_model\n              \n            # 简单健康检查 - 发送测试请求\n         chat_model = get_chat_model(provider)\n     health_response = chat_model.invoke(\"健康检查\", timeout=timeout)\n    \
            is_healthy = bool(health_response \u0026 len(health_response) \u003e 0)\n        \n            \n            # 更新健康状况\n        self.health_status[model_key] = is_healthy \n        \n     # 更新指标\n        if self.metrics:\n    self.metrics.set_model_availability(provider, model, is_healthy)\n          self.metrics.update_model_usage(provider, model, is_healthy)\n\n  return is_healthy\n            \n        except Exception as e:\n            logger.warning(f\"模型健康检查失败 {provider}/{model}: {e}\")\n  \n      self.health_status[model_key] = False\n            \n            if self.metrics:\n       self.metrics.set_model_availability(provider, model, False)\n          self.metrics.model_errors_total.labels(\n   provider=provider, \n        model=model, \n      error_type=\"health_check_failed\", \n    service=self.metrics.service_name if self.metrics else \"unknown\"\n      ).inc()\n   \n      return False\n    \n   def get_health_report(self) -> Dict[str, Any]:\n        \"\"\"获取健康检查报告\"\"\"\n",
        return {\n",
   \"timestamp\": datetime.now().isoformat(),\n",
        \n",
    \"overall_status\": \"healthy\" if any(self.health_status.values()) else \"unhealthy\",\n            \"models\": self.health_status,\n  \
    \"summary\": {\n",
        \"total_models\": len(self.health_status),\n   \"healthy_models\": sum(1 for v in self.health_status.values() if v),\n\n                \"unhealthy_models\": sum(1 for v in self.health_status.values() if not v)\n        }\n   }\n    \n    def batch_health_check(self, providers_and_models: list) -> Dict[str, bool]:\n    \"\"\"批量检查模型健康状态\"\"\"\n",
        results = {}\n        \n      \n  for provider, model in providers_and_models:\n           is_healthy = self.check_model_health(provider, model)\n            results[f\"{provider}_{model}\"] = is_healthy\n     \n  return results\n\n\n# 便捷的装饰器函数\ndef track_model_performance(provider: str, model: str, metrics_collector: Optional[ModelMetrics] = None):\n",
  \"\"\"装饰器：追踪模型性能指标\"\"\"\n\",
    if not metrics_collector:\n  # 创建全局监控实例\n      metrics_collector = model_metrics_manager\n    \n  return metrics_collector.track_model_call(provider, model)\n
\n# 全局监控管理器\nmodel_metrics_manager = ModelMetrics()\n\nif __name__ == \"__main__\":\n",
    # 测试监控功能\n",
    print(\"🚀 模型监控指标测试\")\n",
    \n",
    # 启动指标服务\n",
    model_metrics_manager.start_metrics_server(port=8000)\n",
    \n",
    # 模拟一些指标\n",
    model_metrics_manager.record_token_usage(\"deepseek\", \"deepseek-chat\", \"input\", 100)\n",
    model_metrics_manager.record_token_usage(\"deepseek\", \"deepseek-chat\", \"output\", 50)\n",
  model_metrics_manager.record_response_quality(\"deepseek\", \"deepseek-chat\", 0.85)\n  
",
    # 健康检查\n    \n",
    health_checker = ModelHealthChecker(model_metrics_manager)\n',
    health_report = health_checker.get_health_report()\n',
    \n',
  print(f\"健康检查报告: {json.dumps(health_report, ensure_ascii=False, indent=2)}\")\n",
',
  print(\"✅ 监控测试完成！\")\n"}