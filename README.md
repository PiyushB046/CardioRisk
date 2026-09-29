# CardioRisk: Heart Disease Prediction

Uses the UCI Heart Disease data (all 4 sites, 918 rows after cleaning) with pandas, scikit-learn,
XGBoost and Optuna, stored in PostgreSQL through SQLAlchemy, and served by a FastAPI backend with a
custom web UI (no Streamlit). See `knowledge.md` for background and experiments, and
`IMPLEMENTATION_PLAN.md` for the phases.

## Quick start (local)
```bash
python3 -m venv .venv && .venv/bin/pip install -r requirements.txt
cp .env.example .env              # edit DATABASE_URL if needed
createdb heart_disease
.venv/bin/python -m src.heart.train          # download, clean, load to Postgres, tune, evaluate, EDA (~8 min)
.venv/bin/uvicorn api.main:app --port 8000   # http://localhost:8000   API docs: /docs
.venv/bin/python -m pytest -q tests
```

## Quick start (Docker)
```bash
docker compose up --build        # Postgres 16 + app on http://localhost:8000 (APP_PORT=8001 to change)
```
The image ships with the trained model. On startup it loads the data into the compose Postgres,
and it trains from scratch only if `models/model.joblib` is missing.

## UI
| Tab | Contents |
|---|---|
| Predict | Patient form, risk gauge, per-patient SHAP explanation |
| Model performance | 10 test-set metrics, confusion matrix, ROC, PR, calibration, feature importance, CV model comparison |
| Data | Class balance, missingness by site, distributions, disease rate by category, correlations |
| History | Every prediction, stored in Postgres |

## API
| Method | Path | Purpose |
|---|---|---|
| POST | `/api/predict` | Probability, label and SHAP contributions; logged to `predictions` |
| GET | `/api/metrics` | Full evaluation report |
| GET | `/api/history?limit=25` | Recent predictions |
| GET | `/api/health` | App and database health |

## Results (held-out 20% test set, never used for tuning)
| Metric | Value |
|---|---|
| Accuracy | 85.9% |
| ROC-AUC | 0.929 |
| Recall / Specificity | 91.2% / 79.3% |
| Precision / F1 | 84.5% / 0.877 |
| MCC / Brier | 0.714 / 0.105 |
| CV accuracy (5×5 repeated) | 83.6% ± 3.2% |

The selected model is an RBF SVM. Fifteen further experiments (imputers, engineered features,
feature pruning, CatBoost, LightGBM, ensembles) all landed at 82–84% CV, so this is the data's
ceiling (see `knowledge.md` §8).

## Layout
```
src/heart/   config · db (SQLAlchemy models) · data (ingest/clean) · preprocess · train · evaluate · predict · eda
api/main.py  FastAPI app, serves web/
web/         index.html · styles.css · app.js · eda/ (generated plots)
models/      model.joblib · metrics.json
tests/       cleaning, leakage, models, metrics, API
```

> Educational decision-support demo, not a medical device.
