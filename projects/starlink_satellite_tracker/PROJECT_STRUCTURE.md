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
    │   ├── data_processor.py   # Data handling
    │   └── notify.py           # Notification system
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

### Web Module (`src/web/`)
- **web_app.py**: Flask-based web application with RESTful API
- Provides web interface for satellite tracking, pass predictions, and data visualization
- Includes API endpoints for integration with other systems

### Utilities Module (`src/utils/`)
- **data_processor.py**: Data handling, analysis, and export functionality
- **notify.py**: Notification system with email and Telegram support

### Tests Module (`src/tests/`)
- Contains unit tests and demonstration scripts
- Includes various test files to verify functionality

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