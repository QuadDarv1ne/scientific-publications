# Notification System Documentation

## Overview
The Notification System (`src/utils/notify.py`) provides alerting capabilities for the Starlink Satellite Tracker application. It supports multiple notification channels including email and Telegram, with configurable criteria for when notifications should be sent.

## Class: NotificationSystem

### Constructor
```python
NotificationSystem(config=None)
```

Initializes notification system with configuration.

**Parameters:**
- **config** (dict, optional): Configuration dictionary. If not provided, loads from config.json.

**Attributes:**
- **config** (dict): Configuration settings
- **email_config** (dict): Email notification configuration
- **telegram_config** (dict): Telegram notification configuration
- **logger** (Logger): Module logger

### Methods

#### `send_email_notification(subject, message, recipient)`
Send email notification about satellite pass.

**Parameters:**
- **subject** (str): Email subject
- **message** (str): Email message
- **recipient** (str): Recipient email address

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Checks if email notifications are enabled
2. Validates input parameters
3. Creates email message
4. Establishes SMTP connection
5. Sends email
6. Closes connection
7. Logs result

**Example:**
```python
notifier = NotificationSystem()
success = notifier.send_email_notification(
    "Starlink Pass Alert",
    "Satellite STARLINK-1234 will pass at 18:45",
    "user@example.com"
)
```

#### `send_telegram_notification(message)`
Send Telegram notification about satellite pass.

**Parameters:**
- **message** (str): Notification message

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Checks if Telegram notifications are enabled
2. Validates Telegram library availability
3. Validates input parameters
4. Creates Telegram bot instance
5. Sends message
6. Logs result

**Example:**
```python
success = notifier.send_telegram_notification(
    "Satellite STARLINK-1234 will pass at 18:45"
)
```

#### `notify_upcoming_pass(satellite_name, pass_time, max_elevation, azimuth)`
Send notification about an upcoming satellite pass.

**Parameters:**
- **satellite_name** (str): Satellite name
- **pass_time** (datetime): Pass time
- **max_elevation** (float): Maximum elevation
- **azimuth** (float): Azimuth at maximum elevation

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Validates input parameters
2. Formats notification message
3. Sends email notification if enabled
4. Sends Telegram notification if enabled
5. Logs overall result

**Example:**
```python
from datetime import datetime, timedelta

success = notifier.notify_upcoming_pass(
    "STARLINK-1234",
    datetime.now() + timedelta(minutes=30),
    65.5,
    42.3
)
```

## Usage Examples

### Basic Notification Setup
```python
from src.utils.notify import NotificationSystem

# Initialize notification system
notifier = NotificationSystem()

# Send test notification
success = notifier.notify_upcoming_pass(
    "STARLINK-TEST",
    datetime.now() + timedelta(minutes=45),
    70.2,
    35.8
)

if success:
    print("Notification sent successfully")
else:
    print("Failed to send notification")
```

### Email Configuration
```python
# Enable email notifications in config.json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your_email@gmail.com",
      "password": "your_app_password",  # Use app password for Gmail
      "recipient": "recipient@example.com"
    }
  }
}
```

### Telegram Configuration
```python
# Enable Telegram notifications in config.json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "your_bot_token_here",
      "chat_id": "your_chat_id_here"
    }
  }
}
```

## Configuration

The Notification System uses the following configuration sections:

### notifications
```json
{
  "notifications": {
    "email": {
      "enabled": false,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "",
      "password": "",
      "recipient": ""
    },
    "telegram": {
      "enabled": false,
      "bot_token": "",
      "chat_id": ""
    },
    "min_elevation": 10,
    "min_brightness": -1,
    "advance_notice_minutes": 30
  }
}
```

**Configuration Keys:**

#### Email Settings
- **enabled** (bool): Enable email notifications
- **smtp_server** (str): SMTP server address
- **smtp_port** (int): SMTP server port
- **username** (str): SMTP username
- **password** (str): SMTP password
- **recipient** (str): Notification recipient email

