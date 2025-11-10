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
    
    def setup_scheduled_tasks(self) -> bool:
        """Setup all scheduled tasks based on configuration."""
        try:
            if not self.schedule_config:
                self.logger.warning("No schedule configuration found")
                return False
            
            # Clear any existing scheduled jobs
            schedule.clear()
            
            # Setup TLE update task
            tle_cron = self.schedule_config.get('tle_update_cron', '0 0 */6 * *')
            if tle_cron:
                self._schedule_task(tle_cron, self._update_tle_data, "TLE Update")
            
            # Setup prediction update task
            pred_cron = self.schedule_config.get('prediction_update_cron', '*/30 * * * *')
            if pred_cron:
                self._schedule_task(pred_cron, self._update_predictions, "Prediction Update")
            
            # Setup notification check task
            notif_cron = self.schedule_config.get('notification_check_cron', '*/15 * * * *')
            if notif_cron:
                self._schedule_task(notif_cron, self._check_notifications, "Notification Check")
            
            self.logger.info("Scheduled tasks setup completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Error setting up scheduled tasks: {e}")
            return False
    
    def _schedule_task(self, cron_expression: str, task_function, task_name: str) -> bool:
        """Schedule a task based on cron expression."""
        try:
            # Parse cron expression (simplified version)
            parts = cron_expression.split()
            if len(parts) != 5:
                self.logger.warning(f"Invalid cron expression for {task_name}: {cron_expression}")
                return False
            
            minute, hour, day, month, weekday = parts
            
            # For simplicity, we'll use schedule library's syntax
            # In a real implementation, you might want to use croniter for full cron support
            if cron_expression == '0 0 */6 * *':
                # Every 6 hours
                schedule.every(6).hours.do(task_function).tag(task_name)
            elif cron_expression == '*/30 * * * *':
                # Every 30 minutes
                schedule.every(30).minutes.do(task_function).tag(task_name)
            elif cron_expression == '*/15 * * * *':
                # Every 15 minutes
                schedule.every(15).minutes.do(task_function).tag(task_name)
            else:
                self.logger.warning(f"Unsupported cron expression for {task_name}: {cron_expression}")
                return False
            
            self.logger.info(f"Scheduled {task_name} with cron: {cron_expression}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to schedule {task_name}: {e}")
            return False
    
    def _update_tle_data(self):
        """Update TLE data task."""
        try:
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
            self.logger.info("Starting prediction update task")
            # This would typically update cached predictions
            # For now, we'll just log that the task ran
            self.logger.info("Prediction update completed")
        except Exception as e:
            self.logger.error(f"Prediction update failed: {e}")
    
    def _check_notifications(self):
        """Check and send notifications task."""
        try:
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