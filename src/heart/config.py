import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def _load_dotenv(path: Path) -> None:
    """Minimal .env loader: KEY=VALUE lines; real environment variables take precedence."""
    if path.exists():
        for line in path.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip().strip('"').strip("'"))


_load_dotenv(ROOT / ".env")
RAW_DIR = ROOT / "data" / "raw"
PROCESSED_DIR = ROOT / "data" / "processed"
MODELS_DIR = ROOT / "models"
MODEL_PATH = MODELS_DIR / "model.joblib"
METRICS_PATH = MODELS_DIR / "metrics.json"

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg://localhost/heart_disease")
SEED = 42
OPTUNA_TRIALS = int(os.getenv("OPTUNA_TRIALS", "80"))

UCI_BASE = "https://archive.ics.uci.edu/ml/machine-learning-databases/heart-disease"
SITES = {"cleveland": "Cleveland", "hungarian": "Hungary", "switzerland": "Switzerland", "va": "VA Long Beach"}

COLUMNS = ["age", "sex", "cp", "trestbps", "chol", "fbs", "restecg",
           "thalach", "exang", "oldpeak", "slope", "ca", "thal", "num"]
NUMERIC = ["age", "trestbps", "chol", "thalach", "oldpeak", "ca"]
BINARY = ["sex", "fbs", "exang"]
CATEGORICAL = ["cp", "restecg", "slope", "thal"]  # site dropped: no CV gain, and new patients have no site
FEATURES = NUMERIC + BINARY + CATEGORICAL
