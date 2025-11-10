#!/usr/bin/env python3
"""
Data Processing and Export Example

This example demonstrates how to use the data processor to load,
analyze, and export satellite data.
"""

import sys
import os
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.utils.data_processor import DataProcessor
from src.utils.config_manager import get_config


def main():
    """Demonstrate data processing and export functionality."""
    
    print("📊 Starlink Satellite Tracker - Data Processing Example")
    print("=" * 55)
    
    try:
        # Initialize data processor
        print("Initializing data processor...")
        processor = DataProcessor()
        
        # Load satellite data
        print("Loading satellite data...")
        satellites = processor.load_satellite_data()
        
        if not satellites:
            print("❌ No satellite data available")
            return
        
        print(f"✓ Loaded {len(satellites)} satellites")
        
        # Analyze constellation
        print("\n📈 Analyzing constellation...")
        stats = processor.analyze_constellation(satellites)
        print(f"✓ Analysis complete")
        print(f"   Total satellites: {stats.get('total_satellites', 0)}")
        
        if 'id_range' in stats:
            id_range = stats['id_range']
            print(f"   Satellite ID range: {id_range.get('min', 0)} - {id_range.get('max', 0)}")
            print(f"   Satellites with numeric IDs: {id_range.get('count', 0)}")
        
        # Export to JSON
        print("\n💾 Exporting data to JSON...")
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f'starlink_data_{timestamp}.json'
        
        if processor.export_to_json(satellites, json_filename):
            print(f"✓ Data exported to {json_filename}")
        else:
            print("❌ Failed to export to JSON")
        
        # Export to CSV
        print("\n💾 Exporting data to CSV...")
        csv_filename = f'starlink_data_{timestamp}.csv'
        
        if processor.export_to_csv(satellites, csv_filename):
            print(f"✓ Data exported to {csv_filename}")
        else:
            print("❌ Failed to export to CSV")
        
        # Demonstrate filtering (example)
        print("\n🔍 Filtering satellites (example)...")
        # Note: This is a simple example. In practice, you'd implement
        # more sophisticated filtering based on your needs.
        filtered_count = min(10, len(satellites))  # Just take first 10 as example
        print(f"✓ Filtered {filtered_count} satellites (example)")
        
        # Clear cache
        print("\n🧹 Clearing data processor cache...")
        processor.clear_cache()
        print("✓ Cache cleared")
        
        print(f"\n✅ Data processing example completed successfully!")
        print(f"   Files created:")
        print(f"   - {json_filename}")
        print(f"   - {csv_filename}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()