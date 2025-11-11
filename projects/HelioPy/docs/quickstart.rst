Quick Start Guide
=================

This guide will help you get started with HelioPy.

Basic Usage
-----------

Time Utilities
~~~~~~~~~~~~~~

Working with time conversions::

   from heliopy.utils import time_utils
   from datetime import datetime
   
   # Parse time string
   dt = time_utils.parse_time("2023-10-15 12:00:00")
   
   # Convert to Julian Date
   jd = time_utils.to_julian_date(dt)
   print(f"Julian Date: {jd}")
   
   # Generate time range
   times = time_utils.time_range(
       start=datetime(2023, 10, 15, 0, 0),
       end=datetime(2023, 10, 15, 23, 59),
       step_minutes=60
   )
   print(f"Generated {len(times)} time points")

Mathematical Utilities
~~~~~~~~~~~~~~~~~~~~~~

Coordinate transformations::

   from heliopy.utils import math_utils
   import numpy as np
   
   # Spherical to Cartesian
   r, theta, phi = 1.0, np.pi/4, np.pi/6
   x, y, z = math_utils.spherical_to_cartesian(r, theta, phi)
   
   # Calculate angular separation
   lon1, lat1 = 45.0, 30.0
   lon2, lat2 = 50.0, 35.0
   angle = math_utils.angular_separation(lon1, lat1, lon2, lat2)
   print(f"Angular separation: {angle:.2f}°")

Statistical Analysis
~~~~~~~~~~~~~~~~~~~~

Robust statistics::

   from heliopy.utils import stats_utils
   import numpy as np
   
   # Generate sample data
   data = np.random.normal(100, 15, 1000)
   
   # Calculate robust statistics
   stats = stats_utils.robust_statistics(data)
   print(f"Median: {stats['median']:.2f}")
   print(f"MAD: {stats['mad']:.2f}")
   
   # Remove outliers
   clean_data, mask = stats_utils.remove_outliers(data, threshold=3.0)
   print(f"Removed {np.sum(~mask)} outliers")

Flare Detection
---------------

Detecting solar flares in GOES data::

   from heliopy.events.flare_detector import FlareDetector, GOESData
   from astropy.time import Time
   import numpy as np
   
   # Create synthetic GOES data
   n_points = 1440  # 24 hours at 1-minute cadence
   time_array = Time("2023-10-15 00:00:00") + np.arange(n_points) * 60 / 86400
   fluxes = np.random.uniform(1e-7, 1e-6, n_points)
   
   goes_data = GOESData(
       time=time_array,
       xrsa=fluxes,
       xrsb=fluxes * 1.5,
       satellite="GOES-16"
   )
   
   # Detect flares
   detector = FlareDetector()
   flares = detector.detect_flares(goes_data)
   
   print(f"Detected {len(flares)} flares")
   for flare in flares:
       print(f"Class {flare.class_}: {flare.peak_time}")

Image Processing
----------------

Processing solar images::

   from heliopy.imaging.image_processor import ImageProcessor, SolarImage
   from astropy.time import Time
   import numpy as np
   
   # Create synthetic solar image
   size = 512
   y, x = np.ogrid[-size/2:size/2, -size/2:size/2]
   r = np.sqrt(x**2 + y**2)
   
   # Solar disk with limb darkening
   disk_data = np.zeros((size, size))
   disk_radius = size // 4
   disk_mask = r <= disk_radius
   disk_data[disk_mask] = 1.0 - (r[disk_mask] / disk_radius)**2 * 0.5
   
   image = SolarImage(
       data=disk_data,
       time=Time("2023-10-15 12:00:00"),
       wavelength=193,
       instrument="AIA",
       observatory="SDO"
   )
   
   # Process image
   processor = ImageProcessor()
   normalized = processor.normalize(image.data, method='minmax')
   
   print(f"Image normalized: {normalized.min():.2f} - {normalized.max():.2f}")

Next Steps
----------

* Explore the :doc:`examples` for more detailed use cases
* Check the :doc:`api/core` for full API documentation
* Read the :doc:`contributing` guide to contribute to HelioPy
