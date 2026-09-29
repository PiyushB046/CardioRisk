"""Exploratory data analysis: writes plots to web/eda/ (shown in the UI 'Data' tab) and a summary JSON."""
import json

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from . import data
from .config import ROOT

OUT = ROOT / "web" / "eda"
RED, GREEN, GREY = "#B91C1C", "#0F766E", "#6B5F64"


def _save(fig, name):
    fig.tight_layout()
    fig.savefig(OUT / name, dpi=110, transparent=True)
    plt.close(fig)


def run():
    OUT.mkdir(parents=True, exist_ok=True)
    df = data.load_clean()
    plt.rcParams.update({"font.size": 9, "axes.spines.top": False, "axes.spines.right": False, "axes.edgecolor": GREY, "axes.labelcolor": GREY,
                         "xtick.color": GREY, "ytick.color": GREY, "text.color": GREY})

    # 1. Class balance by site
    fig, ax = plt.subplots(figsize=(6, 3.2))
    ct = df.groupby("site")["target"].agg(["sum", "count"])
    ax.bar(ct.index, ct["count"] - ct["sum"], color=GREEN, label="No disease")
    ax.bar(ct.index, ct["sum"], bottom=ct["count"] - ct["sum"], color=RED, label="Disease")
    ax.set_ylabel("Patients"); ax.legend(frameon=False); ax.set_title("Class balance by site")
    _save(fig, "class_balance.png")

    # 2. Missingness heatmap by site
    cols = ["trestbps", "chol", "fbs", "thalach", "exang", "oldpeak", "slope", "ca", "thal"]
    miss = df[cols].isna().groupby(df["site"]).mean()
    fig, ax = plt.subplots(figsize=(6, 2.6))
    im = ax.imshow(miss.values, cmap="RdPu", vmin=0, vmax=1, aspect="auto")
    ax.set_xticks(range(len(cols)), cols, rotation=30); ax.set_yticks(range(len(miss)), miss.index)
    for i in range(miss.shape[0]):
        for j in range(miss.shape[1]):
            ax.text(j, i, f"{miss.values[i, j]:.0%}", ha="center", va="center", fontsize=7,
                    color="white" if miss.values[i, j] > .5 else "black")
    ax.set_title("Missing values by site"); fig.colorbar(im, ax=ax, fraction=.03)
    _save(fig, "missingness.png")

    # 3. Numeric distributions by target
    num = ["age", "trestbps", "chol", "thalach", "oldpeak"]
    fig, axes = plt.subplots(1, 5, figsize=(12, 2.6))
    for ax, c in zip(axes, num):
        for t, col in [(0, GREEN), (1, RED)]:
            ax.hist(df.loc[df.target == t, c].dropna(), bins=20, alpha=.6, color=col)
        ax.set_title(c)
    fig.suptitle("Distributions: green = no disease, red = disease")
    _save(fig, "distributions.png")

    # 4. Disease rate by categorical level
    cats = {"cp": "Chest pain", "exang": "Exercise angina", "slope": "ST slope", "ca": "Vessels", "thal": "Thal"}
    fig, axes = plt.subplots(1, 5, figsize=(12, 2.6))
    for ax, (c, t) in zip(axes, cats.items()):
        r = df.groupby(c)["target"].mean()
        ax.bar([str(int(i)) for i in r.index], r.values, color=RED); ax.set_ylim(0, 1); ax.set_title(t)
    fig.suptitle("Disease rate by category")
    _save(fig, "categorical_rates.png")

    # 5. Correlation matrix
    cm_cols = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg", "thalach", "exang", "oldpeak", "slope", "ca", "thal", "target"]
    corr = df[cm_cols].corr()
    fig, ax = plt.subplots(figsize=(6.4, 5.4))
    im = ax.imshow(corr, cmap="RdBu_r", vmin=-1, vmax=1)
    ax.set_xticks(range(len(cm_cols)), cm_cols, rotation=60); ax.set_yticks(range(len(cm_cols)), cm_cols)
    fig.colorbar(im, ax=ax, fraction=.04); ax.set_title("Correlation (pairwise complete)")
    _save(fig, "correlation.png")

    summary = {
        "rows": int(len(df)), "positive_rate": round(float(df.target.mean()), 4),
        "by_site": {s: {"rows": int(n), "positive_rate": round(float(p), 4)}
                    for s, (n, p) in df.groupby("site")["target"].agg(["count", "mean"]).iterrows()},
        "top_correlations_with_target": {k: round(float(v), 3) for k, v in
                                         corr["target"].drop("target").abs().sort_values(ascending=False).head(6).items()},
        "plots": ["class_balance.png", "missingness.png", "distributions.png", "categorical_rates.png", "correlation.png"],
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
