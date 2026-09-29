import numpy as np
from sklearn.metrics import (accuracy_score, average_precision_score, balanced_accuracy_score,
                             brier_score_loss, confusion_matrix, f1_score, matthews_corrcoef,
                             precision_score, recall_score, roc_auc_score, roc_curve,
                             precision_recall_curve)
from sklearn.calibration import calibration_curve


def metrics(y, proba, threshold=0.5) -> dict:
    pred = (proba >= threshold).astype(int)
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {
        "accuracy": accuracy_score(y, pred),
        "balanced_accuracy": balanced_accuracy_score(y, pred),
        "precision": precision_score(y, pred, zero_division=0),
        "recall_sensitivity": recall_score(y, pred),
        "specificity": tn / (tn + fp),
        "f1": f1_score(y, pred),
        "roc_auc": roc_auc_score(y, proba),
        "pr_auc": average_precision_score(y, proba),
        "mcc": matthews_corrcoef(y, pred),
        "brier": brier_score_loss(y, proba),
        "confusion_matrix": {"tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)},
        "threshold": threshold,
    }


def curves(y, proba) -> dict:
    fpr, tpr, _ = roc_curve(y, proba)
    prec, rec, _ = precision_recall_curve(y, proba)
    frac, mean_pred = calibration_curve(y, proba, n_bins=8, strategy="quantile")
    r = lambda a: np.round(a, 4).tolist()
    return {"roc": {"fpr": r(fpr), "tpr": r(tpr)}, "pr": {"precision": r(prec), "recall": r(rec)},
            "calibration": {"predicted": r(mean_pred), "observed": r(frac)}}
