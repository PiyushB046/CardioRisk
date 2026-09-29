import numpy as np
import pandas as pd
import pytest
from sklearn.model_selection import StratifiedKFold, cross_val_score, train_test_split

from src.heart import data, train as T
from src.heart.config import FEATURES, SEED, _load_dotenv
from src.heart.evaluate import metrics
from src.heart.preprocess import make_preprocessor, to_model_frame, to_native_xgb


@pytest.fixture(scope="module")
def xy():
    df = data.clean(data.load_raw())
    return to_model_frame(df[FEATURES]), df["target"].to_numpy()


def test_dataset_shape(xy):
    X, y = xy
    assert X.shape == (918, len(FEATURES)) and 0.5 < y.mean() < 0.6


def test_imputer_fitted_on_train_only(xy):
    X, y = xy
    X_tr, X_te, *_ = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    prep = make_preprocessor().fit(X_tr)
    median_chol = prep.named_transformers_["num"].named_steps["impute"].statistics_[2]
    assert median_chol == pytest.approx(X_tr["chol"].median())      # not the full-data median
    assert prep.transform(X_te).shape[0] == len(X_te) and not np.isnan(prep.transform(X_te)).any()


def test_native_xgb_keeps_nan_and_fixed_levels(xy):
    X, _ = xy
    Xn = to_native_xgb(X.head(50))
    assert Xn["ca"].isna().any() or X.head(50)["ca"].notna().all()
    assert list(Xn["cp"].cat.categories) == ["1", "2", "3", "4"]


@pytest.mark.parametrize("builder,params", [
    (T.svm, {"C": 3.5, "gamma": 0.04}),
    (T.lr, {"C": 0.2, "l1_ratio": 0.5}),
    (T.xgb, {"n_estimators": 200, "max_depth": 3, "learning_rate": 0.05}),
])
def test_models_learn(xy, builder, params):
    X, y = xy
    acc = cross_val_score(builder(params), X, y, cv=StratifiedKFold(5, shuffle=True, random_state=SEED)).mean()
    assert acc > 0.78


def test_metrics_perfect_and_inverted():
    y = np.array([0, 0, 1, 1])
    assert metrics(y, np.array([.1, .2, .8, .9]))["accuracy"] == 1.0
    m = metrics(y, np.array([.9, .8, .2, .1]))
    assert m["accuracy"] == 0.0 and m["confusion_matrix"] == {"tn": 0, "fp": 2, "fn": 2, "tp": 0}


def test_dotenv_does_not_override_env(tmp_path, monkeypatch):
    (tmp_path / ".env").write_text("# c\nFOO_X=from_file\nBAR_X='quoted'\n")
    monkeypatch.setenv("FOO_X", "from_env"); monkeypatch.delenv("BAR_X", raising=False)
    _load_dotenv(tmp_path / ".env")
    import os
    assert os.environ["FOO_X"] == "from_env" and os.environ["BAR_X"] == "quoted"
    monkeypatch.delenv("BAR_X")
