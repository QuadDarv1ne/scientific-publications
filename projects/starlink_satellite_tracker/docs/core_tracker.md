# Core Tracker Module Documentation

## Overview
The Core Tracker module (`src/core/main.py`) is the heart of the Starlink Satellite Tracker application. It handles satellite data acquisition, orbital calculations, pass predictions, and visualization.

## Class: StarlinkTracker

### Constructor
```python
StarlinkTracker(config=None)
```

Initializes the Starlink tracker with optional configuration.

**Parameters:**
- **config** (dict, optional): Configuration dictionary. If not provided, loads from config.json.

**Attributes:**
- **config** (dict): Configuration settings
- **satellites** (list): List of loaded EarthSatellite objects
- **ts** (Timescale): Skyfield timescale object
- **earth** (object): Earth data for calculations
- **scheduler** (StarlinkScheduler): Scheduler instance
- **tle_cache** (TLECache): TLE data cache
- **prediction_cache** (dict): Prediction results cache

### Methods

#### `update_tle_data(force=False)`
Downloads latest TLE data from Celestrak or uses cached data.

**Parameters:**
- **force** (bool): If True, forces download even if cached data exists.

**Returns:**
- List of EarthSatellite objects

**Process:**
1. Checks for cached TLE file
2. If not found or expired, downloads from Celestrak
3. Uses backup URLs if primary fails
4. Parses TLE data into satellite objects
5. Caches data for future use

**Example:**
```python
tracker = StarlinkTracker()
satellites = tracker.update_tle_data()
print(f"Loaded {len(satellites)} satellites")
```

#### `predict_passes(latitude, longitude, altitude=0, hours_ahead=24, min_elevation=10)`
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

**Process:**
1. Validates input coordinates
2. Sets up observer location
3. Defines time range for predictions
4. Iterates through satellites to find passes
5. Uses Skyfield's find_events method
6. Caches results for performance

**Example:**
```python
passes = tracker.predict_passes(55.7558, 37.6173, hours_ahead=48)
for p in passes[:5]:
    print(f"{p['satellite']} at {p['time']} - {p['altitude']:.1f}°")
```

#### `visualize_orbits(hours=2)`
Creates a 3D visualization of satellite orbits.

**Parameters:**
- **hours** (float): Duration to visualize orbits (default: 2)

**Process:**
1. Validates matplotlib availability
2. Sets up 3D plot
3. Calculates orbit points for time range
4. Plots orbits for first 5 satellites
5. Adds labels and formatting
6. Displays plot

**Example:**
```python
tracker.visualize_orbits(hours=3)
```

#### `start_scheduler()`
Starts the automated task scheduler.

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Imports scheduler module
2. Initializes scheduler with tracker instance
3. Starts scheduler in background thread
4. Returns success status

#### `stop_scheduler()`
Stops the automated task scheduler.

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Checks if scheduler exists
2. Stops scheduler gracefully
3. Cleans up resources
4. Returns success status

#### `clear_caches()`
Clears all internal caches (TLE cache, prediction cache).

**Process:**
1. Clears TLE cache
2. Clears prediction cache
3. Clears prediction timestamp cache
4. Logs cache clearing

## Class: TLECache

### Constructor
```python
TLECache(max_age_hours=24)
```

Cache for TLE data with expiration.

**Parameters:**
- **max_age_hours** (int): Maximum cache age in hours (default: 24)

**Attributes:**
- **cache** (dict): URL to TLE data mapping
- **timestamps** (dict): URL to timestamp mapping
- **max_age** (timedelta): Maximum cache age
- **logger** (Logger): Module logger

### Methods

#### `get(url)`
Retrieve cached TLE data if not expired.

**Parameters:**
- **url** (str): URL of TLE data

**Returns:**
- str: TLE data if available and not expired, None otherwise

#### `put(url, data)`
Store TLE data in cache.

**Parameters:**
- **url** (str): URL of TLE data
- **data** (str): TLE data to cache

#### `clear()`
Clear all cached TLE data.

## Error Handling

The Core Tracker module includes comprehensive error handling:

1. **Network Errors**: Handles HTTP request failures with retries and backup URLs
2. **File I/O Errors**: Manages file creation, reading, and writing errors
3. **Data Parsing Errors**: Handles malformed TLE data gracefully
4. **Validation Errors**: Validates input parameters and coordinates
5. **Dependency Errors**: Manages missing optional dependencies (matplotlib)

