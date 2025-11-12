"""
Unit tests for Helioviewer data loader.
"""

import unittest
from unittest.mock import patch, MagicMock

from heliopy.data_sources.helioviewer_loader import HelioviewerLoader


class TestHelioviewerLoader(unittest.TestCase):
    """Test cases for HelioviewerLoader class."""

    def setUp(self):
        """Set up test fixtures."""
        self.loader = HelioviewerLoader()

    def test_init(self):
        """Test initialization of HelioviewerLoader."""
        self.assertIsInstance(self.loader, HelioviewerLoader)
        self.assertEqual(self.loader.base_url, "https://api.helioviewer.org/v2/")

    @patch('hvpy.getDataSources')
    def test_get_data_sources(self, mock_get_data_sources):
        """Test get_data_sources method."""
        # Mock the return value
        mock_get_data_sources.return_value = {"test": "data"}
        
        # Test the method
        result = self.loader.get_data_sources()
        
        # Verify the result
        self.assertEqual(result, {"test": "data"})
        mock_get_data_sources.assert_called_once()

    def test_get_wavelength_from_source(self):
        """Test _get_wavelength_from_source method."""
        # Test known source IDs
        self.assertEqual(self.loader._get_wavelength_from_source(14), 193.0)
        self.assertEqual(self.loader._get_wavelength_from_source(13), 171.0)
        self.assertEqual(self.loader._get_wavelength_from_source(999), None)  # Unknown ID

    def test_get_instrument_from_source(self):
        """Test _get_instrument_from_source method."""
        # Test known source IDs
        self.assertEqual(self.loader._get_instrument_from_source(14), "AIA")
        self.assertEqual(self.loader._get_instrument_from_source(999), "Unknown")  # Unknown ID

    def test_get_observatory_from_source(self):
        """Test _get_observatory_from_source method."""
        # Test known source IDs
        self.assertEqual(self.loader._get_observatory_from_source(14), "SDO")
        self.assertEqual(self.loader._get_observatory_from_source(999), "Unknown")  # Unknown ID


if __name__ == '__main__':
    unittest.main()