import numpy as np
from backend.app.infer import extract_features_from_array

def test_extract_features_shape():
    # create dummy B,H,W with 6 bands
    B,H,W = 6, 10, 12
    arr = np.zeros((B,H,W), dtype=float)
    arr[3] = np.ones((H,W))*0.5  # nir
    X, (h,w) = extract_features_from_array(arr)
    assert X.shape[0] == H*W
    assert X.shape[1] == 9

