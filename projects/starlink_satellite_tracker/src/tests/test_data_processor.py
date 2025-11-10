#!/usr/bin/env python3
"""
Unit tests for the data processor
"""

import unittest
import os
import sys
import tempfile
from unittest.mock import patch, mock_open, MagicMock
from datetime import datetime
from typing import List, Dict, Any

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.data_processor import DataProcessor


class TestDataProcessor(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a minimal config for testing
        self.test_config = {
            'data_sources': {
                'tle_cache_path': '/tmp/test_cache/'
            },
            'export': {
                'default_format': 'json',
                'compress_large_files': False
            }
        }
    
    def test_initialization(self):
        """Test DataProcessor initialization."""
        processor = DataProcessor(self.test_config)
        self.assertIsInstance(processor, DataProcessor)
        self.assertEqual(processor.data_directory, '/tmp/test_cache/')
    
    def test_load_satellite_data_empty_directory(self):
        """Test loading satellite data from empty directory."""
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = []
            
            processor = DataProcessor(self.test_config)
            result = processor.load_satellite_data()
            self.assertIsNone(result)
    
    @patch('os.path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data='''STARLINK-1234
1 12345U 12345ABC  23156.12345678  .00000000  00000-0  00000+0 0  1234
2 12345  53.0000 123.4567 0001234 321.4567 123.4567 15.23456789 12345
''')
    def test_load_satellite_data_success(self, mock_file, mock_exists):
        """Test successful loading of satellite data."""
        mock_exists.return_value = True
        
        with patch('os.listdir') as mock_listdir:
            mock_listdir.return_value = ['starlink_tle_20230101.txt']
            
            processor = DataProcessor(self.test_config)
            result = processor.load_satellite_data()
            
            self.assertIsNotNone(result)
            if result is not None:
                self.assertIsInstance(result, list)
                self.assertEqual(len(result), 1)
                self.assertEqual(result[0]['name'], 'STARLINK-1234')
    
    def test_filter_satellites(self):
        """Test filtering satellites by criteria."""
        processor = DataProcessor(self.test_config)
        
        # Test data
        satellites: List[Dict[str, str]] = [
            {'name': 'STARLINK-1234', 'line1': 'line1', 'line2': 'line2'},
            {'name': 'STARLINK-5678', 'line1': 'line1', 'line2': 'line2'},
            {'name': 'STARLINK-9012', 'line1': 'line1', 'line2': 'line2'}
        ]
        
        # Filter by name
        filtered = processor.filter_satellites(satellites, {'name': 'STARLINK-1234'})
        self.assertEqual(len(filtered), 1)
        if filtered:  # Type guard
            self.assertEqual(filtered[0]['name'], 'STARLINK-1234')
        
        # Filter with no criteria
        filtered = processor.filter_satellites(satellites, None)
        self.assertEqual(len(filtered), 3)
        
        # Filter with empty criteria
        filtered = processor.filter_satellites(satellites, {})
        self.assertEqual(len(filtered), 3)
    
    def test_analyze_constellation(self):
        """Test constellation analysis."""
        processor = DataProcessor(self.test_config)
        
        # Test data
        satellites: List[Dict[str, str]] = [
            {'name': 'STARLINK-1234', 'line1': 'line1', 'line2': 'line2'},
            {'name': 'STARLINK-5678', 'line1': 'line1', 'line2': 'line2'},
            {'name': 'STARLINK-9012', 'line1': 'line1', 'line2': 'line2'}
        ]
        
        stats = processor.analyze_constellation(satellites)
        self.assertIn('total_satellites', stats)
        self.assertEqual(stats['total_satellites'], 3)
        self.assertIn('id_range', stats)
        self.assertEqual(stats['id_range']['min'], 1234)
        self.assertEqual(stats['id_range']['max'], 9012)
    
    def test_analyze_empty_constellation(self):
        """Test constellation analysis with empty data."""
        processor = DataProcessor(self.test_config)
        
        stats = processor.analyze_constellation(None)
        self.assertEqual(stats, {})
        
        stats = processor.analyze_constellation([])
        self.assertEqual(stats, {})
    
    @patch('pandas.DataFrame.to_csv')
    def test_export_to_csv_success(self, mock_to_csv):
        """Test successful CSV export."""
        mock_to_csv.return_value = None
        
        processor = DataProcessor(self.test_config)
        data: List[Dict[str, Any]] = [{'name': 'STARLINK-1234', 'id': '1234'}]
        
        result = processor.export_to_csv(data, 'test.csv')
        self.assertTrue(result)
        mock_to_csv.assert_called_once_with('test.csv', index=False)
    
    @patch('pandas.DataFrame.to_csv')
    def test_export_to_csv_empty_data(self, mock_to_csv):
        """Test CSV export with empty data."""
        processor = DataProcessor(self.test_config)
        result = processor.export_to_csv([], 'test.csv')
        self.assertFalse(result)
        mock_to_csv.assert_not_called()
    
    @patch('builtins.open', new_callable=mock_open)
    def test_export_to_json_success(self, mock_file):
        """Test successful JSON export."""
        processor = DataProcessor(self.test_config)
        data: List[Dict[str, Any]] = [{'name': 'STARLINK-1234', 'id': '1234'}]
        
        result = processor.export_to_json(data, 'test.json')
        self.assertTrue(result)
        mock_file.assert_called()
    
    @patch('builtins.open', new_callable=mock_open)
    def test_export_to_json_empty_data(self, mock_file):
        """Test JSON export with empty data."""
        processor = DataProcessor(self.test_config)
        result = processor.export_to_json([], 'test.json')
        self.assertFalse(result)
        mock_file.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)