# 🛰️ Starlink Satellite Tracker - Usage Guide

This guide provides detailed instructions on how to use all features of the Starlink Satellite Tracker, including the newly enhanced capabilities.

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

## 🖥️ Web Interface Usage

### Main Dashboard (`/`)

The main dashboard provides an overview of:
- Current satellite tracking status
- Next visible satellite pass
- Recent activity (upcoming passes)

### Passes Page (`/passes`)

View and predict satellite passes over your location:
- Configure observer location (latitude, longitude, altitude)
- Set time period for predictions (1-168 hours)
- View detailed pass information (time, elevation, azimuth, distance)

### Visualization Page (`/visualization`)

Interactive 3D visualization of satellite orbits:
- Configure time period (1-24 hours)
- Select number of satellites to display (5-30)
- Choose color schemes (default, rainbow, velocity-based)
- Rotate, zoom, and pan the 3D view

### Coverage Page (`/coverage`)

View global Starlink constellation coverage:
- Regional coverage statistics
- Constellation status information

### Settings Page (`/settings`)

Configure all system settings:
- Observer location preferences
- Notification settings (email, Telegram)
- System configuration (data sources, scheduler)

### Export Page (`/export`)

Export satellite data in various formats:
- JSON or CSV format
- Select data to include (TLE data, predictions)
- Choose date range for export

## 📊 API Usage

### Core API Endpoints

#### Get Satellite Positions
```bash
# Get current satellite positions
curl http://localhost:5000/api/satellites
```

#### Get Predicted Passes
```bash
# Get passes for a specific location
curl "http://localhost:5000/api/passes?lat=40.7128&lon=-74.0060&hours=48"
```

#### Get Global Coverage
```bash
# Get global coverage data
curl http://localhost:5000/api/coverage
```

#### Export Data
```bash
# Export data to JSON
curl http://localhost:5000/api/export/json

# Export data to CSV
curl http://localhost:5000/api/export/csv
```

#### Orbit Visualization
```bash
# Get interactive 3D orbit visualization data
curl "http://localhost:5000/api/visualization/orbits?hours=2&satellites=10"
```

#### Clear Cache
```bash
# Clear all cached data
curl -X POST http://localhost:5000/api/cache/clear
```

## ⚙️ Configuration

### Configuration File Structure

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
    "advance_notice_minutes": 30,
    "excluded_satellites": [],
    "excluded_patterns": ["DEBRIS", "TEST"]
  },
  "export": {
    "default_format": "json",
    "include_tle_data": true,
    "include_predictions": true,
    "compress_large_files": true
  }
}
```

## 📧 Notification System

### Email Notifications

To enable email notifications, configure the email section in `config.json`:

```json
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

### Telegram Notifications

To enable Telegram notifications, configure the Telegram section in `config.json`:

```json
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

### Notification Filtering

The notification system includes advanced filtering capabilities:

- **Minimum Elevation**: Only notify for passes above a specified elevation angle
- **Minimum Brightness**: Only notify for satellites brighter than a specified magnitude
- **Excluded Satellites**: Skip notifications for specific satellite names
- **Excluded Patterns**: Skip notifications for satellites matching specific patterns

## 📈 Performance Optimizations

### Enhanced Caching

The system implements multiple caching layers:

1. **TLE Data Caching**: Satellite data cached with expiration
2. **API Response Caching**: Web API responses cached to reduce computation
3. **Prediction Caching**: Pass predictions cached to avoid recalculation
4. **Data Processor Caching**: Export operations cached with LRU eviction

### Memory Management

- Periodic cache cleanup to prevent memory leaks
- Configurable cache sizes and TTL values
- Automatic removal of expired entries

## 🧪 Testing

### Running Tests

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

### Test Coverage

The test suite includes:
- Core tracker functionality tests
- Configuration manager tests
- Data processor tests
- Notification system tests
- Scheduler tests
- Web application tests
- Custom exception tests
- Enhanced caching tests

## 🛠️ Command Line Usage

### Tracker Commands

```bash
# Update TLE data and show upcoming passes
python starlink_tracker.py track --update

# Show 3D visualization of orbits
python starlink_tracker.py track --visualize

# Start scheduler for automated tasks
python starlink_tracker.py track --schedule

# Enable debug mode
python starlink_tracker.py track --debug

# Send notifications for upcoming passes
python starlink_tracker.py track --notify
```

### Web Interface Commands

```bash
# Start the web interface
python starlink_tracker.py web

