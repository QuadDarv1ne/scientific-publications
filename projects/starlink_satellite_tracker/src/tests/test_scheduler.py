#!/usr/bin/env python3
"""
Test script for the scheduler functionality
"""

import sys
import os

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

def test_scheduler_import():
    """Test that scheduler can be imported."""
    print("Testing scheduler import...")
    
    try:
        from utils.scheduler import StarlinkScheduler
        print("✓ Scheduler module imported successfully")
        return True
    except Exception as e:
        print(f"❌ Scheduler module import failed: {e}")
        return False

def test_scheduler_initialization():
    """Test that scheduler can be initialized."""
    print("\nTesting scheduler initialization...")
    
    try:
        from utils.scheduler import StarlinkScheduler
        scheduler = StarlinkScheduler()
        print("✓ Scheduler initialized successfully")
        print(f"  Config keys: {list(scheduler.config.keys()) if scheduler.config else 'None'}")
        return True
    except Exception as e:
        print(f"❌ Scheduler initialization failed: {e}")
        return False

def test_scheduled_jobs():
    """Test that scheduled jobs can be retrieved."""
    print("\nTesting scheduled jobs...")
    
    try:
        from utils.scheduler import StarlinkScheduler
        scheduler = StarlinkScheduler()
        jobs = scheduler.get_scheduled_jobs()
        print("✓ Scheduled jobs retrieved successfully")
        print(f"  Number of jobs: {len(jobs)}")
        for job in jobs:
            print(f"    {job['name']}: Next run at {job['next_run']}")
        return True
    except Exception as e:
        print(f"❌ Scheduled jobs retrieval failed: {e}")
        return False

def main():
    """Run all scheduler tests."""
    print("Starlink Satellite Tracker - Scheduler Test")
    print("=" * 45)
    
    success = True
    success &= test_scheduler_import()
    success &= test_scheduler_initialization()
    success &= test_scheduled_jobs()
    
    print("\n" + "=" * 45)
    if success:
        print("🎉 All scheduler tests passed!")
    else:
        print("❌ Some scheduler tests failed.")
    
    return success

if __name__ == "__main__":
    main()