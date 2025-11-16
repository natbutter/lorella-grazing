"""
Placeholder downloader for Sentinel-2 L2A tiles covering a geometry.

This module contains an example function using sentinelsat to search and download scenes.
For the demo, the function will be a stub that instructs using demo data.
"""

from typing import Optional
from .config import COPERNICUS_USER, COPERNICUS_PASS
from shapely.geometry import mapping
import logging

logger = logging.getLogger(__name__)

def download_sentinel_for_geometry(geometry, out_dir, date_range=None) -> Optional[str]:
    """
    Download nearest Sentinel-2 L2A scene for the given geometry.

    For production: implement search with sentinelsat.CopernicusAPI and download assets.
    For demo: caller will use locally generated sample data instead.

    Returns path to downloaded file or None (demo).
    """
    logger.info("download_sentinel_for_geometry called. COPERNICUS_USER present: %s", bool(COPERNICUS_USER))
    # Placeholder: return None to indicate demo usage
    return None

