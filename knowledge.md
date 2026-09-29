# Knowledge Base — Heart Disease Prediction

## 1. Dataset

**Source:** UCI Machine Learning Repository, *Heart Disease* (Janosi, Steinbrunn, Pfisterer, Detrano, 1988).
The Kaggle mirror (`redwankarimsony/heart-disease-data`, file `heart_disease_uci.csv`) is the same
data: the four UCI "processed" files concatenated, with a `dataset` column naming the site.
We download the four files straight from UCI, which needs no Kaggle API key.

| Site | Rows | Notes |
|---|---|---|
| Cleveland | 303 | Most complete; the file used by most papers |
| Hungary | 294 | Many missing `slope`, `ca`, `thal` |
| Switzerland | 123 | `chol` recorded as 0 for every row (really missing) |
| VA Long Beach | 200 | Heavy missingness |
| **Total** | **920** | |

### Features (14 used attributes)

| Column | Meaning | Type |
|---|---|---|
| age | Age in years | numeric |
| sex | 1 = male, 0 = female | binary |
| cp | Chest pain: 1 typical angina, 2 atypical, 3 non-anginal, 4 asymptomatic | categorical |
| trestbps | Resting blood pressure (mm Hg) | numeric |
| chol | Serum cholesterol (mg/dl) | numeric |
| fbs | Fasting blood sugar > 120 mg/dl | binary |
| restecg | Resting ECG: 0 normal, 1 ST-T abnormality, 2 LV hypertrophy | categorical |
| thalach | Max heart rate achieved | numeric |
| exang | Exercise-induced angina | binary |
| oldpeak | ST depression induced by exercise relative to rest | numeric |
| slope | Slope of peak exercise ST segment: 1 up, 2 flat, 3 down | categorical |
| ca | Number of major vessels colored by fluoroscopy (0–3) | ordinal |
| thal | 3 normal, 6 fixed defect, 7 reversible defect | categorical |
| **num** | Diagnosis 0 (no disease) to 4 | **target** |

**Target:** we predict *presence* of disease (`num > 0` becomes 1). This binary task is the
standard benchmark. Telling apart levels 1–4 is much less reliable on 920 rows.

## 2. Known data problems (and fixes)

| Problem | Fix |
|---|---|
| Missing values are coded as `?` | Parse as NaN |
| `chol == 0` (172 rows, mostly Switzerland) | Treat as missing |
| `trestbps == 0` (1 row) | Treat as missing |
| `ca`, `thal`, `slope` mostly missing outside Cleveland | Impute, and add missing-indicator flags because missingness depends on the site |
| Categorical codes stored as floats | Cast, then one-hot encode (for linear models) |
| Possible exact duplicate rows | Drop them |
| Site differences | Keep `dataset` (site) as a feature |

All imputation happens **inside** the sklearn Pipeline, fitted on training folds only. This
prevents leakage.

## 3. What accuracy is realistic (important)

- Cleveland-only binary task: published CV accuracy is about **83–88%**.
- All 920 rows: about **82–87%** (more missing data).
- Claims of 95–100% online almost always come from the *other* Kaggle file
  (`johnsmith88/heart-disease-dataset`, 1025 rows). That file is 303 Cleveland rows copied
  about 3 times, so train and test share duplicates. That is leakage, not skill.

**Our rule:** report only honest, leakage-free numbers. That means a held-out stratified test
set that is never touched during tuning, plus repeated stratified k-fold CV with mean ± std.
"Accuracy is everything" here means squeezing out every real point, not inflating the number.

## 4. Modelling approach

- Baselines: Logistic Regression and Random Forest (scikit-learn).
- Main model: XGBoost (`XGBClassifier`), tuned with Optuna over repeated stratified CV.
- Also tried: SVM, gradient boosting, and a soft-voting or stacking ensemble of the best
  models.
- Model selection: highest mean CV accuracy (ties broken by ROC-AUC), then one final check
  on the held-out test set.
- Decision threshold: 0.5 by default. A threshold tuned on CV is reported as well.

### Metrics reported
Accuracy, balanced accuracy, precision, recall (sensitivity), specificity, F1, ROC-AUC,
PR-AUC, MCC, Brier score, confusion matrix, and a calibration curve.
In medicine, **recall/sensitivity** (missing a sick patient is costly) matters as much as
accuracy.

## 5. Stack

| Layer | Choice | Why |
|---|---|---|
| ML | pandas, scikit-learn, XGBoost, Optuna | Required stack; Optuna for efficient tuning |
| Storage | PostgreSQL 16 + SQLAlchemy 2.x ORM | Raw data, cleaned data, and a prediction log |
| API | FastAPI + Uvicorn | Fast, typed (Pydantic), automatic `/docs` |
| UI | Custom HTML/CSS/JS single page served by FastAPI, Chart.js for charts | Complete design control, no Streamlit, no build step |
| Explainability | XGBoost SHAP contributions (`pred_contribs`) | Explains each prediction feature by feature in the UI |

## 6. Database schema

- `heart_raw`: rows as downloaded (with `source_site`).
- `heart_clean`: rows after cleaning, plus binary `target`.
- `model_runs`: model name, parameters, and metrics JSON for each training run.
- `predictions`: every UI prediction (inputs, probability, label, model version, timestamp).

Connection string comes from env `DATABASE_URL`
(default `postgresql+psycopg://localhost/heart_disease`).

## 7. References
- UCI: https://archive.ics.uci.edu/ml/datasets/Heart+Disease
- Kaggle mirror: https://www.kaggle.com/datasets/redwankarimsony/heart-disease-data
- scikit-learn: https://scikit-learn.org/stable/supervised_learning.html
- XGBoost: https://xgboost.readthedocs.io
- Detrano et al. (1989), *Am. J. Cardiology* 64:304–310, the original study.

> Disclaimer: this is an educational decision-support demo, not a medical device.

## 8. Accuracy experiments (training set only, repeated 5×5 stratified CV)

| Experiment | CV accuracy |
|---|---|
| **Tuned RBF SVM, median impute + missing flags (shipped)** | **83.6–83.7%** |
| SVM, iterative imputer | 83.6% |
| SVM, KNN imputer | 83.2% |
| SVM, no missing flags | 83.1% |
| SVM + engineered features (HR % of age-max, ST>0, missing count) | 82.7% |
| SVM dropping weak features (fbs / restecg / trestbps / chol) | 82.1–83.3% |
| Soft vote SVM + CatBoost + LR + XGBoost | 83.4% |
| Soft vote SVM + LR + XGBoost | 83.2% |
| CatBoost (native categoricals + NaN) | 82.4% |
| LightGBM | 82.3% |
| XGBoost (native NaN, Optuna 80 trials) | 82.8–83.4% |

**Conclusion:** every approach lands between 82% and 84%, and the fold-to-fold std is about ±2.5%.
The data has hit its ceiling: the remaining errors come from label noise and missing values
(the `ca`/`thal` fields, the strongest predictors, are missing for about 95% of non-Cleveland
patients). No further honest gain is available without more or better data.
