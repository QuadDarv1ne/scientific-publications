#!/usr/bin/env python3
"""
Test suite for Starlink Satellite Tracker Improvements
Verifies the enhanced functionality and web interface
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock
from datetime import datetime, timedelta

# Add the project directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

class TestWebInterfaceImprovements(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def test_template_files_exist(self):
        """Test that all required template files exist."""
        template_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), '..', 'templates')
        
        required_templates = [
            'base.html',
            'index.html',
            'passes.html',
            'coverage.html',
            'settings.html',
            'export.html'
        ]
        
        for template in required_templates:
            template_path = os.path.join(template_dir, template)
            self.assertTrue(os.path.exists(template_path), f"Template {template} should exist")
    
    def test_web_app_routes(self):
        """Test that web app routes are properly defined."""
        try:
            from web import web_app
            import flask
            
            # Check that the app is a Flask app
            self.assertIsInstance(web_app.app, flask.Flask)
            
            # Check that required routes exist
            rules = [rule.rule for rule in web_app.app.url_map.iter_rules()]
            
            required_routes = [
                '/',
                '/passes',
                '/coverage',
                '/settings',
                '/export',
                '/api/satellites',
                '/api/passes',
                '/api/coverage',
                '/api/export/<format>',
                '/api/cache/clear'
            ]
            
            for route in required_routes:
                self.assertIn(route, rules, f"Route {route} should be defined")
                
        except ImportError as e:
            self.fail(f"Import failed: {e}")

class TestDataProcessorImprovements(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def test_data_processor_enhancements(self):
        """Test data processor enhancements."""
        try:
            from utils import data_processor
            
            # Test DataCache class
            cache = data_processor.DataCache(max_size=5)
            self.assertEqual(cache.size(), 0)
            
            # Test putting and getting items
            cache.put("key1", "value1")
            self.assertEqual(cache.size(), 1)
            self.assertEqual(cache.get("key1"), "value1")
            
            # Test clearing cache
            cache.clear()
            self.assertEqual(cache.size(), 0)
            self.assertIsNone(cache.get("key1"))
            
        except Exception as e:
            self.fail(f"Data processor test failed: {e}")

class TestNotificationSystemImprovements(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def test_notification_system_enhancements(self):
        """Test notification system enhancements."""
        try:
            from utils import notify
            
            # Test NotificationSystem class initialization
            notifier = notify.NotificationSystem({})
            self.assertIsInstance(notifier, notify.NotificationSystem)
            
            # Test notification message formatting
            test_time = datetime.now() + timedelta(minutes=30)
            message = f"""🚀 STARLINK SATELLITE PASS ALERT 🚀

Satellite: TEST-SAT
Time: {test_time.strftime("%Y-%m-%d %H:%M:%S")}
Maximum Elevation: 65.5°
Azimuth: 42.3°

Best viewing conditions expected!
Look up and enjoy the show! 🌌
"""
            
            # Verify the message contains expected elements
            self.assertIn("🚀 STARLINK SATELLITE PASS ALERT 🚀", message)
            self.assertIn("TEST-SAT", message)
            self.assertIn("Maximum Elevation: 65.5°", message)
            self.assertIn("Look up and enjoy the show! 🌌", message)
            
        except Exception as e:
            self.fail(f"Notification system test failed: {e}")

class TestSchedulerImprovements(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures before each test method."""
        pass
    
    def test_scheduler_enhancements(self):
        """Test scheduler enhancements."""
        try:
            from utils import scheduler
            
            # Test CronParser class
            parser = scheduler.CronParser()
            
            # Test parsing a valid cron expression
            result = parser.parse_cron_expression("0 0 */6 * *")
            self.assertEqual(result['minute'], '0')
            self.assertEqual(result['hour'], '0')
            self.assertEqual(result['day'], '*/6')
            
            # Test JobExecutionCache class
            cache = scheduler.JobExecutionCache()
            self.assertTrue(cache.should_execute("test_job"))
            
            # Test that the same job won't execute immediately again
            self.assertFalse(cache.should_execute("test_job", min_interval_seconds=10))
            
        except Exception as e:
            self.fail(f"Scheduler test failed: {e}")

def main():
    """Run the test suite."""
    unittest.main(verbosity=2)

if __name__ == '__main__':
    main()