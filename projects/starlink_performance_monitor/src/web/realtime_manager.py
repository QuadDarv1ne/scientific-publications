#!/usr/bin/env python3
"""
Starlink Performance Monitor
Real-time metrics updater manager.
"""

import time
import threading
import logging
from datetime import datetime
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.utils.logging_config import get_logger
from src.monitor.monitor import PerformanceMetric
from src.database.db_manager import get_db_session
from sqlalchemy import desc


class RealTimeUpdater:
    """Real-time metrics updater that sends updates to connected clients."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the real-time updater.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config_path = config_path
        self.running = False
        self.thread = None
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> dict:
        """Load configuration from JSON file."""
        import json
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            return {}
        
    def get_recent_metrics(self, hours: int = 24) -> list:
        """
        Get recent performance metrics.
        
        Args:
            hours: Number of hours of data to retrieve
            
        Returns:
            List with recent metrics
        """
        from src.database.db_manager import get_db_session
        session = get_db_session()
        try:
            # Calculate time threshold
            from datetime import datetime, timedelta
            threshold = datetime.utcnow() - timedelta(hours=hours)
            
            # Query recent metrics
            metrics = session.query(PerformanceMetric).filter(
                PerformanceMetric.timestamp >= threshold
            ).order_by(desc(PerformanceMetric.timestamp)).all()
            
            # Convert to list of dictionaries
            data = [{
                'timestamp': m.timestamp,
                'download_mbps': m.download_mbps,
                'upload_mbps': m.upload_mbps,
                'ping_ms': m.ping_ms,
                'packet_loss_percent': m.packet_loss_percent,
                'server_name': m.server_name
            } for m in metrics]
            
            return data
        except Exception as e:
            self.logger.error(f"Error retrieving metrics from database: {e}")
            return []
        finally:
            session.close()
            
    def start(self):
        """Start the real-time updater in a background thread."""
        if self.running:
            self.logger.warning("Real-time updater is already running")
            return
            
        self.running = True
        self.thread = threading.Thread(target=self._update_loop, daemon=True)
        self.thread.start()
        self.logger.info("Real-time updater started")
        
    def stop(self):
        """Stop the real-time updater."""
        if not self.running:
            self.logger.warning("Real-time updater is not running")
            return
            
        self.running = False
        if self.thread:
            self.thread.join()
        self.logger.info("Real-time updater stopped")
        
    def _update_loop(self):
        """Main update loop that runs in the background thread."""
        while self.running:
            try:
                # Get latest metrics
                metrics_data = self.get_recent_metrics(1)  # Last hour
                
                if metrics_data:
                    latest = metrics_data[0]
                    metrics = {
                        'download_mbps': float(latest['download_mbps']),
                        'upload_mbps': float(latest['upload_mbps']),
                        'ping_ms': float(latest['ping_ms']),
                        'packet_loss_percent': float(latest['packet_loss_percent']),
                        'timestamp': latest['timestamp'].isoformat()
                    }
                    
                    # For now, just log the metrics
                    self.logger.debug(f"Real-time metrics update: {metrics}")
                    
                # Wait before next update
                time.sleep(10)  # Update every 10 seconds
                
            except Exception as e:
                self.logger.error(f"Error in real-time update loop: {e}")
                time.sleep(30)  # Wait longer on error


# Global real-time updater instance
_realtime_updater: RealTimeUpdater | None = None


def start_realtime_updater(config_path: str = "config.json"):
    """
    Start the global real-time updater instance.
    
    Args:
        config_path: Path to configuration file
    """
    global _realtime_updater
    if _realtime_updater is None:
        _realtime_updater = RealTimeUpdater(config_path)
        _realtime_updater.start()


def stop_realtime_updater():
    """Stop the global real-time updater instance."""
    global _realtime_updater
    if _realtime_updater is not None:
        _realtime_updater.stop()
        _realtime_updater = None