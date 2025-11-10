#!/usr/bin/env python3
"""
Configuration manager for Starlink Satellite Tracker
Centralized configuration loading and management
"""

import json
import os
import logging
from typing import Dict, Any, Optional

class ConfigManager:
    """Centralized configuration manager."""
    
    _instance = None
    _config: Dict[str, Any] = {}
    
    def __new__(cls):
        """Singleton pattern to ensure only one config manager exists."""
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """Initialize configuration manager."""
        if not self._config:
            self._config = self._load_config()
    
    def _find_config_file(self) -> Optional[str]:
        """Find the configuration file in common locations."""
        possible_paths = [
            'config.json',
            os.path.join('..', 'config.json'),
            os.path.join('src', 'config.json'),
            os.path.join('..', 'src', 'config.json')
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def _load_config(self) -> Dict[str, Any]:
        """Load configuration from file."""
        config_path = self._find_config_file()
        
        if not config_path:
            logging.warning("Could not find config.json. Using default configuration.")
            return self._default_config()
        
        try:
            with open(config_path, 'r') as f:
                config = json.load(f)
            logging.info(f"Configuration loaded from {config_path}")
            return config
        except Exception as e:
            logging.warning(f"Could not load config.json: {e}. Using default configuration.")
            return self._default_config()
    
    def _default_config(self) -> Dict[str, Any]:
        """Return default configuration."""
        return {
            "data_sources": {
                "celestrak_url": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
                "tle_cache_path": "data/tle_cache/",
                "max_cache_days": 7,
                "backup_urls": [
                    "https://celestrak.org/NORAD/elements/starlink.txt",
                    "https://www.celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=csv"
                ]
            },
            "visualization": {
                "orbit_points": 100,
                "earth_texture": "data/earth_texture.jpg",
                "show_ground_track": True,
                "color_scheme": "dark",
                "plotly_3d": True,
                "matplotlib_2d": True
            },
            "schedule": {
                "tle_update_cron": "0 0 */6 * *",
                "prediction_update_cron": "*/30 * * * *",
                "notification_check_cron": "*/15 * * * *"
            },
            "observer": {
                "default_latitude": 55.7558,
                "default_longitude": 37.6173,
                "default_altitude": 0,
                "timezone": "Europe/Moscow"
            },
            "notifications": {
                "email": {
                    "enabled": False,
                    "smtp_server": "smtp.gmail.com",
                    "smtp_port": 587,
                    "username": "",
                    "password": "",
                    "recipient": ""
                },
                "telegram": {
                    "enabled": False,
                    "bot_token": "",
                    "chat_id": ""
                },
                "min_elevation": 10,
                "min_brightness": -1,
                "advance_notice_minutes": 30,
                "excluded_satellites": [],
                "excluded_patterns": ["DEBRIS", "TEST"]
            },
            "export": {
                "default_format": "json",
                "include_tle_data": True,
                "include_predictions": True,
                "compress_large_files": True
            }
        }
    
    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration."""
        return self._config.copy()
    
    def get_section(self, section_name: str) -> Dict[str, Any]:
        """Get a specific section of the configuration."""
        return self._config.get(section_name, {}).copy()
    
    def get_value(self, section: str, key: str, default=None):
        """Get a specific value from the configuration."""
        return self._config.get(section, {}).get(key, default)
    
    def reload_config(self) -> Dict[str, Any]:
        """Reload configuration from file."""
        self._config = self._load_config()
        return self._config.copy()

def get_config() -> Dict[str, Any]:
    """Get the global configuration."""
    manager = ConfigManager()
    return manager.get_config()

def get_config_section(section_name: str) -> Dict[str, Any]:
    """Get a specific section of the global configuration."""
    manager = ConfigManager()
    return manager.get_section(section_name)

def get_config_value(section: str, key: str, default=None):
    """Get a specific value from the global configuration."""
    manager = ConfigManager()
    return manager.get_value(section, key, default)

# Example usage
if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Get configuration
    config = get_config()
    print("Configuration loaded:")
    print(f"  Data sources: {config.get('data_sources', {})}")
    print(f"  Visualization: {config.get('visualization', {})}")
    
    # Get specific section
    observer_config = get_config_section('observer')
    print(f"  Observer: {observer_config}")
    
    # Get specific value
    default_lat = get_config_value('observer', 'default_latitude', 0.0)
    print(f"  Default latitude: {default_lat}")