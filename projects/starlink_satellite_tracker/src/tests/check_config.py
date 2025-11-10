#!/usr/bin/env python3
"""
Configuration checker for Starlink Satellite Tracker
"""

import json

def check_config():
    """Check the configuration file."""
    try:
        with open('config.json') as f:
            config = json.load(f)
        print("Config file loaded successfully")
        print(f"Config keys: {list(config.keys())}")
        
        # Check specific sections
        if 'observer' in config:
            print(f"Observer config: {config['observer']}")
        else:
            print("No observer section in config")
            
        if 'notifications' in config:
            print(f"Notifications config: {config['notifications']}")
        else:
            print("No notifications section in config")
            
        if 'export' in config:
            print(f"Export config: {config['export']}")
        else:
            print("No export section in config")
            
    except Exception as e:
        print(f"Error loading config: {e}")

if __name__ == "__main__":
    check_config()