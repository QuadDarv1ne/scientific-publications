#!/usr/bin/env python3
"""
Starlink Performance Monitor
Real-time metrics updater for WebSocket connections.
"""

import time
import threading
import logging
from datetime import datetime
import sys
import os

# Add the src directory to the path so we can import modules
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

from src.web.web_app import socketio, WebApp
from src.utils.logging_config import get_logger


class RealTimeUpdater:
    """Real-time metrics updater that sends updates to connected WebSocket clients."""
    
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
        self.web_app = WebApp(config_path)
        
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
                df = self.web_app.get_recent_metrics(1)  # Last hour
                
                if not df.empty:
                    latest = df.iloc[0]
                    metrics = {
                        'download_mbps': float(latest['download_mbps']),
                        'upload_mbps': float(latest['upload_mbps']),
                        'ping_ms': float(latest['ping_ms']),
                        'packet_loss_percent': float(latest['packet_loss_percent']),
                        'timestamp': latest['timestamp'].isoformat()
                    }
                    
                    # Emit metrics to all connected clients
                    socketio.emit('metrics_update', metrics)
                    self.logger.debug(f"Sent real-time metrics update: {metrics}")
                    
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


if __name__ == "__main__":
    # Test the real-time updater
    logging.basicConfig(level=logging.INFO)
    updater = RealTimeUpdater()
    updater.start()
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        updater.stop()