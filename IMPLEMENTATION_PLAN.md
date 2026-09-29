# Implementation Plan

## Phase 0: Environment
- [x] Python venv, `requirements.txt`
- [x] Create the PostgreSQL database `heart_disease`
- [x] Project layout:
  ```
  src/heart/  config.py  db.py  data.py  preprocess.py  train.py  evaluate.py  predict.py
  api/        main.py
  web/        index.html  styles.css  app.js
  data/       raw/  processed/
  models/     (saved pipeline + metrics.json + plots)
  tests/
  ```

## Phase 1: Data ingestion
- [x] Download the 4 UCI processed files (the same data as the Kaggle mirror)
- [x] Merge them, add the `source_site` column, save `data/raw/heart_disease_uci.csv`
- [x] Load into Postgres `heart_raw` with SQLAlchemy

## Phase 2: Cleaning and EDA
- [x] `?` becomes NaN; impossible zeros (`chol`, `trestbps`) become NaN
- [x] Drop duplicates, fix dtypes, binarize the target
- [x] Missingness report by site; class balance; feature distributions
- [x] Write `heart_clean` to Postgres

## Phase 3: Preprocessing pipeline (leakage-safe)
- [x] ColumnTransformer: numeric (iterative/median impute + scale),
      categorical (most-frequent impute + one-hot), missing indicators
- [x] Stratified 80/20 split with a fixed seed; the test set is locked away

## Phase 4: Modelling
- [x] Baselines: Logistic Regression and Random Forest (CV)
- [x] XGBoost + Optuna tuning (repeated stratified 5×5 CV, objective = accuracy)
- [x] Extra candidates: SVM, gradient boosting, soft-voting/stacking ensemble
- [x] Choose the best by CV, refit on all training data, evaluate once on the test set

## Phase 5: Evaluation
- [x] All metrics listed in knowledge.md §4, on both CV and the test set
- [x] Confusion matrix, ROC, PR, and calibration plots; feature importance
- [x] Save `models/metrics.json` and log the run to `model_runs`

## Phase 6: API (FastAPI)
- [x] `POST /api/predict`: probability, label, and per-feature contributions; logs to `predictions`
- [x] `GET /api/metrics`, `GET /api/history`, `GET /api/health`

## Phase 7: UI
- [x] Responsive single-page app: patient form, risk gauge, "why" contribution chart
- [x] Model performance dashboard (metrics, confusion matrix, model comparison)
- [x] Prediction history table

## Phase 8: Quality
- [x] pytest: cleaning rules, pipeline shape, API smoke test
- [x] README with setup and run commands

## Phase 9: Accuracy push
- [x] 15 CV experiments: imputers, engineered features, feature pruning, CatBoost, LightGBM, ensembles
- [x] Result: 82–84% ceiling; the tuned SVM stays (logged in knowledge.md §8)

## Phase 10: Finishing
- [x] EDA report (`src/heart/eda.py`), shown in the UI "Data" tab
- [x] PR curve + feature importance on the performance dashboard
- [x] `.env` configuration (`.env.example`), `OPTUNA_TRIALS` setting
- [x] Dockerfile + docker-compose (Postgres 16 + app)
- [x] Pipeline tests: leakage check, model sanity, metrics, config (10 tests total)
