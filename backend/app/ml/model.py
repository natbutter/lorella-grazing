"""
Wrapper utilities for saving/loading the scikit-learn model.
"""
from joblib import dump, load
from pathlib import Path
from typing import Any

def save_model(estimator: Any, path: str):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    dump(estimator, path)

def load_model(path: str):
    return load(path)

