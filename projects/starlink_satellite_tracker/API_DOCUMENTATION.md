# Starlink Satellite Tracker - API Documentation

## Overview

This document provides comprehensive documentation for all APIs and modules in the Starlink Satellite Tracker application. The system consists of several interconnected modules that work together to provide satellite tracking, prediction, visualization, and notification capabilities.

## Core Tracker Module (`src/core/main.py`)

### Class: StarlinkTracker

The main class responsible for satellite tracking operations.

#### Constructor
```python
StarlinkTracker(config=None)
```
- **config** (dict, optional): Configuration dictionary. If not provided, loads from config.json.

#### Methods

##### `update_tle_data(force=False)`
Downloads latest TLE data from Celestrak or uses cached data.

**Parameters:**
- **force** (bool): If True, forces download even if cached data exists.

**Returns:**
- List of EarthSatellite objects

**Example:**
```python
tracker = StarlinkTracker()
satellites = tracker.update_tle_data()
```

##### `predict_passes(latitude, longitude, altitude=0, hours_ahead=24, min_elevation=10)`
Predicts satellite passes over a specific location.

**Parameters:**
- **latitude** (float): Observer's latitude (-90 to 90)
- **longitude** (float): Observer's longitude (-180 to 180)
- **altitude** (float): Observer's altitude in meters (default: 0)
- **hours_ahead** (int): Prediction period in hours (default: 24)
- **min_elevation** (float): Minimum elevation for pass detection (default: 10)

**Returns:**
- List of dictionaries with pass information:
  - **satellite** (str): Satellite name
  - **time** (datetime): Pass time
  - **altitude** (float): Maximum altitude in degrees
  - **azimuth** (float): Azimuth at maximum altitude
  - **distance** (float): Distance in kilometers

**Example:**
```python
passes = tracker.predict_passes(55.7558, 37.6173, hours_ahead=48)
```

##### `visualize_orbits(hours=2)`
Creates a 3D visualization of satellite orbits.

**Parameters:**
- **hours** (float): Duration to visualize orbits (default: 2)

**Example:**
```python
tracker.visualize_orbits(hours=3)
```

##### `start_scheduler()`
Starts the automated task scheduler.

**Returns:**
- bool: True if successful, False otherwise

##### `stop_scheduler()`
Stops the automated task scheduler.

**Returns:**
- bool: True if successful, False otherwise

##### `clear_caches()`
Clears all internal caches (TLE cache, prediction cache).

## Configuration Manager (`src/utils/config_manager.py`)

### Functions

##### `get_config()`
Returns the complete configuration dictionary.

**Returns:**
- dict: Complete configuration

##### `get_config_section(section_name)`
Returns a specific configuration section.

**Parameters:**
- **section_name** (str): Name of the configuration section

**Returns:**
- dict: Configuration section

##### `get_config_value(section, key, default=None)`
Returns a specific configuration value.

**Parameters:**
- **section** (str): Configuration section name
- **key** (str): Configuration key
- **default**: Default value if key not found

**Returns:**
- Configuration value

##### `reload_config()`
Reloads configuration from file.

**Returns:**
- dict: Reloaded configuration

## Data Processor (`src/utils/data_processor.py`)

### Class: DataProcessor

Handles data processing, filtering, and export operations.

#### Constructor
```python
DataProcessor(config=None)
```
- **config** (dict, optional): Configuration dictionary

#### Methods

##### `load_satellite_data(filename=None)`
Loads satellite data from TLE files.

**Parameters:**
- **filename** (str, optional): Path to TLE file. If None, uses most recent file.

**Returns:**
- List of dictionaries with satellite data

##### `filter_satellites(satellites, criteria=None)`
Filters satellites based on criteria.

**Parameters:**
- **satellites** (list): List of satellite dictionaries
- **criteria** (dict, optional): Filter criteria

**Returns:**
- Filtered list of satellites

##### `export_to_csv(data, filename)`
Exports data to CSV format.

**Parameters:**
- **data** (list): Data to export
- **filename** (str): Output filename

**Returns:**
- bool: True if successful

##### `export_to_json(data, filename)`
Exports data to JSON format.

**Parameters:**
- **data** (list): Data to export
- **filename** (str): Output filename

**Returns:**
- bool: True if successful

##### `analyze_constellation(satellites)`
Performs basic constellation analysis.

**Parameters:**
- **satellites** (list): List of satellite dictionaries

**Returns:**
- dict: Analysis results

##### `clear_cache()`
Clears data processor cache.

## Scheduler (`src/utils/scheduler.py`)

### Class: StarlinkScheduler

Automated task scheduler based on cron expressions.

#### Constructor
```python
StarlinkScheduler(config=None, tracker=None)
```
- **config** (dict, optional): Configuration dictionary
- **tracker** (StarlinkTracker, optional): Tracker instance

#### Methods

##### `setup_scheduled_tasks()`
Sets up all scheduled tasks based on configuration.

**Returns:**
- bool: True if successful

##### `start_scheduler()`
Starts the scheduler in a background thread.

**Returns:**
- bool: True if successful

##### `stop_scheduler()`
Stops the scheduler.

**Returns:**
- bool: True if successful

##### `get_scheduled_jobs()`
Returns information about scheduled jobs.

