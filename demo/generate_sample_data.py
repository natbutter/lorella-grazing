"""
Generate a small synthetic Sentinel-like GeoTIFF for demo/testing.

Bands:
1 B02 (blue)
2 B03 (green)
3 B04 (red)
4 B08 (nir)
5 B11 (swir1)
6 B12 (swir2)
7 LABEL (optional) - synthetic labels for supervised training

Georeference: simple geographic bbox around Lorella Springs approx.
"""
import numpy as np
import rasterio
from rasterio.transform import from_origin
from pathlib import Path

OUT = Path("demo") / "sample_sentinel.tif"

def make_synthetic(width=256, height=256):
    # Create gradients for vegetation patterns
    x = np.linspace(0, 1, width)
    y = np.linspace(0, 1, height)
    xx, yy = np.meshgrid(x, y)
    # Base vegetation: NDVI-like pattern
    ndvi = (np.sin(xx*3.14*2) * 0.3 + yy*0.6 + 0.2)
    ndvi = np.clip(ndvi, -0.2, 0.8)

    # Compose bands using simple relationships
    nir = (0.2 + ndvi * 0.6) * 10000
    red = (0.2 + (1 - ndvi) * 0.4) * 10000 * 0.6
    green = red * 0.9
    blue = (0.15 + xx*0.2) * 10000
    swir1 = (0.1 + ndvi*0.2) * 10000
    swir2 = (0.08 + ndvi*0.25) * 10000

    # labels: threshold NDVI
    labels = np.zeros_like(ndvi, dtype=np.uint8)
    labels[ndvi > 0.4] = 2
    labels[(ndvi > 0.15) & (ndvi <= 0.4)] = 1
    labels[xx < 0.05] = 3  # synthetic cloud strip

    bands = [
        (blue).astype(np.uint16),
        (green).astype(np.uint16),
        (red).astype(np.uint16),
        (nir).astype(np.uint16),
        (swir1).astype(np.uint16),
        (swir2).astype(np.uint16),
        labels.astype(np.uint8)
    ]
    return bands

def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    width = 256
    height = 256
    transform = from_origin(137.3, -14.2, 0.0009, 0.0009)  # arbitrary small resolution
    meta = {
        "driver": "GTiff",
        "height": height,
        "width": width,
        "count": 7,
        "dtype": "uint16",
        "crs": "EPSG:4326",
        "transform": transform
    }
    bands = make_synthetic(width, height)
    with rasterio.open(str(OUT), "w", **meta) as dst:
        for i, b in enumerate(bands, start=1):
            dst.write(b.astype('uint16') if i < 7 else b.astype('uint8'), i)
    print("Wrote demo sample to", OUT)

if __name__ == "__main__":
    main()

