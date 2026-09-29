import numpy as np
import pandas as pd
from fastapi.testclient import TestClient

from api.main import app
from src.heart.data import clean
from src.heart.config import COLUMNS

PATIENT = dict(age=63, sex=1, cp=4, trestbps=145, chol=233, fbs=1, restecg=2, thalach=150,
               exang=1, oldpeak=2.3, slope=3, ca=2, thal=7)


def test_clean_rules():
    raw = pd.DataFrame([[50, 1, 4, 0, 0, 0, 0, 120, 1, 1.0, 9, 5, 4, 2],
                        [50, 1, 4, 0, 0, 0, 0, 120, 1, 1.0, 9, 5, 4, 2]], columns=COLUMNS)
    raw["site"] = "Cleveland"
    df = clean(raw)
    assert len(df) == 1                                   # duplicate dropped
    assert df[["chol", "trestbps", "slope", "ca", "thal"]].isna().all(axis=None)
    assert df.target.iloc[0] == 1                        # num>0 -> 1


def test_api_predict_and_history():
    with TestClient(app) as c:
        assert c.get("/api/health").json()["status"] == "ok"
        r = c.post("/api/predict", json=PATIENT).json()
        assert 0 <= r["probability"] <= 1 and r["label"] in (0, 1) and len(r["explanation"]) == 13
        partial = {k: (v if k in ("age", "sex", "cp") else None) for k, v in PATIENT.items()}
        assert c.post("/api/predict", json=partial).status_code == 200
        assert c.post("/api/predict", json={**PATIENT, "age": 500}).status_code == 422
        assert c.get("/api/history").json()[0]["inputs"]["age"] in (63, 63.0)
        assert c.get("/api/metrics").json()["test"]["default_threshold"]["accuracy"] > 0.8
