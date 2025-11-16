from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
STORAGE_DIR = BASE_DIR / "storage"
MODEL_PATH = os.environ.get("MODEL_PATH", str(BASE_DIR / "ml" / "model.joblib"))
COPERNICUS_USER = os.environ.get("COPERNICUS_USER", "")
COPERNICUS_PASS = os.environ.get("COPERNICUS_PASS", "")
BACKEND_HOST = os.environ.get("BACKEND_HOST", "0.0.0.0")
BACKEND_PORT = int(os.environ.get("BACKEND_PORT", "8000"))

# Ensure storage exists
STORAGE_DIR.mkdir(parents=True, exist_ok=True)

