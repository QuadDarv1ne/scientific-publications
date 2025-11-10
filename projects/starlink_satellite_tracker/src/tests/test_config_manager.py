#!/usr/bin/env python3
"""
Unit tests for the configuration manager
"""

import unittest
import os
import sys
import json
import tempfile
from unittest.mock import patch, mock_open

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.config_manager import ConfigManager, get_config, get_config_section, get_config_value


class TestConfigManager(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Clear the singleton instance for each test
        ConfigManager._instance = None
        ConfigManager._config = {}
    
    def test_singleton_pattern(self):
        """Test that ConfigManager follows singleton pattern."""
        manager1 = ConfigManager()
        manager2 = ConfigManager()
        self.assertIs(manager1, manager2)
    
    def test_default_config_loading(self):
        """Test that default configuration is loaded correctly."""
        manager = ConfigManager()
        config = manager.get_config()
        
        # Check that required sections exist
        self.assertIn('data_sources', config)
        self.assertIn('visualization', config)
        self.assertIn('schedule', config)
        self.assertIn('observer', config)
        self.assertIn('notifications', config)
        self.assertIn('export', config)
        
        # Check specific values
        self.assertEqual(config['data_sources']['celestrak_url'], 
                        "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle")
        self.assertEqual(config['observer']['default_latitude'], 55.7558)
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='''{
        "data_sources": {
            "celestrak_url": "https://test.example.com/test.txt",
            "tle_cache_path": "/tmp/test_cache/"
        },
        "observer": {
            "default_latitude": 40.7128,
            "default_longitude": -74.0060
        }
    }''')
    def test_custom_config_loading(self, mock_file, mock_exists):
        """Test loading custom configuration from file."""
        mock_exists.return_value = True
        
        manager = ConfigManager()
        config = manager.get_config()
        
        # Check custom values
        self.assertEqual(config['data_sources']['celestrak_url'], 
                        "https://test.example.com/test.txt")
        self.assertEqual(config['data_sources']['tle_cache_path'], "/tmp/test_cache/")
        self.assertEqual(config['observer']['default_latitude'], 40.7128)
        self.assertEqual(config['observer']['default_longitude'], -74.0060)
    
    def test_config_section_retrieval(self):
        """Test retrieving specific configuration sections."""
        manager = ConfigManager()
        
        # Test getting observer section
        observer_config = manager.get_section('observer')
        self.assertIn('default_latitude', observer_config)
        self.assertIn('default_longitude', observer_config)
        
        # Test getting non-existent section
        empty_config = manager.get_section('non_existent')
        self.assertEqual(empty_config, {})
    
    def test_config_value_retrieval(self):
        """Test retrieving specific configuration values."""
        manager = ConfigManager()
        
        # Test getting existing value
        lat = manager.get_value('observer', 'default_latitude')
        self.assertEqual(lat, 55.7558)
        
        # Test getting non-existent value with default
        default_value = manager.get_value('observer', 'non_existent_key', 'default')
        self.assertEqual(default_value, 'default')
        
        # Test getting value from non-existent section
        none_value = manager.get_value('non_existent_section', 'any_key')
        self.assertIsNone(none_value)
    
    def test_get_config_functions(self):
        """Test the module-level get_config functions."""
        # Test get_config
        config = get_config()
        self.assertIsInstance(config, dict)
        self.assertIn('data_sources', config)
        
        # Test get_config_section
        observer_config = get_config_section('observer')
        self.assertIsInstance(observer_config, dict)
        self.assertIn('default_latitude', observer_config)
        
        # Test get_config_value
        lat = get_config_value('observer', 'default_latitude')
        self.assertEqual(lat, 55.7558)


if __name__ == '__main__':
    unittest.main(verbosity=2)