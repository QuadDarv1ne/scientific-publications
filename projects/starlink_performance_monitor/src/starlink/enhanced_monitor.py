"""
Enhanced Starlink Monitor with direct dish integration
Extends the base monitor with direct communication to the Starlink dish via gRPC.
"""

import json
import time
import argparse
import logging
from datetime import datetime
from typing import Dict, Any

import speedtest
import ping3
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, Column, Integer, String, Float, DateTime
from sqlalchemy.orm import sessionmaker

# Add project root to path for imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.database.db_manager import get_database_manager, get_db_session
from src.database.models import Base, PerformanceMetric
from src.utils.logging_config import setup_logging, get_logger
from src.utils.weather_data import WeatherDataCollector
from src.starlink.dish import StarlinkDish

# Configure logging
setup_logging(config_file=os.path.join(os.path.dirname(__file__), '..', 'utils', 'logging_config.json'))
logger = get_logger(__name__)

class EnhancedStarlinkMonitor:
    """Enhanced Starlink performance monitoring class with direct dish integration"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the enhanced monitor with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.db_manager = get_database_manager(config_path)
        self.db_engine = self.db_manager.get_engine()
        self.weather_collector = WeatherDataCollector(config_path)
        self.starlink_dish = StarlinkDish()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
            
    def collect_dish_metrics(self) -> Dict[str, Any]:
        """
        Collect metrics directly from the Starlink dish.
        
        Returns:
            Dictionary with dish metrics
        """
        logger.info("Collecting metrics from Starlink dish...")
        try:
            # Connect to the dish
            if not self.starlink_dish.connect():
                logger.error("Failed to connect to Starlink dish")
                return {}
                
            # Get status
            status = self.starlink_dish.get_status()
            
            # Get history
            history = self.starlink_dish.get_history()
            
            # Disconnect
            self.starlink_dish.disconnect()
            
            # Combine all dish data
            dish_metrics = {
                'status': status,
                'history': history,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            logger.info("Successfully collected dish metrics")
            return dish_metrics
        except Exception as e:
            logger.error(f"Error collecting dish metrics: {e}")
            return {}
            
    def run_speedtest(self) -> Dict[str, Any]:
        """
        Run a speedtest and return results.
        
        Returns:
            Dictionary with speedtest results
        """
        logger.info("Running speedtest...")
        try:
            st = speedtest.Speedtest()
            st.get_best_server()
            
            # Run download test
            download_speed = st.download() / 1_000_000  # Convert to Mbps
            logger.info(f"Download speed: {download_speed:.2f} Mbps")
            
            # Run upload test
            upload_speed = st.upload() / 1_000_000  # Convert to Mbps
            logger.info(f"Upload speed: {upload_speed:.2f} Mbps")
            
            # Get ping
            ping = st.results.ping
            logger.info(f"Ping: {ping:.2f} ms")
            
            return {
                'download_mbps': download_speed,
                'upload_mbps': upload_speed,
                'ping_ms': ping,
                'server_name': st.results.server['name']
            }
        except speedtest.ConfigRetrievalError as e:
            logger.error(f"Speedtest configuration error: {e}")
            return {
                'download_mbps': 0.0,
                'upload_mbps': 0.0,
                'ping_ms': 0.0,
                'server_name': 'Unknown'
            }
        except speedtest.SpeedtestException as e:
            logger.error(f"Speedtest error: {e}")
            return {
                'download_mbps': 0.0,
                'upload_mbps': 0.0,
                'ping_ms': 0.0,
                'server_name': 'Unknown'
            }
        except Exception as e:
            logger.error(f"Unexpected error during speedtest: {e}")
            return {
                'download_mbps': 0.0,
                'upload_mbps': 0.0,
                'ping_ms': 0.0,
                'server_name': 'Unknown'
            }
            
    def run_ping_test(self, host: str = "8.8.8.8", count: int = 10) -> Dict[str, float]:
        """
        Run ping tests to measure latency and packet loss.
        
        Args:
            host: Host to ping
            count: Number of pings to send
            
        Returns:
            Dictionary with ping results
        """
        logger.info(f"Running ping test to {host} ({count} packets)...")
        successful_pings = 0
        total_time = 0
        ping_times = []
        
        for i in range(count):
            try:
                delay = ping3.ping(host, timeout=3)
                if delay is not None:
                    successful_pings += 1
                    total_time += delay * 1000  # Convert to ms
                    ping_times.append(delay * 1000)
                time.sleep(0.1)  # Small delay between pings
            except ping3.PingError as e:
                logger.warning(f"Ping {i+1} failed with ping3 error: {e}")
            except Exception as e:
                logger.warning(f"Ping {i+1} failed with unexpected error: {e}")
                
        packet_loss = ((count - successful_pings) / count) * 100
        avg_ping = total_time / successful_pings if successful_pings > 0 else 0
        
        logger.info(f"Packet loss: {packet_loss:.2f}%, Average ping: {avg_ping:.2f} ms")
        
        return {
            'avg_ping_ms': avg_ping,
            'packet_loss_percent': packet_loss,
            'min_ping_ms': min(ping_times) if ping_times else 0,
            'max_ping_ms': max(ping_times) if ping_times else 0
        }
        
    def collect_metrics(self) -> Dict[str, Any]:
        """
        Collect all performance metrics including direct dish data.
        
        Returns:
            Dictionary with all collected metrics
        """
        logger.info("Collecting all performance metrics...")
        
        try:
            # Collect dish metrics
            dish_metrics = self.collect_dish_metrics()
            
            # Run speedtest
            speed_results = self.run_speedtest()
            
            # Run ping tests to multiple servers
            ping_servers = self.config.get('monitoring', {}).get('starlink', {}).get('servers', [
                {'host': '8.8.8.8', 'name': 'Google DNS'},
                {'host': '1.1.1.1', 'name': 'Cloudflare'}
            ])
            
            ping_results = {}
            for server in ping_servers:
                try:
                    host = server['host']
                    results = self.run_ping_test(host)
                    ping_results[server['name']] = results
                except Exception as e:
                    logger.error(f"Error running ping test for {server['name']}: {e}")
                    ping_results[server['name']] = {
                        'avg_ping_ms': 0,
                        'packet_loss_percent': 0,
                        'min_ping_ms': 0,
                        'max_ping_ms': 0
                    }
                
            # Combine all results
            metrics = {
                'timestamp': datetime.utcnow().isoformat(),
                'dish_metrics': dish_metrics,
                'speedtest': speed_results,
                'ping_tests': ping_results
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
                'dish_metrics': {},
                'speedtest': {
                    'download_mbps': 0.0,
                    'upload_mbps': 0.0,
                    'ping_ms': 0.0,
                    'server_name': 'Unknown'
                },
                'ping_tests': {}
            }
        
    def store_metrics(self, metrics: Dict[str, Any]):
        """
        Store metrics in the database.
        
        Args:
            metrics: Dictionary with metrics to store
        """
        logger.info("Storing metrics in database...")
        session = get_db_session()
        
        try:
            # Extract dish metrics
            dish_metrics = metrics.get('dish_metrics', {}).get('status', {})
            
            # Extract speedtest results
            speedtest_data = metrics.get('speedtest', {})
            
            # Get packet loss from ping tests (use average of all servers)
            ping_tests = metrics.get('ping_tests', {})
            packet_loss_values = [test.get('packet_loss_percent', 0) for test in ping_tests.values()]
            avg_packet_loss = sum(packet_loss_values) / len(packet_loss_values) if packet_loss_values else 0
            
            # Create a comprehensive metric record
            metric = PerformanceMetric(
                download_mbps=speedtest_data.get('download_mbps', 0),
                upload_mbps=speedtest_data.get('upload_mbps', 0),
                ping_ms=speedtest_data.get('ping_ms', 0),
                packet_loss_percent=avg_packet_loss,
                server_name=speedtest_data.get('server_name', 'Unknown'),
                location='Starlink',
                # Add dish-specific metrics
                snr=dish_metrics.get('snr', 0),
                obstruction_fraction=dish_metrics.get('obstruction_fraction', 0),
                downlink_throughput_mbps=dish_metrics.get('downlink_throughput_bps', 0) / 1_000_000,
                uplink_throughput_mbps=dish_metrics.get('uplink_throughput_bps', 0) / 1_000_000
            )
            session.add(metric)
            session.commit()
            logger.info("Metrics stored successfully")
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            session.rollback()
        finally:
            session.close()
        
    def _collect_weather_data(self):
        """Collect weather data for correlation analysis."""
        try:
            logger.info("Collecting weather data")
            weather_data = self.weather_collector.get_weather_data()
            if weather_data:
                logger.info(f"Collected weather data for {len(weather_data['data'])} time points")
            else:
                logger.warning("Failed to collect weather data")
        except Exception as e:
            logger.error(f"Error collecting weather data: {e}")
            
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle."""
        logger.info("Starting enhanced monitoring cycle")
        metrics = self.collect_metrics()
        self.store_metrics(metrics)
        
        # Collect weather data periodically (every 6 cycles = every hour if cycle is 10 min)
        if hasattr(self, '_cycle_count'):
            self._cycle_count += 1
        else:
            self._cycle_count = 1
            
        if self._cycle_count % 6 == 0:  # Every 6th cycle
            self._collect_weather_data()
        
        logger.info("Enhanced monitoring cycle completed")
        
    def run_continuous_monitoring(self, interval_minutes: int = 15):
        """
        Run continuous monitoring.
        
        Args:
            interval_minutes: Interval between monitoring cycles in minutes
        """
        logger.info(f"Starting continuous enhanced monitoring (every {interval_minutes} minutes)")
        while True:
            try:
                self.run_monitoring_cycle()
                logger.info(f"Sleeping for {interval_minutes} minutes")
                time.sleep(interval_minutes * 60)
            except KeyboardInterrupt:
                logger.info("Monitoring stopped by user")
                break
            except Exception as e:
                logger.error(f"Error in monitoring cycle: {e}")
                time.sleep(60)  # Wait 1 minute before retrying

def main():
    """Main entry point for the enhanced application."""
    parser = argparse.ArgumentParser(description='Enhanced Starlink Performance Monitor')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--interval', type=int, default=15, help='Monitoring interval in minutes')
    parser.add_argument('--once', action='store_true', help='Run only one monitoring cycle')
    
    args = parser.parse_args()
    
    try:
        monitor = EnhancedStarlinkMonitor(args.config)
        
        if args.once:
            monitor.run_monitoring_cycle()
        else:
            monitor.run_continuous_monitoring(args.interval)
    except FileNotFoundError:
        logger.error(f"Configuration file {args.config} not found")
        print(f"Error: Configuration file {args.config} not found")
        print("Please create a config.json file or specify the correct path with --config")
        return 1
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Error: {e}")
        return 1
        
    return 0

if __name__ == "__main__":
    exit(main())