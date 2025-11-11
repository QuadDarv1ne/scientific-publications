#!/usr/bin/env python3
"""
Notification system for Starlink Satellite Tracker
Sends alerts about upcoming satellite passes via email or Telegram
"""

import smtplib
import ssl
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
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

# Try to import requests for Pushover, but handle if not available
try:
    import requests
    PUSHOVER_AVAILABLE = True
except ImportError:
    PUSHOVER_AVAILABLE = False
    requests = None  # Define requests as None to avoid undefined variable
    logging.warning("requests not available. Pushover notifications disabled.")


class NotificationSystem:
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize notification system with configuration."""
        self.config = config or get_config()
        self.email_config = self.config.get('notifications', {}).get('email', {})
        self.telegram_config = self.config.get('notifications', {}).get('telegram', {})
        self.pushover_config = self.config.get('notifications', {}).get('pushover', {})
        self.notification_config = self.config.get('notifications', {})
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
    
    def send_pushover_notification(self, message: str, title: str = "Starlink Tracker") -> bool:
        """Send Pushover notification about satellite pass."""
        if not self.pushover_config.get('enabled', False):
            self.logger.info("Pushover notifications are disabled")
            return False
            
        if not PUSHOVER_AVAILABLE:
            self.logger.warning("Requests library not available for Pushover")
            return False
            
        try:
            # Validate inputs
            if not message:
                self.logger.error("Message is required for Pushover notification")
                return False
                
            # Validate Pushover configuration
            user_key = self.pushover_config.get('user_key')
            api_token = self.pushover_config.get('api_token')
            
            if not user_key or not api_token:
                self.logger.error("Pushover configuration is incomplete")
                return False
            
            # Send Pushover notification
            pushover_url = "https://api.pushover.net/1/messages.json"
            data = {
                "token": api_token,
                "user": user_key,
                "message": message,
                "title": title
            }
            
            if requests is not None:
                response = requests.post(pushover_url, data=data)
                if response.status_code == 200:
                    self.logger.info("Pushover notification sent")
                    return True
                else:
                    self.logger.error(f"Failed to send Pushover notification: {response.text}")
                    return False
            else:
                self.logger.error("Requests library not available for Pushover notification")
                return False
                
        except Exception as e:
            self.logger.error(f"Failed to send Pushover notification: {e}")
            return False
    
    def should_notify_for_pass(self, satellite_name: str, max_elevation: float, 
                              brightness: float = 0.0, velocity: float = 0.0) -> bool:
        """Determine if a notification should be sent for a satellite pass based on filters."""
        try:
            # Check minimum elevation
            min_elevation = self.notification_config.get('min_elevation', 10)
            if max_elevation < min_elevation:
                self.logger.debug(f"Skipping notification for {satellite_name}: Elevation {max_elevation}° below minimum {min_elevation}°")
                return False
            
            # Check minimum brightness (if provided)
            min_brightness = self.notification_config.get('min_brightness', -1)
            if brightness < min_brightness:
                self.logger.debug(f"Skipping notification for {satellite_name}: Brightness {brightness} below minimum {min_brightness}")
                return False
            
            # Check minimum velocity (if provided)
            min_velocity = self.notification_config.get('min_velocity', 0)
            if velocity > 0 and velocity < min_velocity:
                self.logger.debug(f"Skipping notification for {satellite_name}: Velocity {velocity} km/s below minimum {min_velocity} km/s")
                return False
            
            # Check satellite name filters
            excluded_satellites = self.notification_config.get('excluded_satellites', [])
            if satellite_name in excluded_satellites:
                self.logger.debug(f"Skipping notification for {satellite_name}: Satellite is excluded")
                return False
            
            # Check satellite name patterns
            excluded_patterns = self.notification_config.get('excluded_patterns', [])
            for pattern in excluded_patterns:
                if pattern in satellite_name:
                    self.logger.debug(f"Skipping notification for {satellite_name}: Matches excluded pattern '{pattern}'")
                    return False
            
            # Check for specific included satellites (if specified)
            included_satellites = self.notification_config.get('included_satellites', [])
            if included_satellites and satellite_name not in included_satellites:
                self.logger.debug(f"Skipping notification for {satellite_name}: Satellite not in included list")
                return False
            
            # Check for specific included patterns (if specified)
            included_patterns = self.notification_config.get('included_patterns', [])
            if included_patterns:
                pattern_match = False
                for pattern in included_patterns:
                    if pattern in satellite_name:
                        pattern_match = True
                        break
                if not pattern_match:
                    self.logger.debug(f"Skipping notification for {satellite_name}: Does not match any included pattern")
                    return False
            
            # All filters passed
            return True
            
        except Exception as e:
            self.logger.error(f"Error checking notification filters for {satellite_name}: {e}")
            # If there's an error in filtering, default to allowing notifications
            return True
    
    def notify_upcoming_pass(self, satellite_name: str, pass_time: datetime, 
                           max_elevation: float, azimuth: float, brightness: float = 0.0, velocity: float = 0.0) -> bool:
        """Send notification about an upcoming satellite pass."""
        try:
            # Validate inputs
            if not satellite_name or not pass_time:
                self.logger.error("Satellite name and pass time are required")
                return False
            
            # Check if we should notify based on filters
            if not self.should_notify_for_pass(satellite_name, max_elevation, brightness, velocity):
                self.logger.info(f"Skipping notification for {satellite_name} based on filters")
                return True  # Not an error, just filtered out
            
            # Format message
            time_str = pass_time.strftime("%Y-%m-%d %H:%M:%S")
            message = f"""🚀 STARLINK SATELLITE PASS ALERT 🚀

Satellite: {satellite_name}
Time: {time_str}
Maximum Elevation: {max_elevation:.1f}°
Azimuth: {azimuth:.1f}°
Brightness: {brightness:.1f} mag
Velocity: {velocity:.2f} km/s

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
            
            if self.pushover_config.get('enabled', False):
                pushover_success = self.send_pushover_notification(message, "Starlink Satellite Pass")
                success = success and pushover_success
            
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