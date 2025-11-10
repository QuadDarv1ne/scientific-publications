#!/usr/bin/env python3
"""
Starlink Performance Monitor
Unit tests for the report generation module.
"""

import unittest
import json
import tempfile
import os
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock
import pandas as pd

from src.reports.generate_report import ReportGenerator, PerformanceMetric


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.test_config = {
            "database": {
                "type": "sqlite"
            }
        }
        
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_config)
        self.temp_config.close()
        
    def tearDown(self):
        """Tear down test fixtures."""
        os.unlink(self.temp_config.name)
        
    def test_init(self):
        """Test initialization of ReportGenerator."""
        with patch('src.reports.generate_report.create_engine') as mock_create_engine:
            generator = ReportGenerator(self.temp_config.name)
            self.assertIsNotNone(generator)
            self.assertEqual(generator.config, self.test_config)
            
    def test_load_config(self):
        """Test loading configuration."""
        with patch('src.reports.generate_report.create_engine') as mock_create_engine:
            generator = ReportGenerator(self.temp_config.name)
            config = generator._load_config(self.temp_config.name)
            self.assertEqual(config, self.test_config)
            
    def test_load_config_missing(self):
        """Test loading missing configuration."""
        with patch('src.reports.generate_report.create_engine') as mock_create_engine:
            generator = ReportGenerator("nonexistent.json")
            config = generator._load_config("nonexistent.json")
            self.assertEqual(config, {})
            
    def test_generate_daily_report(self):
        """Test generating a daily report."""
        with patch('src.reports.generate_report.create_engine') as mock_create_engine, \
             patch.object(ReportGenerator, 'get_metrics_for_period') as mock_get_metrics:
            
            # Mock metrics data
            mock_metrics_data = [
                {
                    'timestamp': datetime(2025, 11, 10, 10, 0, 0),
                    'download_mbps': 100.0,
                    'upload_mbps': 50.0,
                    'ping_ms': 25.0,
                    'packet_loss_percent': 2.0,
                    'server_name': 'Test Server'
                },
                {
                    'timestamp': datetime(2025, 11, 10, 11, 0, 0),
                    'download_mbps': 95.0,
                    'upload_mbps': 48.0,
                    'ping_ms': 28.0,
                    'packet_loss_percent': 1.5,
                    'server_name': 'Test Server'
                }
            ]
            
            mock_get_metrics.return_value = pd.DataFrame(mock_metrics_data)
            
            generator = ReportGenerator(self.temp_config.name)
            report_date = datetime(2025, 11, 10)
            report = generator.generate_daily_report(report_date)
            
            self.assertEqual(report['date'], '2025-11-10')
            self.assertIn('summary', report)
            self.assertIn('metrics', report)
            self.assertEqual(len(report['metrics']), 2)
            
            # Check summary statistics
            summary = report['summary']
            self.assertEqual(summary['total_tests'], 2)
            self.assertEqual(summary['avg_download_mbps'], 97.5)
            self.assertEqual(summary['avg_upload_mbps'], 49.0)
            self.assertEqual(summary['avg_ping_ms'], 26.5)
            self.assertEqual(summary['avg_packet_loss_percent'], 1.75)
            
    def test_generate_weekly_report(self):
        """Test generating a weekly report."""
        with patch('src.reports.generate_report.create_engine') as mock_create_engine, \
             patch.object(ReportGenerator, 'get_metrics_for_period') as mock_get_metrics:
            
            # Mock metrics data
            mock_metrics_data = [
                {
                    'timestamp': datetime(2025, 11, 10, 10, 0, 0),
                    'download_mbps': 100.0,
                    'upload_mbps': 50.0,
                    'ping_ms': 25.0,
                    'packet_loss_percent': 2.0,
                    'server_name': 'Test Server'
                },
                {
                    'timestamp': datetime(2025, 11, 11, 10, 0, 0),
                    'download_mbps': 95.0,
                    'upload_mbps': 48.0,
                    'ping_ms': 28.0,
                    'packet_loss_percent': 1.5,
                    'server_name': 'Test Server'
                }
            ]
            
            mock_get_metrics.return_value = pd.DataFrame(mock_metrics_data)
            
            generator = ReportGenerator(self.temp_config.name)
            report_date = datetime(2025, 11, 10)  # Monday
            report = generator.generate_weekly_report(report_date)
            
            self.assertIn('week', report)
            self.assertIn('summary', report)
            self.assertIn('metrics', report)
            self.assertEqual(len(report['metrics']), 2)
            
    def test_generate_custom_report(self):
        """Test generating a custom report."""
        with patch('src.reports.generate_report.create_engine') as mock_create_engine, \
             patch.object(ReportGenerator, 'get_metrics_for_period') as mock_get_metrics:
            
            # Mock metrics data
            mock_metrics_data = [
                {
                    'timestamp': datetime(2025, 11, 10, 10, 0, 0),
                    'download_mbps': 100.0,
                    'upload_mbps': 50.0,
                    'ping_ms': 25.0,
                    'packet_loss_percent': 2.0,
                    'server_name': 'Test Server'
                },
                {
                    'timestamp': datetime(2025, 11, 11, 10, 0, 0),
                    'download_mbps': 95.0,
                    'upload_mbps': 48.0,
                    'ping_ms': 28.0,
                    'packet_loss_percent': 1.5,
                    'server_name': 'Test Server'
                }
            ]
            
            mock_get_metrics.return_value = pd.DataFrame(mock_metrics_data)
            
            generator = ReportGenerator(self.temp_config.name)
            start_date = datetime(2025, 11, 10)
            end_date = datetime(2025, 11, 11)
            report = generator.generate_custom_report(start_date, end_date)
            
            self.assertIn('period', report)
            self.assertIn('summary', report)
            self.assertIn('metrics', report)
            self.assertEqual(len(report['metrics']), 2)
            
    def test_save_report_as_json(self):
        """Test saving report as JSON."""
        with patch('src.reports.generate_report.create_engine') as mock_create_engine:
            generator = ReportGenerator(self.temp_config.name)
            
            # Create a temporary output file
            temp_output = tempfile.NamedTemporaryFile(suffix='.json', delete=False)
            temp_output.close()
            
            try:
                report_data = {
                    'test': 'data',
                    'metrics': [{'download_mbps': 100.0}]
                }
                
                generator.save_report_as_json(report_data, temp_output.name)
                
                # Verify the file was created
                self.assertTrue(os.path.exists(temp_output.name))
                
                # Verify the content
                with open(temp_output.name, 'r') as f:
                    saved_data = json.load(f)
                    self.assertEqual(saved_data, report_data)
            finally:
                # Clean up
                if os.path.exists(temp_output.name):
                    os.unlink(temp_output.name)
                    
    def test_save_report_as_csv(self):
        """Test saving report as CSV."""
        with patch('src.reports.generate_report.create_engine') as mock_create_engine:
            generator = ReportGenerator(self.temp_config.name)
            
            # Create a temporary output file
            temp_output = tempfile.NamedTemporaryFile(suffix='.csv', delete=False)
            temp_output.close()
            
            try:
                report_data = {
                    'metrics': [
                        {'timestamp': '2025-11-10T10:00:00', 'download_mbps': 100.0},
                        {'timestamp': '2025-11-10T11:00:00', 'download_mbps': 95.0}
                    ]
                }
                
                generator.save_report_as_csv(report_data, temp_output.name)
                
                # Verify the file was created
                self.assertTrue(os.path.exists(temp_output.name))
                
                # Verify the content
                df = pd.read_csv(temp_output.name)
                self.assertEqual(len(df), 2)
                self.assertIn('timestamp', df.columns)
                self.assertIn('download_mbps', df.columns)
            finally:
                # Clean up
                if os.path.exists(temp_output.name):
                    os.unlink(temp_output.name)

    def test_generate_performance_chart(self):
        """Test generating performance chart."""
        with patch('src.reports.generate_report.create_engine') as mock_create_engine:
            generator = ReportGenerator(self.temp_config.name)
            
            # Test with empty data
            report_data = {'metrics': []}
            generator.generate_performance_chart(report_data, 'test.png')
            
            # Test with sample data
            report_data = {
                'metrics': [
                    {
                        'timestamp': '2025-11-10T10:00:00',
                        'download_mbps': 100.0,
                        'upload_mbps': 50.0,
                        'ping_ms': 25.0,
                        'packet_loss_percent': 2.0
                    }
                ]
            }
            
            # This should not raise an exception
            generator.generate_performance_chart(report_data, 'test.png')


if __name__ == '__main__':
    unittest.main()