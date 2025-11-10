#!/usr/bin/env python3
"""
Test script to verify the new project structure
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_imports():
    """Test that all modules can be imported."""
    print("Testing imports...")
    
    try:
        from core.main import StarlinkTracker
        print("✓ Core module imported successfully")
    except Exception as e:
        print(f"❌ Core module import failed: {e}")
        return False
    
    try:
        from utils.data_processor import DataProcessor
        print("✓ Utils module imported successfully")
    except Exception as e:
        print(f"❌ Utils module import failed: {e}")
        return False
    
    try:
        from utils.notify import NotificationSystem
        print("✓ Notification module imported successfully")
    except Exception as e:
        print(f"❌ Notification module import failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test that configuration can be loaded."""
    print("\nTesting configuration...")
    
    try:
        from core.main import StarlinkTracker
        tracker = StarlinkTracker()
        print("✓ Configuration loaded successfully")
        print(f"  Config keys: {list(tracker.config.keys())}")
        return True
    except Exception as e:
        print(f"❌ Configuration loading failed: {e}")
        return False

def main():
    """Run all tests."""
    print("Starlink Satellite Tracker - Structure Test")
    print("=" * 45)
    
    success = True
    success &= test_imports()
    success &= test_configuration()
    
    print("\n" + "=" * 45)
    if success:
        print("🎉 All tests passed! Project structure is correct.")
    else:
        print("❌ Some tests failed.")
    
    return success

if __name__ == "__main__":
    main()