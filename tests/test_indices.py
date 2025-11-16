import numpy as np
from backend.app.ml.features import ndvi, ndwi, bsi

def test_ndvi_simple():
    nir = np.array([[0.6, 0.2]])
    red = np.array([[0.2, 0.2]])
    out = ndvi(nir, red)
    assert out.shape == (1,2)
    assert out[0,0] > out[0,1]

def test_ndwi_simple():
    g = np.array([[0.4]])
    nir = np.array([[0.2]])
    out = ndwi(g, nir)
    assert out[0,0] > 0

def test_bsi_bounds():
    b = np.array([[0.2]])
    r = np.array([[0.2]])
    n = np.array([[0.2]])
    s = np.array([[0.2]])
    out = bsi(b,r,n,s)
    assert out.shape == (1,1)

