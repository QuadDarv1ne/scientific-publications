#!/usr/bin/env python3
"""
Test suite for Enhanced Notification System
Verifies the enhanced notification filtering functionality
"""

import unittest
import sys
import os
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add the project directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from utils.notify import NotificationSystem


class TestEnhancedNotificationSystem(unittest.TestCase):
    """Test suite for enhanced notification system."""

    def setUp(self):
        """Set up test fixtures before each test method."""
        self.test_config = {
            'notifications': {
                'email': {
                    'enabled': False,
                    'smtp_server': 'smtp.test.com',
                    'smtp_port': 587,
                    'username': 'test@test.com',
                    'password': 'password',
                    'recipient': 'recipient@test.com'
                },
                'telegram': {
                    'enabled': False,
                    'bot_token': 'test_token',
                    'chat_id': 'test_chat_id'
                },
                'min_elevation': 10,
                'min_brightness': -1,
                'advance_notice_minutes': 30,
                'excluded_satellites': ['STARLINK-TEST'],
                'excluded_patterns': ['DEBRIS', 'TEST']
            }
        }

    def test_notification_system_initialization(self):
        """Test notification system initialization."""
        notifier = NotificationSystem(self.test_config)
        self.assertIsInstance(notifier, NotificationSystem)
        self.assertEqual(notifier.notification_config, self.test_config['notifications'])

    def test_should_notify_for_pass_basic(self):
        """Test basic pass notification filtering."""
        notifier = NotificationSystem(self.test_config)
        
        # Test pass that meets criteria
        should_notify = notifier.should_notify_for_pass(
            "STARLINK-1234", 
            max_elevation=45.0, 
            brightness=1.0
        )
        self.assertTrue(should_notify)
        
        # Test pass below minimum elevation
        should_notify = notifier.should_notify_for_pass(
            "STARLINK-1234", 
            max_elevation=5.0,  # Below min_elevation of 10
            brightness=1.0
        )
        self.assertFalse(should_notify)

    def test_should_notify_for_pass_brightness_filter(self):
        """Test brightness filtering."""
        notifier = NotificationSystem(self.test_config)
        
        # Test pass below minimum brightness
        should_notify = notifier.should_notify_for_pass(
            "STARLINK-1234", 
            max_elevation=45.0,
            brightness=-2.0  # Below min_brightness of -1
        )
        self.assertFalse(should_notify)

    def test_should_notify_for_pass_excluded_satellite(self):
        """Test excluded satellite filtering."""
        notifier = NotificationSystem(self.test_config)
        
        # Test excluded specific satellite
        should_notify = notifier.should_notify_for_pass(
            "STARLINK-TEST",  # Excluded satellite
            max_elevation=45.0,
            brightness=1.0
        )
        self.assertFalse(should_notify)

    def test_should_notify_for_pass_excluded_pattern(self):
        """Test excluded pattern filtering."""
        notifier = NotificationSystem(self.test_config)
        
        # Test satellite matching excluded pattern
        should_notify = notifier.should_notify_for_pass(
            "STARLINK-DEBRIS-123",  # Contains "DEBRIS" pattern
            max_elevation=45.0,
            brightness=1.0
        )
        self.assertFalse(should_notify)
        
        # Test satellite matching another excluded pattern
        should_notify = notifier.should_notify_for_pass(
            "STARLINK-TEST-456",  # Contains "TEST" pattern
            max_elevation=45.0,
            brightness=1.0
        )
        self.assertFalse(should_notify)

    def test_notify_upcoming_pass_filtering(self):
        """Test that notify_upcoming_pass respects filters."""
        notifier = NotificationSystem(self.test_config)
        
        # Mock the actual notification methods to avoid sending real notifications
        with patch.object(notifier, 'send_email_notification', return_value=True) as mock_email, \
             patch.object(notifier, 'send_telegram_notification', return_value=True) as mock_telegram, \
             patch.object(notifier, 'should_notify_for_pass', return_value=False) as mock_filter:
            
            # Call notify_upcoming_pass with parameters that would normally trigger notification
            result = notifier.notify_upcoming_pass(
                "STARLINK-EXCLUDED",  # Should be filtered out
                datetime.now() + timedelta(minutes=15),
                max_elevation=45.0,
                azimuth=120.0,
                brightness=1.0
            )
            
            # Should return True (not an error) but not actually send notifications
            self.assertTrue(result)
            mock_filter.assert_called_once()
            mock_email.assert_not_called()
            mock_telegram.assert_not_called()

    @patch('utils.notify.smtplib.SMTP')
    def test_send_email_notification_disabled(self, mock_smtp):
        """Test email notification when disabled."""
        # Modify config to disable email
        config = self.test_config.copy()
        config['notifications']['email']['enabled'] = False
        notifier = NotificationSystem(config)
        
        result = notifier.send_email_notification(
            "Test Subject", 
            "Test Message", 
            "recipient@test.com"
        )
        
        self.assertFalse(result)
        mock_smtp.assert_not_called()

    def test_send_telegram_notification_disabled(self):
        """Test Telegram notification when disabled."""
        # Modify config to disable telegram
        config = self.test_config.copy()
        config['notifications']['telegram']['enabled'] = False
        notifier = NotificationSystem(config)
        
        result = notifier.send_telegram_notification("Test Message")
        
        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main(verbosity=2)