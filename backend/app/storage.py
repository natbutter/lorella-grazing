"""
Simple storage helpers for saving outputs under timestamped folders.
"""
from pathlib import Path
from datetime import datetime
from typing import Tuple
import json
from .config import STORAGE_DIR

def new_run_folder(ts: datetime = None) -> Path:
    if ts is None:
        ts = datetime.utcnow()
    folder = STORAGE_DIR / ts.strftime("%Y-%m-%dT%H-%M-%SZ")
    folder.mkdir(parents=True, exist_ok=True)
    return folder

def save_summary_geojson(folder: Path, summary: dict):
    target = folder / "summary.geojson"
    with open(target, "w") as f:
        json.dump(summary, f)
    return target

def list_runs():
    runs = []
    for p in sorted(STORAGE_DIR.iterdir(), reverse=True):
        if p.is_dir():
            runs.append(p.name)
    return runs

