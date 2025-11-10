# Configuration Manager Documentation

## Overview
The Configuration Manager (`src/utils/config_manager.py`) provides centralized configuration management for the Starlink Satellite Tracker application. It implements a singleton pattern to ensure consistent configuration access across all modules.

## Class: ConfigManager

### Constructor
```python
ConfigManager()
```

Initializes the configuration manager. Uses singleton pattern to ensure only one instance exists.

**Attributes:**
- **_instance** (ConfigManager): Singleton instance
- **_config** (dict): Loaded configuration data

### Methods

#### `_find_config_file()`
Finds the configuration file in common locations.

**Returns:**
- str: Path to config.json if found, None otherwise

**Search Order:**
1. `config.json` in current directory
2. `../config.json` (parent directory)
3. `src/config.json`
4. `../src/config.json`

#### `_load_config()`
Loads configuration from file.

**Returns:**
- dict: Configuration data

**Process:**
1. Finds config file using `_find_config_file()`
2. If not found, uses default configuration
3. Loads JSON from file
4. Handles loading errors gracefully

#### `_default_config()`
Returns default configuration.

**Returns:**
- dict: Default configuration with all required sections

**Default Configuration Structure:**
```json
{
  "data_sources": {
    "celestrak_url": "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle",
    "tle_cache_path": "data/tle_cache/",
    "max_cache_days": 7,
    "backup_urls": [
      "https://celestrak.org/NORAD/elements/starlink.txt"
    ]
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
    }
  },
  "export": {
    "default_format": "json",
    "include_tle_data": true,
    "include_predictions": true,
    "compress_large_files": true
  }
}
```

#### `get_config()`
Get the current configuration.

**Returns:**
- dict: Copy of current configuration

#### `get_section(section_name)`
Get a specific section of the configuration.

**Parameters:**
- **section_name** (str): Name of configuration section

**Returns:**
- dict: Copy of configuration section

#### `get_value(section, key, default=None)`
Get a specific value from the configuration.

**Parameters:**
- **section** (str): Configuration section name
- **key** (str): Configuration key
- **default**: Default value if key not found

**Returns:**
- Configuration value or default

#### `reload_config()`
Reload configuration from file.

**Returns:**
- dict: Reloaded configuration

## Functions

### `get_config()`
Get the global configuration.

**Returns:**
- dict: Global configuration

### `get_config_section(section_name)`
Get a specific section of the global configuration.

**Parameters:**
- **section_name** (str): Name of configuration section

**Returns:**
- dict: Configuration section

### `get_config_value(section, key, default=None)`
Get a specific value from the global configuration.

**Parameters:**
- **section** (str): Configuration section name
- **key** (str): Configuration key
- **default**: Default value if key not found

**Returns:**
- Configuration value or default

## Design Patterns

### Singleton Pattern
The ConfigManager uses the singleton pattern to ensure:
1. Only one configuration instance exists
2. Consistent configuration across all modules
3. Centralized configuration management
4. Efficient memory usage

### Implementation:
```python
class ConfigManager:
    _instance = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(ConfigManager, cls).__new__(cls)
        return cls._instance
```

## Usage Examples

### Basic Usage
```python
from src.utils.config_manager import get_config

# Get complete configuration
config = get_config()

# Get specific section
data_sources = get_config_section('data_sources')

# Get specific value
celestrak_url = get_config_value('data_sources', 'celestrak_url')
```

### Direct Class Usage
```python
from src.utils.config_manager import ConfigManager

# Get configuration manager instance
manager = ConfigManager()

# Get configuration
config = manager.get_config()

# Get specific section
observer_config = manager.get_section('observer')

# Get specific value
latitude = manager.get_value('observer', 'default_latitude', 0.0)
```

### Reloading Configuration
```python
from src.utils.config_manager import get_config

# Initial configuration
config = get_config()

# After modifying config.json
config = ConfigManager().reload_config()
```

## Configuration Sections

### data_sources
Configuration for TLE data sources and caching.

**Keys:**
- **celestrak_url** (str): Primary TLE data source URL
- **tle_cache_path** (str): Path for cached TLE files
- **max_cache_days** (int): Maximum cache age in days
- **backup_urls** (list): List of backup TLE sources

### visualization
Configuration for visualization settings.

