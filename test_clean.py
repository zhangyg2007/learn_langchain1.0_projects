#!/usr/bin/env python3
import os, sys

print("LangChain Environment Test")
print("=" * 30)

try:
    import config
    print("✅ config imported successfully")
    print("Available classes:", [name for name in dir(config) if not name.startswith('_')])
except Exception as e:
    print(f"❌ config import failed: {e}")
    sys.exit(1)

print("\nEnvironment variables:")
for var in ['DEEPSEEK_API_KEY', 'ZHIPU_API_KEY', 'MOONSHOT_API_KEY']:
    status = "✅" if os.getenv(var) else "❌"
    print(f"{status} {var}: {'configured' if os.getenv(var) else 'not configured'}")

print("\nTest completed.")
