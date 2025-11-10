# Starlink Satellite Tracker - Developer Guide

## Table of Contents
1. [Project Architecture](#project-architecture)
2. [Code Structure](#code-structure)
3. [Module Design](#module-design)
4. [Development Environment](#development-environment)
5. [Testing](#testing)
6. [Coding Standards](#coding-standards)
7. [API Design](#api-design)
8. [Performance Considerations](#performance-considerations)
9. [Security](#security)
10. [Deployment](#deployment)
11. [Contributing](#contributing)

## Project Architecture

### Overview
The Starlink Satellite Tracker follows a modular architecture with clear separation of concerns:

```
Presentation Layer (Web UI/API)
        ↓
Application Layer (Business Logic)
        ↓
Data Layer (TLE Processing/Storage)
        ↓
External Services (Celestrak, Notifications)
```

### Key Components

1. **Core Tracker**: Main satellite tracking logic
2. **Web Interface**: Flask-based web application
3. **Utilities**: Configuration, data processing, scheduling, notifications
4. **Tests**: Unit tests and integration tests
5. **Data Storage**: File-based caching system

### Data Flow

1. TLE data is downloaded from Celestrak
2. Data is parsed and cached
3. Predictions are calculated using Skyfield library
4. Results are cached for performance
5. Data is exposed via API or web interface
6. Notifications are sent based on configuration

## Code Structure

### Directory Layout
```
starlink_satellite_tracker/
├── src/
│   ├── core/           # Core tracking functionality
│   ├── web/            # Web interface and API
│   ├── utils/          # Utility modules
│   └── tests/          # Test suite
├── data/               # Data cache directory
├── templates/          # Web templates
├── config.json         # Configuration file
├── requirements.txt    # Dependencies
└── starlink_tracker.py # Main entry point
```

### Module Dependencies
```
core.main ← utils.config_manager
web.web_app ← core.main, utils.config_manager
utils.scheduler ← core.main, utils.config_manager
utils.data_processor ← utils.config_manager
utils.notify ← utils.config_manager
```

## Module Design

### Core Tracker (`src/core/main.py`)

#### Key Classes
- **StarlinkTracker**: Main tracking class
- **TLECache**: TLE data caching system
- **PredictionCache**: Results caching system

#### Design Patterns
- Singleton pattern for configuration management
- Caching pattern for performance optimization
- Observer pattern for scheduler integration

#### Key Methods
- `update_tle_data()`: Handles data fetching and caching
- `predict_passes()`: Calculates satellite passes with caching
- `visualize_orbits()`: Creates orbital visualizations
- `start_scheduler()`: Integrates with scheduler system

### Configuration Manager (`src/utils/config_manager.py`)

#### Key Classes
- **ConfigManager**: Singleton configuration manager
- **CronParser**: Cron expression parser (in scheduler)

#### Design Patterns
- Singleton pattern for global configuration access
- Factory pattern for configuration loading

#### Key Methods
- `get_config()`: Returns complete configuration
- `get_config_section()`: Returns specific section
- `get_config_value()`: Returns specific value
- `reload_config()`: Reloads configuration from file

### Data Processor (`src/utils/data_processor.py`)

#### Key Classes
- **DataProcessor**: Data processing and export
- **DataCache**: Generic data caching system

#### Design Patterns
- Strategy pattern for export formats
- Decorator pattern for caching

#### Key Methods
- `load_satellite_data()`: Loads TLE data
- `filter_satellites()`: Filters satellite data
- `export_to_csv()`: Exports to CSV
- `export_to_json()`: Exports to JSON
- `analyze_constellation()`: Analyzes satellite constellation

### Scheduler (`src/utils/scheduler.py`)

#### Key Classes
- **StarlinkScheduler**: Task scheduling system
- **JobExecutionCache**: Prevents duplicate job execution
- **CronParser**: Cron expression parser

#### Design Patterns
- Observer pattern for task execution
- Decorator pattern for job scheduling

#### Key Methods
- `setup_scheduled_tasks()`: Configures scheduled tasks
- `start_scheduler()`: Starts background scheduler
- `stop_scheduler()`: Stops scheduler
- `_update_tle_data()`: Scheduled TLE update task
- `_check_notifications()`: Scheduled notification task

### Notification System (`src/utils/notify.py`)

#### Key Classes
- **NotificationSystem**: Notification management

#### Design Patterns
- Strategy pattern for notification methods
- Factory pattern for message creation

#### Key Methods
- `send_email_notification()`: Sends email
- `send_telegram_notification()`: Sends Telegram message
- `notify_upcoming_pass()`: Sends pass notification

### Web Application (`src/web/web_app.py`)

#### Key Classes
- **APICache**: API response caching
- **Flask Application**: Web framework

#### Design Patterns
- MVC pattern for web interface
- Decorator pattern for caching and error handling

#### Key Methods
- `cached()`: Caching decorator
- `handle_api_errors()`: Error handling decorator
- API endpoints for data access
- Web page rendering

## Development Environment

### Prerequisites
- Python 3.8+
- pip package manager
- Virtual environment (recommended)
- Git for version control

### Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd starlink_satellite_tracker
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Install development dependencies:
```bash
pip install pytest pytest-cov pylint black sphinx sphinx-rtd-theme
```

### IDE Recommendations
- **VS Code**: With Python extension
- **PyCharm**: Professional or Community edition
- **Vim/Neovim**: With Python plugins

### Code Editor Configuration
Recommended settings:
- Line length: 88 characters (Black standard)
- Indentation: 4 spaces
- Encoding: UTF-8
- Line endings: LF (Unix)

## Testing

### Test Structure
```
src/tests/
├── test_core_tracker.py      # Core tracker tests
├── test_config_manager.py    # Configuration tests
├── test_data_processor.py    # Data processor tests
├── test_scheduler.py         # Scheduler tests
├── test_notify.py            # Notification tests
├── test_web_app.py           # Web application tests
└── test_integration.py       # Integration tests
```

### Running Tests

#### Unit Tests
```bash
# Run all tests
python -m pytest src/tests/ -v

# Run specific test file
python -m pytest src/tests/test_core_tracker.py -v

# Run specific test class
python -m pytest src/tests/test_core_tracker.py::TestStarlinkTracker -v

# Run with coverage
python -m pytest src/tests/ --cov=src --cov-report=html
```

#### Test Coverage
Aim for >80% code coverage. Check coverage with:
```bash
python -m pytest src/tests/ --cov=src --cov-report=term-missing
```

### Writing Tests

#### Test Structure
```python
import unittest
from unittest.mock import patch, MagicMock

class TestModule(unittest.TestCase):
    def setUp(self):
        # Setup test fixtures
        pass
    
    def tearDown(self):
        # Cleanup after tests
        pass
    
    @patch('module.dependency')
    def test_method_success(self, mock_dependency):
        # Arrange
        mock_dependency.return_value = expected_result
        
        # Act
        result = method_under_test()
        
        # Assert
        self.assertEqual(result, expected_result)
        mock_dependency.assert_called_once()
    
    def test_method_failure(self):
        # Test error conditions
        with self.assertRaises(ExpectedException):
            method_under_test(invalid_input)
```

#### Mocking Best Practices
1. Mock external dependencies (HTTP requests, file I/O)
2. Use specific mocks for predictable behavior
3. Verify mock interactions with assert_called methods
4. Mock at the appropriate level (unit vs integration)

### Integration Tests
```python
def test_full_workflow(self):
    """Test complete workflow from TLE download to prediction."""
    # This would test the entire flow without mocking
    # Use sparingly as these are slower
    pass
```

## Coding Standards

### Python Style Guide
Follow PEP 8 with these additional guidelines:

#### Naming Conventions
- Classes: PascalCase (`StarlinkTracker`)
- Functions/Methods: snake_case (`update_tle_data`)
- Variables: snake_case (`satellite_count`)
- Constants: UPPER_SNAKE_CASE (`MAX_CACHE_DAYS`)
- Private members: leading underscore (`_private_method`)

#### Code Organization
1. Import statements at top
2. Module docstring
3. Constants
4. Classes
5. Functions
6. Main execution block

#### Documentation
Every public method should have:
```python
def method_name(param1: str, param2: int = 0) -> bool:
    """
    Brief description of what the method does.
    
    Args:
        param1 (str): Description of param1
        param2 (int): Description of param2 (default: 0)
        
    Returns:
        bool: Description of return value
        
    Raises:
        ValueError: When invalid parameters are provided
        
    Example:
        >>> method_name("example", 5)
        True
    """
    pass
```

### Type Hints
Use type hints for all function parameters and return values:

```python
from typing import List, Dict, Optional, Any

def process_satellites(satellites: List[Dict[str, str]], 
                      criteria: Optional[Dict[str, Any]] = None) -> List[Dict[str, str]]:
    """Process satellite data with optional filtering."""
    pass
```

### Error Handling
1. Use specific exception types
2. Log errors appropriately
3. Provide meaningful error messages
4. Fail fast for unrecoverable errors

```python
import logging

logger = logging.getLogger(__name__)

def risky_operation():
    try:
        # Risky code
        pass
    except SpecificException as e:
        logger.error(f"Operation failed: {e}")
        raise  # Re-raise if needed
    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        raise RuntimeError("Operation failed unexpectedly") from e
```

### Code Quality Tools

#### Linting
```bash
pylint src/
```

#### Formatting
```bash
black src/
```

#### Static Analysis
```bash
# Type checking with mypy (if added to requirements)
mypy src/
```

## API Design

### RESTful Principles
1. Use HTTP methods appropriately (GET, POST, PUT, DELETE)
2. Use nouns for resource names
3. Use HTTP status codes correctly
4. Version APIs when breaking changes occur

### API Endpoints
```
GET    /api/satellites        # Get satellite data
GET    /api/passes            # Get pass predictions
GET    /api/coverage          # Get coverage data
GET    /api/export/{format}   # Export data
POST   /api/cache/clear       # Clear cache
```

### Response Format
```json
{
  "data": {...},
  "meta": {
    "count": 100,
    "timestamp": "2025-11-10T15:30:00Z"
  }
}
```

### Error Responses
```json
{
  "error": {
    "code": "INVALID_PARAMETER",
    "message": "Latitude must be between -90 and 90",
    "details": {
      "parameter": "lat",
      "value": "100"
    }
  }
}
```

### Rate Limiting
Implement rate limiting to prevent abuse:
- 100 requests per hour per IP
- 10 requests per minute for expensive operations

### Authentication
For future expansion, consider:
- API keys for programmatic access
- OAuth for user authentication
- JWT tokens for session management

## Performance Considerations

### Caching Strategy

#### Cache Layers
1. **TLE Cache**: Memory cache for TLE data (6 hours)
2. **Prediction Cache**: Results cache (15 minutes)
3. **API Cache**: Web API responses (varies by endpoint)
4. **Data Processor Cache**: Processed data cache

#### Cache Invalidation
```python
class Cache:
    def __init__(self, ttl=300):
        self.ttl = ttl
        self.cache = {}
        self.timestamps = {}
    
    def get(self, key):
        if key in self.cache:
            if time.time() - self.timestamps[key] < self.ttl:
                return self.cache[key]
            else:
                # Expired, remove
                del self.cache[key]
                del self.timestamps[key]
        return None
```

### Memory Management
1. Limit satellite processing to first N satellites
2. Use generators for large datasets
3. Clear caches periodically
4. Monitor memory usage in long-running processes

### Database Considerations
Currently uses file-based storage. For scaling:
1. Consider SQLite for local storage
2. PostgreSQL/MongoDB for distributed systems
3. Redis for caching layer

### Asynchronous Processing
For long-running operations:
1. Use threading for I/O bound tasks
2. Consider asyncio for high-concurrency scenarios
3. Implement job queues for background processing

## Security

### Input Validation
```python
def validate_coordinates(lat: float, lon: float) -> bool:
    """Validate geographic coordinates."""
    if not (-90 <= lat <= 90):
        raise ValueError(f"Invalid latitude: {lat}")
    if not (-180 <= lon <= 180):
        raise ValueError(f"Invalid longitude: {lon}")
    return True
```

### Configuration Security
1. Never commit sensitive data to repository
2. Use environment variables for secrets
3. Encrypt sensitive configuration data
4. Implement configuration validation

### API Security
1. Implement rate limiting
2. Use HTTPS in production
3. Validate all input parameters
4. Sanitize output data
5. Implement proper error handling

### Dependency Security
1. Regularly update dependencies
2. Use pip-audit to check for vulnerabilities
3. Pin dependency versions in requirements.txt
4. Review dependency licenses

## Deployment

### Production Deployment

#### Server Requirements
- Python 3.8+
- 2GB RAM minimum
- 500MB disk space
- Internet access for TLE downloads

#### Deployment Steps
1. Clone repository to server
2. Create virtual environment
3. Install dependencies
4. Configure config.json for production
5. Set up systemd service or similar process manager
6. Configure reverse proxy (nginx/Apache)
7. Set up SSL certificate
8. Monitor logs and performance

#### Docker Deployment
Create Dockerfile:
```dockerfile
FROM python:3.8-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 5000
CMD ["python", "starlink_tracker.py", "web"]
```

Build and run:
```bash
docker build -t starlink-tracker .
docker run -p 5000:5000 starlink-tracker
```

### Environment Configuration
Use environment variables for sensitive configuration:
```python
import os

# In config_manager.py
def _load_config(self):
    config = self._load_from_file()
    
    # Override with environment variables
    if 'CELESTRAK_URL' in os.environ:
        config['data_sources']['celestrak_url'] = os.environ['CELESTRAK_URL']
    
    return config
```

### Monitoring and Logging
1. Implement structured logging
2. Set up log rotation
3. Monitor key metrics (cache hit rates, API response times)
4. Set up alerting for errors
5. Use application performance monitoring (APM) tools

### Backup and Recovery
1. Regular backups of configuration
2. Backup scripts for cached data
3. Disaster recovery procedures
4. Test backup restoration regularly

## Contributing

### Development Workflow
1. Fork the repository
2. Create feature branch
3. Implement changes
4. Write/update tests
5. Update documentation
6. Run tests and linters
7. Submit pull request

### Pull Request Guidelines
1. Each PR should address one feature or bug fix
2. Include tests for new functionality
3. Update documentation as needed
4. Follow coding standards
5. Include clear description of changes
6. Reference related issues

### Code Review Process
1. At least one approval required
2. Review for correctness, performance, security
3. Check adherence to coding standards
4. Verify tests pass
5. Ensure documentation is updated

### Release Process
1. Update version number
2. Update CHANGELOG.md
3. Create git tag
4. Build distribution packages
5. Publish to package repository
6. Update documentation

### Community Guidelines
1. Be respectful and inclusive
2. Provide constructive feedback
3. Help newcomers
4. Follow code of conduct
5. Report issues responsibly

### Getting Started for New Contributors
1. Read this developer guide
2. Set up development environment
3. Run existing tests
4. Start with small bug fixes
5. Join community discussions
6. Follow project roadmap