#!/usr/bin/env python3
"""
Scheduling and Notifications Example

This example demonstrates how to use the scheduler and notification system
to automate satellite tracking tasks and send alerts.
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.main import StarlinkTracker
from src.utils.scheduler import StarlinkScheduler
from src.utils.notify import NotificationSystem
from src.utils.config_manager import get_config


def main():
    """Demonstrate scheduling and notification functionality."""
    
    print("⏰ Starlink Satellite Tracker - Scheduling & Notifications Example")
    print("=" * 65)
    
    try:
        # Initialize components
        print("Initializing components...")
        tracker = StarlinkTracker()
        scheduler = StarlinkScheduler(tracker=tracker)
        notifier = NotificationSystem()
        
        # Show configuration
        config = get_config()
        schedule_config = config.get('schedule', {})
        print(f"📋 Schedule configuration:")
        for key, value in schedule_config.items():
            print(f"   {key}: {value}")
        
        # Setup scheduled tasks
        print("\n⚙️  Setting up scheduled tasks...")
        if scheduler.setup_scheduled_tasks():
            print("✓ Scheduled tasks setup successfully")
        else:
            print("❌ Failed to setup scheduled tasks")
            return
        
        # Show scheduled jobs
        print("\n📅 Scheduled jobs:")
        jobs = scheduler.get_scheduled_jobs()
        if jobs:
            for job in jobs:
                name = job.get('name', 'Unknown')
                next_run = job.get('next_run', 'Unknown')
                print(f"   {name}: Next run at {next_run}")
        else:
            print("   No scheduled jobs found")
        
        # Test notification system
        print("\n🔔 Testing notification system...")
        
        # Check if any notification methods are enabled
        email_enabled = config.get('notifications', {}).get('email', {}).get('enabled', False)
        telegram_enabled = config.get('notifications', {}).get('telegram', {}).get('enabled', False)
        
        if email_enabled or telegram_enabled:
            print("   Sending test notification...")
            success = notifier.notify_upcoming_pass(
                "STARLINK-TEST",
                datetime.now() + timedelta(minutes=30),
                65.5,
                42.3
            )
            
            if success:
                print("✓ Test notification sent successfully")
            else:
                print("❌ Failed to send test notification")
        else:
            print("   No notification methods enabled in configuration")
            print("   To test notifications, enable email or Telegram in config.json")
        
        # Demonstrate manual task execution
        print("\n🔧 Demonstrating manual task execution...")
        print("   Executing TLE update task...")
        try:
            # This would normally be called by the scheduler
            satellites = tracker.update_tle_data(force=True)
            print(f"   ✓ TLE update completed, loaded {len(satellites) if satellites else 0} satellites")
        except Exception as e:
            print(f"   ❌ TLE update failed: {e}")
        
        # Clear scheduler cache
        print("\n🧹 Clearing scheduler cache...")
        scheduler.clear_cache()
        print("✓ Scheduler cache cleared")
        
        print(f"\n✅ Scheduling and notifications example completed!")
        print(f"   Note: Scheduler runs in background. To see it in action,")
        print(f"   you would need to let it run for the scheduled intervals.")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()