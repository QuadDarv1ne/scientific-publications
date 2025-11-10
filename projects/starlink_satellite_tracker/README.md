# 🛰️ Starlink Satellite Tracker & Visualizer

![Starlink Tracker Preview](https://via.placeholder.com/800x400?text=Starlink+Tracker+Preview) <!-- Замените на реальный скриншот -->

**Real-time satellite tracking and visualization system for SpaceX Starlink constellation**

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green)](LICENSE)
[![Stars](https://img.shields.io/github/stars/yourusername/starlink-tracker?style=social)](https://github.com/yourusername/starlink-tracker)

## 🚀 Quick Start

```bash
# Clone the repository
git clone <repository-url>

# Install dependencies
pip install -r requirements.txt

# Run the tracker
python starlink_tracker.py track --help

# Start the web interface
python starlink_tracker.py web

# Or run directly from source directories
python src/core/main.py --help
python src/web/web_app.py
```

## 📖 Description

Starlink Satellite Tracker & Visualizer — это Python-приложение для отслеживания спутников Starlink в реальном времени с возможностью 3D-визуализации их орбит и прогнозирования прохождений над вашим местоположением. Проект использует астрономические вычисления для точного расчета позиций спутников и предоставляет интерактивные визуализации для лучшего понимания космического созвездия.

**Key Features:**
- 📡 Automatic download of up-to-date TLE (Two-Line Elements) data from Celestrak
- 🌍 Accurate satellite position calculations using the Skyfield library
- 🗺️ Interactive 3D visualization of satellite orbits
- 📍 Prediction of satellite visibility over your location
- 🔔 Notifications about satellite passes over your region
- 📊 Export data to CSV/JSON for further analysis
- 🌐 Visualization of Starlink coverage on a world map

## 🚀 Features

### 📡 Automatic Data Updates
- Daily download of fresh TLE data from official sources
- Data caching for offline operation
- Error handling when sources are unavailable
- Backup URLs for resilient data fetching

### 🌍 Visibility Calculation
- Determination of satellite rise and set times
- Calculation of altitude and azimuth for optimal observation
- Filtering satellites by minimum height above the horizon
- Consideration of local time and time zones

### 🎨 Visualization
- **3D Orbits**: Interactive visualization in matplotlib/plotly
- **Coverage Map**: Display of current satellite positions on a world map
- **Height Graphs**: Visualization of pass trajectories over the observation point
- **Motion Animation**: Dynamic display of satellite movement

### 🔔 Notification System
- Email notifications about satellite passes
- Push notifications via Telegram bot
- Setting criteria for notifications (minimum height, brightness)

## ⚙️ Requirements

### System Requirements
- Python 3.8 or newer
- 2 GB RAM
- 500 MB free disk space
- Internet connection for downloading TLE data

### Python Dependencies
```bash
skyfield
matplotlib
numpy
pandas
requests
flask
geopy
plotly
dash
schedule
python-telegram-bot
```

Install dependencies with:
```bash
pip install -r requirements.txt
```

## 📚 Module Documentation

### Core Tracker (`src/core/main.py`)
The main module responsible for satellite tracking and calculations.

**Key Methods:**
- `update_tle_data()`: Downloads latest TLE data from Celestrak
- `predict_passes()`: Predicts satellite passes over a location
- `visualize_orbits()`: Creates 3D visualization of satellite orbits
- `start_scheduler()`: Starts automated background tasks
- `clear_caches()`: Clears all internal caches

**Example Usage:**
```python
from src.core.main import StarlinkTracker

# Initialize tracker
tracker = StarlinkTracker()

# Update satellite data
satellites = tracker.update_tle_data()

# Predict passes for Moscow
passes = tracker.predict_passes(latitude=55.7558, longitude=37.6173)

# Visualize orbits
tracker.visualize_orbits()
```

### Configuration Manager (`src/utils/config_manager.py`)
Centralized configuration management system using singleton pattern.

**Key Methods:**
- `get_config()`: Returns the complete configuration
- `get_config_section()`: Returns a specific configuration section
- `get_config_value()`: Returns a specific configuration value
- `reload_config()`: Reloads configuration from file

**Configuration File Structure:**
```json
{
  "data_sources": {
    "celestrak_url": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
    "tle_cache_path": "data/tle_cache/",
    "max_cache_days": 7,
    "backup_urls": [
      "https://celestrak.org/NORAD/elements/starlink.txt",
      "https://www.celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=csv"
    ]
  },
  "visualization": {
    "orbit_points": 100,
    "earth_texture": "data/earth_texture.jpg",
    "show_ground_track": true,
    "color_scheme": "dark",
    "plotly_3d": true,
    "matplotlib_2d": true
  },
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",
    "prediction_update_cron": "*/30 * * * *",
    "notification_check_cron": "*/15 * * * *"
  },
  "observer": {
    "default_latitude": 55.7558,
    "default_longitude": 37.6173,
    "default_altitude": 0,
    "timezone": "Europe/Moscow"
  },
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
  },
  "export": {
    "default_format": "json",
    "include_tle_data": true,
    "include_predictions": true,
    "compress_large_files": true
  }
}
```

### Data Processor (`src/utils/data_processor.py`)
Handles data analysis, filtering, and export functionality with caching.

**Key Methods:**
- `load_satellite_data()`: Loads satellite data from TLE files
- `filter_satellites()`: Filters satellites by criteria
- `export_to_csv()`: Exports data to CSV format
- `export_to_json()`: Exports data to JSON format
- `analyze_constellation()`: Performs basic constellation analysis
- `clear_cache()`: Clears data processor cache

**Example Usage:**
```python
from src.utils.data_processor import DataProcessor

# Initialize processor
processor = DataProcessor()

# Load satellite data
satellites = processor.load_satellite_data()

# Analyze constellation
stats = processor.analyze_constellation(satellites)

# Export to CSV
processor.export_to_csv(satellites, 'starlink_data.csv')
```

### Scheduler (`src/utils/scheduler.py`)
Automated task scheduler based on cron expressions with execution cache.

**Key Methods:**
- `start_scheduler()`: Starts the background scheduler
- `stop_scheduler()`: Stops the scheduler
- `setup_scheduled_tasks()`: Configures scheduled tasks
- `get_scheduled_jobs()`: Returns information about scheduled jobs
- `clear_cache()`: Clears scheduler execution cache

**Supported Cron Expressions:**
- `0 0 */6 * *`: Every 6 hours
- `*/30 * * * *`: Every 30 minutes
- `*/15 * * * *`: Every 15 minutes
- `0 0 * * *`: Daily at midnight
- `0 * * * *`: Hourly

**Scheduler Configuration Example:**
```python
# In config.json
{
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",
    "prediction_update_cron": "*/30 * * * *",
    "notification_check_cron": "*/15 * * * *"
  }
}
```

### Notification System (`src/utils/notify.py`)
Sends alerts about upcoming satellite passes via email or Telegram.

**Key Methods:**
- `send_email_notification()`: Sends email notifications
- `send_telegram_notification()`: Sends Telegram notifications
- `notify_upcoming_pass()`: Sends notification about satellite pass

**Configuration:**
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

**Email Notification Setup:**
```python
# Enable email notifications in config.json
{
  "notifications": {
    "email": {
      "enabled": true,
      "smtp_server": "smtp.gmail.com",
      "smtp_port": 587,
      "username": "your_email@gmail.com",
      "password": "your_app_password",
      "recipient": "recipient@example.com"
    }
  }
}
```

**Telegram Notification Setup:**
```python
# Enable Telegram notifications in config.json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "your_bot_token",
      "chat_id": "your_chat_id"
    }
  }
}
```

### Web Application (`src/web/web_app.py`)
Flask-based web interface with RESTful API and caching.

**API Endpoints:**
- `GET /api/satellites`: Returns current satellite positions
- `GET /api/passes`: Returns predicted satellite passes
- `GET /api/coverage`: Returns global coverage data
- `GET /api/export/<format>`: Exports data in specified format (json, csv)
- `POST /api/cache/clear`: Clears API cache

**Web Pages:**
- `/` - Main dashboard with current satellite positions
- `/passes` - Calendar of passes over your location
- `/coverage` - World map of Starlink coverage
- `/settings` - Observer settings and notifications
- `/export` - Export data in various formats

**API Usage Examples:**
```bash
# Get current satellite positions
curl http://localhost:5000/api/satellites

# Get passes for a specific location
curl "http://localhost:5000/api/passes?lat=40.7128&lon=-74.0060&hours=48"

# Export data to JSON
curl http://localhost:5000/api/export/json

# Clear cache
curl -X POST http://localhost:5000/api/cache/clear
```

## 🖥️ Web Interface

When running web_app.py, the following pages are available:

- `/` - Main dashboard with current satellite positions
- `/passes` - Calendar of passes over your location
- `/coverage` - World map of Starlink coverage
- `/settings` - Observer settings and notifications
- `/export` - Export data in various formats

### Starting the Web Interface

```bash
# Using the main script
python starlink_tracker.py web

# Or directly from the web directory
python src/web/web_app.py
```

After starting, open your browser to http://localhost:5000

## 🧪 Testing

The project includes a comprehensive test suite:

```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific test module
python src/tests/test_config_manager.py

# Run tests with coverage
python -m pytest src/tests/ --cov=src --cov-report=html

# Run a specific test class
python -m pytest src/tests/test_core_tracker.py::TestStarlinkTracker -v
```

## 🛠️ Command Line Arguments

### Tracker Arguments
```bash
usage: main.py [-h] [--update] [--visualize] [--notify] [--schedule] [--debug]

Starlink Satellite Tracker

optional arguments:
  -h, --help      show this help message and exit
  --update        Force update TLE data
  --visualize     Show 3D visualization (default: False)
  --notify        Send notifications for upcoming passes
  --schedule      Start scheduler for automated tasks
  --debug         Enable debug logging
```

### Usage Examples

```bash
# Update TLE data and show upcoming passes
python starlink_tracker.py track --update

# Show 3D visualization of orbits
python starlink_tracker.py track --visualize

# Start scheduler for automated tasks
python starlink_tracker.py track --schedule

# Enable debug mode
python starlink_tracker.py track --debug

# Or run directly from the src/core directory
python src/core/main.py --update
```

## 📊 Pass Report Example

```
Starlink Passes Report for Moscow Observatory
Generated: 2025-11-10 15:30:00 MSK
Period: Next 24 hours

┌───────────────┬────────────┬────────────┬────────────┬──────────────┐
│ Satellite ID  │ Start Time │ Max Height │ Duration   │ Max Elevation│
├───────────────┼────────────┼────────────┼────────────┼──────────────┤
│ STARLINK-1234 │ 18:45:23   │ 65°        │ 4m 12s     │ 42°          │
│ STARLINK-5678 │ 19:12:08   │ 78°        │ 5m 37s     │ 58°          │
│ STARLINK-9012 │ 20:03:45   │ 45°        │ 3m 21s     │ 28°          │
└───────────────┴────────────┴────────────┴────────────┴──────────────┘
```

## 🔧 Configuration

### Configuration File (`config.json`)

```json
{
  "data_sources": {
    "celestrak_url": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
    "tle_cache_path": "data/tle_cache/",
    "max_cache_days": 7
  },
  "visualization": {
    "orbit_points": 100,
    "earth_texture": "data/earth_texture.jpg",
    "show_ground_track": true,
    "color_scheme": "dark"
  },
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",
    "prediction_update_cron": "*/30 * * * *",
    "notification_check_cron": "*/15 * * * *"
  }
}
```

## 📈 Performance Optimizations

The system includes several performance optimizations:

1. **Caching**: 
   - TLE data caching in memory with expiration
   - API response caching in web interface
   - Prediction result caching
   - Data processor caching for export operations

2. **Data Processing**:
   - Efficient TLE parsing
   - Selective satellite processing (first N satellites)
   - Compressed data export for large datasets

3. **Scheduler Optimization**:
   - Execution cache to prevent duplicate job runs
   - Configurable cron-based scheduling
   - Background threading for non-blocking operations

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 📞 Contact

Project Link: [https://github.com/yourusername/starlink-tracker](https://github.com/yourusername/starlink-tracker)