#### Telegram Settings
- **enabled** (bool): Enable Telegram notifications
- **bot_token** (str): Telegram bot token
- **chat_id** (str): Telegram chat ID

#### Notification Criteria
- **min_elevation** (float): Minimum elevation for notifications
- **min_brightness** (float): Minimum brightness for notifications
- **advance_notice_minutes** (int): Minutes before pass for notification

## Integration Points

### With Configuration Manager
```python
from src.utils.config_manager import get_config
from src.utils.notify import NotificationSystem

config = get_config()
notifier = NotificationSystem(config)
```

### With Scheduler
```python
from src.utils.scheduler import StarlinkScheduler
from src.utils.notify import NotificationSystem

notifier = NotificationSystem()
scheduler = StarlinkScheduler()  # Would integrate with notification checks
```

### With Core Tracker
```python
from src.core.main import StarlinkTracker
from src.utils.notify import NotificationSystem

tracker = StarlinkTracker()
notifier = NotificationSystem()

# Use predictions to trigger notifications
passes = tracker.predict_passes(55.7558, 37.6173)
for p in passes:
    # Filter based on criteria
    if p['altitude'] > 10:  # min_elevation
        notifier.notify_upcoming_pass(
            p['satellite'],
            p['time'],
            p['altitude'],
            p['azimuth']
        )
```

## Error Handling

The Notification System includes comprehensive error handling:

1. **SMTP Errors**: Handles connection and authentication failures
2. **Email Validation**: Validates email addresses and content
3. **Telegram Errors**: Manages Telegram API failures
4. **Network Errors**: Handles connectivity issues
5. **Configuration Errors**: Validates configuration on startup

### Example Error Handling
```python
try:
    notifier = NotificationSystem()
    success = notifier.send_email_notification(
        "Test Subject",
        "Test Message",
        "recipient@example.com"
    )
    if not success:
        print("Email notification failed")
except Exception as e:
    print(f"Notification error: {e}")
```

## Dependencies

### Required
- **smtplib**: SMTP email sending
- **ssl**: SSL/TLS encryption for email
- **email.mime**: Email message construction

### Optional
- **python-telegram-bot**: Telegram notification support

## Security Considerations

### Credential Management
1. **Never commit passwords** to version control
2. **Use environment variables** for sensitive data
3. **Use app passwords** for Gmail and similar services
4. **Encrypt configuration** files in production

### Secure Configuration Example
```python
import os

# In config.json, reference environment variables
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "${EMAIL_USERNAME}",
      "password": "${EMAIL_PASSWORD}",
      "recipient": "recipient@example.com"
    }
  }
}

# Set environment variables
# export EMAIL_USERNAME="your_email@gmail.com"
# export EMAIL_PASSWORD="your_app_password"
```

### TLS/SSL Encryption
Email notifications use TLS encryption:
```python
server = smtplib.SMTP(smtp_server, smtp_port)
server.starttls(context=ssl.create_default_context())
```

## Performance Optimization

### Connection Management
1. **Per-message connections**: Creates new SMTP connection for each message
2. **Efficient Telegram**: Uses existing bot instance for messages

### Error Recovery
1. **Graceful failures**: Individual notification failures don't stop others
2. **Retry logic**: Could be extended for retry on transient failures
3. **Logging**: Detailed logging for debugging issues

## Testing

The Notification System includes comprehensive unit tests in `src/tests/test_notify.py` that cover:

1. **Initialization Tests**: Constructor behavior with various configurations
2. **Email Tests**: Email sending functionality
3. **Telegram Tests**: Telegram notification functionality
4. **Pass Notification Tests**: Upcoming pass notifications
5. **Configuration Tests**: Configuration validation
6. **Error Handling Tests**: Various error conditions

