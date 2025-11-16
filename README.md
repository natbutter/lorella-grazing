# Grazing Mapper — Lorella Springs demo

**One-line quick start**
```bash
docker-compose up --build
```

## Overview

This repository contains a complete demo web application that maps grazing conditions for cattle on the Lorella Springs (NT, Australia) property using Sentinel-2-like synthetic data, a baseline RandomForest classifier, and a React + Leaflet frontend.

Key features:

* FastAPI backend serving inference endpoints, raster tiles, and historical results.
* Baseline ML pipeline (RandomForest) trained on per-pixel spectral bands + indices.
* Monthly pipeline runner to fetch latest tiles, run inference, and store timestamped outputs.
* React frontend displaying base map, Sentinel-2 imagery, and classification overlay with historical months selector.
* Demo mode with synthetic GeoTIFF data generator so it runs offline.
* Tests for indices, feature extraction, and demo pipeline.

### Quick walk-through (offline demo)

1. Build and start everything with Docker Compose:
```
docker-compose up --build
```

This builds three services:

* `backend` — FastAPI app (http://localhost:8000
)

* `frontend` — React app (http://localhost:3000
)

* `scheduler` — Cron-like container that can run the monthly pipeline (runs a demo once at start)

2. Generate demo data (alternative to letting scheduler create it):
```
make demo-data
```

3. Train the demo model on synthetic data:
```
make train-demo
```

This creates `backend/app/ml/model.joblib`.

4. Run the monthly pipeline manually (or the scheduler will run it once on startup):
```
./scheduler/run_monthly_pipeline.sh
```

This produces a timestamped folder under `storage/` with `imagery.tif`, `classification.tif`, and `summary.geojson`.

5. Open the frontend:
```
http://localhost:3000
```
Use the dropdown to select historical months, toggle layers and opacity. Click on the map to see pixel attributes (date, NDVI, class probabilities).

### File layout

See repository root for files. Notable files:

* `demo/generate_sample_data.py` — produces small Sentinel-like GeoTIFFs covering Lorella Springs.
* `backend/app/ml/train_demo.py` — trains RandomForest on demo data.
* `backend/app/infer.py` — functions for running inference and saving GeoTIFFs & summaries.
* `backend/app/api.py` — FastAPI endpoints (list dates, start inference, serve tiles).
* `frontend/src` — React + Leaflet SPA.

### Design notes and decisions

**Why RandomForest + spectral indices?**

* Works well with limited labels and small tabular features.
* Per-pixel spectral indices like NDVI/NDWI are strong correlates of vegetation health.
* Fast to train and explainable; good baseline before moving to deep segmentation models.

**Next steps to improve**

* Collect field truth (ground sampling) and richer labels.
* Use patch-based deep learning (UNet-style) for spatial context.
* Add temporal models (LSTM / TS models) for change detection.
* Use higher resolution (Planet) for fine-grained pasture condition.

### Data licensing and plug-in to real Sentinel-2
* Sentinel-2 data (Copernicus) are free under standard Copernicus terms.
* To plug in real data:
 * Provide Copernicus Open Access Hub credentials via environment variables (see `.env.example`).

backend/app/data/downloader.py contains placeholder code that uses sentinelsat — fill in credentials.

Real ingestion needs processing to L2A (SCL/cloud mask), and possibly Sentinel Hub integration for tiled access.

Running without Docker (developer)

Create a virtualenv and install backend requirements:

python -m venv venv
source venv/bin/activate
pip install -r backend/requirements.txt


Generate sample data, train, and run uvicorn:

python demo/generate_sample_data.py
python backend/app/ml/train_demo.py
uvicorn backend.app.main:app --reload --port 8000


Install frontend deps and run:

cd frontend
npm install
npm start

Environment variables

Create .env from .env.example and fill placeholders. Important variables:

COPERNICUS_USER / COPERNICUS_PASS - (optional) for real Sentinel downloads

BACKEND_HOST, BACKEND_PORT

Tests

Run tests:

make test


Tests use pytest and will run a demo pipeline in temporary folders.

Security & privacy notes

This demo stores data locally in storage/. For production, secure storage (S3, access controls) is recommended.

When using real data, ensure credentials are kept out of source control (use secrets manager).

Consider costs for storage and processing when scaling.

Make targets

make build — build docker images

make demo-data — generate sample data

make train-demo — train model on demo data

make run — start docker-compose

make test — run tests
