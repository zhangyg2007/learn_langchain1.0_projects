"""Simple monitoring metrics module"""

import time
import json
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ModelMetrics:
    """Simple model metrics collector"""
    
    def __init__(self):
        self.metrics = {
            "requests": {},
            "response_times": {}
        }
    
    def record_request(self, provider, model, status, duration):
        """Record a model request"""
        key = f"{provider}_{model}"
        
        if key not in self.metrics["requests"]:
            self.metrics["requests"][key] = {"success": 0, "error": 0, "total": 0}
        
        self.metrics["requests"][key][status] += 1
        self.metrics["requests"][key]["total"] += 1
        
        if status == "success" and duration > 0:
            if key not in self.metrics["response_times"]:
                self.metrics["response_times"][key] = []
            self.metrics["response_times"][key].append(duration)
    
    def get_summary(self):
        """Get metrics summary"""
        summary = {
            "timestamp": datetime.now().isoformat(),
            "total_requests": 0,
            "providers": {}
        }
        
        for key, data in self.metrics["requests"].items():
            provider = key.split("_")[0]
            success_rate = data["success"] / data["total"] if data["total"] > 0 else 0
            
            summary["providers"][provider] = {
                "requests": data["total"],
                "success_rate": success_rate
            }
            summary["total_requests"] += data["total"]
        
        return summary

# Global metrics instance
model_metrics = ModelMetrics()

if __name__ == "__main__":
    print("Testing monitoring metrics...")
    
    model_metrics.record_request("deepseek", "deepseek-chat", "success", 1.2)
    model_metrics.record_request("deepseek", "deepseek-chat", "success", 0.8)
    model_metrics.record_request("zhipu", "glm-4", "success", 1.5)
    
    summary = model_metrics.get_summary()
    print("Summary:", json.dumps(summary, ensure_ascii=False, indent=2))
    
    print("✅ Monitoring metrics test completed!")
