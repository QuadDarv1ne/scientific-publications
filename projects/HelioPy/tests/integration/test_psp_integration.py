"""
Integration tests for Parker Solar Probe functionality in core data loader.
"""

import unittest
from unittest.mock import patch, MagicMock

from heliopy.core.data_loader import DataLoader


class TestPSPIntegration(unittest.TestCase):
    """Integration tests for Parker Solar Probe functionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.data_loader = DataLoader()

    def test_psp_loader_initialization(self):
        """Test that PSP loader is properly initialized."""
        self.assertTrue(hasattr(self.data_loader, 'psp_loader'))

    @patch('heliopy.data_sources.psp_loader.PSPLoader.load_sweap')
    def test_load_psp_sweap(self, mock_load_sweap):
        """Test load_psp_sweap method."""
        # Mock the return value
        mock_df = MagicMock()
        mock_load_sweap.return_value = mock_df
        
        # Test the method
        result = self.data_loader.load_psp_sweap("2023-10-15", "spc")
        
        # Verify the result
        self.assertEqual(result, mock_df)
        mock_load_sweap.assert_called_once_with("2023-10-15", "spc")

    @patch('heliopy.data_sources.psp_loader.PSPLoader.load_fld')
    def test_load_psp_fld(self, mock_load_fld):
        """Test load_psp_fld method."""
        # Mock the return value
        mock_df = MagicMock()
        mock_load_fld.return_value = mock_df
        
        # Test the method
        result = self.data_loader.load_psp_fld("2023-10-15", "mag_rtn")
        
        # Verify the result
        self.assertEqual(result, mock_df)
        mock_load_fld.assert_called_once_with("2023-10-15", "mag_rtn")


if __name__ == '__main__':
    unittest.main()