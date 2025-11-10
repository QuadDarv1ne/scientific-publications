#!/usr/bin/env python3
"""
Test data processor with configuration
"""

from data_processor import DataProcessor
import json

def test_data_processor():
    """Test the data processor with configuration."""
    # Load configuration
    try:
        with open('config.json') as f:
            config = json.load(f)
        print("Config loaded successfully")
    except Exception as e:
        print(f"Could not load config: {e}")
        config = {}
    
    # Initialize processor
    processor = DataProcessor(config)
    print("DataProcessor initialized with config")
    print(f"Export config: {processor.export_config}")
    
    # Test loading satellite data
    satellites = processor.load_satellite_data()
    if satellites:
        print(f"Loaded {len(satellites)} satellites")
        
        # Analyze constellation
        stats = processor.analyze_constellation(satellites)
        print(f"Constellation stats: {stats}")
    else:
        print("No satellite data available")

if __name__ == "__main__":
    test_data_processor()