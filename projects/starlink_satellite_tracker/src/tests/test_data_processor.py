#!/usr/bin/env python3
"""
Test data processor with configuration
"""

import sys
import os
import json

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.data_processor import DataProcessor

def test_data_processor():
    """Test the data processor with configuration."""
    # Load configuration
    try:
        config_path = os.path.join(os.path.dirname(__file__), '..', '..', 'config.json')
        with open(config_path) as f:
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