"""测试当前环境配置"""
import sys
sys.path.insert(0, '.')

print("🔧 测试完整环境配置")
print("-" * 40)
print("当前工作目录:", sys.path[0])
print("Python版本:", sys.version[:60])

# 测试基础模块导入
try:
    import config
    print("✅ config 模块导入成功")
    classes = [n for n in dir(config) if not n.startswith('_')]
    print("可用类:", classes)
except Exception as e:
   print("❌ config 模块导入失败:", e)

# 测试环境变量
try:
    from support.enterprise_support import SystemDiagnostics
    diag = SystemDiagnostics()
    env_check = diag.check_environment_variables()
   print("环境变量配置:", env_check['configured_count'], '/', env_check['total_vars'], '个已配置')
except Exception as e:
    print("❌ 企业支持模块导入失败:", e)

# 测试监控模块
try:
    from monitoring.metrics_simple import ModelMetrics
    metrics = ModelMetrics()
    print("✅ 监控模块导入成功")
except Exception as e:
    print("❌ 监控模块导入失败:", e)

print("=" * 40)
print("✅ 环境测试完成")
