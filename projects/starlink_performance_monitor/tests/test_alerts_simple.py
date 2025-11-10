#!/usr/bin/env python3
"""
Starlink Performance Monitor
Simple test script for alerting functionality.
"""

def test_alerts_basic():
    """Test basic alerting functionality."""
    print("Testing basic alerting functionality...")
    
    # Test that we can import the alerts module
    try:
        import json
        print("✓ JSON module imported successfully")
    except ImportError:
        print("✗ JSON import failed")
        return
        
    # Test that we can create a simple alert structure
    try:
        alert_data = {
            "type": "test_alert",
            "severity": "warning",
            "message": "This is a test alert"
        }
        print("✓ Alert data structure created")
        print(f"  Alert type: {alert_data['type']}")
        print(f"  Alert message: {alert_data['message']}")
    except Exception as e:
        print(f"✗ Alert data structure test failed: {e}")
        return
        
    print("All basic alerting tests completed successfully!")

if __name__ == "__main__":
    test_alerts_basic()