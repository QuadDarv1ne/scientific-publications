# Scheduler Documentation

## Overview
The Scheduler (`src/utils/scheduler.py`) provides automated task scheduling for the Starlink Satellite Tracker application. It uses cron-like expressions to schedule recurring tasks and includes execution caching to prevent duplicate runs.

## Class: StarlinkScheduler

### Constructor
```python
StarlinkScheduler(config=None, tracker=None)
```

Initializes scheduler with configuration and tracker instance.

**Parameters:**
- **config** (dict, optional): Configuration dictionary. If not provided, loads from config.json.
- **tracker** (StarlinkTracker, optional): Tracker instance for executing tasks.

**Attributes:**
- **config** (dict): Configuration settings
- **tracker** (StarlinkTracker): Tracker instance
- **schedule_config** (dict): Schedule configuration section
- **running** (bool): Scheduler running status
- **thread** (Thread): Background thread for scheduler
- **logger** (Logger): Module logger
- **execution_cache** (JobExecutionCache): Execution cache to prevent duplicates

### Methods

#### `setup_scheduled_tasks()`
Setup all scheduled tasks based on configuration.

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Clears existing scheduled jobs
2. Sets up TLE update task
3. Sets up prediction update task
4. Sets up notification check task
5. Logs setup completion

**Example:**
```python
scheduler = StarlinkScheduler()
success = scheduler.setup_scheduled_tasks()
if success:
    print("Scheduled tasks setup successfully")
```

#### `start_scheduler()`
Start the scheduler in a background thread.

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Checks if already running
2. Sets up scheduled tasks
3. Starts background thread
4. Begins executing scheduled jobs

**Example:**
```python
scheduler = StarlinkScheduler(tracker=tracker)
if scheduler.start_scheduler():
    print("Scheduler started successfully")
else:
    print("Failed to start scheduler")
```

#### `stop_scheduler()`
Stop the scheduler.

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Checks if running
2. Stops background thread
3. Clears scheduled jobs
4. Clears execution cache

**Example:**
```python
if scheduler.stop_scheduler():
    print("Scheduler stopped successfully")
```

#### `_run_scheduler()`
Run the scheduler loop in background thread.

**Process:**
1. Continuously checks for pending jobs
2. Executes pending jobs
3. Sleeps between checks
4. Handles errors gracefully

#### `get_scheduled_jobs()`
Get information about scheduled jobs.

**Returns:**
- list: Scheduled job information

**Example:**
```python
jobs = scheduler.get_scheduled_jobs()
for job in jobs:
    print(f"Job: {job['name']}, Next run: {job['next_run']}")
```

#### `clear_cache()`
Clear the execution cache.

**Process:**
1. Clears execution cache
2. Logs cache clearing

## Class: CronParser

Utility class for parsing cron expressions.

### Static Methods

#### `parse_cron_expression(cron_expression)`
Parse a cron expression into its components.

**Parameters:**
- **cron_expression** (str): A cron expression in the format "minute hour day month weekday"

**Returns:**
- dict: Dictionary with parsed components

**Example:**
```python
components = CronParser.parse_cron_expression("0 0 */6 * *")
print(components)  # {'minute': '0', 'hour': '0', 'day': '*/6', 'month': '*', 'weekday': '*'}
```

#### `cron_to_schedule_job(cron_expression, job_function, job_tag)`
Convert a cron expression to a schedule job.

**Parameters:**
- **cron_expression** (str): A cron expression
- **job_function**: The function to schedule
- **job_tag** (str): Tag for the job

**Returns:**
- bool: True if successful, False otherwise

**Supported Cron Expressions:**
- `0 0 */6 * *`: Every 6 hours
- `*/30 * * * *`: Every 30 minutes
- `*/15 * * * *`: Every 15 minutes
- `0 0 * * *`: Daily at midnight
- `0 * * * *`: Hourly

## Class: JobExecutionCache

Cache for tracking job execution times to prevent duplicate runs.

### Constructor
```python
JobExecutionCache()
```

**Attributes:**
- **execution_times** (dict): Job name to last execution time mapping
- **logger** (Logger): Module logger

### Methods

#### `should_execute(job_name, min_interval_seconds=60)`
Check if job should be executed based on last execution time.

**Parameters:**
- **job_name** (str): Name of the job
- **min_interval_seconds** (int): Minimum interval between executions (default: 60)

**Returns:**
- bool: True if job should execute, False otherwise

#### `clear()`
Clear execution times cache.

## Usage Examples

### Basic Scheduling
```python
from src.utils.scheduler import StarlinkScheduler
from src.core.main import StarlinkTracker

# Initialize tracker and scheduler
tracker = StarlinkTracker()
scheduler = StarlinkScheduler(tracker=tracker)

# Start scheduler
if scheduler.start_scheduler():
    print("Scheduler started")
    
    # Get scheduled jobs info
    jobs = scheduler.get_scheduled_jobs()
    for job in jobs:
        print(f"Job: {job['name']}")
        
    # Keep running or do other work
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        scheduler.stop_scheduler()
```

### Manual Task Setup
```python
# Setup tasks manually
scheduler = StarlinkScheduler()
if scheduler.setup_scheduled_tasks():
    print("Tasks setup successfully")
```

### Custom Configuration
```python
# Custom schedule configuration
custom_config = {
    'schedule': {
        'tle_update_cron': '0 0 * * *',      # Daily
        'prediction_update_cron': '*/15 * * * *',  # Every 15 minutes
        'notification_check_cron': '*/5 * * * *'   # Every 5 minutes
    }
}

scheduler = StarlinkScheduler(config=custom_config, tracker=tracker)
```

