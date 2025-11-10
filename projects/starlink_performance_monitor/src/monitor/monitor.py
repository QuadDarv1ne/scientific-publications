#!/usr/bin/env python3
"""
Starlink Performance Monitor
Main monitoring application that collects and stores performance metrics.
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
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# Add project root to path for imports
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import setup_logging, get_logger

# Configure logging
setup_logging(config_file=os.path.join(os.path.dirname(__file__), '..', 'utils', 'logging_config.json'))
logger = get_logger(__name__)

Base = declarative_base()

class PerformanceMetric(Base):
    """ORM model for performance metrics"""
    __tablename__ = 'performance_metrics'
    
    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    download_mbps = Column(Float)
    upload_mbps = Column(Float)
    ping_ms = Column(Float)
    packet_loss_percent = Column(Float)  # Added packet loss tracking
    server_name = Column(String(100))
    location = Column(String(100))

class StarlinkMonitor:
    """Main Starlink performance monitoring class"""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the monitor with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.config = self._load_config(config_path)
        self.db_engine = self._setup_database()
        self.db_session = sessionmaker(bind=self.db_engine)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
            
    def _setup_database(self):
        """Setup database connection."""
        db_config = self.config.get('database', {})
        db_type = db_config.get('type', 'sqlite')
        
        if db_type == 'postgresql':
            db_url = f"postgresql://{db_config.get('user', 'user')}:{db_config.get('password', 'password')}@" \
                     f"{db_config.get('host', 'localhost')}:{db_config.get('port', 5432)}/{db_config.get('name', 'starlink_monitor')}"
        else:
            db_url = "sqlite:///starlink_monitor.db"
            
        engine = create_engine(db_url)
        Base.metadata.create_all(engine)
        return engine
        
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
        Collect all performance metrics.
        
        Returns:
            Dictionary with all collected metrics
        """
        logger.info("Collecting performance metrics...")
        
        try:
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
                'speedtest': speed_results,
                'ping_tests': ping_results
            }
            
            return metrics
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            return {
                'timestamp': datetime.utcnow().isoformat(),
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
        session = self.db_session()
        
        try:
            # Store speedtest results
            speedtest_data = metrics.get('speedtest', {})
            
            # Get packet loss from ping tests (use average of all servers)
            ping_tests = metrics.get('ping_tests', {})
            packet_loss_values = [test.get('packet_loss_percent', 0) for test in ping_tests.values()]
            avg_packet_loss = sum(packet_loss_values) / len(packet_loss_values) if packet_loss_values else 0
            
            metric = PerformanceMetric(
                download_mbps=speedtest_data.get('download_mbps', 0),
                upload_mbps=speedtest_data.get('upload_mbps', 0),
                ping_ms=speedtest_data.get('ping_ms', 0),
                packet_loss_percent=avg_packet_loss,  # Added packet loss tracking
                server_name=speedtest_data.get('server_name', 'Unknown'),
                location='Starlink'
            )
            session.add(metric)
            session.commit()
            logger.info("Metrics stored successfully")
        except Exception as e:
            logger.error(f"Failed to store metrics: {e}")
            session.rollback()
        finally:
            session.close()
            
    def run_monitoring_cycle(self):
        """Run a single monitoring cycle."""
        logger.info("Starting monitoring cycle")
        metrics = self.collect_metrics()
        self.store_metrics(metrics)
        logger.info("Monitoring cycle completed")
        
    def run_continuous_monitoring(self, interval_minutes: int = 15):
        """
        Run continuous monitoring.
        
        Args:
            interval_minutes: Interval between monitoring cycles in minutes
        """
        logger.info(f"Starting continuous monitoring (every {interval_minutes} minutes)")
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
    """Main entry point for the application."""
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--interval', type=int, default=15, help='Monitoring interval in minutes')
    parser.add_argument('--once', action='store_true', help='Run only one monitoring cycle')
    
    args = parser.parse_args()
    
    try:
        monitor = StarlinkMonitor(args.config)
        
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
