#!/usr/bin/env python3
"""
Complete Starlink Tracker Example

This example demonstrates a complete workflow using all major components
of the Starlink Satellite Tracker application.
"""

import sys
import os
import time
from datetime import datetime, timedelta

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.main import StarlinkTracker
from src.utils.data_processor import DataProcessor
from src.utils.scheduler import StarlinkScheduler
from src.utils.notify import NotificationSystem
from src.utils.config_manager import get_config


def demonstrate_core_tracking(tracker):
    """Demonstrate core tracking functionality."""
    print("\n1. 🛰️  Core Tracking Functionality")
    print("-" * 40)
    
    # Update TLE data
    print("Updating TLE data...")
    satellites = tracker.update_tle_data()
    print(f"✓ Loaded {len(satellites)} satellites")
    
    # Get configuration for location
    config = get_config()
    lat = config.get('observer', {}).get('default_latitude', 55.7558)
    lon = config.get('observer', {}).get('default_longitude', 37.6173)
    
    print(f"Predicting passes for location ({lat}, {lon})...")
    passes = tracker.predict_passes(
        latitude=lat,
        longitude=lon,
        hours_ahead=24,
        min_elevation=10
    )
    print(f"✓ Found {len(passes)} upcoming passes")
    
    # Show next pass
    if passes:
        next_pass = passes[0]
        print(f"Next pass: {next_pass['satellite']} at {next_pass['time']}")
    
    return satellites, passes


def demonstrate_data_processing(satellites):
    """Demonstrate data processing functionality."""
    print("\n2. 📊 Data Processing Functionality")
    print("-" * 40)
    
    # Initialize data processor
    processor = DataProcessor()
    
    # Analyze constellation
    print("Analyzing constellation...")
    stats = processor.analyze_constellation(satellites)
    print(f"✓ Analysis complete")
    print(f"  Total satellites: {stats.get('total_satellites', 0)}")
    
    # Export data
    print("Exporting data...")
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_file = f'complete_example_{timestamp}.json'
    csv_file = f'complete_example_{timestamp}.csv'
    
    json_success = processor.export_to_json(satellites, json_file)
    csv_success = processor.export_to_csv(satellites, csv_file)
    
    if json_success and csv_success:
        print(f"✓ Data exported to {json_file} and {csv_file}")
    else:
        print("❌ Some exports failed")
    
    return processor


def demonstrate_scheduling(tracker):
    """Demonstrate scheduling functionality."""
    print("\n3. ⏰ Scheduling Functionality")
    print("-" * 40)
    
    # Initialize scheduler
    scheduler = StarlinkScheduler(tracker=tracker)
    
    # Setup tasks
    print("Setting up scheduled tasks...")
    if scheduler.setup_scheduled_tasks():
        print("✓ Scheduled tasks setup successfully")
    else:
        print("❌ Failed to setup scheduled tasks")
        return scheduler
    
    # Show jobs
    jobs = scheduler.get_scheduled_jobs()
    print(f"Found {len(jobs)} scheduled jobs:")
    for job in jobs:
        name = job.get('name', 'Unknown')
        print(f"  - {name}")
    
    return scheduler


def demonstrate_notifications(passes):
    """Demonstrate notification functionality."""
    print("\n4. 🔔 Notification Functionality")
    print("-" * 40)
    
    # Initialize notification system
    notifier = NotificationSystem()
    
    # Check configuration
    config = get_config()
    email_enabled = config.get('notifications', {}).get('email', {}).get('enabled', False)
    telegram_enabled = config.get('notifications', {}).get('telegram', {}).get('enabled', False)
    
    if email_enabled or telegram_enabled:
        print("Sending test notification...")
        if passes:
            next_pass = passes[0]
            success = notifier.notify_upcoming_pass(
                next_pass['satellite'],
                next_pass['time'],
                next_pass['altitude'],
                next_pass['azimuth']
            )
            
            if success:
                print("✓ Test notification sent successfully")
            else:
                print("❌ Failed to send test notification")
        else:
            print("❌ No passes available for notification")
    else:
        print("No notification methods enabled in configuration")
        print("To test notifications, enable email or Telegram in config.json")
    
    return notifier


def main():
    """Demonstrate complete workflow."""
    
    print("🌟 Starlink Satellite Tracker - Complete Example")
    print("=" * 55)
    print("This example demonstrates all major components working together")
    
    try:
        # Initialize core tracker
        print("\n🚀 Initializing Starlink Tracker...")
        tracker = StarlinkTracker()
        print("✓ Tracker initialized successfully")
        
        # Demonstrate core tracking
        satellites, passes = demonstrate_core_tracking(tracker)
        
        # Demonstrate data processing
        processor = demonstrate_data_processing(satellites)
        
        # Demonstrate scheduling
        scheduler = demonstrate_scheduling(tracker)
        
        # Demonstrate notifications
        notifier = demonstrate_notifications(passes)
        
        # Clean up caches
        print("\n5. 🧹 Cleanup")
        print("-" * 40)
        tracker.clear_caches()
        processor.clear_cache()
        scheduler.clear_cache()
        print("✓ All caches cleared")
        
        print(f"\n🎉 Complete example finished successfully!")
        print(f"   Key accomplishments:")
        print(f"   • Tracked {len(satellites)} satellites")
        print(f"   • Found {len(passes)} upcoming passes")
        print(f"   • Analyzed constellation data")
        print(f"   • Exported data to JSON and CSV")
        print(f"   • Configured automated scheduling")
        print(f"   • Tested notification system")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()