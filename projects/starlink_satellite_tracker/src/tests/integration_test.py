#!/usr/bin/env python3
"""
Integration test for Starlink Satellite Tracker
Tests the interaction between different components of the system
"""

import json
import os
import sys
from datetime import datetime

# Add the project directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

def test_configuration_loading():
    """Test that configuration is loaded correctly."""
    print("Testing configuration loading...")
    
    # Test main tracker
    from core.main import StarlinkTracker
    tracker = StarlinkTracker()
    
    # Check that config is loaded
    assert 'data_sources' in tracker.config
    assert 'observer' in tracker.config
    assert 'notifications' in tracker.config
    assert 'export' in tracker.config
    
    print("✓ Configuration loading test passed")
    return True

def test_data_processor_with_config():
    """Test that data processor uses configuration correctly."""
    print("Testing data processor with configuration...")
    
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Test data processor
    from utils import data_processor
    processor = data_processor.DataProcessor(config)
    
    # Check that export config is loaded
    assert hasattr(processor, 'export_config')
    assert 'compress_large_files' in processor.export_config
    
    # Test loading satellite data
    satellites = processor.load_satellite_data()
    assert satellites is not None
    
    print("✓ Data processor with configuration test passed")
    return True

def test_export_functionality():
    """Test export functionality with configuration."""
    print("Testing export functionality...")
    
    # Load configuration
    with open('config.json', 'r') as f:
        config = json.load(f)
    
    # Test data processor
    from utils import data_processor
    processor = data_processor.DataProcessor(config)
    
    # Load satellite data
    satellites = processor.load_satellite_data()
    
    if satellites:
        # Test export to JSON
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        json_filename = f'test_export_{timestamp}.json'
        
        result = processor.export_to_json(satellites[:1], json_filename)
        assert result == True
        assert os.path.exists(json_filename) or os.path.exists(json_filename + '.gz')
        
        # Clean up test file
        if os.path.exists(json_filename):
            os.remove(json_filename)
        if os.path.exists(json_filename + '.gz'):
            os.remove(json_filename + '.gz')
        
        # Test export to CSV
        csv_filename = f'test_export_{timestamp}.csv'
        
        result = processor.export_to_csv(satellites[:1], csv_filename)
        assert result == True
        assert os.path.exists(csv_filename) or os.path.exists(csv_filename + '.gz')
        
        # Clean up test file
        if os.path.exists(csv_filename):
            os.remove(csv_filename)
        if os.path.exists(csv_filename + '.gz'):
            os.remove(csv_filename + '.gz')
    
    print("✓ Export functionality test passed")
    return True

def test_web_app_config():
    """Test that web app uses configuration correctly."""
    print("Testing web application configuration...")
    
    # Import web app components
    from web import web_app
    
    # Check that configuration is loaded
    assert hasattr(web_app, 'DEFAULT_LATITUDE')
    assert hasattr(web_app, 'DEFAULT_LONGITUDE')
    
    # Check default values
    assert isinstance(web_app.DEFAULT_LATITUDE, (int, float))
    assert isinstance(web_app.DEFAULT_LONGITUDE, (int, float))
    
    print("✓ Web application configuration test passed")
    return True

def main():
    """Run all integration tests."""
    print("Starlink Satellite Tracker - Integration Tests")
    print("=" * 50)
    
    tests = [
        test_configuration_loading,
        test_data_processor_with_config,
        test_export_functionality,
        test_web_app_config
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            result = test()
            if result:
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ {test.__name__} failed with error: {e}")
            failed += 1
    
    print("\n" + "=" * 50)
    print(f"Tests completed: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All integration tests passed!")
        return True
    else:
        print("❌ Some tests failed.")
        return False

if __name__ == "__main__":
    main()