"""Ingestion + cleaning. Raw and clean tables are written to Postgres via SQLAlchemy."""
import urllib.request

import numpy as np
import pandas as pd

from .config import COLUMNS, PROCESSED_DIR, RAW_DIR, SITES, UCI_BASE
from .db import engine


def download() -> None:
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    for key in SITES:
        path = RAW_DIR / f"processed.{key}.data"
        if not path.exists():
            urllib.request.urlretrieve(f"{UCI_BASE}/processed.{key}.data", path)


def load_raw() -> pd.DataFrame:
    frames = []
    for key, site in SITES.items():
        df = pd.read_csv(RAW_DIR / f"processed.{key}.data", header=None, names=COLUMNS, na_values="?")
        df["site"] = site
        frames.append(df)
    return pd.concat(frames, ignore_index=True)


def clean(raw: pd.DataFrame) -> pd.DataFrame:
    df = raw.copy()
    df = df.apply(lambda s: pd.to_numeric(s, errors="coerce") if s.name != "site" else s)
    # Physiologically impossible zeros are missing values in disguise.
    df.loc[df["chol"] == 0, "chol"] = np.nan
    df.loc[df["trestbps"] == 0, "trestbps"] = np.nan
    # Out-of-range codes -> NaN.
    df.loc[~df["ca"].isin([0, 1, 2, 3]), "ca"] = np.nan
    df.loc[~df["thal"].isin([3, 6, 7]), "thal"] = np.nan
    df.loc[~df["slope"].isin([1, 2, 3]), "slope"] = np.nan
    df = df.drop_duplicates().reset_index(drop=True)
    df["target"] = (df["num"] > 0).astype(int)
    return df


def run() -> pd.DataFrame:
    download()
    raw = load_raw()
    raw.to_sql("heart_raw", engine, if_exists="replace", index=False)
    df = clean(raw)
    df.to_sql("heart_clean", engine, if_exists="replace", index=False)
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    raw.to_csv(RAW_DIR / "heart_disease_uci.csv", index=False)
    df.to_csv(PROCESSED_DIR / "heart_clean.csv", index=False)
    return df


def load_clean() -> pd.DataFrame:
    df = pd.read_sql_table("heart_clean", engine)
    df.columns = [str(c) for c in df.columns]  # SQLAlchemy returns quoted_name objects, which sklearn rejects
    return df


if __name__ == "__main__":
    df = run()
    print(f"clean rows: {len(df)}  positives: {df.target.mean():.3f}")
    print("missing % by site:\n", df.drop(columns=["num", "target"]).isna().groupby(df.site).mean().round(2).T)
