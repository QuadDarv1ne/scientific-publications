# Web Application Documentation

## Overview
The Web Application (`src/web/web_app.py`) provides a Flask-based web interface and RESTful API for the Starlink Satellite Tracker application. It offers real-time satellite tracking, pass predictions, coverage visualization, and data export capabilities through both a web interface and API endpoints.

## Flask Application

### Application Instance
```python
app = Flask(__name__)
```

The main Flask application instance with integrated caching and error handling.

**Attributes:**
- **config** (dict): Application configuration
- **api_cache** (APICache): API response caching system
- **tracker_instance** (StarlinkTracker): Core tracker instance

## Class: APICache

### Constructor
```python
APICache(default_ttl=300)
```

Simple in-memory cache for API responses.

**Parameters:**
- **default_ttl** (int): Default time-to-live in seconds (default: 300)

**Attributes:**
- **cache** (dict): Key to cached data mapping
- **timestamps** (dict): Key to timestamp mapping
- **default_ttl** (int): Default cache expiration time
- **logger** (Logger): Module logger

### Methods

#### `get(key)`
Retrieve cached data if not expired.

**Parameters:**
- **key** (str): Cache key

**Returns:**
- Cached data if available and not expired, None otherwise

#### `set(key, value)`
Store data in cache.

**Parameters:**
- **key** (str): Cache key
- **value**: Data to cache

#### `clear()`
Clear all cached data.

## Decorators

### `cached(ttl=300)`
Cache decorator for API endpoints.

**Parameters:**
- **ttl** (int): Time-to-live in seconds (default: 300)

**Usage:**
```python
@app.route('/api/satellites')
@cached(ttl=600)
def api_satellites():
    # This response will be cached for 10 minutes
    pass
```

### `handle_api_errors`
Error handler decorator for API endpoints.

**Usage:**
```python
@app.route('/api/passes')
@handle_api_errors
def api_passes():
    # Errors in this function will be handled automatically
    pass
```

## API Endpoints

### GET `/api/satellites`
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

**Caching:** 10 minutes

### GET `/api/passes`
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

**Caching:** 5 minutes

### GET `/api/coverage`
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

**Caching:** 1 hour

### GET `/api/export/<format>`
Exports data in specified format.

**Path Parameters:**
- **format** (str): Export format (json, csv)

**Response:**
- Data in requested format

**Caching:** No caching (generates fresh data)

### POST `/api/cache/clear`
Clears API cache.

**Response:**
```json
{
  "message": "Cache cleared successfully"
}
```

## Web Pages

### `/` (Dashboard)
Main dashboard showing current satellite positions and next pass.

**Template:** `index.html`

**Features:**
- Satellite count display
- Next pass information
- System status indicators

### `/passes` (Passes)
Detailed view of upcoming satellite passes.

**Template:** `passes.html`

**Features:**
- Table of passes with times and positions
- Filter by time period
- Location-specific predictions

### `/coverage` (Coverage)
World map showing Starlink coverage.

**Template:** `coverage.html`

**Features:**
- Global coverage visualization
- Regional statistics
- Satellite density display

### `/settings` (Settings)
Configuration page for observer location and notifications.

**Template:** `settings.html`

**Features:**
- Observer location settings
- Notification preferences
- System configuration

### `/export` (Export)
Page for exporting satellite data.

**Template:** `export.html`

**Features:**
- Export in JSON or CSV format
- Select data types to include
- Download exported files

## Usage Examples

### Starting the Web Application
```bash
# Using the main script
python starlink_tracker.py web

# Or directly from the web directory
python src/web/web_app.py
```

### API Usage
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

### Python API Client
```python
import requests

# Get satellite data
response = requests.get('http://localhost:5000/api/satellites')
satellites = response.json()

# Get passes for New York
params = {'lat': 40.7128, 'lon': -74.0060, 'hours': 48}
response = requests.get('http://localhost:5000/api/passes', params=params)
passes = response.json()

# Export to CSV
response = requests.get('http://localhost:5000/api/export/csv')
with open('satellites.csv', 'wb') as f:
    f.write(response.content)
```

## Caching System

### Cache Decorator Usage
```python
@app.route('/api/data')
@cached(ttl=300)  # Cache for 5 minutes
def api_data():
    # Expensive operation
    return jsonify(data)
```

### Cache Management
```python
# Clear cache endpoint
@app.route('/api/cache/clear', methods=['POST'])
def clear_cache():
    api_cache.clear()
    return jsonify({'message': 'Cache cleared'})
```

### Cache TTL Values
- **Satellites**: 600 seconds (10 minutes)
- **Passes**: 300 seconds (5 minutes)
- **Coverage**: 3600 seconds (1 hour)
- **Export**: No caching (always fresh)

## Error Handling

### API Error Decorator
```python
@app.route('/api/data')
@handle_api_errors
def api_data():
    # Any exception here will be caught and returned as JSON
    raise ValueError("Something went wrong")
```

**Error Response:**
```json
{
  "error": "Internal server error",
  "message": "Something went wrong"
}
```

### Custom Error Handlers
```python
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500
```

## Performance Optimization

### Caching Strategy
The web application implements multi-level caching:

1. **API Response Caching**: Cache expensive API responses
2. **Tracker Caching**: Leverage core tracker's built-in caching
3. **Template Caching**: Flask template caching (if enabled)

### Resource Management
1. **Connection Pooling**: Reuse tracker instance
2. **Memory Management**: Clear caches periodically
3. **Efficient Data Transfer**: Limit data in API responses

### Scalability Considerations
1. **Background Processing**: Use scheduler for heavy tasks
2. **Asynchronous Operations**: Consider async for high load
3. **Load Balancing**: Deploy multiple instances behind load balancer

