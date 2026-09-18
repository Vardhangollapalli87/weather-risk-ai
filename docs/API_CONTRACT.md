# API Contract (planned)

All responses use ISO-8601 timestamps, metric units, and a `source`/`retrieved_at` provenance field. Exact models are Pydantic-defined during implementation.

| Method/path | Purpose | Key response |
|---|---|---|
| `GET /health` | service health | status, version |
| `GET /locations?query=` | provider-backed place search | id, name, country, latitude, longitude, timezone |
| `GET /weather?latitude=&longitude=` | normalized current/recent/forecast data | current, hourly, daily_summary, provenance, freshness |
| `POST /analysis` | model, deterministic risk, and constrained explanation | weather, ml_prediction, risk, explanation, status |

`POST /analysis` accepts an optional selected location name plus coordinates; it never accepts client-provided weather values. A success response separates normalized `weather`, calibrated `ml_prediction`, deterministic `risk`, and `explanation` (`summary`, `why_this_risk`, `key_factors`, `what_to_watch`, `disclaimer`, `source`). The explanation is evidence-constrained and defaults to `source: "template"` when no LLM provider is configured or its output is invalid. If the model artifact is absent it returns `503 ML_MODEL_UNAVAILABLE`. Error format: `{ "error": { "code", "message", "request_id", "retryable" } }`.
