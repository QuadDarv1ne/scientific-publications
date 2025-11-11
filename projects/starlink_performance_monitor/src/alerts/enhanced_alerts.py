#!/usr/bin/env python3
"""
Starlink Performance Monitor
Enhanced alerting system with escalation policies.
"""

import json
import logging
from datetime import datetime, timedelta, UTC
from typing import Dict, Any, List, Optional
import sys
import os

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
from src.database.db_manager import get_database_manager, get_db_session
from src.utils.logging_config import get_logger


class Alert:
    """Represents an alert with escalation tracking."""
    
    def __init__(self, alert_data: Dict[str, Any]):
        """
        Initialize an alert.
        
        Args:
            alert_data: Dictionary containing alert information
        """
        self.type = alert_data.get('type')
        self.severity = alert_data.get('severity', 'warning')
        self.message = alert_data.get('message')
        self.timestamp = alert_data.get('timestamp')
        self.value = alert_data.get('value')
        self.threshold = alert_data.get('threshold')
        self.escalation_level = alert_data.get('escalation_level', 0)
        self.first_occurrence = alert_data.get('first_occurrence', datetime.now(UTC))
        self.last_notification = alert_data.get('last_notification', None)
        self.notification_count = alert_data.get('notification_count', 0)
        
    def to_dict(self) -> Dict[str, Any]:
        """
        Convert alert to dictionary.
        
        Returns:
            Dictionary representation of the alert
        """
        return {
            'type': self.type,
            'severity': self.severity,
            'message': self.message,
            'timestamp': self.timestamp,
            'value': self.value,
            'threshold': self.threshold,
            'escalation_level': self.escalation_level,
            'first_occurrence': self.first_occurrence,
            'last_notification': self.last_notification,
            'notification_count': self.notification_count
        }