## Security

### Input Validation
```python
# Validate coordinates
try:
    lat = float(request.args.get('lat', DEFAULT_LATITUDE))
    if not (-90 <= lat <= 90):
        return jsonify({'error': 'Invalid latitude'}), 400
except ValueError:
    return jsonify({'error': 'Invalid latitude format'}), 400
```

### CORS and Headers
```python
# Security headers (would be added in production)
@app.after_request
def after_request(response):
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'DENY'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    return response
```

### Rate Limiting
```python
# Would implement rate limiting for production
from flask_limiter import Limiter

limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_limits=["100 per hour", "10 per minute"]
)
```

## Integration Points

### With Core Tracker
```python
from core.main import StarlinkTracker

# Global tracker instance
tracker_instance = StarlinkTracker()

@app.route('/api/satellites')
def api_satellites():
    satellites = tracker_instance.update_tle_data()
    # Process and return data
```

### With Configuration Manager
```python
from utils.config_manager import get_config

config = get_config()
DEFAULT_LATITUDE = config['observer'].get('default_latitude', 55.7558)
```

### With Data Processor
```python
from utils.data_processor import DataProcessor

@app.route('/api/export/<format>')
def api_export(format):
    processor = DataProcessor()
    # Export data using processor
```

## Testing

The Web Application includes comprehensive unit tests in `src/tests/test_web_app.py` that cover:

1. **Endpoint Tests**: All API endpoints
2. **Caching Tests**: Cache decorator functionality
3. **Error Handling Tests**: Error decorator behavior
4. **Validation Tests**: Input parameter validation
5. **Integration Tests**: Complete request/response cycles

### Example Test
```python
import unittest
from unittest.mock import patch
import json

class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()
    
    def test_api_satellites(self):
        response = self.app.get('/api/satellites')
        self.assertEqual(response.status_code, 200)
        data = json.loads(response.data)
        self.assertIn('satellites', data)
```

## Dependencies

### Required
- **flask**: Web framework
- **requests**: HTTP requests (indirect dependency)
- **json**: JSON handling

### Optional
- **flask-cors**: Cross-origin resource sharing
- **flask-limiter**: Rate limiting
- **gunicorn**: Production WSGI server

## Configuration

The Web Application uses the following configuration sections:

### observer
```json
{
  "observer": {
    "default_latitude": 55.7558,
    "default_longitude": 37.6173
  }
}
```

### web (implied)
```json
{
  "web": {
    "host": "0.0.0.0",
    "port": 5000,
    "debug": false
  }
}
```

## Extensibility

The Web Application is designed for easy extension:

1. **New API Endpoints**: Add routes for additional functionality
2. **Custom Templates**: Create new web pages
3. **Authentication**: Add user authentication and authorization
4. **Advanced Caching**: Implement Redis or Memcached
5. **Real-time Updates**: Add WebSocket support for live data

### Adding New Endpoints
```python
@app.route('/api/custom')
@handle_api_errors
@cached(ttl=300)
def api_custom():
    """New custom API endpoint."""
    data = get_custom_data()
    return jsonify(data)
```

### Custom Error Responses
```python
@app.route('/api/protected')
@handle_api_errors
def api_protected():
    if not is_authorized():
        return jsonify({'error': 'Unauthorized'}), 401
    # Protected functionality
```

## Best Practices

### When Using This Module

1. **Secure Deployment**: Don't use debug mode in production
2. **Input Validation**: Always validate API parameters
3. **Error Handling**: Use error decorators consistently
4. **Caching**: Apply caching to expensive operations
5. **Monitoring**: Log API requests and responses

### Performance Tips

1. **Cache Appropriately**: Set reasonable TTL values
2. **Limit Data**: Paginate large result sets
3. **Compress Responses**: Use gzip for large responses
4. **Database Optimization**: Optimize data access patterns

### Security Best Practices

1. **HTTPS**: Use TLS in production
2. **Input Sanitization**: Sanitize all user inputs
3. **Rate Limiting**: Implement request rate limiting
4. **Authentication**: Add authentication for sensitive endpoints
5. **Security Headers**: Set appropriate HTTP security headers

## Troubleshooting

### Common Issues

1. **Port Conflicts**: Change port in app.run()
2. **Permission Errors**: Run with appropriate permissions
3. **Dependency Issues**: Install missing packages
4. **Cache Problems**: Clear cache when debugging
5. **Network Issues**: Check firewall and network settings

### Debugging

Enable debug mode for development:
```python
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
```

Check logs for detailed error information:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Testing Endpoints

Test API endpoints manually:
```bash
# Test satellites endpoint
curl -v http://localhost:5000/api/satellites

# Test passes endpoint
curl -v "http://localhost:5000/api/passes?lat=40.7128&lon=-74.0060"

# Test cache clearing
curl -v -X POST http://localhost:5000/api/cache/clear
```

### Monitoring

Add request logging:
```python
@app.before_request
def log_request_info():
    logger.info(f"Request: {request.method} {request.url}")

@app.after_request
def log_response_info(response):
    logger.info(f"Response: {response.status}")
    return response
```

## Deployment

### Production Deployment
```python
# Production WSGI server (gunicorn example)
# gunicorn -w 4 -b 0.0.0.0:5000 web_app:app
```

### Environment Configuration
```python
import os

# Environment-based configuration
DEBUG = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
HOST = os.environ.get('FLASK_HOST', '0.0.0.0')
PORT = int(os.environ.get('FLASK_PORT', 5000))
```

### Health Checks
```python
@app.route('/health')
def health_check():
    """Health check endpoint for monitoring."""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })
```