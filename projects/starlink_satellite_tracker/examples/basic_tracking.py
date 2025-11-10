#!/usr/bin/env python3
"""
Basic Starlink Satellite Tracking Example

This example demonstrates how to use the core tracking functionality
to predict satellite passes and visualize orbits.
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.core.main import StarlinkTracker
from src.utils.config_manager import get_config


def main():
    """Demonstrate basic satellite tracking functionality."""
    
    print("🚀 Starlink Satellite Tracker - Basic Example")
    print("=" * 50)
    
    try:
        # Initialize tracker
        print("Initializing tracker...")
        tracker = StarlinkTracker()
        
        # Update TLE data
        print("Updating TLE data...")
        satellites = tracker.update_tle_data()
        print(f"✓ Loaded {len(satellites)} satellites")
        
        # Get configuration for default location
        config = get_config()
        default_lat = config.get('observer', {}).get('default_latitude', 55.7558)
        default_lon = config.get('observer', {}).get('default_longitude', 37.6173)
        
        print(f"\n📍 Predicting passes for default location:")
        print(f"   Latitude: {default_lat}")
        print(f"   Longitude: {default_lon}")
        
        # Predict passes
        print("Predicting satellite passes...")
        passes = tracker.predict_passes(
            latitude=default_lat,
            longitude=default_lon,
            hours_ahead=24,
            min_elevation=10
        )
        
        print(f"✓ Found {len(passes)} upcoming passes in the next 24 hours")
        
        # Display next 5 passes
        print("\n📡 Next 5 Satellite Passes:")
        print("-" * 60)
        print(f"{'Satellite':<15} {'Time':<20} {'Altitude':<10} {'Azimuth':<10}")
        print("-" * 60)
        
        for p in passes[:5]:
            time_str = p['time'].strftime('%Y-%m-%d %H:%M:%S')
            print(f"{p['satellite']:<15} {time_str:<20} {p['altitude']:<10.1f} {p['azimuth']:<10.1f}")
        
        # Demonstrate cache clearing
        print("\n🧹 Clearing caches...")
        tracker.clear_caches()
        print("✓ Caches cleared")
        
        print("\n✅ Basic tracking example completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()