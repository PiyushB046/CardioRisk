"""Train, tune, compare and select the most accurate leakage-free model."""
import json
import warnings

import joblib
import numpy as np
import optuna
from sklearn.base import clone
from sklearn.ensemble import (ExtraTreesClassifier, RandomForestClassifier,
                              StackingClassifier, VotingClassifier)
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import (RepeatedStratifiedKFold, StratifiedKFold,
                                     cross_val_predict, cross_validate, train_test_split)
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import FunctionTransformer
from sklearn.svm import SVC
from xgboost import XGBClassifier

from . import data
from .config import FEATURES, METRICS_PATH, MODEL_PATH, MODELS_DIR, OPTUNA_TRIALS, SEED
from .db import ModelRun, SessionLocal, init_db
from .evaluate import curves, metrics
from .preprocess import make_preprocessor, to_model_frame, to_native_xgb

warnings.filterwarnings("ignore")
optuna.logging.set_verbosity(optuna.logging.WARNING)
CV = RepeatedStratifiedKFold(n_splits=5, n_repeats=5, random_state=SEED)


def pipe(model, scale=True):
    return Pipeline([("prep", make_preprocessor(scale)), ("model", model)])


def cv_score(estimator, X, y):
    s = cross_validate(estimator, X, y, cv=CV, scoring=["accuracy", "roc_auc", "f1", "recall"], n_jobs=-1)
    return {k.replace("test_", ""): (float(v.mean()), float(v.std())) for k, v in s.items() if k.startswith("test_")}


def tune(name, build, space, X, y):
    def objective(trial):
        return cross_validate(build(space(trial)), X, y, cv=CV, scoring="accuracy", n_jobs=-1)["test_score"].mean()
    study = optuna.create_study(direction="maximize", sampler=optuna.samplers.TPESampler(seed=SEED))
    study.optimize(objective, n_trials=OPTUNA_TRIALS)
    print(f"  {name:<8} best CV acc {study.best_value:.4f}")
    return study.best_params


def xgb_space(t):
    return dict(n_estimators=t.suggest_int("n_estimators", 100, 800), max_depth=t.suggest_int("max_depth", 2, 6),
                learning_rate=t.suggest_float("learning_rate", 0.005, 0.2, log=True),
                subsample=t.suggest_float("subsample", 0.5, 1.0), colsample_bytree=t.suggest_float("colsample_bytree", 0.3, 1.0),
                min_child_weight=t.suggest_float("min_child_weight", 1, 10), gamma=t.suggest_float("gamma", 0, 5),
                reg_lambda=t.suggest_float("reg_lambda", 1e-3, 10, log=True), reg_alpha=t.suggest_float("reg_alpha", 1e-3, 5, log=True))


def xgb(p):
    # Native NaN + categorical handling: XGBoost learns the best branch for missing values itself.
    return Pipeline([("prep", FunctionTransformer(to_native_xgb)),
                     ("model", XGBClassifier(**p, enable_categorical=True, tree_method="hist",
                                             eval_metric="logloss", random_state=SEED, n_jobs=1))])


def rf_space(t):
    return dict(n_estimators=t.suggest_int("n_estimators", 200, 800), max_depth=t.suggest_int("max_depth", 3, 16),
                min_samples_leaf=t.suggest_int("min_samples_leaf", 1, 10), max_features=t.suggest_float("max_features", 0.1, 0.8))


def rf(p):
    return pipe(RandomForestClassifier(**p, random_state=SEED, n_jobs=1), scale=False)


def lr_space(t):
    return dict(C=t.suggest_float("C", 1e-3, 10, log=True), l1_ratio=t.suggest_float("l1_ratio", 0, 1))


def lr(p):
    return pipe(LogisticRegression(**p, penalty="elasticnet", solver="saga", max_iter=5000))


def svm_space(t):
    return dict(C=t.suggest_float("C", 1e-2, 50, log=True), gamma=t.suggest_float("gamma", 1e-4, 1, log=True))


def svm(p):
    return pipe(SVC(**p, probability=True, random_state=SEED))


