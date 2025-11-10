#!/usr/bin/env python3
"""
Notification system for Starlink Satellite Tracker
Sends alerts about upcoming satellite passes via email or Telegram
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import requests
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, Optional

# Import our configuration manager
from utils.config_manager import get_config

# Try to import telegram bot, but handle if not available
try:
    from telegram import Bot
    TELEGRAM_AVAILABLE = True
except ImportError:
    TELEGRAM_AVAILABLE = False
    Bot = None  # Define Bot as None to avoid undefined variable
    logging.warning("python-telegram-bot not installed. Telegram notifications disabled.")


class NotificationSystem:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize notification system with configuration."""
        self.config = config or get_config()
        self.email_config = self.config.get('notifications', {}).get('email', {})
        self.telegram_config = self.config.get('notifications', {}).get('telegram', {})
        self.logger = logging.getLogger(__name__)
        
    def send_email_notification(self, subject: str, message: str, recipient: str) -> bool:
        """Send email notification about satellite pass."""
        if not self.email_config.get('enabled', False):
            self.logger.info("Email notifications are disabled")
            return False
            
        try:
            # Validate inputs
            if not subject or not message or not recipient:
                self.logger.error("Invalid email parameters: subject, message, and recipient are required")
                return False
                
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('username', '')
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Validate SMTP configuration
            smtp_server = self.email_config.get('smtp_server')
            smtp_port = self.email_config.get('smtp_port')
            username = self.email_config.get('username')
            password = self.email_config.get('password')
            
            if not smtp_server or not smtp_port or not username or not password:
                self.logger.error("Email configuration is incomplete")
                return False
            
            # Create SMTP session
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls(context=ssl.create_default_context())
            server.login(username, password)
            
            # Send email
            text = msg.as_string()
            server.sendmail(username, recipient, text)
            server.quit()
            
            self.logger.info(f"Email notification sent to {recipient}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to send email notification: {e}")
            return False
    
    def send_telegram_notification(self, message: str) -> bool:
        """Send Telegram notification about satellite pass."""
        if not self.telegram_config.get('enabled', False):
            self.logger.info("Telegram notifications are disabled")
            return False
            
        if not TELEGRAM_AVAILABLE:
            self.logger.warning("Telegram library not available")
            return False
            
        try:
            # Validate inputs
            if not message:
                self.logger.error("Message is required for Telegram notification")
                return False
                
            # Validate Telegram configuration
            bot_token = self.telegram_config.get('bot_token')
            chat_id = self.telegram_config.get('chat_id')
            
            if not bot_token or not chat_id:
                self.logger.error("Telegram configuration is incomplete")
                return False
            
            if Bot is not None:
                bot = Bot(token=bot_token)
                bot.send_message(chat_id=chat_id, text=message)
                self.logger.info("Telegram notification sent")
                return True
            else:
                self.logger.warning("Telegram Bot is not available")
                return False
            
        except Exception as e:
            self.logger.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def notify_upcoming_pass(self, satellite_name: str, pass_time: datetime, 
                           max_elevation: float, azimuth: float) -> bool:
        """Send notification about an upcoming satellite pass."""
        try:
            # Validate inputs
            if not satellite_name or not pass_time:
                self.logger.error("Satellite name and pass time are required")
                return False
                
            # Format message
            time_str = pass_time.strftime("%Y-%m-%d %H:%M:%S")
            message = f"""🚀 STARLINK SATELLITE PASS ALERT 🚀

Satellite: {satellite_name}
Time: {time_str}
Maximum Elevation: {max_elevation:.1f}°
Azimuth: {azimuth:.1f}°

Best viewing conditions expected!
Look up and enjoy the show! 🌌
"""
            
            # Send notifications based on configuration
            success = True
            
            if self.email_config.get('enabled', False):
                recipient = self.email_config.get('recipient', '')
                if recipient:
                    email_success = self.send_email_notification(
                        "Starlink Satellite Pass Alert", 
                        message, 
                        recipient
                    )
                    success = success and email_success
                else:
                    self.logger.warning("Email recipient not configured")
            
            if self.telegram_config.get('enabled', False):
                telegram_success = self.send_telegram_notification(message)
                success = success and telegram_success
            
            if success:
                self.logger.info(f"Notification sent successfully for {satellite_name}")
            else:
                self.logger.warning(f"Some notifications failed for {satellite_name}")
                
            return success
            
        except Exception as e:
            self.logger.error(f"Error sending notification for {satellite_name}: {e}")
            return False


def create_notification_example():
    """Create an example of how to use the notification system."""
    try:
        # Initialize notification system with config
        notifier = NotificationSystem()
        
        # Example notification
        success = notifier.notify_upcoming_pass(
            "STARLINK-1234",
            datetime.now() + timedelta(minutes=45),
            65.5,
            42.3
        )
        
        if success:
            print("Notification example completed successfully")
        else:
            print("Notification example failed")
            
    except Exception as e:
        print(f"Error in notification example: {e}")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Run example
    create_notification_example()