class EnhancedAlertSystem:
    """Enhanced alert system with escalation policies."""
    
    def __init__(self, config_path: str = "config.json"):
        """
        Initialize the enhanced alert system with configuration.
        
        Args:
            config_path: Path to configuration file
        """
        self.logger = get_logger(__name__)
        self.config = self._load_config(config_path)
        self.db_manager = get_database_manager(config_path)
        self.db_engine = self.db_manager.get_engine()
        
        # Initialize alert history storage
        self.alert_history = []
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from JSON file."""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            self.logger.warning(f"Config file {config_path} not found, using defaults")
            return {}
            
    def check_thresholds(self) -> List[Alert]:
        """
        Check current metrics against configured thresholds.
        
        Returns:
            List of alerts that were triggered
        """
        self.logger.info("Checking performance thresholds")
        alerts = []
        
        # Get the latest metric
        session = get_db_session()
        try:
            latest_metric = session.query(PerformanceMetric).order_by(
                desc(PerformanceMetric.timestamp)
            ).first()
            
            if not latest_metric:
                self.logger.info("No metrics found in database")
                return alerts
                
            # Check thresholds
            notifications_config = self.config.get('notifications', {})
            
            # Check Telegram thresholds
            telegram_config = notifications_config.get('telegram', {})
            if telegram_config.get('enabled', False):
                thresholds = telegram_config.get('thresholds', {})
                alert_dicts = self._check_metric_thresholds(latest_metric, thresholds)
                alerts.extend([Alert(alert_dict) for alert_dict in alert_dicts])
                
            # Check email thresholds
            email_config = notifications_config.get('email', {})
            if email_config.get('enabled', False):
                thresholds = email_config.get('thresholds', {})
                alert_dicts = self._check_metric_thresholds(latest_metric, thresholds)
                alerts.extend([Alert(alert_dict) for alert_dict in alert_dicts])
                
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
        
    def should_escalate(self, alert: Alert) -> bool:
        """
        Determine if an alert should be escalated based on escalation policies.
        
        Args:
            alert: Alert to check for escalation
            
        Returns:
            True if alert should be escalated, False otherwise
        """
        # Get escalation configuration
        notifications_config = self.config.get('notifications', {})
        escalation_config = notifications_config.get('escalation', {})
        
        # If no escalation config, don't escalate
        if not escalation_config:
            return False
            
        # Check if enough time has passed since last notification
        if alert.last_notification:
            time_since_last = datetime.utcnow() - alert.last_notification
            escalation_intervals = escalation_config.get('intervals', [60, 120, 240])  # minutes
            
            if alert.escalation_level < len(escalation_intervals):
                required_interval = timedelta(minutes=escalation_intervals[alert.escalation_level])
                if time_since_last < required_interval:
                    return False
                    
        return True
        
    def escalate_alert(self, alert: Alert) -> Alert:
        """
        Escalate an alert to the next level.
        
        Args:
            alert: Alert to escalate
            
        Returns:
            Escalated alert
        """
        alert.escalation_level += 1
        alert.last_notification = datetime.utcnow()
        alert.notification_count += 1
        return alert
        
    def send_telegram_alert(self, alert: Alert):
        """
        Send an alert via Telegram with escalation support.
        
        Args:
            alert: Alert to send
        """
        if not TELEGRAM_AVAILABLE or telegram is None:
            self.logger.warning("Telegram module not available, skipping Telegram alert")
            return
            
        notifications_config = self.config.get('notifications', {})
        telegram_config = notifications_config.get('telegram', {})
        
        if not telegram_config.get('enabled', False):
            return
            
        try:
            bot_token = telegram_config.get('bot_token')
            chat_id = telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                self.logger.warning("Telegram bot token or chat ID not configured")
                return
                
            bot = telegram.Bot(token=bot_token)
            
            # Add escalation information to message
            escalation_info = ""
            if alert.escalation_level > 0:
                escalation_info = f"\n🚨 ESCALATION LEVEL: {alert.escalation_level}"
                if alert.notification_count > 1:
                    escalation_info += f" (Notification #{alert.notification_count})"
                    
            message = f"🚨 Starlink Performance Alert\n\n{alert.message}{escalation_info}\n\nTime: {alert.timestamp}"
            bot.send_message(chat_id=chat_id, text=message)
            self.logger.info(f"Sent Telegram alert: {alert.message}")
        except Exception as e:
            self.logger.error(f"Failed to send Telegram alert: {e}")
            
    def send_email_alert(self, alert: Alert):
        """
        Send an alert via email with escalation support.
        
        Args:
            alert: Alert to send
        """
        # TODO: Implement email alerting with escalation
        escalation_info = ""
        if alert.escalation_level > 0:
            escalation_info = f" ESCALATION LEVEL: {alert.escalation_level}"
            if alert.notification_count > 1:
                escalation_info += f" (Notification #{alert.notification_count})"
                
        self.logger.info(f"Email alert would be sent: {alert.message}{escalation_info}")
        
    def process_alerts(self):
        """Process all alerts with escalation policies."""
        alerts = self.check_thresholds()
        
        if not alerts:
            self.logger.info("No alerts to process")
            return
            
        self.logger.info(f"Processing {len(alerts)} alerts")
        
        # Process each alert with escalation logic
        for alert in alerts:
            # Check if alert should be escalated
            if self.should_escalate(alert):
                alert = self.escalate_alert(alert)
                
            # Send notifications based on escalation level
            notifications_config = self.config.get('notifications', {})
            
            # Send Telegram notification
            telegram_config = notifications_config.get('telegram', {})
            if telegram_config.get('enabled', False):
                self.send_telegram_alert(alert)
                
            # Send email notification
            email_config = notifications_config.get('email', {})
            if email_config.get('enabled', False):
                self.send_email_alert(alert)
                
            self.logger.info(f"Processed alert: {alert.message}")
            
            # Add to alert history
            self.alert_history.append(alert)
            
            # Keep only recent alert history (last 100 alerts)
            if len(self.alert_history) > 100:
                self.alert_history = self.alert_history[-100:]


def main():
    """Main entry point for the enhanced alert system."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Starlink Performance Monitor Enhanced Alert System')
    parser.add_argument('--config', default='config.json', help='Configuration file path')
    parser.add_argument('--check', action='store_true', help='Check thresholds and send alerts')
    
    args = parser.parse_args()
    
    alert_system = EnhancedAlertSystem(args.config)
    
    if args.check:
        alert_system.process_alerts()


if __name__ == "__main__":
    main()