# Data Processor Documentation

## Overview
The Data Processor (`src/utils/data_processor.py`) handles data analysis, filtering, and export functionality for the Starlink Satellite Tracker application. It provides utilities for loading, processing, and exporting satellite data with built-in caching for performance optimization.

## Class: DataProcessor

### Constructor
```python
DataProcessor(config=None)
```

Initializes data processor with optional configuration.

**Parameters:**
- **config** (dict, optional): Configuration dictionary. If not provided, loads from config.json.

**Attributes:**
- **config** (dict): Configuration settings
- **logger** (Logger): Module logger
- **export_config** (dict): Export configuration section
- **data_directory** (str): Path to TLE cache directory
- **cache** (DataCache): Data caching system
- **_satellite_cache** (dict): Satellite data cache
- **_cache_expiry** (timedelta): Cache expiration time

### Methods

#### `load_satellite_data(filename=None)`
Load satellite data from TLE file or cache.

**Parameters:**
- **filename** (str, optional): Path to TLE file. If None, uses most recent file.

**Returns:**
- List of dictionaries with satellite data, or None on error

**Process:**
1. If filename not provided, finds most recent TLE file
2. Checks cache for existing data
3. If not cached, loads and parses TLE file
4. Stores data in cache
5. Returns satellite data

**Example:**
```python
processor = DataProcessor()
satellites = processor.load_satellite_data()
print(f"Loaded {len(satellites)} satellites")
```

#### `filter_satellites(satellites, criteria=None)`
Filter satellites based on provided criteria.

**Parameters:**
- **satellites** (list): List of satellite dictionaries
- **criteria** (dict, optional): Filter criteria

**Returns:**
- Filtered list of satellites

**Process:**
1. If no criteria or satellites, returns input
2. Generates cache key from criteria
3. Checks cache for filtered results
4. If not cached, applies filters
5. Stores results in cache
6. Returns filtered satellites

**Example:**
```python
# Filter satellites by name pattern
criteria = {'name': 'STARLINK-1234'}
filtered = processor.filter_satellites(satellites, criteria)
```

#### `export_to_csv(data, filename)`
Export data to CSV format.

**Parameters:**
- **data** (list): Data to export
- **filename** (str): Output filename

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Validates input data
2. Checks cache for export result
3. Converts data to DataFrame
4. Exports to CSV (compressed if large)
5. Updates cache
6. Returns success status

**Example:**
```python
success = processor.export_to_csv(satellites, 'starlink_data.csv')
if success:
    print("Export successful")
```

#### `export_to_json(data, filename)`
Export data to JSON format.

**Parameters:**
- **data** (list): Data to export
- **filename** (str): Output filename

**Returns:**
- bool: True if successful, False otherwise

**Process:**
1. Validates input data
2. Checks cache for export result
3. Wraps data with metadata
4. Exports to JSON (compressed if large)
5. Updates cache
6. Returns success status

**Example:**
```python
success = processor.export_to_json(satellites, 'starlink_data.json')
if success:
    print("Export successful")
```

#### `analyze_constellation(satellites)`
Perform basic analysis on the satellite constellation.

**Parameters:**
- **satellites** (list): List of satellite dictionaries

**Returns:**
- dict: Analysis results

**Process:**
1. Validates input data
2. Checks cache for analysis results
3. Calculates statistics
4. Extracts satellite IDs
5. Computes ID ranges
6. Updates cache
7. Returns analysis results

**Analysis Results:**
```json
{
  "total_satellites": 100,
  "analysis_date": "2025-11-10T15:30:00",
  "id_range": {
    "min": 1234,
    "max": 5678,
    "count": 85
  }
}
```

**Example:**
```python
stats = processor.analyze_constellation(satellites)
print(f"Total satellites: {stats['total_satellites']}")
```

#### `clear_cache()`
Clear all cached data.

**Process:**
1. Clears internal data cache
2. Logs cache clearing

## Class: DataCache

### Constructor
```python
DataCache(max_size=100)
```

Simple in-memory cache for processed data.

**Parameters:**
- **max_size** (int): Maximum cache size (default: 100)

**Attributes:**
- **cache** (dict): Key-value cache storage
- **access_times** (dict): Key to last access time mapping
- **max_size** (int): Maximum cache size
- **logger** (Logger): Module logger

### Methods

#### `get(key)`
Retrieve item from cache.

**Parameters:**
- **key** (str): Cache key

**Returns:**
- Cached value if found, None otherwise

#### `put(key, value)`
Store item in cache.

**Parameters:**
- **key** (str): Cache key
- **value**: Value to cache

**Process:**
1. If cache is full, removes oldest entry
2. Stores value with current timestamp
3. Updates access time

#### `clear()`
Clear all cache entries.

#### `size()`
Get current cache size.

**Returns:**
- int: Number of cached items

## Usage Examples

### Basic Data Processing
```python
from src.utils.data_processor import DataProcessor

# Initialize processor
processor = DataProcessor()

# Load satellite data
satellites = processor.load_satellite_data()

if satellites:
    # Analyze constellation
    stats = processor.analyze_constellation(satellites)
    print(f"Constellation analysis: {stats}")
    
    # Export to CSV
    processor.export_to_csv(satellites, 'starlink_export.csv')
    
    # Export to JSON
    processor.export_to_json(satellites, 'starlink_export.json')
```

