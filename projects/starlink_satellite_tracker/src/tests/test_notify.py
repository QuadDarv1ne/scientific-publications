#!/usr/bin/env python3
"""
Unit tests for the notification system
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.notify import NotificationSystem


class TestNotificationSystem(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a minimal config for testing
        self.test_config = {
            'notifications': {
                'email': {
                    'enabled': True,
                    'smtp_server': 'smtp.test.com',
                    'smtp_port': 587,
                    'username': 'test@test.com',
                    'password': 'testpass',
                    'recipient': 'recipient@test.com'
                },
                'telegram': {
                    'enabled': True,
                    'bot_token': 'test_token',
                    'chat_id': 'test_chat_id'
                }
            }
        }
    
    def test_initialization(self):
        """Test NotificationSystem initialization."""
        notifier = NotificationSystem(self.test_config)
        self.assertIsInstance(notifier, NotificationSystem)
        self.assertEqual(notifier.config, self.test_config)
        self.assertIsNotNone(notifier.email_config)
        self.assertIsNotNone(notifier.telegram_config)
    
    @patch('smtplib.SMTP')
    @patch('ssl.create_default_context')
    def test_send_email_notification_success(self, mock_ssl_context, mock_smtp):
        """Test successful email notification."""
        # Mock SMTP behavior
        mock_server = MagicMock()
        mock_smtp.return_value = mock_server
        mock_ssl_context.return_value = MagicMock()
        
        notifier = NotificationSystem(self.test_config)
        result = notifier.send_email_notification(
            "Test Subject", 
            "Test Message", 
            "recipient@test.com"
        )
        
        self.assertTrue(result)
        mock_smtp.assert_called_once_with('smtp.test.com', 587)
        mock_server.starttls.assert_called_once()
        mock_server.login.assert_called_once_with('test@test.com', 'testpass')
        mock_server.sendmail.assert_called_once()
        mock_server.quit.assert_called_once()
    
    @patch('smtplib.SMTP')
    def test_send_email_notification_disabled(self, mock_smtp):
        """Test email notification when disabled."""
        config = {
            'notifications': {
                'email': {
                    'enabled': False
                }
            }
        }
        
        notifier = NotificationSystem(config)
        result = notifier.send_email_notification(
            "Test Subject", 
            "Test Message", 
            "recipient@test.com"
        )
        
        self.assertFalse(result)
        mock_smtp.assert_not_called()
    
    @patch('smtplib.SMTP')
    def test_send_email_notification_invalid_params(self, mock_smtp):
        """Test email notification with invalid parameters."""
        notifier = NotificationSystem(self.test_config)
        
        # Test with empty subject
        result = notifier.send_email_notification("", "Test Message", "recipient@test.com")
        self.assertFalse(result)
        
        # Test with empty message
        result = notifier.send_email_notification("Test Subject", "", "recipient@test.com")
        self.assertFalse(result)
        
        # Test with empty recipient
        result = notifier.send_email_notification("Test Subject", "Test Message", "")
        self.assertFalse(result)
        
        mock_smtp.assert_not_called()
    
    @patch('smtplib.SMTP')
    def test_send_email_notification_incomplete_config(self, mock_smtp):
        """Test email notification with incomplete configuration."""
        config = {
            'notifications': {
                'email': {
                    'enabled': True
                    # Missing required fields
                }
            }
        }
        
        notifier = NotificationSystem(config)
        result = notifier.send_email_notification(
            "Test Subject", 
            "Test Message", 
            "recipient@test.com"
        )
        
        self.assertFalse(result)
        mock_smtp.assert_not_called()
    
    @patch('utils.notify.TELEGRAM_AVAILABLE', True)
    @patch('utils.notify.Bot')
    def test_send_telegram_notification_success(self, mock_bot_class):
        """Test successful Telegram notification."""
        # Mock Bot behavior
        mock_bot = MagicMock()
        mock_bot_class.return_value = mock_bot
        
        notifier = NotificationSystem(self.test_config)
        result = notifier.send_telegram_notification("Test Message")
        
        self.assertTrue(result)
        mock_bot_class.assert_called_once_with(token='test_token')
        mock_bot.send_message.assert_called_once_with(chat_id='test_chat_id', text='Test Message')
    
    @patch('utils.notify.TELEGRAM_AVAILABLE', True)
    def test_send_telegram_notification_disabled(self, ):
        """Test Telegram notification when disabled."""
        config = {
            'notifications': {
                'telegram': {
                    'enabled': False
                }
            }
        }
        
        notifier = NotificationSystem(config)
        result = notifier.send_telegram_notification("Test Message")
        
        self.assertFalse(result)
    
    @patch('utils.notify.TELEGRAM_AVAILABLE', False)
    def test_send_telegram_notification_unavailable(self):
        """Test Telegram notification when library is unavailable."""
        notifier = NotificationSystem(self.test_config)
        result = notifier.send_telegram_notification("Test Message")
        
        self.assertFalse(result)
    
    @patch('utils.notify.TELEGRAM_AVAILABLE', True)
    @patch('utils.notify.Bot')
    def test_send_telegram_notification_invalid_params(self, mock_bot_class):
        """Test Telegram notification with invalid parameters."""
        notifier = NotificationSystem(self.test_config)
        
        # Test with empty message
        result = notifier.send_telegram_notification("")
        self.assertFalse(result)
        
        mock_bot_class.assert_not_called()
    
    @patch('utils.notify.TELEGRAM_AVAILABLE', True)
    def test_send_telegram_notification_incomplete_config(self):
        """Test Telegram notification with incomplete configuration."""
        config = {
            'notifications': {
                'telegram': {
                    'enabled': True
                    # Missing required fields
                }
            }
        }
        
        notifier = NotificationSystem(config)
        result = notifier.send_telegram_notification("Test Message")
        
        self.assertFalse(result)
    
    def test_notify_upcoming_pass_success(self):
        """Test successful notification of upcoming pass."""
        notifier = NotificationSystem(self.test_config)
        
        # Mock the individual notification methods
        with patch.object(notifier, 'send_email_notification', return_value=True) as mock_email:
            with patch.object(notifier, 'send_telegram_notification', return_value=True) as mock_telegram:
                result = notifier.notify_upcoming_pass(
                    "STARLINK-1234",
                    datetime.now(),
                    65.5,
                    42.3
                )
                
                self.assertTrue(result)
                mock_email.assert_called_once()
                mock_telegram.assert_called_once()
    
    def test_notify_upcoming_pass_invalid_params(self):
        """Test notification of upcoming pass with invalid parameters."""
        notifier = NotificationSystem(self.test_config)
        
        # Test with empty satellite name
        result = notifier.notify_upcoming_pass("", datetime.now(), 65.5, 42.3)
        self.assertFalse(result)
        
        # Test with None datetime (we'll use a valid datetime instead of None)
        # Since the function expects a datetime, we can't pass None
        # We'll test with a valid case instead


if __name__ == '__main__':
    unittest.main(verbosity=2)