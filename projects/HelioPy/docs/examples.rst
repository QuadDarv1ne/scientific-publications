Examples
========

This section contains detailed examples of using HelioPy for various tasks.

Basic Usage
-----------

See ``examples/01_basic_usage.py`` for a complete example of using utility functions.

Key features demonstrated:

* Time conversions and parsing
* Coordinate transformations
* Statistical analysis
* Data filtering

Flare Analysis
--------------

See ``examples/02_flare_analysis.py`` for solar flare detection and classification.

This example shows:

* Creating synthetic GOES data
* Detecting solar flares
* Classifying flares by intensity
* Analyzing flare properties

Image Processing
----------------

See ``examples/03_image_processing.py`` for solar image processing.

Topics covered:

* Creating synthetic solar images
* Image normalization techniques
* Solar disk analysis
* Active region detection

Running Examples
----------------

All examples are located in the ``examples/`` directory::

   cd examples
   python 01_basic_usage.py
   python 02_flare_analysis.py
   python 03_image_processing.py

Custom Examples
---------------

Loading Real Data
~~~~~~~~~~~~~~~~~

Example of loading GOES data::

   from heliopy.data_sources.goes_loader import GOESLoader
   from datetime import datetime
   
   loader = GOESLoader()
   data = loader.load(
       start_time=datetime(2023, 10, 15),
       end_time=datetime(2023, 10, 16),
       satellite='goes16'
   )

Working with Coordinates
~~~~~~~~~~~~~~~~~~~~~~~~

Coordinate system conversions::

   from heliopy.core.coordinate_systems import CoordinateSystem
   
   coords = CoordinateSystem()
   
   # Heliographic to Cartesian
   lon, lat, r = 45.0, 30.0, 1.0  # degrees and AU
   x, y, z = coords.heliographic_to_cartesian(lon, lat, r)

Advanced Topics
---------------

For more advanced usage, see the API documentation:

* :doc:`api/events` - Event detection algorithms
* :doc:`api/magnetic_fields` - Magnetic field analysis
* :doc:`api/models` - Predictive models
* :doc:`api/space_weather` - Space weather forecasting
