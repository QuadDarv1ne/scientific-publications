"""
Unit tests for Parker Solar Probe data loader.
"""

import unittest
from unittest.mock import patch, MagicMock

from heliopy.data_sources.psp_loader import PSPLoader


class TestPSPLoader(unittest.TestCase):
    """Test cases for PSPLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = PSPLoader()

    def test_init(self):
        """Test initialization of PSPLoader."""
        self.assertIsInstance(self.loader, PSPLoader)
        self.assertEqual(self.loader.base_url, "https://spdf.gsfc.nasa.gov/pub/data/psp/")

    def test_load_sweap_spc(self):
        """Test load_sweap method with spc data type."""
        # Test with valid data
        result = self.loader.load_sweap("2023-10-15", "spc")
        self.assertIsNotNone(result)
        self.assertIn("time", result.columns)
        self.assertIn("density", result.columns)
        self.assertIn("velocity", result.columns)
        self.assertIn("temperature", result.columns)

    def test_load_sweap_spe(self):
        """Test load_sweap method with spe data type."""
        # Test with valid data
        result = self.loader.load_sweap("2023-10-15", "spe")
        self.assertIsNotNone(result)
        self.assertIn("time", result.columns)
        self.assertIn("energy", result.columns)
        self.assertIn("flux", result.columns)

    def test_load_sweap_invalid_type(self):
        """Test load_sweap method with invalid data type."""
        with self.assertRaises(ValueError):
            self.loader.load_sweap("2023-10-15", "invalid")

    def test_load_fld_mag_rtn(self):
        """Test load_fld method with mag_rtn data type."""
        # Test with valid data
        result = self.loader.load_fld("2023-10-15", "mag_rtn")
        self.assertIsNotNone(result)
        self.assertIn("time", result.columns)
        self.assertIn("Br", result.columns)
        self.assertIn("Bt", result.columns)
        self.assertIn("Bn", result.columns)
        self.assertIn("Btot", result.columns)

    def test_load_fld_invalid_type(self):
        """Test load_fld method with invalid data type."""
        with self.assertRaises(ValueError):
            self.loader.load_fld("2023-10-15", "invalid")


if __name__ == '__main__':
    unittest.main()