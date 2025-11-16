"""
Feature extraction utilities.
Computes indices like NDVI, NDWI, BSI and a simple cloud mask.
"""
from typing import Tuple
import numpy as np

def ndvi(nir: np.ndarray, red: np.ndarray) -> np.ndarray:
    """
    NDVI = (NIR - Red) / (NIR + Red)
    """
    np.seterr(divide='ignore', invalid='ignore')
    denom = (nir + red).astype(float)
    nd = (nir - red) / denom
    nd[np.isnan(nd)] = 0.0
    return nd

def ndwi(green: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """
    NDWI = (Green - NIR) / (Green + NIR)
    """
    np.seterr(divide='ignore', invalid='ignore')
    denom = (green + nir).astype(float)
    nd = (green - nir) / denom
    nd[np.isnan(nd)] = 0.0
    return nd

def bsi(blue: np.ndarray, red: np.ndarray, nir: np.ndarray, swir: np.ndarray) -> np.ndarray:
    """
    Bare Soil Index (BSI) simplified:
    BSI = (SWIR + Red - NIR - Blue) / (SWIR + Red + NIR + Blue)
    """
    np.seterr(divide='ignore', invalid='ignore')
    denom = (swir + red + nir + blue).astype(float)
    out = (swir + red - nir - blue) / denom
    out[np.isnan(out)] = 0.0
    return out

def simple_cloud_mask(blue: np.ndarray, cirrus: np.ndarray = None, threshold: float = 0.2) -> np.ndarray:
    """
    Very simple cloud mask based on bright blue reflectance (band 2) thresholding.
    Returns boolean mask: True where cloud.
    """
    # blue expected to be scaled reflectance 0-1 or 0-10000 depending on input; we assume 0-10000 and normalize if max>1
    if blue.max() > 2:
        b = blue / 10000.0
    else:
        b = blue
    mask = b > threshold
    return mask