**Keys:**
- **orbit_points** (int): Number of points in orbit visualization
- **earth_texture** (str): Path to Earth texture file
- **show_ground_track** (bool): Whether to show ground track
- **color_scheme** (str): Color scheme for visualizations

### schedule
Configuration for automated scheduling.

**Keys:**
- **tle_update_cron** (str): Cron expression for TLE updates
- **prediction_update_cron** (str): Cron expression for prediction updates
- **notification_check_cron** (str): Cron expression for notification checks

### observer
Configuration for default observer location.

**Keys:**
- **default_latitude** (float): Default observer latitude
- **default_longitude** (float): Default observer longitude
- **default_altitude** (float): Default observer altitude
- **timezone** (str): Observer timezone

### notifications
Configuration for notification settings.

**Keys:**
- **email** (dict): Email notification settings
  - **enabled** (bool): Enable email notifications
  - **smtp_server** (str): SMTP server address
  - **smtp_port** (int): SMTP server port
  - **username** (str): SMTP username
  - **password** (str): SMTP password
  - **recipient** (str): Notification recipient
- **telegram** (dict): Telegram notification settings
  - **enabled** (bool): Enable Telegram notifications
  - **bot_token** (str): Telegram bot token
  - **chat_id** (str): Telegram chat ID

### export
Configuration for data export settings.

**Keys:**
- **default_format** (str): Default export format
- **include_tle_data** (bool): Include TLE data in exports
- **include_predictions** (bool): Include predictions in exports
- **compress_large_files** (bool): Compress large export files

## Error Handling

The configuration manager handles several error conditions:

1. **File Not Found**: Uses default configuration if config.json is missing
2. **JSON Parse Errors**: Falls back to default configuration on parse errors
3. **Missing Keys**: Returns default values for missing configuration keys
4. **Type Errors**: Handles type mismatches gracefully

### Example Error Handling
```python
try:
    config = get_config()
    url = get_config_value('data_sources', 'celestrak_url')
except Exception as e:
    print(f"Configuration error: {e}")
    # Use hardcoded defaults
    url = "https://celestrak.org/NORAD/elements/gp.php?GROUP=starlink&FORMAT=tle"
```

## Testing

The configuration manager includes comprehensive unit tests in `src/tests/test_config_manager.py` that cover:

1. **Singleton Behavior**: Ensures only one instance exists
2. **Configuration Loading**: Tests file loading and default fallback
3. **Value Retrieval**: Tests get_value with various scenarios
4. **Section Retrieval**: Tests get_section functionality
5. **Reloading**: Tests configuration reloading
6. **Error Conditions**: Tests error handling scenarios

## Best Practices

### When Using This Module

1. **Use Functions**: Prefer `get_config()` over direct class instantiation
2. **Provide Defaults**: Always provide sensible defaults for configuration values
3. **Validate Inputs**: Validate configuration values after retrieval
4. **Handle Errors**: Wrap configuration access in try-except blocks
5. **Document Keys**: Document all configuration keys in your modules

### Configuration File Management

1. **Version Control**: Keep config.json in version control with sensitive data removed
2. **Environment Override**: Consider environment variable overrides for sensitive data
3. **Backup**: Keep backups of production configuration
4. **Validation**: Validate configuration on application startup

### Performance Considerations

1. **Caching**: Configuration is loaded once and cached
2. **Copying**: Methods return copies to prevent accidental modification
3. **Lazy Loading**: Configuration is loaded on first access
4. **Memory**: Configuration is stored in memory for fast access

## Extensibility

The configuration manager is designed for easy extension:

1. **Custom Sections**: Add new configuration sections as needed
2. **Validation**: Add configuration validation methods
3. **Environment Variables**: Extend to support environment variable overrides
4. **Multiple Sources**: Extend to support multiple configuration sources

## Troubleshooting

### Common Issues

1. **Configuration Not Found**: Ensure config.json exists in expected locations
2. **Invalid JSON**: Check config.json syntax with a JSON validator
3. **Missing Keys**: Verify all required keys are present
4. **Type Mismatches**: Ensure values are correct types

### Debugging

Enable debug logging to troubleshoot configuration issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs for configuration loading messages and errors.

### Testing Configuration

Test configuration loading in isolation:
```python
# Test configuration loading
from src.utils.config_manager import ConfigManager

manager = ConfigManager()
config = manager.reload_config()
print("Configuration loaded successfully")
print(f"Data sources: {config.get('data_sources', {})}")
```