#!/usr/bin/env python3
"""
Starlink Performance Monitor
Test script for enhanced alerting functionality.
"""

import sys
import os
import tempfile
import json
from datetime import datetime

import importlib.util
import sys
import os

# Add the src directory to the path so we can import modules
src_path = os.path.join(os.path.dirname(__file__), '..', 'src')
sys.path.insert(0, src_path)

def test_alert_class():
    """Test the Alert class functionality."""
    print("Testing Alert class...")
    
    # Test creating an alert
    alert_data = {
        'type': 'download_speed',
        'severity': 'warning',
        'message': 'Download speed is below threshold',
        'timestamp': datetime.utcnow(),
        'value': 25.0,
        'threshold': 50.0
    }
    
    try:
        # Dynamically import the Alert class
        alerts_path = os.path.join(src_path, 'alerts', 'enhanced_alerts.py')
        spec = importlib.util.spec_from_file_location("enhanced_alerts", alerts_path)
        alerts_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(alerts_module)
        
        alert = alerts_module.Alert(alert_data)
        print("✓ Alert class created successfully")
        
        # Test converting to dictionary
        alert_dict = alert.to_dict()
        print("✓ Alert converted to dictionary")
        print(f"  Alert type: {alert_dict['type']}")
        print(f"  Alert message: {alert_dict['message']}")
        
    except Exception as e:
        print(f"✗ Alert class test failed: {e}")
        return
        
    print("All Alert class tests completed successfully!")


def test_enhanced_alert_system():
    """Test the EnhancedAlertSystem class functionality."""
    print("\nTesting EnhancedAlertSystem class...")
    
    # Create a temporary config file
    test_config = {
        "database": {
            "type": "sqlite",
            "echo": False
        },
        "notifications": {
            "telegram": {
                "enabled": False,
                "thresholds": {
                    "download_mbps": 50,
                    "upload_mbps": 10,
                    "ping_ms": 100,
                    "packet_loss_percent": 5
                }
            },
            "email": {
                "enabled": False
            }
        }
    }
    
    with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as temp_config:
        json.dump(test_config, temp_config)
        temp_config_path = temp_config.name
    
    try:
        # Dynamically import the EnhancedAlertSystem class
        alerts_path = os.path.join(src_path, 'alerts', 'enhanced_alerts.py')
        spec = importlib.util.spec_from_file_location("enhanced_alerts", alerts_path)
        alerts_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(alerts_module)
        
        alert_system = alerts_module.EnhancedAlertSystem(temp_config_path)
        print("✓ EnhancedAlertSystem class created successfully")
        
        # Test loading configuration
        config = alert_system.config
        print("✓ Configuration loaded successfully")
        print(f"  Database type: {config['database']['type']}")
        
    except Exception as e:
        print(f"✗ EnhancedAlertSystem class test failed: {e}")
        return
    finally:
        # Clean up temporary config file
        if os.path.exists(temp_config_path):
            os.unlink(temp_config_path)
        
    print("All EnhancedAlertSystem class tests completed successfully!")


if __name__ == "__main__":
    test_alert_class()
    test_enhanced_alert_system()