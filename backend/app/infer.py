"""
Inference utilities and a CLI to run the demo pipeline.
Also provides a small function that the API uses to perform inference on input geometry.

Outputs:
 - imagery.tif  (source/synthetic)
 - classification.tif (INT8)
 - summary.geojson (areas per class)
"""
import argparse
from pathlib import Path
from datetime import datetime
import numpy as np
import rasterio
from rasterio.transform import from_origin
from rasterio import Affine
import json
from .ml.features import ndvi, ndwi, bsi, simple_cloud_mask
from .ml.model import load_model
from .storage import new_run_folder, save_summary_geojson
from .config import MODEL_PATH
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("infer")

def read_imagery(path: str):
    with rasterio.open(path) as src:
        arrs = [src.read(i) for i in range(1, min(6, src.count)+1)]
        meta = src.meta.copy()
    arr = np.stack(arrs, axis=0)  # B, H, W
    return arr, meta

def extract_features_from_array(arr: np.ndarray):
    """
    arr: B, H, W in order B02,B03,B04,B08,B11,B12
    returns feature array: H*W x features
    """
    blue = arr[0].astype(float)
    green = arr[1].astype(float)
    red = arr[2].astype(float)
    nir = arr[3].astype(float)
    swir1 = arr[4].astype(float)
    swir2 = arr[5].astype(float)
    ndvi_img = ndvi(nir, red)
    ndwi_img = ndwi(green, nir)
    bsi_img = bsi(blue, red, nir, swir1)
    H, W = blue.shape
    X = np.column_stack([
        blue.reshape(-1),
        green.reshape(-1),
        red.reshape(-1),
        nir.reshape(-1),
        swir1.reshape(-1),
        swir2.reshape(-1),
        ndvi_img.reshape(-1),
        ndwi_img.reshape(-1),
        bsi_img.reshape(-1),
    ])
    return X, (H, W)

def run_inference(imagery_tif: str, model_path: str = MODEL_PATH, out_folder: str = None):
    # Read imagery
    arr, meta = read_imagery(imagery_tif)
    X, (H, W) = extract_features_from_array(arr)
    # Load model
    model = load_model(model_path)
    proba = model.predict_proba(X)
    preds = model.predict(X)
    # reshape back
    class_raster = preds.reshape(H, W).astype('uint8')
    # Save classification GeoTIFF aligned with source
    if out_folder is None:
        out_folder = new_run_folder()
    else:
        out_folder = Path(out_folder)
        out_folder.mkdir(parents=True, exist_ok=True)

    class_meta = meta.copy()
    class_meta.update({
        "count": 1,
        "dtype": "uint8"
    })
    class_path = out_folder / "classification.tif"
    with rasterio.open(class_path, "w", **class_meta) as dst:
        dst.write(class_raster, 1)

    # Also copy the source imagery to output folder for display
    imagery_out = out_folder / "imagery.tif"
    # For simplicity, copy file
    import shutil
    shutil.copy(imagery_tif, imagery_out)

    # Summarize area per class (pixel counts -> approximate areas)
    unique, counts = np.unique(class_raster, return_counts=True)
    summary = {"date": datetime.utcnow().isoformat(), "classes": []}
    pixel_area = abs(meta['transform'][0] * meta['transform'][4])  # approx
    for c, cnt in zip(unique.tolist(), counts.tolist()):
        summary["classes"].append({
            "class": int(c),
            "pixels": int(cnt),
            "approx_area_m2": float(cnt * pixel_area)
        })
    summary_path = save_summary_geojson(out_folder, summary)
    logger.info("Wrote outputs to %s", out_folder)
    return {
        "folder": str(out_folder),
        "classification_tif": str(class_path),
        "imagery_tif": str(imagery_out),
        "summary": summary
    }

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--imagery", default="demo/sample_sentinel.tif", help="Input imagery (demo)")
    parser.add_argument("--model", default=MODEL_PATH, help="Model path")
    parser.add_argument("--out", default=None, help="Output folder (optional)")
    parser.add_argument("--demo-run", action="store_true", help="Run demo pipeline: generate data, train model, infer")
    args = parser.parse_args()
    if args.demo_run:
        # Generate sample data and train if necessary
        import demo.generate_sample_data as gen
        gen.main()  # create demo/sample_sentinel.tif
        from .ml.train_demo import train_and_save
        train_and_save()
        from .config import STORAGE_DIR
        res = run_inference("demo/sample_sentinel.tif", out_folder=None)
        print(res)
    else:
        res = run_inference(args.imagery, model_path=args.model, out_folder=args.out)
        print(res)

