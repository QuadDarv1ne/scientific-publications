# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [2.0.0] - 2024-11-11

### Added

- Prometheus metrics exporter on port 9817
- Docker deployment with docker-compose
- Comprehensive documentation (README.md, DOCKER.md)
- PostgreSQL database support
- ML-based anomaly detection and forecasting
- Web dashboard with real-time updates
- Alert system with notifications
- Weather data integration
- Automated report generation

### Fixed

- Windows file locking issues in logging system
- SQLAlchemy sessionmaker pattern
- Flask-SocketIO compatibility with Python 3.14
- Deprecated datetime.utcnow() warnings
- SQLAlchemy declarative_base import warnings

### Changed

- Updated to SQLAlchemy 2.0+ API
- Improved logging with rotating file handlers
- Enhanced error handling and validation
- Optimized database connection pooling

### Security

- Added .dockerignore for secure builds
- Environment-based configuration
- Non-root Docker user

## [1.0.0] - 2024-01-01

### Added

- Initial release
- Basic Starlink monitoring functionality
- Speed test integration
- SQLite database storage
- Simple web interface

[2.0.0]: https://github.com/QuadDarv1ne/starlink_performance_monitor/compare/v1.0.0...v2.0.0
[1.0.0]: https://github.com/QuadDarv1ne/starlink_performance_monitor/releases/tag/v1.0.0
