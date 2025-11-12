"""
Universal data loader.
"""

from datetime import datetime
from pathlib import Path
from typing import Optional, Union

import pandas as pd

from heliopy.data_sources.ace_loader import ACELoader
from heliopy.data_sources.goes_loader import GOESLoader
from heliopy.data_sources.helioviewer_loader import HelioviewerLoader
from heliopy.data_sources.psp_loader import PSPLoader
from heliopy.data_sources.sdo_loader import SDOLoader
from heliopy.data_sources.soho_loader import SOHOLoader
from heliopy.utils.config import get_config


class DataLoader:
    """Universal class for loading data from various sources."""

    def __init__(self, cache_dir: Optional[Path] = None):
        """
        Initialize the data loader.

        Parameters
        ----------
        cache_dir : Path, optional
            Directory for caching data.
        """
        config = get_config()
        self.cache_dir = cache_dir or config.cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        # Инициализация загрузчиков для различных источников
        self.sdo_loader = SDOLoader(cache_dir=self.cache_dir)
        self.soho_loader = SOHOLoader(cache_dir=self.cache_dir)
        self.goes_loader = GOESLoader(cache_dir=self.cache_dir)
        self.ace_loader = ACELoader(cache_dir=self.cache_dir)
        self.helioviewer_loader = HelioviewerLoader(cache_dir=self.cache_dir)
        self.psp_loader = PSPLoader(cache_dir=self.cache_dir)

    def load_sdo_aia(self, date: Union[str, datetime], wavelength: int, **kwargs) -> "SolarImage":
        """
        Load SDO/AIA data.

        Parameters
        ----------
        date : str or datetime
            Observation date.
        wavelength : int
            Wavelength in angstroms (94, 131, 171, 193, 211, 304, 335).
        **kwargs
            Additional parameters.

        Returns
        -------
        SolarImage
            Object with image data.
        """
        return self.sdo_loader.load_aia(date, wavelength, **kwargs)

    def load_sdo_hmi(
        self, date: Union[str, datetime], data_type: str = "magnetogram", **kwargs
    ) -> "SolarImage":
        """
        Load SDO/HMI data.

        Parameters
        ----------
        date : str or datetime
            Observation date.
        data_type : str
            Data type ('magnetogram', 'continuum', 'dopplergram').
        **kwargs
            Additional parameters.

        Returns
        -------
        SolarImage
            Object with image data.
        """
        return self.sdo_loader.load_hmi(date, data_type, **kwargs)

    def load_soho_lasco(
        self, date: Union[str, datetime], coronagraph: str = "C2", **kwargs
    ) -> "SolarImage":
        """
        Load SOHO/LASCO data.

        Parameters
        ----------
        date : str or datetime
            Observation date.
        coronagraph : str
            Coronagraph ('C2' or 'C3').
        **kwargs
            Additional parameters.

        Returns
        -------
        SolarImage
            Object with image data.
        """
        return self.soho_loader.load_lasco(date, coronagraph, **kwargs)

    def load_goes(self, date: Union[str, datetime], **kwargs) -> "GOESData":
        """
        Load GOES data.

        Parameters
        ----------
        date : str or datetime
            Observation date.
        **kwargs
            Additional parameters.

        Returns
        -------
        GOESData
            Object with GOES data.
        """
        return self.goes_loader.load(date, **kwargs)

    def load_ace(self, date: Union[str, datetime], **kwargs) -> "ACEData":
        """
        Load ACE data.

        Parameters
        ----------
        date : str or datetime
            Observation date.
        **kwargs
            Additional parameters.

        Returns
        -------
        ACEData
            Object with ACE data.
        """
        return self.ace_loader.load(date, **kwargs)

    def load_helioviewer(
        self, date: Union[str, datetime], source_id: int = 14, **kwargs
    ) -> "SolarImage":
        """
        Load Helioviewer data.

        Parameters
        ----------
        date : str or datetime
            Observation date.
        source_id : int
            Source ID (default is SDO/AIA 193Å).
        **kwargs
            Additional parameters.

        Returns
        -------
        SolarImage
            Object with image data.
        """
        return self.helioviewer_loader.load_image(date, source_id, **kwargs)

    def get_helioviewer_sources(self) -> dict:
        """
        Get available Helioviewer data sources.

        Returns
        -------
        dict
            Dictionary with information about data sources.
        """
        return self.helioviewer_loader.get_data_sources()

    def load_psp_sweap(
        self, date: Union[str, datetime], data_type: str = "spc", **kwargs
    ) -> pd.DataFrame:
        """
        Load PSP SWEAP data.

        Parameters
        ----------
        date : str or datetime
            Observation date.
        data_type : str
            Data type ('spc' or 'spe').
        **kwargs
            Additional parameters.

        Returns
        -------
        DataFrame
            SWEAP data.
        """
        return self.psp_loader.load_sweap(date, data_type, **kwargs)

    def load_psp_fld(
        self, date: Union[str, datetime], data_type: str = "mag_rtn", **kwargs
    ) -> pd.DataFrame:
        """
        Load PSP FIELDS data.

        Parameters
        ----------
        date : str or datetime
            Observation date.
        data_type : str
            Data type ('mag_rtn' or 'mag_sc').
        **kwargs
            Additional parameters.

        Returns
        -------
        DataFrame
            FIELDS data.
        """
        return self.psp_loader.load_fld(date, data_type, **kwargs)


# Convenience functions (as in README)
def load_sdo_aia(date: Union[str, datetime], wavelength: int, **kwargs):
    """Convenience function for loading SDO/AIA data."""
    loader = DataLoader()
    return loader.load_sdo_aia(date, wavelength, **kwargs)


def load_soho_lasco(date: Union[str, datetime], coronagraph: str = "C2", **kwargs):
    """Convenience function for loading SOHO/LASCO data."""
    loader = DataLoader()
    return loader.load_soho_lasco(date, coronagraph, **kwargs)


def load_goes(date: Union[str, datetime], **kwargs):
    """Convenience function for loading GOES data."""
    loader = DataLoader()
    return loader.load_goes(date, **kwargs)

def load_helioviewer(date: Union[str, datetime], source_id: int = 14, **kwargs):
    """Convenience function for loading Helioviewer data."""
    loader = DataLoader()
    return loader.load_helioviewer(date, source_id, **kwargs)

def load_psp_sweap(date: Union[str, datetime], data_type: str = "spc", **kwargs):
    """Convenience function for loading PSP SWEAP data."""
    loader = DataLoader()
    return loader.load_psp_sweap(date, data_type, **kwargs)

def load_psp_fld(date: Union[str, datetime], data_type: str = "mag_rtn", **kwargs):
    """Convenience function for loading PSP FIELDS data."""
    loader = DataLoader()
    return loader.load_psp_fld(date, data_type, **kwargs)
