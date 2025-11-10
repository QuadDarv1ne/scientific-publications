#!/usr/bin/env python3
"""
Test suite for Starlink Satellite Tracker Core Module
Verifies core functionality of the tracking system
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the project directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

class TestStarlinkTracker(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config = {
            'data_sources': {
                'celestrak_url': 'https://test.example.com/test.txt',
                'tle_cache_path': 'test_cache/',
                'max_cache_days': 7
            },
            'visualization': {
                'orbit_points': 100,
                'earth_texture': 'data/earth_texture.jpg',
                'show_ground_track': True,
                'color_scheme': 'dark'
            },
            'schedule': {
                'tle_update_cron': '0 0 */6 * *',
                'prediction_update_cron': '*/30 * * * *',
                'notification_check_cron': '*/15 * * * *'
            }
        }
    
    @patch('core.main.load')
    @patch('os.makedirs')
    def test_initialization_success(self, mock_makedirs, mock_load):
        """Test successful initialization."""
        # Mock time scale and earth data
        mock_ts = MagicMock()
        mock_earth = MagicMock()
        # Mock load.timescale() to return mock_ts and load('earth.bsp') to return mock_earth
        mock_load.timescale.return_value = mock_ts
        mock_load.side_effect = lambda x: mock_earth if x == 'earth.bsp' else mock_load.timescale()
        
        mock_makedirs.return_value = None
        
        from core.main import StarlinkTracker
        tracker = StarlinkTracker(self.test_config)
        
        self.assertIsInstance(tracker, StarlinkTracker)
        self.assertEqual(tracker.ts, mock_ts)
        self.assertEqual(tracker.earth, mock_earth)
    
    @patch('core.main.load')
    @patch('os.makedirs')
    def test_initialization_with_earth_load_failure(self, mock_makedirs, mock_load):
        """Test initialization when earth data fails to load."""
        # Mock time scale
        mock_ts = MagicMock()
        mock_load.timescale.return_value = mock_ts
        
        # Mock load to raise exception when called with 'earth.bsp'
        def load_side_effect(arg):
            if arg == 'earth.bsp':
                raise Exception("Earth data load failed")
            return mock_load.timescale()
        
        mock_load.side_effect = load_side_effect
        
        mock_makedirs.return_value = None
        
        from core.main import StarlinkTracker
        tracker = StarlinkTracker(self.test_config)
        
        self.assertIsInstance(tracker, StarlinkTracker)
        # When earth data fails to load, it should be set to None
        self.assertIsNone(tracker.earth)
    
    @patch('core.main.load')
    @patch('os.makedirs')
    def test_initialization_with_directory_creation_failure(self, mock_makedirs, mock_load):
        """Test initialization when directory creation fails."""
        # Mock time scale
        mock_ts = MagicMock()
        mock_earth = MagicMock()
        mock_load.timescale.return_value = mock_ts
        mock_load.side_effect = lambda x: mock_earth if x == 'earth.bsp' else mock_load.timescale()
        
        # Simulate directory creation failure
        mock_makedirs.side_effect = Exception("Permission denied")
        
        from core.main import StarlinkTracker
        with self.assertRaises(Exception):
            StarlinkTracker(self.test_config)
    
    @patch('requests.get')
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_update_tle_data_use_cache(self, mock_getmtime, mock_exists, mock_get):
        """Test TLE data update using cached data."""
        mock_exists.return_value = True
        mock_getmtime.return_value = datetime.now().timestamp() - 3600  # 1 hour ago
        
        from core.main import StarlinkTracker
        tracker = StarlinkTracker(self.test_config)
        
        # Mock _load_tle_from_file
        with patch.object(tracker, '_load_tle_from_file', return_value=['sat1', 'sat2']) as mock_load:
            result = tracker.update_tle_data(force=False)
            
            self.assertEqual(result, ['sat1', 'sat2'])
            mock_load.assert_called_once()
            mock_get.assert_not_called()  # Should not download when using cache
    
    @patch('requests.get')
    @patch('os.path.exists')
    @patch('os.path.getmtime')
    def test_update_tle_data_force_update(self, mock_getmtime, mock_exists, mock_get):
        """Test forced TLE data update."""
        mock_exists.return_value = True
        mock_getmtime.return_value = datetime.now().timestamp() - 3600  # 1 hour ago
        
        # Mock HTTP response
        mock_response = MagicMock()
        mock_response.text = '''STARLINK-1234
1 12345U 12345ABC  23156.12345678  .00000000  00000-0  00000+0 0  1234
2 12345  53.0000 123.4567 0001234 321.4567 123.4567 15.23456789 12345
'''
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        from core.main import StarlinkTracker
        tracker = StarlinkTracker(self.test_config)
        
        # Mock file operations
        with patch('builtins.open') as mock_open:
            result = tracker.update_tle_data(force=True)
            
            self.assertIsNotNone(result)
            mock_get.assert_called_once_with('https://test.example.com/test.txt', timeout=30)
            mock_open.assert_called()  # Should write to file
    
    def test_predict_passes_no_satellites(self):
        """Test pass prediction with no satellites loaded."""
        from core.main import StarlinkTracker
        tracker = StarlinkTracker(self.test_config)
        
        with self.assertRaises(ValueError) as context:
            tracker.predict_passes(55.7558, 37.6173)
        
        self.assertIn("No satellites loaded", str(context.exception))
    
    @patch('core.main.load')
    def test_predict_passes_invalid_coordinates(self, mock_load):
        """Test pass prediction with invalid coordinates."""
        # Mock the initialization to bypass earth loading issues
        mock_ts = MagicMock()
        mock_earth = MagicMock()
        mock_load.timescale.return_value = mock_ts
        mock_load.side_effect = lambda x: mock_earth if x == 'earth.bsp' else mock_load.timescale()
        
        from core.main import StarlinkTracker
        tracker = StarlinkTracker(self.test_config)
        
        # Add a mock satellite to bypass the "no satellites" check
        mock_satellite = MagicMock()
        tracker.satellites = [mock_satellite]
        tracker.earth = mock_earth
        tracker.ts = mock_ts
        
        # Test invalid latitude
        with self.assertRaises(ValueError) as context:
            tracker.predict_passes(100, 37.6173)  # Latitude > 90
        
        self.assertIn("Invalid latitude", str(context.exception))
        
        # Test invalid longitude
        with self.assertRaises(ValueError) as context:
            tracker.predict_passes(55.7558, 200)  # Longitude > 180
        
        self.assertIn("Invalid longitude", str(context.exception))


if __name__ == '__main__':
    unittest.main(verbosity=2)