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
    def __init__(self, config=None):
        """Initialize notification system with configuration."""
        self.config = config or get_config()
        self.email_config = self.config.get('notifications', {}).get('email', {})
        self.telegram_config = self.config.get('notifications', {}).get('telegram', {})
        
    def send_email_notification(self, subject, message, recipient):
        """Send email notification about satellite pass."""
        if not self.email_config.get('enabled', False):
            return False
            
        try:
            # Create message
            msg = MIMEMultipart()
            msg['From'] = self.email_config.get('username')
            msg['To'] = recipient
            msg['Subject'] = subject
            
            msg.attach(MIMEText(message, 'plain'))
            
            # Create SMTP session
            server = smtplib.SMTP(self.email_config.get('smtp_server'), 
                                self.email_config.get('smtp_port'))
            server.starttls(context=ssl.create_default_context())
            server.login(self.email_config.get('username'), 
                        self.email_config.get('password'))
            
            # Send email
            text = msg.as_string()
            server.sendmail(self.email_config.get('username'), recipient, text)
            server.quit()
            
            logging.info(f"Email notification sent to {recipient}")
            return True
            
        except Exception as e:
            logging.error(f"Failed to send email notification: {e}")
            return False
    
    def send_telegram_notification(self, message):
        """Send Telegram notification about satellite pass."""
        if not self.telegram_config.get('enabled', False) or not TELEGRAM_AVAILABLE:
            return False
            
        try:
            if TELEGRAM_AVAILABLE and Bot is not None:
                bot = Bot(token=self.telegram_config.get('bot_token'))
                bot.send_message(chat_id=self.telegram_config.get('chat_id'), text=message)
                logging.info("Telegram notification sent")
                return True
            else:
                logging.warning("Telegram not available, skipping notification")
                return False
            
        except Exception as e:
            logging.error(f"Failed to send Telegram notification: {e}")
            return False
    
    def notify_upcoming_pass(self, satellite_name, pass_time, max_elevation, azimuth):
        """Send notification about an upcoming satellite pass."""
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
            # In a real implementation, you'd have recipient emails configured
            # For now, we'll just log that we would send an email
            logging.info(f"Would send email: {message}")
            # success &= self.send_email_notification(
            #     "Starlink Satellite Pass Alert", 
            #     message, 
            #     self.email_config.get('recipient', '')
            # )
        
        if self.telegram_config.get('enabled', False):
            success &= self.send_telegram_notification(message)
        
        return success


def create_notification_example():
    """Create an example of how to use the notification system."""
    # Initialize notification system with config
    notifier = NotificationSystem()
    
    # Example notification
    notifier.notify_upcoming_pass(
        "STARLINK-1234",
        datetime.now() + timedelta(minutes=45),
        65.5,
        42.3
    )


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Run example
    create_notification_example()