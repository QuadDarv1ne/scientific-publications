#!/usr/bin/env python3
"""
Starlink Performance Monitor
Unit tests for core functionality.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock

from monitor import StarlinkMonitor, PerformanceMetric

class TestStarlinkMonitor(unittest.TestCase):
    """Test cases for StarlinkMonitor class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.test_config = {
            "database": {
                "type": "sqlite"
            },
            "monitoring": {
                "starlink": {
                    "servers": [
                        {"host": "8.8.8.8", "name": "Google DNS"},
                        {"host": "1.1.1.1", "name": "Cloudflare"}
                    ]
                }
            }
        }
        
        self.temp_config = tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False)
        json.dump(self.test_config, self.temp_config)
        self.temp_config.close()
        
    def tearDown(self):
        """Tear down test fixtures."""
        os.unlink(self.temp_config.name)
        
    def test_init(self):
        """Test initialization of StarlinkMonitor."""
        monitor = StarlinkMonitor(self.temp_config.name)
        self.assertIsNotNone(monitor)
        self.assertEqual(monitor.config, self.test_config)
        
    def test_load_config(self):
        """Test loading configuration."""
        monitor = StarlinkMonitor(self.temp_config.name)
        config = monitor._load_config(self.temp_config.name)
        self.assertEqual(config, self.test_config)
        
    def test_load_config_missing(self):
        """Test loading missing configuration."""
        monitor = StarlinkMonitor("nonexistent.json")
        config = monitor._load_config("nonexistent.json")
        self.assertEqual(config, {})
        
    @patch('monitor.speedtest.Speedtest')
    def test_run_speedtest(self, mock_speedtest):
        """Test running speedtest."""
        # Mock the speedtest results
        mock_st = MagicMock()
        mock_st.download.return_value = 100_000_000  # 100 Mbps in bits
        mock_st.upload.return_value = 50_000_000     # 50 Mbps in bits
        mock_st.results.ping = 25
        mock_st.results.server = {'name': 'Test Server'}
        mock_speedtest.return_value = mock_st
        
        monitor = StarlinkMonitor(self.temp_config.name)
        results = monitor.run_speedtest()
        
        self.assertEqual(results['download_mbps'], 100.0)
        self.assertEqual(results['upload_mbps'], 50.0)
        self.assertEqual(results['ping_ms'], 25.0)
        self.assertEqual(results['server_name'], 'Test Server')
        
    @patch('monitor.ping3.ping')
    def test_run_ping_test(self, mock_ping):
        """Test running ping test."""
        # Mock successful pings
        mock_ping.return_value = 0.025  # 25ms in seconds
        
        monitor = StarlinkMonitor(self.temp_config.name)
        results = monitor.run_ping_test('8.8.8.8', count=4)
        
        self.assertEqual(results['packet_loss_percent'], 0.0)
        self.assertEqual(results['avg_ping_ms'], 25.0)
        self.assertEqual(results['min_ping_ms'], 25.0)
        self.assertEqual(results['max_ping_ms'], 25.0)
        
    @patch('monitor.ping3.ping')
    def test_run_ping_test_with_loss(self, mock_ping):
        """Test running ping test with packet loss."""
        # Mock some failed pings
        mock_ping.side_effect = [0.025, 0.030, None, 0.035]  # 25%, 30%, fail, 35ms
        
        monitor = StarlinkMonitor(self.temp_config.name)
        results = monitor.run_ping_test('8.8.8.8', count=4)
        
        self.assertEqual(results['packet_loss_percent'], 25.0)
        self.assertEqual(results['avg_ping_ms'], 30.0)  # Average of successful pings
        self.assertEqual(results['min_ping_ms'], 25.0)
        self.assertEqual(results['max_ping_ms'], 35.0)

class TestPerformanceMetric(unittest.TestCase):
    """Test cases for PerformanceMetric ORM model."""
    
    def test_performance_metric_creation(self):
        """Test creating a PerformanceMetric instance."""
        metric = PerformanceMetric(
            download_mbps=100.5,
            upload_mbps=50.2,
            ping_ms=25.3,
            server_name="Test Server",
            location="Starlink"
        )
        
        self.assertEqual(metric.download_mbps, 100.5)
        self.assertEqual(metric.upload_mbps, 50.2)
        self.assertEqual(metric.ping_ms, 25.3)
        self.assertEqual(metric.server_name, "Test Server")
        self.assertEqual(metric.location, "Starlink")

if __name__ == '__main__':
    unittest.main()