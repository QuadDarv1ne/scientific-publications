#!/usr/bin/env python3
"""
Starlink Performance Monitor
Unit tests for the alerts module.
"""

import unittest
import json
import tempfile
import os
from datetime import datetime
from typing import Dict, Any
from unittest.mock import patch, MagicMock

from alerts import AlertSystem, PerformanceMetric


class TestAlertSystem(unittest.TestCase):
    """Test cases for AlertSystem class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary config file
        self.test_config: Dict[str, Any] = {
            "database": {
                "type": "sqlite"
            },
            "notifications": {
                "telegram": {
                    "enabled": False,
                    "thresholds": {
                        "download_mbps": 50.0,
                        "upload_mbps": 10.0,
                        "ping_ms": 100.0,
                        "packet_loss_percent": 5.0
                    }
                },
                "email": {
                    "enabled": False,
                    "thresholds": {
                        "download_mbps": 50.0,
                        "upload_mbps": 10.0,
                        "ping_ms": 100.0,
                        "packet_loss_percent": 5.0
                    }
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
        """Test initialization of AlertSystem."""
        alert_system = AlertSystem(self.temp_config.name)
        self.assertIsNotNone(alert_system)
        self.assertEqual(alert_system.config, self.test_config)
        
    def test_load_config(self):
        """Test loading configuration."""
        alert_system = AlertSystem(self.temp_config.name)
        config = alert_system._load_config(self.temp_config.name)
        self.assertEqual(config, self.test_config)
        
    def test_load_config_missing(self):
        """Test loading missing configuration."""
        alert_system = AlertSystem("nonexistent.json")
        config = alert_system._load_config("nonexistent.json")
        self.assertEqual(config, {})
        
    def test_check_metric_thresholds_no_alerts(self):
        """Test checking thresholds when no alerts should be triggered."""
        alert_system = AlertSystem(self.temp_config.name)
        
        # Create a metric that meets all thresholds
        metric = MagicMock()
        metric.download_mbps = 100.0
        metric.upload_mbps = 20.0
        metric.ping_ms = 50.0
        metric.packet_loss_percent = 1.0
        metric.timestamp = datetime.utcnow()
        
        thresholds: Dict[str, float] = {
            "download_mbps": 50.0,
            "upload_mbps": 10.0,
            "ping_ms": 100.0,
            "packet_loss_percent": 5.0
        }
        
        alerts = alert_system._check_metric_thresholds(metric, thresholds)
        self.assertEqual(len(alerts), 0)
        
    def test_check_metric_thresholds_with_alerts(self):
        """Test checking thresholds when alerts should be triggered."""
        alert_system = AlertSystem(self.temp_config.name)
        
        # Create a metric that violates thresholds
        metric = MagicMock()
        metric.download_mbps = 25.0  # Below threshold of 50
        metric.upload_mbps = 5.0     # Below threshold of 10
        metric.ping_ms = 150.0       # Above threshold of 100
        metric.packet_loss_percent = 10.0  # Above threshold of 5
        metric.timestamp = datetime.utcnow()
        
        thresholds: Dict[str, float] = {
            "download_mbps": 50.0,
            "upload_mbps": 10.0,
            "ping_ms": 100.0,
            "packet_loss_percent": 5.0
        }
        
        alerts = alert_system._check_metric_thresholds(metric, thresholds)
        self.assertEqual(len(alerts), 4)
        
        # Check that all alert types are present
        alert_types = [alert['type'] for alert in alerts]
        self.assertIn('download_speed', alert_types)
        self.assertIn('upload_speed', alert_types)
        self.assertIn('high_ping', alert_types)
        self.assertIn('high_packet_loss', alert_types)
        
    def test_send_email_alert(self):
        """Test sending email alerts."""
        alert_system = AlertSystem(self.temp_config.name)
        
        alert = {
            'type': 'download_speed',
            'severity': 'warning',
            'message': 'Download speed 25.00 Mbps is below threshold 50 Mbps',
            'timestamp': datetime.utcnow(),
            'value': 25.0,
            'threshold': 50.0
        }
        
        # This should not raise an exception
        alert_system.send_email_alert(alert)
        
    @patch('alerts.TELEGRAM_AVAILABLE', False)
    def test_send_telegram_alert_telegram_unavailable(self):
        """Test sending Telegram alerts when Telegram is not available."""
        alert_system = AlertSystem(self.temp_config.name)
        
        alert = {
            'type': 'download_speed',
            'severity': 'warning',
            'message': 'Download speed 25.00 Mbps is below threshold 50 Mbps',
            'timestamp': datetime.utcnow(),
            'value': 25.0,
            'threshold': 50.0
        }
        
        # This should not raise an exception
        alert_system.send_telegram_alert(alert)


if __name__ == '__main__':
    unittest.main()