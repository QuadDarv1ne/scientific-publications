#!/usr/bin/env python3
"""
Test script for the main tracker with scheduler functionality
"""

import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


def test_tracker_with_scheduler():
    """Test that tracker with scheduler works."""
    print("Testing tracker with scheduler...")

    try:
        from core.main import StarlinkTracker

        tracker = StarlinkTracker()
        print("✓ Tracker initialized successfully")

        # Test scheduler methods
        if hasattr(tracker, "start_scheduler"):
            print("✓ Scheduler methods available")
        else:
            print("❌ Scheduler methods not available")
            return False

        return True
    except Exception as e:
        print(f"❌ Tracker with scheduler test failed: {e}")
        return False


def main():
    """Run the test."""
    print("Starlink Satellite Tracker - Main with Scheduler Test")
    print("=" * 55)

    success = test_tracker_with_scheduler()

    print("\n" + "=" * 55)
    if success:
        print("🎉 Main tracker with scheduler test passed!")
    else:
        print("❌ Main tracker with scheduler test failed.")

    return success


if __name__ == "__main__":
    main()
