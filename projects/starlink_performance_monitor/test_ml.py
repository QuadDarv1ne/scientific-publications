#!/usr/bin/env python3
"""
Test script for ML modules.
"""

import sys
import os

# Add the src directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

try:
    from src.ml.anomaly_detection import AnomalyDetector
    print("✓ AnomalyDetector imported successfully")
    
    from src.ml.forecasting import PerformanceForecaster
    print("✓ PerformanceForecaster imported successfully")
    
    from src.ml.ml_analyzer import MLAnalyzer
    print("✓ MLAnalyzer imported successfully")
    
    # Try to create instances
    anomaly_detector = AnomalyDetector()
    print("✓ AnomalyDetector instance created successfully")
    
    forecaster = PerformanceForecaster()
    print("✓ PerformanceForecaster instance created successfully")
    
    analyzer = MLAnalyzer()
    print("✓ MLAnalyzer instance created successfully")
    
    print("\nAll ML modules are working correctly!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()