# Start web interface with debug logging
python starlink_tracker.py web --debug
```

## 🤖 Scheduler Configuration

The scheduler supports configurable cron expressions:

- `0 0 */6 * *`: Every 6 hours (TLE updates)
- `*/30 * * * *`: Every 30 minutes (Prediction updates)
- `*/15 * * * *`: Every 15 minutes (Notification checks)

Customize these in the `schedule` section of `config.json`.

## 📊 Data Export

### Export Formats

- **JSON**: Structured data export with metadata
- **CSV**: Tabular data export for spreadsheet applications

### Export Options

- Include TLE data
- Include prediction results
- Compress large files automatically
- Select date ranges for export

## 🔧 Troubleshooting

### Common Issues

1. **TLE Data Not Updating**: Check internet connection and data source URLs
2. **Visualization Not Working**: Ensure matplotlib and plotly are installed
3. **Notifications Not Sending**: Verify configuration and credentials
4. **Scheduler Not Running**: Check cron expressions and system time

### Debugging

Enable debug logging to get detailed information:

```bash
python starlink_tracker.py track --debug
python starlink_tracker.py web --debug
```

## 📈 Performance Tips

1. **Cache Management**: Regularly clear cache if memory usage is high
2. **Satellite Selection**: Limit number of satellites for visualization
3. **Update Frequency**: Adjust scheduler intervals based on needs
4. **Data Retention**: Configure appropriate cache expiration times

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a pull request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Table of Contents
1. [Installation](#installation)
2. [Basic Usage](#basic-usage)
3. [Configuration](#configuration)
4. [Command Line Interface](#command-line-interface)
5. [Web Interface](#web-interface)
6. [API Usage](#api-usage)
7. [Notification Setup](#notification-setup)
8. [Data Export](#data-export)
9. [Advanced Features](#advanced-features)
10. [Troubleshooting](#troubleshooting)

## Installation

### Prerequisites
- Python 3.8 or newer
- pip package manager
- Internet connection for downloading TLE data

### Installation Steps

1. Clone the repository:
```bash
git clone <repository-url>
cd starlink_satellite_tracker
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Verify installation:
```bash
python starlink_tracker.py track --help
```

## Basic Usage

### Quick Start
To quickly see satellite passes over your location:

```bash
python starlink_tracker.py track
```

This will:
1. Download the latest TLE data (if needed)
2. Predict passes over the default location (Moscow)
3. Display the results

### Custom Location
To predict passes for a custom location:

```bash
python starlink_tracker.py track --update
```

Then modify the config.json file to set your location:

```json
{
  "observer": {
    "default_latitude": 40.7128,
    "default_longitude": -74.0060,
    "default_altitude": 0,
    "timezone": "America/New_York"
  }
}
```

## Configuration

### Configuration File Structure
The main configuration file is `config.json` in the project root. Here's a breakdown of all configuration options:

#### Data Sources
```json
{
  "data_sources": {
    "celestrak_url": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
    "tle_cache_path": "data/tle_cache/",
    "max_cache_days": 7,
    "backup_urls": [
      "https://celestrak.org/NORAD/elements/starlink.txt"
    ]
  }
}
```

#### Visualization Settings
```json
{
  "visualization": {
    "orbit_points": 100,
    "earth_texture": "data/earth_texture.jpg",
    "show_ground_track": true,
    "color_scheme": "dark",
    "plotly_3d": true,
    "matplotlib_2d": true
  }
}
```

#### Scheduling
```json
{
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",
    "prediction_update_cron": "*/30 * * * *",
    "notification_check_cron": "*/15 * * * *"
  }
}
```

#### Observer Settings
```json
{
  "observer": {
    "default_latitude": 55.7558,
    "default_longitude": 37.6173,
    "default_altitude": 0,
    "timezone": "Europe/Moscow"
  }
}
```

#### Notifications
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

#### Export Settings
```json
{
  "export": {
    "default_format": "json",
    "include_tle_data": true,
    "include_predictions": true,
    "compress_large_files": true
  }
}
```

## Command Line Interface

### Main Commands

#### Track Command
```bash
python starlink_tracker.py track [options]
```

Options:
- `--update`: Force update TLE data
- `--visualize`: Show 3D visualization
- `--notify`: Send notifications for upcoming passes
- `--schedule`: Start scheduler for automated tasks
- `--debug`: Enable debug logging

#### Web Command
```bash
python starlink_tracker.py web
```

Starts the web interface on http://localhost:5000

### Examples

#### Update TLE Data and Show Passes
```bash
python starlink_tracker.py track --update
```

#### Show 3D Visualization
```bash
python starlink_tracker.py track --visualize
```

#### Start Automated Scheduler
```bash
python starlink_tracker.py track --schedule
```

#### Enable Debug Mode
```bash
python starlink_tracker.py track --debug
```

## Web Interface

### Starting the Web Interface
```bash
python starlink_tracker.py web
```

Or directly:
```bash
python src/web/web_app.py
```

### Web Pages

