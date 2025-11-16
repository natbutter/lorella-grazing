"""
Train a demo RandomForest classifier on synthetic GeoTIFF data.

- Loads synthetic sample data produced by demo/generate_sample_data.py
- Extracts pixel-wise features: B02,B03,B04,B08,B11,B12 + NDVI, NDWI, BSI, cloud mask
- Trains RandomForest classifier with simple cross-validation and saves model.joblib
"""
import numpy as np
import rasterio
from rasterio.windows import Window
import os
from pathlib import Path
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_predict
from sklearn.metrics import classification_report, confusion_matrix
from joblib import dump
from .features import ndvi, ndwi, bsi, simple_cloud_mask
from .model import save_model
from ..data import sample_property
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("train_demo")

DEMO_TIF = Path(__file__).resolve().parents[2] / "demo" / "sample_sentinel.tif"
MODEL_OUT = Path(__file__).resolve().parents[1] / "ml" / "model.joblib"

def load_sample_features(tif_path: str):
    """
    Read small sample GeoTIFF and build feature matrix X and labels y.
    For the demo, the sample GeoTIFF stores a synthetic label in band 7 if present.
    Bands mapping:
      1: B02 (blue)
      2: B03 (green)
      3: B04 (red)
      4: B08 (nir)
      5: B11 (swir1)
      6: B12 (swir2)
      7: LABEL (optional) -- contains integer class code
    """
    with rasterio.open(tif_path) as src:
        bands = [src.read(i) for i in range(1, src.count+1)]
        arrs = np.stack(bands[:6], axis=-1)  # H x W x 6
        labels = None
        if src.count >= 7:
            labels = src.read(7)
    # compute indices
    blue = arrs[..., 0].astype(float)
    green = arrs[..., 1].astype(float)
    red = arrs[..., 2].astype(float)
    nir = arrs[..., 3].astype(float)
    swir1 = arrs[..., 4].astype(float)
    swir2 = arrs[..., 5].astype(float)
    ndvi_img = ndvi(nir, red)
    ndwi_img = ndwi(green, nir)
    bsi_img = bsi(blue, red, nir, swir1)

    # Flatten
    H, W, _ = arrs.shape
    X = np.column_stack([
        arrs.reshape(-1, 6),
        ndvi_img.reshape(-1),
        ndwi_img.reshape(-1),
        bsi_img.reshape(-1)
    ])
    y = None
    if labels is not None:
        y = labels.reshape(-1)
    return X, y

def train_and_save():
    X, y = load_sample_features(str(DEMO_TIF))
    # For demo: if no labels, create synthetic labels based on NDVI thresholds
    if y is None:
        ndvi_col = X[:, 6]
        # classes: 0: Poor, 1: Moderate, 2: Good, 3: Cloud/NoData
        y = np.zeros_like(ndvi_col, dtype=int)
        y[ndvi_col > 0.4] = 2
        y[(ndvi_col > 0.15) & (ndvi_col <= 0.4)] = 1
        # synthetic clouds where blue is bright
        blue = X[:, 0]
        cloud_mask = blue > 2500
        y[cloud_mask] = 3

    # Filter out no-data pixels if any (here assume none)
    # Train RandomForest with cross-validation
    clf = RandomForestClassifier(n_estimators=50, n_jobs=2, random_state=42)
    skf = StratifiedKFold(n_splits=3, shuffle=True, random_state=42)
    logger.info("Running cross-validated predictions for evaluation...")
    y_pred = cross_val_predict(clf, X, y, cv=skf, n_jobs=2)
    logger.info("Classification report:\n%s", classification_report(y, y_pred))
    logger.info("Confusion matrix:\n%s", confusion_matrix(y, y_pred))

    # Fit on all data and save
    clf.fit(X, y)
    save_model(clf, str(MODEL_OUT))
    logger.info("Saved model to %s", MODEL_OUT)

if __name__ == "__main__":
    train_and_save()

