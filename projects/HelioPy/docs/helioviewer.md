# Helioviewer Integration

## Overview

Helioviewer is a web-based tool for browsing and downloading solar and heliospheric datasets. This integration allows HelioPy to access a wide variety of solar observation data from multiple missions and instruments.

## Available Data Sources

The Helioviewer integration provides access to data from:

- **SDO (Solar Dynamics Observatory)**
  - AIA (Atmospheric Imaging Assembly)
    - 193Å (ID: 14)
    - 171Å (ID: 13)
    - 211Å (ID: 15)
    - 304Å (ID: 16)
    - 1600Å (ID: 17)
    - 1700Å (ID: 18)
    - 4500Å (ID: 19)

- **SOHO (Solar and Heliospheric Observatory)**
  - EIT (Extreme ultraviolet Imaging Telescope)
    - 171Å (ID: 6)
    - 195Å (ID: 7)
    - 284Å (ID: 8)
    - 304Å (ID: 9)

## Usage

### Python API

```python
from heliopy import load_helioviewer

# Load an image from Helioviewer
date = "2023-10-15T12:00:00"
source_id = 14  # SDO/AIA 193Å
image = load_helioviewer(date, source_id)

# Get available data sources
sources = data_loader.get_helioviewer_sources()
```

### Command Line Interface

```bash
# Show available Helioviewer data sources
python -m heliopy helioviewer
```

### Web Interface

The web interface includes a dedicated Helioviewer page that allows users to:
- Browse available data sources
- Visualize solar images from different instruments
- Select specific wavelengths and observation times

## Requirements

To use the Helioviewer functionality, you need to install the `hvpy` package:

```bash
pip install hvpy
```

## API Endpoints

The web application provides the following API endpoints for Helioviewer integration:

- `GET /api/helioviewer/sources` - Get available data sources

## Future Improvements

Planned enhancements for the Helioviewer integration include:

1. **Enhanced Data Loading**: Full implementation of image loading from the Helioviewer API
2. **Advanced Visualization**: Multi-wavelength composite images
3. **Time Series Analysis**: Animation creation from temporal sequences
4. **Metadata Integration**: Enhanced metadata extraction and processing
5. **Caching Improvements**: Better local caching of downloaded data

## References

- [Helioviewer Project](https://www.helioviewer.org/)
- [Helioviewer API Documentation](https://api.helioviewer.org/docs/v2/)
- [hvpy Library](https://pypi.org/project/hvpy/)