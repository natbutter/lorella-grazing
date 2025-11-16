import os
import shutil
from demo.generate_sample_data import main as gen_main
from backend.app.ml.train_demo import train_and_save
from backend.app.infer import run_inference
from backend.app.storage import list_runs

def test_demo_end_to_end(tmp_path):
    # generate sample data
    gen_main()
    # train
    train_and_save()
    # run inference to a temp folder
    out = run_inference("demo/sample_sentinel.tif", out_folder=str(tmp_path/"out"))
    assert os.path.exists(out["classification_tif"])
    assert os.path.exists(out["imagery_tif"])
    assert "summary" in out

