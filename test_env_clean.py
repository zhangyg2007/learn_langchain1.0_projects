#!/usr/bin/env python3
"""Clean environment test"""
import sys
sys.path.insert(0, '.')

def main():
    print("Testing environment...")
    
    # Test imports
    try:
        import config
        print("OK: config imported")
        classes = [n for n in dir(config) if not n.startswith('_')]
print("Available:", classes)
    except Exception as e:
        print("ERROR:", e)
  
  print("✓ Environment test complete")

if __name__ == "__main__":
    main()
