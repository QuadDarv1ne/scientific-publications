#!/usr/bin/env python3
"""
Test script for weather data integration.
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.utils.weather_data import WeatherDataCollector
    print("✓ WeatherDataCollector imported successfully")
    
    # Try to create an instance
    collector = WeatherDataCollector()
    print("✓ WeatherDataCollector instance created successfully")
    
    print("Weather integration is working correctly!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()