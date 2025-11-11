#!/usr/bin/env python3
"""
Starlink Performance Monitor
Prometheus exporter for metrics.

Exports performance metrics in Prometheus format for integration with
monitoring systems like Prometheus + Grafana.

Inspired by: https://github.com/danopstech/starlink_exporter
"""

import sys
import os
from datetime import datetime, UTC, timedelta
from typing import Dict, Any, Optional
import argparse
import time

# Add project root to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.db_manager import get_database_manager, get_db_session
from src.database.models import PerformanceMetric
from src.utils.logging_config import setup_logging, get_logger

# Try to import prometheus_client
try:
    from prometheus_client import start_http_server, Gauge, Counter, Histogram, Info
    PROMETHEUS_AVAILABLE = True
except ImportError:
    PROMETHEUS_AVAILABLE = False
    print("Warning: prometheus_client not installed. Install with: pip install prometheus-client")


# Configure logging
setup_logging()
logger = get_logger(__name__)


class StarlinkPrometheusExporter:
    """
    Prometheus exporter for Starlink performance metrics.
    
    Exposes metrics in Prometheus format on a HTTP endpoint.
    """
    
    def __init__(self, config_path: str = "config.json", port: int = 9817):
        """
        Initialize the Prometheus exporter.
        
        Args:
            config_path: Path to configuration file
            port: HTTP port to expose metrics (default: 9817, same as starlink_exporter)
        """
        if not PROMETHEUS_AVAILABLE:
            raise ImportError("prometheus_client is required. Install with: pip install prometheus-client")
        
        self.config_path = config_path
        self.port = port
        self.db_manager = get_database_manager(config_path)
        
        # Define Prometheus metrics
        self._define_metrics()
        
        logger.info(f"Starlink Prometheus Exporter initialized on port {port}")
    
    def _define_metrics(self):
        """Define all Prometheus metrics."""
        
        # Performance metrics
        self.download_mbps = Gauge(
            'starlink_download_mbps',
            'Download speed in Mbps'
        )
        self.upload_mbps = Gauge(
            'starlink_upload_mbps',
            'Upload speed in Mbps'
        )
        self.ping_ms = Gauge(
            'starlink_ping_ms',
            'Ping latency in milliseconds'
        )
        self.packet_loss_percent = Gauge(
            'starlink_packet_loss_percent',
            'Packet loss percentage'
        )
        
        # Starlink-specific metrics (if available)
        self.snr = Gauge(
            'starlink_dish_snr',
            'Signal to Noise Ratio'
        )
        self.obstruction_fraction = Gauge(
            'starlink_dish_fraction_obstruction_ratio',
            'Fraction of sky obstructed'
        )
        self.downlink_throughput_mbps = Gauge(
            'starlink_dish_downlink_throughput_mbps',
            'Dish downlink throughput in Mbps'
        )
        self.uplink_throughput_mbps = Gauge(
            'starlink_dish_uplink_throughput_mbps',
            'Dish uplink throughput in Mbps'
        )
        
        # Monitoring metrics
        self.scrape_duration_seconds = Histogram(
            'starlink_scrape_duration_seconds',
            'Time to scrape metrics from database'
        )
        self.scrape_counter = Counter(
            'starlink_scrape_total',
            'Total number of metric scrapes'
        )
        self.up = Gauge(
            'starlink_up',
            'Was the last scrape successful (1 = success, 0 = failure)'
        )
        
        # Info metric
        self.info = Info(
            'starlink_exporter',
            'Information about the Starlink exporter'
        )
        self.info.info({
            'version': '1.0.0',
            'project': 'starlink_performance_monitor'
        })
        
        logger.info("Prometheus metrics defined")
    
    def update_metrics(self) -> bool:
        """
        Update all Prometheus metrics from the database.
        
        Returns:
            True if successful, False otherwise
        """
        start_time = time.time()
        
        try:
            session = get_db_session(self.config_path)
            
            # Get the most recent metric
            metric = session.query(PerformanceMetric)\
                .order_by(PerformanceMetric.timestamp.desc())\
                .first()
            
            if metric:
                # Update basic performance metrics
                if metric.download_mbps is not None:
                    self.download_mbps.set(metric.download_mbps)
                if metric.upload_mbps is not None:
                    self.upload_mbps.set(metric.upload_mbps)
                if metric.ping_ms is not None:
                    self.ping_ms.set(metric.ping_ms)
                if metric.packet_loss_percent is not None:
                    self.packet_loss_percent.set(metric.packet_loss_percent)
                
                # Update Starlink-specific metrics if available
                if metric.snr is not None:
                    self.snr.set(metric.snr)
                if metric.obstruction_fraction is not None:
                    self.obstruction_fraction.set(metric.obstruction_fraction)
                if metric.downlink_throughput_mbps is not None:
                    self.downlink_throughput_mbps.set(metric.downlink_throughput_mbps)
                if metric.uplink_throughput_mbps is not None:
                    self.uplink_throughput_mbps.set(metric.uplink_throughput_mbps)
                
                # Mark scrape as successful
                self.up.set(1)
                logger.debug(f"Updated metrics from database (timestamp: {metric.timestamp})")
            else:
                logger.warning("No metrics found in database")
                self.up.set(0)
            
            session.close()
            
            # Update scrape metrics
            duration = time.time() - start_time
            self.scrape_duration_seconds.observe(duration)
            self.scrape_counter.inc()
            
            return True
            
        except Exception as e:
            logger.error(f"Error updating metrics: {e}")
            self.up.set(0)
            return False
    
    def run(self, update_interval: int = 3):
        """
        Start the Prometheus HTTP server and continuously update metrics.
        
        Args:
            update_interval: Interval in seconds between metric updates (default: 3s)
        """
        # Start Prometheus HTTP server
        start_http_server(self.port)
        logger.info(f"Prometheus exporter started on http://localhost:{self.port}/metrics")
        logger.info(f"Updating metrics every {update_interval} seconds")
        
        # Continuously update metrics
        while True:
            try:
                self.update_metrics()
                time.sleep(update_interval)
            except KeyboardInterrupt:
                logger.info("Prometheus exporter stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in metrics update loop: {e}")
                time.sleep(update_interval)


def main():
    """Main entry point for the Prometheus exporter."""
    parser = argparse.ArgumentParser(
        description='Starlink Performance Monitor - Prometheus Exporter'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Configuration file path (default: config.json)'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=9817,
        help='HTTP port to expose metrics (default: 9817)'
    )
    parser.add_argument(
        '--interval',
        type=int,
        default=3,
        help='Metrics update interval in seconds (default: 3)'
    )
    
    args = parser.parse_args()
    
    try:
        exporter = StarlinkPrometheusExporter(
            config_path=args.config,
            port=args.port
        )
        exporter.run(update_interval=args.interval)
    except ImportError as e:
        logger.error(f"Import error: {e}")
        print("\nTo use the Prometheus exporter, install prometheus_client:")
        print("pip install prometheus-client")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
