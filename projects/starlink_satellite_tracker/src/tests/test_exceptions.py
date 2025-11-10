#!/usr/bin/env python3
"""
Test suite for Starlink Tracker Custom Exceptions
Verifies that custom exceptions work correctly
"""

import unittest
import sys
import os

# Add the project directory to the path so we can import our modules
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

from core.main import (
    StarlinkTrackerError, 
    TLEDataError, 
    PredictionError, 
    SchedulerError, 
    VisualizationError
)


class TestStarlinkTrackerExceptions(unittest.TestCase):
    """Test suite for custom exception classes."""

    def test_starlink_tracker_error_base(self):
        """Test base exception class."""
        # Test instantiation
        error = StarlinkTrackerError("Test error message")
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Test error message")
        
        # Test with no message
        error = StarlinkTrackerError()
        self.assertIsInstance(error, Exception)

    def test_tle_data_error(self):
        """Test TLE data exception."""
        # Test instantiation
        error = TLEDataError("TLE data error")
        self.assertIsInstance(error, StarlinkTrackerError)
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "TLE data error")

    def test_prediction_error(self):
        """Test prediction exception."""
        # Test instantiation
        error = PredictionError("Prediction error")
        self.assertIsInstance(error, StarlinkTrackerError)
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Prediction error")

    def test_scheduler_error(self):
        """Test scheduler exception."""
        # Test instantiation
        error = SchedulerError("Scheduler error")
        self.assertIsInstance(error, StarlinkTrackerError)
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Scheduler error")

    def test_visualization_error(self):
        """Test visualization exception."""
        # Test instantiation
        error = VisualizationError("Visualization error")
        self.assertIsInstance(error, StarlinkTrackerError)
        self.assertIsInstance(error, Exception)
        self.assertEqual(str(error), "Visualization error")


if __name__ == '__main__':
    unittest.main(verbosity=2)