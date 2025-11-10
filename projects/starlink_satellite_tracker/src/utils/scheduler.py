#!/usr/bin/env python3
"""
Scheduler utility for Starlink Satellite Tracker
Handles automated tasks based on cron-like schedules defined in config.json
"""

import schedule
import time
import threading
import logging
from datetime import datetime
import json
import os
from typing import Dict, Any, Optional

# Import our configuration manager
from utils.config_manager import get_config


class JobExecutionCache:
    """Cache for tracking job execution times to prevent duplicate runs."""
    
    def __init__(self):
        self.execution_times = {}
        self.logger = logging.getLogger(__name__)
    
    def should_execute(self, job_name: str, min_interval_seconds: int = 60) -> bool:
        """Check if job should be executed based on last execution time."""
        now = datetime.now()
        if job_name in self.execution_times:
            elapsed = (now - self.execution_times[job_name]).total_seconds()
            if elapsed < min_interval_seconds:
                self.logger.debug(f"Skipping {job_name}, last executed {elapsed:.1f}s ago")
                return False
        
        # Update execution time
        self.execution_times[job_name] = now
        return True
    
    def clear(self) -> None:
        """Clear execution times cache."""
        self.execution_times.clear()


class CronParser:
    """Utility class for parsing cron expressions."""
    
    @staticmethod
    def parse_cron_expression(cron_expression: str) -> Dict[str, str]:
        """
        Parse a cron expression into its components.
        
        Args:
            cron_expression: A cron expression in the format "minute hour day month weekday"
            
        Returns:
            Dictionary with parsed components
        """
        try:
            parts = cron_expression.strip().split()
            if len(parts) != 5:
                raise ValueError(f"Invalid cron expression: {cron_expression}. Expected 5 parts.")
            
            return {
                'minute': parts[0],
                'hour': parts[1],
                'day': parts[2],
                'month': parts[3],
                'weekday': parts[4]
            }
        except Exception as e:
            logging.error(f"Error parsing cron expression '{cron_expression}': {e}")
            raise
    
    @staticmethod
    def cron_to_schedule_job(cron_expression: str, job_function, job_tag: str) -> bool:
        """
        Convert a cron expression to a schedule job.
        
        Args:
            cron_expression: A cron expression
            job_function: The function to schedule
            job_tag: Tag for the job
            
        Returns:
            True if successful, False otherwise
        """
        try:
            parts = cron_expression.strip().split()
            if len(parts) != 5:
                logging.warning(f"Invalid cron expression: {cron_expression}")
                return False
            
            minute, hour, day, month, weekday = parts
            
            # Handle special cases
            if cron_expression == '0 0 */6 * *':
                # Every 6 hours
                schedule.every(6).hours.do(job_function).tag(job_tag)
            elif cron_expression == '*/30 * * * *':
                # Every 30 minutes
                schedule.every(30).minutes.do(job_function).tag(job_tag)
            elif cron_expression == '*/15 * * * *':
                # Every 15 minutes
                schedule.every(15).minutes.do(job_function).tag(job_tag)
            elif cron_expression == '0 0 * * *':
                # Daily at midnight
                schedule.every().day.at("00:00").do(job_function).tag(job_tag)
            elif cron_expression == '0 * * * *':
                # Hourly
                schedule.every().hour.do(job_function).tag(job_tag)
            else:
                # Try to parse more complex expressions
                if CronParser._is_simple_interval(minute, hour):
                    # Simple interval like "*/N * * * *"
                    if minute.startswith('*/') and hour == '*':
                        try:
                            interval = int(minute[2:])
                            if interval > 0:
                                schedule.every(interval).minutes.do(job_function).tag(job_tag)
                                return True
                        except ValueError:
                            pass
                
                # Fall back to basic scheduling if we can't parse
                logging.warning(f"Unsupported cron expression '{cron_expression}', using default 1 hour interval")
                schedule.every().hour.do(job_function).tag(job_tag)
            
            return True
            
        except Exception as e:
            logging.error(f"Error converting cron expression '{cron_expression}' to schedule job: {e}")
            return False
    
    @staticmethod
    def _is_simple_interval(minute: str, hour: str) -> bool:
        """Check if the cron expression represents a simple interval."""
        return minute.startswith('*/') and hour == '*'


