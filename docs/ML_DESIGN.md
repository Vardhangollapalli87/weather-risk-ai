# ML Design

## Target

Binary target `significant_rain_next_24h = precipitation_sum(t+1...t+24) >= 20 mm`. The 20 mm operating definition is configurable and will be verified against class balance before final training; it is not a flood threshold.

## Implemented Phase 2 dataset and safeguards

The completed initial run used Open-Meteo historical/reanalysis data (not station observations) for Hyderabad, Mumbai, and Bengaluru, India, from 2022-01-01 through 2024-12-31. It retrieved 78,912 rows; 0 timestamps were invalid, 0 source rows were missing, and 141 edge rows were removed because complete past rolling windows or future 24-hour target windows were unavailable. The final dataset has 78,771 rows: 4,536 positive (5.76%) and 74,235 negative.

Data are sorted and validated per location before features are created. `future_24h_precipitation_mm` is explicitly the sum of `t+1` through `t+24`; it is never a feature. Previous-hour and rolling features use only the current/past row direction. The saved CSV is local at `data/processed/phase2_dataset.csv` and ignored by Git.

## Features, split, models, and decision rule

Feature schema v1: temperature, relative humidity, mean sea-level pressure, wind speed, cloud cover, current precipitation, previous-hour precipitation, rolling 6-hour precipitation, rolling 24-hour precipitation, hour, month, hour sine, and hour cosine. No location coordinates or future values are features.

The global chronological split was 70% training (55,139 rows, 2022-01-01T23:00Z–2024-02-06T18:00Z), 15% validation (11,816 rows, to 2024-07-19T21:00Z), and 15% held-out test (11,816 rows, to 2024-12-30T23:00Z). Class weighting is `balanced`; no synthetic oversampling was used. Logistic Regression and Random Forest (200 trees, minimum leaf size 5) were sigmoid-calibrated using training data only. The selected model is a calibrated Random Forest, selected by validation PR-AUC (with recall tie-break) and validation-only threshold selection.

| Validation model | threshold | PR-AUC | ROC-AUC | recall | precision | F1 | Brier |
|---|---:|---:|---:|---:|---:|---:|---:|
| Logistic Regression | 0.35 | 0.60500 | 0.93706 | 0.52235 | 0.58529 | 0.55203 | 0.03599 |
| Random Forest | 0.55 | 0.61307 | 0.93855 | 0.61034 | 0.56170 | 0.58501 | 0.04131 |

Final held-out test result for the selected frozen setup: PR-AUC 0.55054, ROC-AUC 0.88573, recall 0.44683, precision 0.64967, F1 0.52949, Brier score 0.04859, confusion matrix `[[10719, 213], [489, 395]]`. The validation-to-test PR-AUC drop is a material limitation; this is a student-scale decision-support model, not a production forecast or flood model.

## Runtime contract

The persisted local, Git-ignored `models/weather_risk_model.joblib` includes the calibrated model and reproducibility metadata. Its companion JSON includes source, dates, feature schema, threshold, splits, comparisons, and metrics. Runtime shares the same feature builder, validates exact feature names, and returns `P(next_24h_precipitation >= 20 mm)`, classification, target, model version, feature schema version, and status. Missing artifact or required weather fields fails clearly; no forecast-only substitute exists in Phase 2.
