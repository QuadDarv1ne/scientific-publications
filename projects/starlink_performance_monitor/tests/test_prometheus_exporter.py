#!/usr/bin/env python3
"""
Starlink Performance Monitor
Unit tests for Prometheus exporter functionality.
"""

import unittest
import json
import tempfile
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, UTC

# Fix import paths to use src directory
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.database.models import PerformanceMetric


class TestPrometheusExporter(unittest.TestCase):
    """Test cases for Prometheus exporter."""
    
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
        
    def test_prometheus_import(self):
        """Test that prometheus_client can be imported."""
        try:
            from src.exporters.prometheus_exporter import PROMETHEUS_AVAILABLE
            self.assertIsNotNone(PROMETHEUS_AVAILABLE)
            print(f"Prometheus client available: {PROMETHEUS_AVAILABLE}")
        except ImportError as e:
            self.skipTest(f"prometheus_client not installed: {e}")
    
    def test_exporter_initialization(self):
        """Test Prometheus exporter initialization."""
        try:
            # First check if prometheus_client is available
            import prometheus_client
            from src.exporters.prometheus_exporter import StarlinkPrometheusExporter
            
            exporter = StarlinkPrometheusExporter(self.temp_config.name, port=9999)
            self.assertIsNotNone(exporter)
            self.assertEqual(exporter.port, 9999)
            
            print("✓ Prometheus exporter initialization test passed")
        except ImportError:
            self.skipTest("prometheus_client not available")
    
    @patch('src.exporters.prometheus_exporter.get_db_session')
    def test_update_metrics(self, mock_get_session):
        """Test updating Prometheus metrics from database."""
        try:
            # First check if prometheus_client is available
            import prometheus_client
            from src.exporters.prometheus_exporter import StarlinkPrometheusExporter
            
            # Mock database session
            mock_session = MagicMock()
            mock_get_session.return_value = mock_session
            
            # Create a mock metric
            mock_metric = PerformanceMetric(
                download_mbps=100.5,
                upload_mbps=50.2,
                ping_ms=25.3,
                packet_loss_percent=2.1,
                server_name="Test Server",
                snr=15.5,
                obstruction_fraction=0.02
            )
            mock_metric.timestamp = datetime.now(UTC)
            
            # Configure mock query
            mock_query = MagicMock()
            mock_query.order_by.return_value.first.return_value = mock_metric
            mock_session.query.return_value = mock_query
            
            # Create exporter and update metrics
            exporter = StarlinkPrometheusExporter(self.temp_config.name, port=9999)
            result = exporter.update_metrics()
            
            # Verify metrics were updated
            self.assertTrue(result)
            
            print("✓ Prometheus metrics update test passed")
        except ImportError:
            self.skipTest("prometheus_client not available")


if __name__ == '__main__':
    unittest.main()
