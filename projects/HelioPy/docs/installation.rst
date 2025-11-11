Installation
============

Requirements
------------

HelioPy requires Python 3.8 or higher.

Installing with pip
-------------------

From source::

   git clone https://github.com/QuadDarv1ne/scientific-publications.git
   cd scientific-publications/projects/HelioPy
   pip install -e .

Installing dependencies
-----------------------

Base dependencies::

   pip install -r requirements/base.txt

Development dependencies::

   pip install -r requirements/dev.txt

Documentation dependencies::

   pip install -r requirements/docs.txt

Optional dependencies
---------------------

For SDO/SOHO data support::

   pip install sunpy

Verifying installation
----------------------

Test the installation::

   python -c "import heliopy; print(heliopy.__version__)"

Run the test suite::

   pytest tests/

Virtual environment
-------------------

It's recommended to use a virtual environment::

   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On Linux/macOS
   source venv/bin/activate

Common issues
-------------

**ImportError: No module named 'sunpy'**

SunPy is an optional dependency. Install it with::

   pip install sunpy

Or use the library without SDO/SOHO data loaders.

**Python version mismatch**

Check your Python version::

   python --version

HelioPy requires Python 3.8 or higher.