#### Dashboard (`/`)
Main dashboard showing:
- Current satellite count
- Next predicted pass
- System status

#### Passes (`/passes`)
Detailed view of upcoming satellite passes:
- Table of passes with times and positions
- Filter by time period
- Location-specific predictions

#### Coverage (`/coverage`)
World map showing:
- Current Starlink constellation coverage
- Regional statistics
- Satellite density visualization

#### Settings (`/settings`)
Configuration options:
- Observer location settings
- Notification preferences
- System configuration

#### Export (`/export`)
Data export functionality:
- Export in JSON or CSV format
- Select data types to include
- Download exported files

### API Endpoints

#### GET `/api/satellites`
Returns current satellite positions.

Example:
```bash
curl http://localhost:5000/api/satellites
```

Response:
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

Example:
```bash
curl "http://localhost:5000/api/passes?lat=40.7128&lon=-74.0060&hours=48"
```

Response:
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
    "latitude": 40.7128,
    "longitude": -74.0060
  },
  "period_hours": 48
}
```

#### GET `/api/coverage`
Returns global coverage data.

Example:
```bash
curl http://localhost:5000/api/coverage
```

Response:
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

Example:
```bash
curl http://localhost:5000/api/export/json
curl http://localhost:5000/api/export/csv
```

#### POST `/api/cache/clear`
Clears API cache.

Example:
```bash
curl -X POST http://localhost:5000/api/cache/clear
```

## API Usage

### Python API Examples

#### Basic Tracking
```python
from src.core.main import StarlinkTracker

# Initialize tracker
tracker = StarlinkTracker()

# Update satellite data
satellites = tracker.update_tle_data()

# Predict passes for New York
passes = tracker.predict_passes(
    latitude=40.7128, 
    longitude=-74.0060,
    hours_ahead=48
)

# Print results
for p in passes[:10]:
    print(f"{p['satellite']}: {p['time']} at {p['altitude']:.1f}°")
```

#### Data Processing
```python
from src.utils.data_processor import DataProcessor

# Initialize processor
processor = DataProcessor()

# Load satellite data
satellites = processor.load_satellite_data()

# Analyze constellation
stats = processor.analyze_constellation(satellites)
print(f"Total satellites: {stats['total_satellites']}")

# Export to CSV
processor.export_to_csv(satellites, 'starlink_data.csv')
```

#### Configuration Management
```python
from src.utils.config_manager import get_config, get_config_value

# Get complete configuration
config = get_config()

# Get specific values
latitude = get_config_value('observer', 'default_latitude', 0.0)
celestrak_url = get_config_value('data_sources', 'celestrak_url')
```

#### Scheduling
```python
from src.utils.scheduler import StarlinkScheduler
from src.core.main import StarlinkTracker

# Initialize tracker and scheduler
tracker = StarlinkTracker()
scheduler = StarlinkScheduler(tracker=tracker)

# Start scheduler
if scheduler.start_scheduler():
    print("Scheduler started successfully")
else:
    print("Failed to start scheduler")
```

## Notification Setup

### Email Notifications

1. Enable email notifications in config.json:
```json
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

2. For Gmail, you'll need to:
   - Enable 2-factor authentication
   - Generate an app password
   - Use the app password instead of your regular password

### Telegram Notifications

1. Create a Telegram bot:
   - Talk to @BotFather on Telegram
   - Use `/newbot` command
   - Follow instructions to get your bot token

2. Get your chat ID:
   - Talk to your new bot
   - Send any message
   - Visit `https://api.telegram.org/bot<BOT_TOKEN>/getUpdates`
   - Find your chat ID in the response

3. Configure in config.json:
```json
{
  "notifications": {
    "telegram": {
      "enabled": true,
      "bot_token": "your_bot_token_here",
      "chat_id": "your_chat_id_here"
    }
  }
}
```

### Testing Notifications
```python
from src.utils.notify import NotificationSystem

# Initialize notification system
notifier = NotificationSystem()

# Send test notification
success = notifier.notify_upcoming_pass(
    "STARLINK-TEST",
    datetime.now() + timedelta(minutes=30),
    65.5,
    42.3
)

if success:
    print("Notification sent successfully")
else:
    print("Failed to send notification")
```

## Data Export

### Export Formats

#### JSON Export
```python
from src.utils.data_processor import DataProcessor

processor = DataProcessor()
satellites = processor.load_satellite_data()

# Export to JSON
processor.export_to_json(satellites, 'starlink_export.json')
```

Resulting JSON structure:
```json
{
  "satellites": [
    {
      "name": "STARLINK-1234",
      "line1": "1 12345U 12345ABC  23156.12345678  .00000000  00000-0  00000+0 0  1234",
      "line2": "2 12345  53.0000 123.4567 0001234 321.4567 123.4567 15.23456789 12345"
    }
  ],
  "exported": "2025-11-10T15:30:00",
  "count": 100,
  "version": "1.0"
}
```

