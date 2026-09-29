from functools import lru_cache

import joblib
import numpy as np
import pandas as pd
import xgboost as xgb

from .config import MODEL_PATH
from .preprocess import to_model_frame


@lru_cache
def load():
    return joblib.load(MODEL_PATH)


def predict(record: dict) -> dict:
    bundle = load()
    X = to_model_frame(pd.DataFrame([record])[bundle["features"]])
    proba = float(bundle["model"].predict_proba(X)[0, 1])

    # Per-feature SHAP contributions (log-odds) from the XGBoost explainer model.
    exp = bundle["explainer"]
    Xn = exp.named_steps["prep"].transform(X)
    booster = exp.named_steps["model"].get_booster()
    contribs = booster.predict(xgb.DMatrix(Xn, enable_categorical=True), pred_contribs=True)[0]
    names = booster.feature_names
    explanation = sorted(({"feature": n, "value": None if pd.isna(record.get(n)) else record.get(n),
                           "contribution": round(float(c), 4)} for n, c in zip(names, contribs[:-1])),
                         key=lambda d: -abs(d["contribution"]))
    return {"probability": round(proba, 4), "label": int(proba >= bundle["threshold"]),
            "threshold": bundle["threshold"], "model": bundle["name"], "explanation": explanation,
            "base_value": round(float(contribs[-1]), 4)}
