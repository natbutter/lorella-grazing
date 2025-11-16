"""
FastAPI endpoints:
 - /health
 - /runs -> list available run dates
 - /run (POST) -> trigger inference (demo uses sample data)
 - /tiles/{z}/{x}/{y}.png -> returns PNG tile for classification for latest run or requested run via ?run=
 - /summary/{run}.geojson -> serve summary
"""
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse, FileResponse
from fastapi.middleware.cors import CORSMiddleware
from .storage import list_runs, new_run_folder
from .infer import run_inference
from .config import MODEL_PATH
from pathlib import Path
import os
import logging
from typing import Optional
from rio_tiler.utils import array_to_image
from rio_tiler.io import COGReader
import numpy as np
import io
from PIL import Image

logger = logging.getLogger("api")

app = FastAPI(title="Grazing Mapper API")
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/runs")
def runs():
    return {"runs": list_runs()}

@app.post("/run")
def run_demo():
    """
    Trigger a demo run: generates demo data, trains the demo model, runs inference.
    """
    # For safety, this uses demo data in repo
    from .ml.train_demo import train_and_save
    train_and_save()
    from .infer import run_inference
    res = run_inference("demo/sample_sentinel.tif", model_path=MODEL_PATH)
    return res

@app.get("/summary/{run_id}")
def get_summary(run_id: str):
    p = Path(os.path.join("storage", run_id, "summary.geojson"))
    if not p.exists():
        raise HTTPException(status_code=404, detail="Run not found")
    return FileResponse(str(p), media_type="application/geo+json")

@app.get("/tile/{z}/{x}/{y}.png")
def tile(z: int, x: int, y: int, run: Optional[str] = Query(None)):
    """
    Serve a PNG tile for classification raster using rio-tiler/COGReader.
    For demo, classification.tif are small and not COGs; we open and tile in-memory.
    """
    runs = list_runs()
    if run is None:
        if not runs:
            raise HTTPException(status_code=404, detail="No runs available")
        run = runs[0]  # latest
    tif = Path("storage") / run / "classification.tif"
    if not tif.exists():
        raise HTTPException(status_code=404, detail="Classification not found for run")
    # Read full classification into array and generate tile using rio-tiler helpers
    with rasterio.open(str(tif)) as src:
        # Calculate bounds & transform handled by rio-tiler typically. Here we will generate a simple tile by resampling.
        # Compute tile window in pixel coordinates
        import mercantile
        tile_bounds = mercantile.bounds(x, y, z)
        # convert bounds to src rowcol
        from rasterio.warp import transform_bounds
        # transform tile_bounds (EPSG:3857) to src crs (likely EPSG:4326) — but our demo uses geographic.
        # For simplicity, read whole and crop naively (demo)
        arr = src.read(1)
        # Scale arr to 0-255 for colors
        cmap = {
            0: (180, 50, 50),   # poor
            1: (240, 180, 60),  # moderate
            2: (60, 180, 75),   # good
            3: (200,200,200)    # cloud/no-data
        }
        # Create 256x256 tile by resampling arr to 256x256
        tile_img = Image.new("RGBA", (256, 256))
        # Resize array
        from PIL import Image as PILImage
        pil_arr = PILImage.fromarray(arr.astype('uint8'))
        pil_resized = pil_arr.resize((256,256), resample=PILImage.NEAREST)
        px = np.array(pil_resized)
        rgb = np.zeros((256,256,3), dtype=np.uint8)
        for k,v in cmap.items():
            mask = px == k
            rgb[mask] = v
        img = Image.fromarray(rgb)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        return FileResponse(buf, media_type="image/png")

