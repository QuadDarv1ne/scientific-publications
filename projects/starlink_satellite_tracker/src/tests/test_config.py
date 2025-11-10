#!/usr/bin/env python3
"""
Test configuration loading for Starlink Satellite Tracker
"""

import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from core.main import StarlinkTracker

def test_config_loading():
    """Test that configuration is loaded correctly."""
    tracker = StarlinkTracker()
    print("Configuration loaded successfully")
    print(f"Config keys: {list(tracker.config.keys())}")
    
    # Check specific sections
    if 'observer' in tracker.config:
        print(f"Observer config: {tracker.config['observer']}")
    else:
        print("No observer section in config")
        
    if 'notifications' in tracker.config:
        print(f"Notifications config: {tracker.config['notifications']}")
    else:
        print("No notifications section in config")
        
    if 'export' in tracker.config:
        print(f"Export config: {tracker.config['export']}")
    else:
        print("No export section in config")

if __name__ == "__main__":
    test_config_loading()