def main():
    init_db()
    print(f"Optuna trials per model: {OPTUNA_TRIALS}")
    df = data.run()
    X, y = to_model_frame(df[FEATURES]), df["target"].to_numpy()
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, stratify=y, random_state=SEED)
    print(f"train {len(X_tr)} / test {len(X_te)} (test set locked until final evaluation)")

    print("Tuning with Optuna, repeated stratified 5x5 CV ...")
    tuned = {
        "logreg": lr(tune("logreg", lr, lr_space, X_tr, y_tr)),
        "rf": rf(tune("rf", rf, rf_space, X_tr, y_tr)),
        "svm": svm(tune("svm", svm, svm_space, X_tr, y_tr)),
        "xgboost": xgb(tune("xgboost", xgb, xgb_space, X_tr, y_tr)),
    }
    tuned["extratrees"] = pipe(ExtraTreesClassifier(n_estimators=500, min_samples_leaf=3, max_features=0.5,
                                                   random_state=SEED, n_jobs=1), scale=False)
    base = [(n, m) for n, m in tuned.items()]
    tuned["voting"] = VotingClassifier(base, voting="soft", n_jobs=1)
    tuned["stacking"] = StackingClassifier(base, final_estimator=LogisticRegression(C=1.0, max_iter=2000),
                                           cv=StratifiedKFold(5, shuffle=True, random_state=SEED), n_jobs=1)

    print("Comparing all candidates on identical CV folds ...")
    comparison = {}
    for name, model in tuned.items():
        comparison[name] = cv_score(model, X_tr, y_tr)
        a = comparison[name]["accuracy"]
        print(f"  {name:<11} acc {a[0]:.4f} ± {a[1]:.4f}   auc {comparison[name]['roc_auc'][0]:.4f}")

    best = max(comparison, key=lambda n: (round(comparison[n]["accuracy"][0], 3), comparison[n]["roc_auc"][0]))
    print(f"Selected: {best}")

    # Tune the decision threshold on out-of-fold training predictions only (never the test set).
    oof = cross_val_predict(clone(tuned[best]), X_tr, y_tr, cv=StratifiedKFold(5, shuffle=True, random_state=SEED),
                            method="predict_proba")[:, 1]
    grid = np.round(np.arange(0.30, 0.71, 0.01), 2)
    thr = float(grid[np.argmax([((oof >= t) == y_tr).mean() for t in grid])])

    final = clone(tuned[best]).fit(X_tr, y_tr)
    explainer = clone(tuned["xgboost"]).fit(X_tr, y_tr)
    p_te = final.predict_proba(X_te)[:, 1]
    test = {"default_threshold": metrics(y_te, p_te, 0.5), "tuned_threshold": metrics(y_te, p_te, thr)}
    print(f"HELD-OUT TEST  acc@0.5 {test['default_threshold']['accuracy']:.4f}  acc@{thr} {test['tuned_threshold']['accuracy']:.4f}"
          f"  auc {test['default_threshold']['roc_auc']:.4f}")

    # Production model: refit on all 918 rows with the chosen configuration.
    production = clone(tuned[best]).fit(X, y)
    production_explainer = clone(tuned["xgboost"]).fit(X, y)
    MODELS_DIR.mkdir(exist_ok=True)
    joblib.dump({"model": production, "explainer": production_explainer, "name": best, "threshold": 0.5,
                 "features": FEATURES}, MODEL_PATH)

    booster = explainer.named_steps["model"]
    names = booster.get_booster().feature_names
    importance = sorted(zip(names, booster.feature_importances_.round(4).tolist()), key=lambda x: -x[1])[:15]
    report = {
        "selected_model": best, "n_train": len(X_tr), "n_test": len(X_te), "cv_scheme": "RepeatedStratifiedKFold(5x5)",
        "cv_comparison": comparison, "cv_oof_best_threshold": thr, "test": test, "curves": curves(y_te, p_te),
        "feature_importance": importance,
        "params": {n: {k: v for k, v in m.named_steps["model"].get_params().items() if isinstance(v, (int, float, str)) and v == v}
                   for n, m in tuned.items() if isinstance(m, Pipeline)},
    }
    METRICS_PATH.write_text(json.dumps(report, indent=2, default=float))
    with SessionLocal() as s:
        s.add(ModelRun(model_name=best, params=report["params"].get(best, {}),
                       metrics={"cv": comparison[best], "test": test["default_threshold"]}))
        s.commit()
    print(f"Saved {MODEL_PATH.name} and {METRICS_PATH.name}")
    from . import eda
    eda.run()
    print("EDA plots written to web/eda/")


if __name__ == "__main__":
    main()
