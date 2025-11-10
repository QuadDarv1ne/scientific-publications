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

# Import from the new manager instead of web_app
from src.web.realtime_manager import start_realtime_updater, stop_realtime_updater
from src.utils.logging_config import get_logger


# For backward compatibility, re-export the functions
__all__ = ['start_realtime_updater', 'stop_realtime_updater']

if __name__ == "__main__":
    # Test the real-time updater
    logging.basicConfig(level=logging.INFO)
    from src.web.realtime_manager import RealTimeUpdater
    updater = RealTimeUpdater()
    updater.start()
    
    try:
        # Keep the script running
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        updater.stop()