# Starlink Satellite Tracker - Project Structure

## Overview
This document describes the organized project structure for the Starlink Satellite Tracker application.

## Directory Structure
```
starlink_satellite_tracker/
├── README.md
├── requirements.txt
├── config.json
├── starlink_tracker.py          # Main entry point
├── PROJECT_STRUCTURE.md         # This file
├── data/
│   └── tle_cache/              # TLE data cache
├── templates/                  # Web templates
│   ├── base.html
│   ├── index.html
│   ├── passes.html
│   ├── coverage.html
│   ├── settings.html
│   └── export.html
└── src/                        # Source code
   ├── __init__.py
   ├── core/                   # Core tracking functionality
   │   ├── __init__.py
   │   └── main.py             # Main tracking logic
   ├── web/                    # Web interface
   │   ├── __init__.py
   │   └── web_app.py          # Flask web application
   ├── utils/                  # Utility modules
   │   ├── __init__.py
   │   ├── config_manager.py   # Centralized configuration management
   │   ├── data_processor.py   # Data handling and export
   │   ├── notify.py           # Notification system
   │   └── scheduler.py        # Automated task scheduler
   └── tests/                  # Test files
       ├── __init__.py
       ├── test_tracker.py     # Unit tests
       └── various demo and test scripts
```

## Module Descriptions

### Core Module (`src/core/`)
- **main.py**: Contains the main StarlinkTracker class with satellite tracking functionality
- Implements TLE data downloading, processing, and satellite position calculations
- Handles configuration loading and error management
- Includes caching mechanisms for performance optimization

### Web Module (`src/web/`)
- **web_app.py**: Flask-based web application with RESTful API
- Provides web interface for satellite tracking, pass predictions, and data visualization
- Includes API endpoints for integration with other systems
- Features caching for API responses and error handling

### Utilities Module (`src/utils/`)
- **config_manager.py**: Centralized configuration management with singleton pattern
- **data_processor.py**: Data handling, analysis, filtering, and export functionality with caching
- **notify.py**: Notification system with email and Telegram support
- **scheduler.py**: Automated task scheduler based on cron expressions with execution cache

### Tests Module (`src/tests/`)
- Contains unit tests and demonstration scripts
- Includes various test files to verify functionality
- Provides examples of how to use different modules

## Key Features of the Structure

1. **Modular Organization**: Clear separation of concerns between core logic, web interface, and utilities
2. **Configuration Management**: Centralized configuration file accessible from all modules
3. **Data Persistence**: Dedicated data directory for caching TLE files
4. **Web Templates**: Separate directory for HTML templates
5. **Testing**: Organized test directory for verification
6. **Entry Point**: Main entry point script for easy execution

## Usage Examples

### Running the Tracker
```bash
python starlink_tracker.py track --help
```

### Starting the Web Interface
```bash
python starlink_tracker.py web
```

### Running Tests
```bash
python -m pytest src/tests/ -v
```

## Benefits of This Structure

1. **Maintainability**: Clear organization makes it easy to locate and modify specific functionality
2. **Scalability**: Modular design allows for easy addition of new features
3. **Testability**: Separation of concerns facilitates comprehensive testing
4. **Deployment**: Organized structure simplifies deployment and packaging
5. **Collaboration**: Clear structure helps team members understand the codebase

## API Documentation

### Core Tracker API (`src/core/main.py`)
- `StarlinkTracker.update_tle_data(force=False)`: Downloads latest TLE data from Celestrak
- `StarlinkTracker.predict_passes(latitude, longitude, altitude=0, hours_ahead=24, min_elevation=10)`: Predicts satellite passes over a location
- `StarlinkTracker.visualize_orbits(hours=2)`: Creates 3D visualization of satellite orbits
- `StarlinkTracker.start_scheduler()`: Starts automated background tasks
- `StarlinkTracker.clear_caches()`: Clears all internal caches

### Configuration Manager API (`src/utils/config_manager.py`)
- `get_config()`: Returns the complete configuration
- `get_config_section(section_name)`: Returns a specific configuration section
- `get_config_value(section, key, default=None)`: Returns a specific configuration value

### Data Processor API (`src/utils/data_processor.py`)
- `DataProcessor.load_satellite_data(filename=None)`: Loads satellite data from TLE files
- `DataProcessor.filter_satellites(satellites, criteria=None)`: Filters satellites by criteria
- `DataProcessor.export_to_csv(data, filename)`: Exports data to CSV format
- `DataProcessor.export_to_json(data, filename)`: Exports data to JSON format
- `DataProcessor.analyze_constellation(satellites)`: Performs basic constellation analysis

### Scheduler API (`src/utils/scheduler.py`)
- `StarlinkScheduler.start_scheduler()`: Starts the background scheduler
- `StarlinkScheduler.stop_scheduler()`: Stops the scheduler
- `StarlinkScheduler.setup_scheduled_tasks()`: Configures scheduled tasks
- `StarlinkScheduler.get_scheduled_jobs()`: Returns information about scheduled jobs

### Notification System API (`src/utils/notify.py`)
- `NotificationSystem.send_email_notification(subject, message, recipient)`: Sends email notifications
- `NotificationSystem.send_telegram_notification(message)`: Sends Telegram notifications
- `NotificationSystem.notify_upcoming_pass(satellite_name, pass_time, max_elevation, azimuth)`: Sends notification about satellite pass

### Web Application API (`src/web/web_app.py`)
- `GET /api/satellites`: Returns current satellite positions
- `GET /api/passes`: Returns predicted satellite passes
- `GET /api/coverage`: Returns global coverage data
- `GET /api/export/<format>`: Exports data in specified format (json, csv)
- `POST /api/cache/clear`: Clears API cache