#### CSV Export
```python
# Export to CSV
processor.export_to_csv(satellites, 'starlink_export.csv')
```

### Web Export
Through the web interface:
1. Navigate to `/export`
2. Select export format (JSON/CSV)
3. Click export button
4. Download the file

### API Export
```
# Export via API
curl http://localhost:5000/api/export/json -o starlink_data.json
curl http://localhost:5000/api/export/csv -o starlink_data.csv
```

## Advanced Features

### Custom Scheduling
The scheduler supports cron expressions for custom automation:

```json
{
  "schedule": {
    "tle_update_cron": "0 0 */6 * *",      // Every 6 hours
    "prediction_update_cron": "*/30 * * * *", // Every 30 minutes
    "notification_check_cron": "*/15 * * * *"  // Every 15 minutes
  }
}
```

Supported cron patterns:
- `0 0 */6 * *`: Every 6 hours
- `*/30 * * * *`: Every 30 minutes
- `*/15 * * * *`: Every 15 minutes
- `0 0 * * *`: Daily at midnight
- `0 * * * *`: Hourly

### Caching System
The application uses multiple caching layers for performance:

1. **TLE Cache**: Memory cache for TLE data (6 hours default)
2. **Prediction Cache**: Cache for prediction results (15 minutes default)
3. **API Cache**: Cache for web API responses (varies by endpoint)
4. **Data Processor Cache**: Cache for processed data

Clear caches when needed:
```python
# Clear all caches
tracker.clear_caches()

# Clear API cache
curl -X POST http://localhost:5000/api/cache/clear
```

### Visualization Customization
Customize visualization settings in config.json:

```json
{
  "visualization": {
    "orbit_points": 200,           // More detailed orbits
    "show_ground_track": false,    // Hide ground track
    "color_scheme": "light",       // Light color scheme
    "plotly_3d": true,             // Enable 3D plots
    "matplotlib_2d": false         // Disable 2D plots
  }
}
```

## Troubleshooting

### Common Issues

#### TLE Data Download Failures
**Symptom**: "Failed to download TLE data" error
**Solutions**:
1. Check internet connection
2. Verify Celestrak URL in config.json
3. Check backup URLs are configured
4. Ensure firewall allows outbound connections

#### Missing Dependencies
**Symptom**: ImportError messages
**Solution**:
```bash
pip install -r requirements.txt
```

#### Permission Errors
**Symptom**: "Permission denied" when creating cache directories
**Solutions**:
1. Run with appropriate permissions
2. Change cache directory in config.json to writable location

#### Visualization Issues
**Symptom**: "Matplotlib not installed" error
**Solution**:
```bash
pip install matplotlib
```

#### Email Notification Failures
**Symptom**: Email notifications not sending
**Solutions**:
1. Verify SMTP settings in config.json
2. Check username/password
3. For Gmail, ensure app password is used
4. Check recipient email address

#### Telegram Notification Failures
**Symptom**: Telegram notifications not sending
**Solutions**:
1. Verify bot token
2. Check chat ID
3. Ensure bot is not blocked
4. Install python-telegram-bot:
   ```bash
   pip install python-telegram-bot
   ```

### Debugging

#### Enable Debug Logging
```bash
python starlink_tracker.py track --debug
```

#### Check Logs
Logs are output to console by default. For file logging, modify the logging configuration in each module.

#### Test Individual Components
```bash
# Test configuration
python src/utils/config_manager.py

# Test data processor
python src/utils/data_processor.py

# Test scheduler
python src/utils/scheduler.py
```

### Performance Tuning

#### Cache Settings
Adjust cache TTL values in the code for your needs:
- Longer TTL for less frequent updates
- Shorter TTL for rapidly changing data

#### Satellite Processing Limits
The system processes a limited number of satellites for performance:
- Modify satellite limits in prediction functions
- Adjust orbit_points for visualization detail

#### Memory Usage
Monitor memory usage with large datasets:
- Clear caches periodically
- Use compressed export for large files
- Monitor system resources during operation

### Getting Help

#### Documentation
- README.md: Project overview and quick start
- PROJECT_STRUCTURE.md: Code organization
- API_DOCUMENTATION.md: Detailed API reference
- This USAGE_GUIDE.md: Comprehensive usage instructions

#### Support
For issues not covered in this guide:
1. Check the GitHub issues page
2. Review existing documentation
3. Submit a detailed bug report with:
   - Error messages
   - Steps to reproduce
   - System information
   - Configuration details

#### Contributing
1. Fork the repository
2. Create feature branches
3. Submit pull requests with clear descriptions
4. Follow coding standards in the project