**Returns:**
- list: Scheduled job information

##### `clear_cache()`
Clears scheduler execution cache.

## Notification System (`src/utils/notify.py`)

### Class: NotificationSystem

Sends notifications via email or Telegram.

#### Constructor
```python
NotificationSystem(config=None)
```
- **config** (dict, optional): Configuration dictionary

#### Methods

##### `send_email_notification(subject, message, recipient)`
Sends email notification.

**Parameters:**
- **subject** (str): Email subject
- **message** (str): Email message
- **recipient** (str): Recipient email address

**Returns:**
- bool: True if successful

##### `send_telegram_notification(message)`
Sends Telegram notification.

**Parameters:**
- **message** (str): Notification message

**Returns:**
- bool: True if successful

##### `notify_upcoming_pass(satellite_name, pass_time, max_elevation, azimuth)`
Sends notification about upcoming satellite pass.

**Parameters:**
- **satellite_name** (str): Satellite name
- **pass_time** (datetime): Pass time
- **max_elevation** (float): Maximum elevation
- **azimuth** (float): Azimuth at maximum elevation

**Returns:**
- bool: True if successful

## Web Application API (`src/web/web_app.py`)

### RESTful API Endpoints

#### GET `/api/satellites`
Returns current satellite positions.

**Response:**
```json
{
  "satellites": [
    {
      "name": "STARLINK-1234",
      "id": "1234"
    }
  ],
  "count": 100,
  "updated": "2025-11-10T15:30:00"
}
```

#### GET `/api/passes`
Returns predicted satellite passes.

**Query Parameters:**
- **lat** (float): Latitude (default: from config)
- **lon** (float): Longitude (default: from config)
- **hours** (int): Prediction period (default: 24)

**Response:**
```json
{
  "passes": [
    {
      "satellite": "STARLINK-1234",
      "time": "2025-11-10T18:45:23",
      "altitude": 65.5,
      "azimuth": 42.3,
      "distance": 350.2
    }
  ],
  "count": 15,
  "location": {
    "latitude": 55.7558,
    "longitude": 37.6173
  },
  "period_hours": 24
}
```

#### GET `/api/coverage`
Returns global coverage data.

**Response:**
```json
{
  "regions": [
    {
      "name": "North America",
      "satellite_count": 1500,
      "coverage_percentage": 98.5
    }
  ],
  "total_satellites": 2500,
  "global_coverage": 92.1
}
```

#### GET `/api/export/<format>`
Exports data in specified format.

**Path Parameters:**
- **format** (str): Export format (json, csv)

**Response:**
- Data in requested format

#### POST `/api/cache/clear`
Clears API cache.

**Response:**
```json
{
  "message": "Cache cleared successfully"
}
```

### Web Pages

#### `/` (Dashboard)
Main dashboard showing current satellite positions and next pass.

#### `/passes` (Passes)
Calendar view of upcoming satellite passes.

#### `/coverage` (Coverage)
World map showing Starlink coverage.

#### `/settings` (Settings)
Configuration page for observer location and notifications.

#### `/export` (Export)
Page for exporting satellite data.

## Error Handling

All modules include comprehensive error handling with logging. Common error responses include:

- **400 Bad Request**: Invalid parameters
- **404 Not Found**: Resource not found
- **500 Internal Server Error**: Server error

## Caching

The system implements multiple caching layers:

1. **TLE Cache**: Memory cache for TLE data with expiration
2. **Prediction Cache**: Cache for prediction results
3. **API Cache**: Cache for web API responses
4. **Data Processor Cache**: Cache for processed data

Cache TTL values are configurable and vary by data type.

## Configuration Reference

### data_sources
- **celestrak_url**: Primary TLE data source
- **tle_cache_path**: Path for cached TLE files
- **max_cache_days**: Maximum cache age in days
- **backup_urls**: List of backup TLE sources

### visualization
- **orbit_points**: Number of points in orbit visualization
- **earth_texture**: Path to Earth texture file
- **show_ground_track**: Whether to show ground track
- **color_scheme**: Color scheme for visualizations
- **plotly_3d**: Enable Plotly 3D visualization
- **matplotlib_2d**: Enable Matplotlib 2D visualization

### schedule
- **tle_update_cron**: Cron expression for TLE updates
- **prediction_update_cron**: Cron expression for prediction updates
- **notification_check_cron**: Cron expression for notification checks

### observer
- **default_latitude**: Default observer latitude
- **default_longitude**: Default observer longitude
- **default_altitude**: Default observer altitude
- **timezone**: Observer timezone

### notifications
- **email.enabled**: Enable email notifications
- **email.smtp_server**: SMTP server address
- **email.smtp_port**: SMTP server port
- **email.username**: SMTP username
- **email.password**: SMTP password
- **email.recipient**: Notification recipient
- **telegram.enabled**: Enable Telegram notifications
- **telegram.bot_token**: Telegram bot token
- **telegram.chat_id**: Telegram chat ID
- **min_elevation**: Minimum elevation for notifications
- **min_brightness**: Minimum brightness for notifications
- **advance_notice_minutes**: Minutes before pass for notification

### export
- **default_format**: Default export format
- **include_tle_data**: Include TLE data in exports
- **include_predictions**: Include predictions in exports
- **compress_large_files**: Compress large export files