## Cron Expression Support

### Supported Patterns

1. **Every 6 hours**: `0 0 */6 * *`
2. **Every 30 minutes**: `*/30 * * * *`
3. **Every 15 minutes**: `*/15 * * * *`
4. **Daily at midnight**: `0 0 * * *`
5. **Hourly**: `0 * * * *`
6. **Simple intervals**: `*/N * * * *` (every N minutes)

### Cron Format
```
* * * * *
│ │ │ │ │
│ │ │ │ └── Day of week (0-7, Sunday = 0 or 7)
│ │ │ └──── Month (1-12)
│ │ └────── Day of month (1-31)
│ └──────── Hour (0-23)
└────────── Minute (0-59)
```

### Special Characters
- **\***: Any value
- **,**: Value list separator
- **-**: Range of values
- **/**: Step values
- **@reboot**: Run once at startup

## Task Functions

### `_update_tle_data()`
Update TLE data task.

**Process:**
1. Checks execution cache
2. Calls tracker.update_tle_data(force=True)
3. Logs completion

### `_update_predictions()`
Update predictions task.

**Process:**
1. Checks execution cache
2. Performs prediction updates
3. Logs completion

### `_check_notifications()`
Check and send notifications task.

**Process:**
1. Checks execution cache
2. Checks for upcoming passes
3. Sends notifications
4. Logs completion

## Performance Optimization

### Execution Cache
The scheduler uses an execution cache to prevent duplicate runs:

```python
# Prevents same job from running multiple times within minimum interval
if execution_cache.should_execute("TLE Update", 300):  # 5 minutes
    # Execute job
    pass
```

### Background Threading
The scheduler runs in a background thread to avoid blocking the main application:

```python
self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
self.thread.start()
```

### Resource Management
1. Graceful shutdown of background threads
2. Cleanup of scheduled jobs on stop
3. Memory-efficient cache management

## Integration Points

### With Configuration Manager
```python
from src.utils.config_manager import get_config
from src.utils.scheduler import StarlinkScheduler

config = get_config()
scheduler = StarlinkScheduler(config=config)
```

### With Core Tracker
```python
from src.core.main import StarlinkTracker
from src.utils.scheduler import StarlinkScheduler

tracker = StarlinkTracker()
scheduler = StarlinkScheduler(tracker=tracker)
```

## Error Handling

The Scheduler includes comprehensive error handling:

1. **Scheduling Errors**: Handles invalid cron expressions
2. **Execution Errors**: Manages task execution failures
3. **Threading Errors**: Handles background thread issues
4. **Network Errors**: Manages network-related task failures
5. **Resource Errors**: Handles resource cleanup failures

### Example Error Handling
```python
try:
    scheduler = StarlinkScheduler(tracker=tracker)
    if scheduler.start_scheduler():
        print("Scheduler started")
    else:
        print("Failed to start scheduler")
except Exception as e:
    print(f"Scheduler error: {e}")
```

## Testing

The Scheduler includes comprehensive unit tests in `src/tests/test_scheduler.py` that cover:

1. **Initialization Tests**: Constructor behavior with various configurations
2. **Task Setup Tests**: Scheduled task configuration
3. **Execution Tests**: Task execution and caching
4. **Cron Parsing Tests**: Cron expression parsing
5. **Start/Stop Tests**: Scheduler lifecycle management
6. **Error Handling Tests**: Various error conditions

## Dependencies

### Required
- **schedule**: Task scheduling library
- **threading**: Background thread management

## Configuration

The Scheduler uses the following configuration sections:

### schedule
```json
{
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",
    "prediction_update_cron": "*/30 * * * *",
    "notification_check_cron": "*/15 * * * *"
  }
}
```

## Extensibility

The Scheduler is designed for easy extension:

1. **Custom Tasks**: Add new scheduled tasks
2. **Advanced Scheduling**: Implement complex scheduling logic
3. **External Triggers**: Add support for external event triggers
4. **Monitoring**: Add detailed scheduling metrics

## Best Practices

### When Using This Module

1. **Single Instance**: Use one scheduler instance per application
2. **Graceful Shutdown**: Always stop scheduler before application exit
3. **Error Handling**: Wrap scheduler operations in try-except blocks
4. **Logging**: Enable logging to monitor scheduler activity
5. **Resource Management**: Monitor thread and memory usage

### Configuration Tips

1. **Appropriate Intervals**: Set reasonable cron intervals
2. **Resource Consideration**: Consider system resources when scheduling
3. **Backup Plans**: Have fallback mechanisms for critical tasks
4. **Monitoring**: Monitor scheduled job execution

## Troubleshooting

### Common Issues

1. **Tasks Not Running**: Check cron expressions and intervals
2. **Duplicate Execution**: Verify execution cache is working
3. **Threading Issues**: Ensure proper start/stop sequence
4. **Configuration Errors**: Validate schedule configuration

### Debugging

Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs for detailed scheduling information and errors.

### Testing Scheduler

Test scheduler functionality in isolation:
```python
# Test scheduler setup
from src.utils.scheduler import StarlinkScheduler

scheduler = StarlinkScheduler()
if scheduler.setup_scheduled_tasks():
    print("Scheduler tasks setup successfully")
    
    # Check scheduled jobs
    jobs = scheduler.get_scheduled_jobs()
    print(f"Scheduled {len(jobs)} jobs")
```