### Filtering Data
```python
# Filter satellites by criteria
criteria = {
    'name': 'STARLINK'  # This would need to match exactly
}

# For more flexible filtering, you might need to implement custom logic
filtered = []
for sat in satellites:
    if 'STARLINK' in sat.get('name', ''):
        filtered.append(sat)

# Or use the filter method with exact matches
filtered = processor.filter_satellites(satellites, criteria)
```

### Data Analysis
```python
# Perform detailed analysis
stats = processor.analyze_constellation(satellites)

print(f"Total satellites tracked: {stats['total_satellites']}")
if 'id_range' in stats:
    id_range = stats['id_range']
    print(f"Satellite ID range: {id_range['min']} to {id_range['max']}")
    print(f"Satellites with numeric IDs: {id_range['count']}")
```

## Performance Optimization

### Caching Strategy
The Data Processor implements a multi-layer caching system:

1. **Data Cache**: Generic cache for processed data
2. **Export Cache**: Cache for export operations
3. **Analysis Cache**: Cache for analysis results

### Cache Management
```python
# Clear cache when needed
processor.clear_cache()

# Check cache size
print(f"Cache size: {processor.cache.size()}")
```

### Memory Management
1. Limited cache size (100 items by default)
2. Automatic removal of oldest entries
3. Timestamp-based expiration checking

## Integration Points

### With Configuration Manager
```python
from src.utils.config_manager import get_config
from src.utils.data_processor import DataProcessor

config = get_config()
processor = DataProcessor(config)
```

### With Core Tracker
```python
from src.core.main import StarlinkTracker
from src.utils.data_processor import DataProcessor

tracker = StarlinkTracker()
processor = DataProcessor()

# Load data processed by tracker
satellites = processor.load_satellite_data()
```

## Error Handling

The Data Processor includes comprehensive error handling:

1. **File I/O Errors**: Handles missing or inaccessible files
2. **Data Parsing Errors**: Manages malformed TLE data
3. **Export Errors**: Handles CSV/JSON export failures
4. **Memory Errors**: Manages cache size limitations
5. **Validation Errors**: Validates input parameters

### Example Error Handling
```python
try:
    satellites = processor.load_satellite_data()
    if satellites:
        processor.export_to_csv(satellites, 'export.csv')
    else:
        print("No satellite data available")
except FileNotFoundError:
    print("TLE data file not found")
except PermissionError:
    print("Permission denied accessing data directory")
except Exception as e:
    print(f"Data processing error: {e}")
```

## Testing

The Data Processor includes comprehensive unit tests in `src/tests/test_data_processor.py` that cover:

1. **Initialization Tests**: Constructor behavior with various configurations
2. **Data Loading Tests**: File loading and caching
3. **Filtering Tests**: Satellite filtering functionality
4. **Export Tests**: CSV and JSON export operations
5. **Analysis Tests**: Constellation analysis
6. **Cache Tests**: Cache management operations
7. **Error Handling Tests**: Various error conditions

## Dependencies

### Required
- **pandas**: Data processing and CSV export
- **json**: JSON export and parsing

### Optional
- **gzip**: Compressed file export

## Configuration

The Data Processor uses the following configuration sections:

### export
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

### data_sources
```json
{
  "data_sources": {
    "tle_cache_path": "data/tle_cache/"
  }
}
```

## Extensibility

The Data Processor is designed for easy extension:

1. **Custom Export Formats**: Add new export methods
2. **Advanced Filtering**: Implement complex filtering logic
3. **Enhanced Analysis**: Add detailed constellation analysis
4. **Database Integration**: Extend to support database storage

## Best Practices

### When Using This Module

1. **Initialize Once**: Create one processor instance per operation set
2. **Handle Errors**: Always wrap calls in try-except blocks
3. **Clear Caches**: Periodically clear caches to manage memory
4. **Validate Data**: Check data before processing
5. **Use Appropriate Formats**: Choose export format based on use case

### Performance Tips

1. **Use Caching**: Leverage built-in caching for repeated operations
2. **Batch Operations**: Group related operations together
3. **Monitor Cache Size**: Keep track of cache usage
4. **Clear When Done**: Clear caches after large operations

## Troubleshooting

### Common Issues

1. **File Not Found**: Ensure TLE cache directory exists and has files
2. **Permission Errors**: Check directory and file permissions
3. **Memory Issues**: Clear caches periodically for large datasets
4. **Export Failures**: Verify disk space and permissions

### Debugging

Enable debug logging to troubleshoot issues:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

Check logs for detailed error information and cache operations.

### Testing Data Processing

Test data processing in isolation:
```python
# Test data loading
from src.utils.data_processor import DataProcessor

processor = DataProcessor()
satellites = processor.load_satellite_data()

if satellites:
    print(f"Successfully loaded {len(satellites)} satellites")
else:
    print("Failed to load satellite data")
```