### Mocking External Services
```python
import unittest
from unittest.mock import patch, MagicMock

class TestNotificationSystem(unittest.TestCase):
    @patch('smtplib.SMTP')
    def test_send_email_notification_success(self, mock_smtp):
        # Setup mock
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        
        # Test
        notifier = NotificationSystem(self.test_config)
        success = notifier.send_email_notification(
            "Test", "Message", "recipient@example.com"
        )
        
        # Assert
        self.assertTrue(success)
        mock_smtp.assert_called_once()
        mock_server.sendmail.assert_called_once()
```

## Extensibility

The Notification System is designed for easy extension:

1. **Additional Channels**: Add SMS, Slack, or other notification methods
2. **Advanced Formatting**: Implement rich message formatting
3. **Template System**: Add template-based message generation
4. **Delivery Guarantees**: Implement message queuing for guaranteed delivery

### Adding New Notification Channels
```python
def send_sms_notification(self, message, phone_number):
    """Send SMS notification."""
    # Implementation for SMS service
    pass

def send_slack_notification(self, message, channel):
    """Send Slack notification."""
    # Implementation for Slack API
    pass
```

## Best Practices

### When Using This Module

1. **Secure Credentials**: Never store passwords in code or config files
2. **Handle Failures**: Wrap notification calls in try-except blocks
3. **Validate Configuration**: Check configuration before sending notifications
4. **Monitor Delivery**: Log notification attempts and results
5. **Respect Limits**: Don't send too many notifications too quickly

### Email Best Practices

1. **Use App Passwords**: For Gmail and other services with 2FA
2. **Validate Recipients**: Ensure recipient addresses are valid
3. **Meaningful Subjects**: Use clear, descriptive subject lines
4. **Plain Text**: Keep messages simple and readable

### Telegram Best Practices

1. **Bot Permissions**: Ensure bot has permission to send messages
2. **Chat ID Validation**: Verify chat ID is correct
3. **Message Formatting**: Use appropriate formatting for Telegram
4. **Error Handling**: Handle Telegram API rate limits

## Troubleshooting

### Common Issues

1. **Email Authentication Failures**: Check username/password, use app passwords
2. **SMTP Connection Issues**: Verify SMTP server and port settings
3. **Telegram Bot Issues**: Check bot token and chat ID
4. **Network Problems**: Ensure internet connectivity
5. **Configuration Errors**: Validate configuration file syntax

### Debugging

Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs for detailed error information and connection attempts.

### Testing Notifications

Test notification functionality in isolation:
```python
# Test email notification
from src.utils.notify import NotificationSystem

notifier = NotificationSystem()
success = notifier.send_email_notification(
    "Test Subject",
    "Test Message",
    "test@example.com"
)

if success:
    print("Email test successful")
else:
    print("Email test failed")
```

### Verification Steps

1. **Check Configuration**: Verify all settings are correct
2. **Test Connectivity**: Ensure network access to SMTP/Telegram servers
3. **Validate Credentials**: Confirm usernames, passwords, tokens
4. **Review Logs**: Check application logs for detailed error messages
5. **Manual Testing**: Send test messages outside the application

## Advanced Features

### Custom Message Templates
```python
def format_pass_message(self, satellite_name, pass_time, max_elevation, azimuth):
    """Format custom pass notification message."""
    return f"""
🚀 STARLINK PASS ALERT 🚀

Satellite: {satellite_name}
Time: {pass_time.strftime('%Y-%m-%d %H:%M:%S')}
Maximum Elevation: {max_elevation:.1f}°
Azimuth: {azimuth:.1f}°

Best viewing conditions expected!
Look up and enjoy the show! 🌌
"""
```

### Priority Notifications
```python
def send_priority_notification(self, message, priority='normal'):
    """Send notification with priority level."""
    # Implementation for priority-based notifications
    pass
```

### Notification History
```python
def get_notification_history(self):
    """Get history of sent notifications."""
    # Implementation for tracking notification history
    pass
```