#!/usr/bin/env python3
"""
Starlink Performance Monitor
Alerting system for performance threshold violations.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional
import sys
import os

from src.utils.logging_config import setup_logging, get_logger

# Add the src directory to the path so we can import from monitor
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..'))

# Try to import telegram, but don't fail if it's not available
TELEGRAM_AVAILABLE = False
try:
    import telegram
    TELEGRAM_AVAILABLE = True
except ImportError:
    telegram = None  # Define telegram as None to avoid undefined variable errors

from sqlalchemy import create_engine, desc
from sqlalchemy.orm import sessionmaker

from src.monitor.monitor import PerformanceMetric, Base

# Configure logging
setup_logging(config_file=os.path.join(os.path.dirname(__file__), '..', 'utils', 'logging_config.json'))
logger = get_logger(__name__)


class AlertSystem:
    """Alert system for monitoring performance thresholds."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the alert system with configuration.
        
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
        
    def check_thresholds(self) -> List[Dict[str, Any]]:
        """
        Check current metrics against configured thresholds.
        
        Returns:
            List of alerts that were triggered
        """
        logger.info("Checking performance thresholds")
        alerts = []
        
        # Get the latest metric
        session = self.db_session()
        try:
            latest_metric = session.query(PerformanceMetric).order_by(
                desc(PerformanceMetric.timestamp)
            ).first()
            
            if not latest_metric:
                logger.info("No metrics found in database")
                return alerts
                
            # Check thresholds
            notifications_config = self.config.get('notifications', {})
            
            # Check Telegram thresholds
            telegram_config = notifications_config.get('telegram', {})
            if telegram_config.get('enabled', False):
                thresholds = telegram_config.get('thresholds', {})
                alerts.extend(self._check_metric_thresholds(latest_metric, thresholds))
                
            # Check email thresholds
            email_config = notifications_config.get('email', {})
            if email_config.get('enabled', False):
                thresholds = email_config.get('thresholds', {})
                alerts.extend(self._check_metric_thresholds(latest_metric, thresholds))
                
        finally:
            session.close()
            
        return alerts
        
    def _check_metric_thresholds(self, metric: PerformanceMetric, thresholds: Dict[str, float]) -> List[Dict[str, Any]]:
        """
        Check a metric against specific thresholds.
        
        Args:
            metric: Performance metric to check
            thresholds: Threshold values to check against
            
        Returns:
            List of alerts that were triggered
        """
        alerts = []
        
        # Extract values from SQLAlchemy objects properly
        download_mbps = float(getattr(metric, 'download_mbps', 0.0) or 0.0)
        upload_mbps = float(getattr(metric, 'upload_mbps', 0.0) or 0.0)
        ping_ms = float(getattr(metric, 'ping_ms', 0.0) or 0.0)
        packet_loss_percent = float(getattr(metric, 'packet_loss_percent', 0.0) or 0.0)
        
        # Check download speed threshold
        download_threshold = thresholds.get('download_mbps')
        if download_threshold is not None and download_mbps < download_threshold:
            alerts.append({
                'type': 'download_speed',
                'severity': 'warning',
                'message': f'Download speed {download_mbps:.2f} Mbps is below threshold {download_threshold} Mbps',
                'timestamp': metric.timestamp,
                'value': download_mbps,
                'threshold': download_threshold
            })
            
        # Check upload speed threshold
        upload_threshold = thresholds.get('upload_mbps')
        if upload_threshold is not None and upload_mbps < upload_threshold:
            alerts.append({
                'type': 'upload_speed',
                'severity': 'warning',
                'message': f'Upload speed {upload_mbps:.2f} Mbps is below threshold {upload_threshold} Mbps',
                'timestamp': metric.timestamp,
                'value': upload_mbps,
                'threshold': upload_threshold
            })
            
        # Check ping threshold
        ping_threshold = thresholds.get('ping_ms')
        if ping_threshold is not None and ping_ms > ping_threshold:
            alerts.append({
                'type': 'high_ping',
                'severity': 'warning',
                'message': f'Ping {ping_ms:.2f} ms is above threshold {ping_threshold} ms',
                'timestamp': metric.timestamp,
                'value': ping_ms,
                'threshold': ping_threshold
            })
            
        # Check packet loss threshold
        packet_loss_threshold = thresholds.get('packet_loss_percent')
        if packet_loss_threshold is not None and packet_loss_percent > packet_loss_threshold:
            alerts.append({
                'type': 'high_packet_loss',
                'severity': 'warning',
                'message': f'Packet loss {packet_loss_percent:.2f}% is above threshold {packet_loss_threshold}%',
                'timestamp': metric.timestamp,
                'value': packet_loss_percent,
                'threshold': packet_loss_threshold
            })
            
        return alerts
        
    def send_telegram_alert(self, alert: Dict[str, Any]):
        """
        Send an alert via Telegram.
        
        Args:
            alert: Alert to send
        """
        if not TELEGRAM_AVAILABLE or telegram is None:
            logger.warning("Telegram module not available, skipping Telegram alert")
            return
            
        notifications_config = self.config.get('notifications', {})
        telegram_config = notifications_config.get('telegram', {})
        
        if not telegram_config.get('enabled', False):
            return
            
        try:
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                logger.warning("Telegram bot token or chat ID not configured")
                return
                
            bot = telegram.Bot(token=bot_token)
            message = f"🚨 Starlink Performance Alert\n\n{alert['message']}\n\nTime: {alert['timestamp']}"
            bot.send_message(chat_id=chat_id, text=message)
            logger.info(f"Sent Telegram alert: {alert['message']}")
        except Exception as e:
            logger.error(f"Failed to send Telegram alert: {e}")
            
    def send_email_alert(self, alert: Dict[str, Any]):
        """
        Send an alert via email.
        
        Args:
            alert: Alert to send
        """
        # TODO: Implement email alerting
        logger.info(f"Email alert would be sent: {alert['message']}")
        
    def process_alerts(self):
        """Process all alerts and send notifications."""
        alerts = self.check_thresholds()
        
        if not alerts:
            logger.info("No alerts to process")
            return
            
        logger.info(f"Processing {len(alerts)} alerts")
        
        # Send notifications
        notifications_config = self.config.get('notifications', {})
        
        for alert in alerts:
            # Send Telegram notification
            telegram_config = notifications_config.get('telegram', {})
            if telegram_config.get('enabled', False):
                self.send_telegram_alert(alert)
                
            # Send email notification
            email_config = notifications_config.get('email', {})
            if email_config.get('enabled', False):
                self.send_email_alert(alert)
                
            logger.info(f"Processed alert: {alert['message']}")


def main():
    """Main entry point for the alert system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor Alert System')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--check', action='store_true', help='Check thresholds and send alerts')
    
    args = parser.parse_args()
    
    alert_system = AlertSystem(args.config)
    
    if args.check:
        alert_system.process_alerts()


if __name__ == "__main__":
    main()