### Example Error Handling
```python
try:
    satellites = tracker.update_tle_data()
except requests.RequestException as e:
    logger.error(f"Failed to download TLE data: {e}")
except ValueError as e:
    logger.error(f"Invalid data: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
```

## Performance Optimization

### Caching
The module implements multiple caching layers:
1. **TLE Cache**: Memory cache for downloaded TLE data
2. **File Cache**: Disk cache for TLE files
3. **Prediction Cache**: Results cache for pass predictions

### Resource Management
1. Limits satellite processing to first N satellites for performance
2. Uses efficient data structures
3. Implements lazy loading where appropriate
4. Clears caches periodically to manage memory

## Integration Points

### With Configuration Manager
```python
from utils.config_manager import get_config
config = get_config()
tracker = StarlinkTracker(config)
```

### With Scheduler
```python
from utils.scheduler import StarlinkScheduler
scheduler = StarlinkScheduler(tracker=tracker)
```

### With Data Processor
```python
from utils.data_processor import DataProcessor
processor = DataProcessor()
satellites = processor.load_satellite_data()
```

## Usage Examples

### Basic Tracking
```python
from src.core.main import StarlinkTracker

# Initialize tracker
tracker = StarlinkTracker()

# Update satellite data
satellites = tracker.update_tle_data()

# Predict passes for Moscow
passes = tracker.predict_passes(latitude=55.7558, longitude=37.6173)

# Print results
print(f"Found {len(passes)} upcoming passes:")
for p in passes[:10]:
    print(f"  {p['satellite']}: {p['time'].strftime('%Y-%m-%d %H:%M:%S')} "
          f"at {p['altitude']:.1f}° alt")
```

### Visualization
```python
# Show 3D visualization
tracker.visualize_orbits(hours=2)
```

### Automated Scheduling
```python
# Start automated scheduler
if tracker.start_scheduler():
    print("Scheduler started")
else:
    print("Failed to start scheduler")
```

## Testing

The module includes comprehensive unit tests in `src/tests/test_core_tracker.py` that cover:

1. **Initialization Tests**: Constructor behavior with various configurations
2. **TLE Update Tests**: Data fetching with caching and error handling
3. **Prediction Tests**: Pass prediction with various parameters
4. **Validation Tests**: Input validation and error conditions
5. **Integration Tests**: Complete workflow testing

## Dependencies

### Required
- **skyfield**: Orbital calculations
- **requests**: HTTP requests for TLE data
- **numpy**: Numerical computations
- **pandas**: Data processing (optional)

### Optional
- **matplotlib**: 3D visualization
- **plotly**: Alternative visualization

## Configuration

The module uses the following configuration sections:

### data_sources
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

### visualization
```json
{
  "visualization": {
    "orbit_points": 100,
    "earth_texture": "data/earth_texture.jpg",
    "show_ground_track": true,
    "color_scheme": "dark"
  }
}
```

### observer
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

## Extensibility

The module is designed for easy extension:

1. **Custom Prediction Algorithms**: Can be added by subclassing
2. **Additional Data Sources**: Support for multiple TLE sources
3. **Enhanced Visualization**: Pluggable visualization backends
4. **Extended Caching**: Additional cache layers for specific use cases

## Best Practices

### When Using This Module

1. **Initialize Once**: Create one tracker instance per application
2. **Handle Errors**: Always wrap calls in try-except blocks
3. **Respect Rate Limits**: Don't call update_tle_data too frequently
4. **Clear Caches**: Periodically clear caches to manage memory
5. **Validate Inputs**: Always validate coordinates and parameters

### Performance Tips

1. **Use Caching**: Leverage built-in caching for repeated operations
2. **Limit Satellites**: Process only needed satellites for predictions
3. **Batch Operations**: Group related operations together
4. **Monitor Memory**: Keep track of cache sizes and memory usage

## Troubleshooting

### Common Issues

1. **TLE Download Failures**: Check internet connection and URLs
2. **Missing Dependencies**: Install required packages
3. **Permission Errors**: Ensure write access to cache directory
4. **Memory Issues**: Clear caches periodically
5. **Visualization Problems**: Install matplotlib

### Debugging

Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs for detailed error information and performance metrics.