class StarlinkScheduler:
    def __init__(self, config: Optional[Dict[str, Any]] = None, tracker=None):
        """Initialize scheduler with configuration and tracker instance."""
        self.config = config or get_config()
        self.tracker = tracker
        self.schedule_config = self.config.get('schedule', {})
        self.running = False
        self.thread = None
        
        # Setup logging
        self.logger = logging.getLogger(__name__)
        logging.basicConfig(level=logging.INFO, 
                          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        
        # Initialize execution cache
        self.execution_cache = JobExecutionCache()
    
    def setup_scheduled_tasks(self) -> bool:
        """Setup all scheduled tasks based on configuration."""
        try:
            if not self.schedule_config or not isinstance(self.schedule_config, dict) or len(self.schedule_config) == 0:
                self.logger.warning("No schedule configuration found")
                return False
            
            # Clear any existing scheduled jobs
            schedule.clear()
            
            # Setup TLE update task
            tle_cron = self.schedule_config.get('tle_update_cron', '0 0 */6 * *')
            if tle_cron:
                if not CronParser.cron_to_schedule_job(tle_cron, self._update_tle_data, "TLE Update"):
                    self.logger.warning(f"Failed to schedule TLE update with cron: {tle_cron}")
                else:
                    self.logger.info(f"Scheduled TLE Update with cron: {tle_cron}")
            
            # Setup prediction update task
            pred_cron = self.schedule_config.get('prediction_update_cron', '*/30 * * * *')
            if pred_cron:
                if not CronParser.cron_to_schedule_job(pred_cron, self._update_predictions, "Prediction Update"):
                    self.logger.warning(f"Failed to schedule Prediction Update with cron: {pred_cron}")
                else:
                    self.logger.info(f"Scheduled Prediction Update with cron: {pred_cron}")
            
            # Setup notification check task
            notif_cron = self.schedule_config.get('notification_check_cron', '*/15 * * * *')
            if notif_cron:
                if not CronParser.cron_to_schedule_job(notif_cron, self._check_notifications, "Notification Check"):
                    self.logger.warning(f"Failed to schedule Notification Check with cron: {notif_cron}")
                else:
                    self.logger.info(f"Scheduled Notification Check with cron: {notif_cron}")
            
            self.logger.info("Scheduled tasks setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up scheduled tasks: {e}")
            return False
    
    def _update_tle_data(self):
        """Update TLE data task."""
        try:
            # Check execution cache to prevent duplicate runs
            if not self.execution_cache.should_execute("TLE Update", 300):  # 5 minutes minimum
                return
            
            self.logger.info("Starting TLE data update task")
            if self.tracker:
                satellites = self.tracker.update_tle_data(force=True)
                self.logger.info(f"TLE data update completed. Loaded {len(satellites) if satellites else 0} satellites")
            else:
                self.logger.warning("No tracker instance available for TLE update")
        except Exception as e:
            self.logger.error(f"TLE data update failed: {e}")
    
    def _update_predictions(self):
        """Update predictions task."""
        try:
            # Check execution cache to prevent duplicate runs
            if not self.execution_cache.should_execute("Prediction Update", 600):  # 10 minutes minimum
                return
            
            self.logger.info("Starting prediction update task")
            # This would typically update cached predictions
            # For now, we'll just log that the task ran
            self.logger.info("Prediction update completed")
        except Exception as e:
            self.logger.error(f"Prediction update failed: {e}")
    
    def _check_notifications(self):
        """Check and send notifications task."""
        try:
            # Check execution cache to prevent duplicate runs
            if not self.execution_cache.should_execute("Notification Check", 300):  # 5 minutes minimum
                return
            
            self.logger.info("Starting notification check task")
            # This would check for upcoming passes and send notifications
            # For now, we'll just log that the task ran
            self.logger.info("Notification check completed")
        except Exception as e:
            self.logger.error(f"Notification check failed: {e}")
    
    def start_scheduler(self) -> bool:
        """Start the scheduler in a background thread."""
        try:
            if self.running:
                self.logger.warning("Scheduler is already running")
                return True
            
            if not self.setup_scheduled_tasks():
                self.logger.error("Failed to setup scheduled tasks")
                return False
            
            self.running = True
            self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
            self.thread.start()
            self.logger.info("Scheduler started")
            return True
            
        except Exception as e:
            self.logger.error(f"Error starting scheduler: {e}")
            self.running = False
            return False
    
    def stop_scheduler(self) -> bool:
        """Stop the scheduler."""
        try:
            if not self.running:
                self.logger.warning("Scheduler is not running")
                return True
            
            self.running = False
            if self.thread:
                self.thread.join(timeout=5)
            schedule.clear()
            self.execution_cache.clear()
            self.logger.info("Scheduler stopped")
            return True
            
        except Exception as e:
            self.logger.error(f"Error stopping scheduler: {e}")
            return False
    
    def _run_scheduler(self):
        """Run the scheduler loop."""
        while self.running:
            try:
                schedule.run_pending()
                time.sleep(1)
            except Exception as e:
                self.logger.error(f"Scheduler error: {e}")
                time.sleep(10)  # Wait longer on error
    
    def get_scheduled_jobs(self) -> list:
        """Get information about scheduled jobs."""
        try:
            jobs = []
            for job in schedule.get_jobs():
                # Handle tags properly
                tags = getattr(job, 'tags', None)
                if tags and isinstance(tags, (set, list)) and len(tags) > 0:
                    name = list(tags)[0] if isinstance(tags, set) else tags[0]
                else:
                    name = 'Unknown'
                
                jobs.append({
                    'name': name,
                    'next_run': getattr(job, 'next_run', None),
                    'interval': str(getattr(job, 'interval', 'Unknown'))
                })
            return jobs
        except Exception as e:
            self.logger.error(f"Error getting scheduled jobs: {e}")
            return []
    
    def clear_cache(self) -> None:
        """Clear the execution cache."""
        self.execution_cache.clear()
        self.logger.info("Scheduler execution cache cleared")


def main():
    """Example usage of the scheduler."""
    # Setup logging
    logging.basicConfig(level=logging.INFO, 
                       format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Initialize scheduler
    scheduler = StarlinkScheduler()
    
    # Start scheduler
    if scheduler.start_scheduler():
        try:
            # Keep the main thread alive
            while True:
                # Show scheduled jobs every 30 seconds
                jobs = scheduler.get_scheduled_jobs()
                if jobs:
                    logging.info("Scheduled jobs:")
                    for job in jobs:
                        logging.info(f"  {job['name']}: Next run at {job['next_run']}")
                
                time.sleep(30)
        except KeyboardInterrupt:
            logging.info("Stopping scheduler...")
            scheduler.stop_scheduler()
    else:
        logging.error("Failed to start scheduler")


if __name__ == "__main__":
    main()