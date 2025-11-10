#!/usr/bin/env python3
"""
Unit tests for the scheduler
"""

import unittest
import os
import sys
from unittest.mock import patch, MagicMock

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from utils.scheduler import StarlinkScheduler, CronParser


class TestCronParser(unittest.TestCase):
    
    def test_parse_cron_expression_valid(self):
        """Test parsing valid cron expressions."""
        cron_expr = "0 0 */6 * *"
        result = CronParser.parse_cron_expression(cron_expr)
        
        self.assertEqual(result['minute'], '0')
        self.assertEqual(result['hour'], '0')
        self.assertEqual(result['day'], '*/6')
        self.assertEqual(result['month'], '*')
        self.assertEqual(result['weekday'], '*')
    
    def test_parse_cron_expression_invalid(self):
        """Test parsing invalid cron expressions."""
        with self.assertRaises(ValueError):
            CronParser.parse_cron_expression("0 0 */6 *")  # Missing weekday part
    
    def test_is_simple_interval(self):
        """Test checking for simple intervals."""
        self.assertTrue(CronParser._is_simple_interval('*/15', '*'))
        self.assertTrue(CronParser._is_simple_interval('*/30', '*'))
        self.assertFalse(CronParser._is_simple_interval('0', '*'))
        self.assertFalse(CronParser._is_simple_interval('*/15', '1'))


class TestStarlinkScheduler(unittest.TestCase):
    
    def setUp(self):
        """Set up test fixtures before each test method."""
        # Create a minimal config for testing
        self.test_config = {
            'schedule': {
                'tle_update_cron': '0 0 */6 * *',
                'prediction_update_cron': '*/30 * * * *',
                'notification_check_cron': '*/15 * * * *'
            }
        }
    
    def test_initialization(self):
        """Test StarlinkScheduler initialization."""
        scheduler = StarlinkScheduler(self.test_config)
        self.assertIsInstance(scheduler, StarlinkScheduler)
        self.assertEqual(scheduler.config, self.test_config)
        self.assertFalse(scheduler.running)
    
    @patch('schedule.clear')
    @patch('utils.scheduler.CronParser.cron_to_schedule_job')
    def test_setup_scheduled_tasks_success(self, mock_cron_to_schedule, mock_clear):
        """Test successful setup of scheduled tasks."""
        mock_cron_to_schedule.return_value = True
        mock_clear.return_value = None
        
        scheduler = StarlinkScheduler(self.test_config)
        result = scheduler.setup_scheduled_tasks()
        
        self.assertTrue(result)
        self.assertEqual(mock_cron_to_schedule.call_count, 3)  # Three tasks
        mock_clear.assert_called_once()
    
    @patch('schedule.clear')
    @patch('utils.scheduler.CronParser.cron_to_schedule_job')
    def test_setup_scheduled_tasks_no_config(self, mock_cron_to_schedule, mock_clear):
        """Test setup of scheduled tasks with no config."""
        # Pass a config with no 'schedule' section
        scheduler = StarlinkScheduler({'data_sources': {}})
        result = scheduler.setup_scheduled_tasks()
        
        self.assertFalse(result)
        mock_cron_to_schedule.assert_not_called()
        mock_clear.assert_called_once()
    
    def test_start_scheduler_not_running(self):
        """Test starting scheduler when not already running."""
        scheduler = StarlinkScheduler(self.test_config)
        
        with patch.object(scheduler, 'setup_scheduled_tasks', return_value=True):
            with patch('threading.Thread') as mock_thread:
                mock_thread_instance = MagicMock()
                mock_thread.return_value = mock_thread_instance
                
                result = scheduler.start_scheduler()
                
                self.assertTrue(result)
                self.assertTrue(scheduler.running)
                mock_thread.assert_called_once()
                mock_thread_instance.start.assert_called_once()
    
    def test_start_scheduler_already_running(self):
        """Test starting scheduler when already running."""
        scheduler = StarlinkScheduler(self.test_config)
        scheduler.running = True
        
        result = scheduler.start_scheduler()
        
        self.assertTrue(result)  # Should return True but not start new thread
        # No thread should be created when already running
    
    def test_stop_scheduler_running(self):
        """Test stopping scheduler when running."""
        scheduler = StarlinkScheduler(self.test_config)
        scheduler.running = True
        # Create a mock thread object
        scheduler.thread = MagicMock()
        
        with patch('threading.Thread.join') as mock_join:
            with patch('schedule.clear') as mock_clear:
                result = scheduler.stop_scheduler()
                
                self.assertTrue(result)
                self.assertFalse(scheduler.running)
                scheduler.thread.join.assert_called_once_with(timeout=5)
                mock_clear.assert_called_once()
    
    def test_stop_scheduler_not_running(self):
        """Test stopping scheduler when not running."""
        scheduler = StarlinkScheduler(self.test_config)
        
        with patch('schedule.clear') as mock_clear:
            result = scheduler.stop_scheduler()
            
            self.assertTrue(result)
            self.assertFalse(scheduler.running)
            mock_clear.assert_called_once()
    
    @patch('schedule.get_jobs')
    def test_get_scheduled_jobs_success(self, mock_get_jobs):
        """Test getting scheduled jobs successfully."""
        # Mock job objects
        mock_job1 = MagicMock()
        mock_job1.tags = {'Test Job 1'}
        mock_job1.next_run = '2023-01-01 12:00:00'
        mock_job1.interval = '30 minutes'
        
        mock_job2 = MagicMock()
        mock_job2.tags = {'Test Job 2'}
        mock_job2.next_run = '2023-01-01 13:00:00'
        mock_job2.interval = '1 hour'
        
        mock_get_jobs.return_value = [mock_job1, mock_job2]
        
        scheduler = StarlinkScheduler(self.test_config)
        jobs = scheduler.get_scheduled_jobs()
        
        self.assertEqual(len(jobs), 2)
        self.assertEqual(jobs[0]['name'], 'Test Job 1')
        self.assertEqual(jobs[1]['name'], 'Test Job 2')
    
    @patch('schedule.get_jobs')
    def test_get_scheduled_jobs_exception(self, mock_get_jobs):
        """Test getting scheduled jobs when an exception occurs."""
        mock_get_jobs.side_effect = Exception("Test exception")
        
        scheduler = StarlinkScheduler(self.test_config)
        jobs = scheduler.get_scheduled_jobs()
        
        self.assertEqual(jobs, [])  # Should return empty list on exception


if __name__ == '__main__':
    unittest.main(verbosity=2)