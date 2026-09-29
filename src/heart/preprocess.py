"""Leakage-safe preprocessing: every imputer/scaler is fitted inside CV folds via Pipeline."""
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

from .config import BINARY, CATEGORICAL, NUMERIC

MISSING_FLAG_COLS = ["chol", "slope", "ca", "thal", "thalach"]


def make_preprocessor(scale: bool = True) -> ColumnTransformer:
    num_steps = [("impute", SimpleImputer(strategy="median", add_indicator=True))]
    if scale:
        num_steps.append(("scale", StandardScaler()))
    return ColumnTransformer(
        [
            ("num", Pipeline(num_steps), NUMERIC),
            ("bin", SimpleImputer(strategy="most_frequent"), BINARY),
            ("cat", Pipeline([
                ("impute", SimpleImputer(strategy="constant", fill_value="missing")),
                ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
            ]), CATEGORICAL),
        ],
        verbose_feature_names_out=False,
    )


def to_model_frame(df):
    """Cast categoricals to strings so '1.0' and '1' can't diverge between training and API input."""
    import pandas as pd
    X = df.copy()
    for c in X.columns:
        if c in CATEGORICAL:
            X[c] = X[c].map(lambda v: None if pd.isna(v) else (v if isinstance(v, str) else str(int(v))))
        else:
            X[c] = pd.to_numeric(X[c], errors="coerce").astype(float)
    return X


CATEGORY_LEVELS = {
    "cp": ["1", "2", "3", "4"], "restecg": ["0", "1", "2"], "slope": ["1", "2", "3"],
    "thal": ["3", "6", "7"], "site": ["Cleveland", "Hungary", "Switzerland", "VA Long Beach"],
}


def to_native_xgb(X):
    """Keep NaNs for XGBoost's learned missing-value branches; categoricals become pandas Categorical."""
    import pandas as pd
    X = X.copy()
    for c in X.columns:
        if c in CATEGORY_LEVELS:
            X[c] = pd.Categorical(X[c], categories=CATEGORY_LEVELS[c])
        else:
            X[c] = pd.to_numeric(X[c], errors="coerce").astype(float)
    return X
