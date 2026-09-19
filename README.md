# WeatherRisk AI

**Real-Time Weather & Rainfall Risk Intelligence Agent**

WeatherRisk AI is a public dashboard that turns live weather forecasts and recent rainfall into an explainable, short-horizon **significant-rainfall risk** assessment. It helps users understand whether the next 24 hours warrant attention; it is not a flood model, official alert system, or safety guarantee.

## What it does

1. Searches a place through Open-Meteo geocoding.
2. Retrieves current, recent, and next-24-hour weather from Open-Meteo.
3. Runs a persisted ML model for `P(next_24h_precipitation >= 20 mm)`.
4. Applies a separate deterministic Low/Moderate/High risk policy.
5. Uses LangGraph to assemble verified evidence and create a constrained explanation; a deterministic template is used when no LLM is configured.
6. Renders the result in a responsive React dashboard.

```text
React → FastAPI → Open-Meteo → normalized weather → ML inference
      → deterministic risk engine → LangGraph evidence explanation → dashboard
```

## Stack

- React, TypeScript, Vite, standard CSS
- Python, FastAPI, Pydantic, HTTPX
- Open-Meteo forecast, geocoding, and historical/reanalysis APIs
- pandas, NumPy, scikit-learn, joblib
- LangGraph and pytest

## ML and risk policy

The target is whether total precipitation in the **following 24 hours** reaches the application-defined 20 mm threshold. It is not an official rainfall or flood-warning threshold. The model was trained from Open-Meteo historical/reanalysis data for Hyderabad, Mumbai, and Bengaluru (2022–2024), not station observations. Its held-out PR-AUC is 0.55054; see [ML design](docs/ML_DESIGN.md) for all real metrics and limitations.

Risk is not decided by the model or an LLM. The deterministic engine combines calibrated ML probability, forecast 24-hour rainfall, maximum hourly precipitation probability, and recent 24-hour rainfall with the documented weights and bands in [Architecture](docs/ARCHITECTURE.md).

## Local setup

Prerequisites: Python 3.11+ and Node.js 20+.

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
npm install --prefix frontend
Copy-Item .env.example .env
Copy-Item frontend\.env.example frontend\.env
```

The local trained model artifact is expected at `models/weather_risk_model.joblib`. Generate it when absent:

```powershell
.\.venv\Scripts\python.exe ml\train_model.py
```

Start the backend and frontend in separate terminals:

```powershell
.\.venv\Scripts\python.exe -m uvicorn app.main:app --app-dir backend --reload
npm run dev --prefix frontend
```

Open the Vite URL (normally `http://localhost:5173`).

## Environment

Backend variables are documented in [.env.example](.env.example): CORS origins, weather HTTP timeout/retries/cache/freshness, and optional LLM placeholders. Open-Meteo P0 needs no API key. Do not expose backend secrets through `VITE_*` variables.

Frontend uses the build-time `VITE_API_BASE_URL` from [frontend/.env.example](frontend/.env.example). Set it to the local backend URL for development; the frontend fails closed when it is missing rather than guessing a production endpoint.

## Production deployment

Deploy the React static build and FastAPI modular monolith separately:

```text
Browser → static frontend hosting → HTTPS → FastAPI backend → Open-Meteo / Nominatim / local model artifact
```

Build the frontend with the public backend URL supplied at build time. Do not use a localhost value in production and do not put secrets in `VITE_*` variables:

```powershell
Set-Item Env:VITE_API_BASE_URL "https://your-backend.example"
npm run build --prefix frontend
```

Configure the backend using a private environment file or hosting-platform environment settings. At minimum, set `APP_ENV=production`, `CORS_ORIGINS` to the exact deployed frontend origin, and `MODEL_ARTIFACT_PATH` to the model artifact available in the runtime filesystem. The examples in [.env.example](.env.example) document HTTP timeout, cache/retry, Nominatim, and optional LLM settings. `GET /health` is suitable for a platform health check and intentionally does not call external providers.

The model artifact (`models/weather_risk_model.joblib`) is approximately 66 MB and is intentionally ignored by Git. A deployment must supply it through an approved build artifact, secure volume, or platform artifact mechanism; a source-only checkout cannot serve `/analysis` without it. The backend resolves a relative `MODEL_ARTIFACT_PATH` from the repository root, so it remains independent of the Uvicorn working directory.

Nominatim reverse geocoding is backend-only, bounded by the configured HTTP timeout, cached, and invoked only after a user explicitly requests browser location access. It returns locality-level identity only, never street-address data.

Docker was assessed but is not included: because the model is deliberately absent from source control, a generic image would either fail to build or incorrectly bake a local artifact into the image. Use the hosting platform's artifact/volume mechanism first, then add a deployment-specific image once that model-delivery path is chosen.

WeatherRisk AI is decision-support software. It is not an official weather warning or flood prediction system.

## API

- `GET /health`
- `GET /locations?query=Hyderabad`
- `GET /weather?latitude=17.385&longitude=78.4867`
- `POST /analysis` with `{ "latitude", "longitude", "location_name?" }`

See [API contract](docs/API_CONTRACT.md) for response/error semantics.

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest -q
npm run build --prefix frontend
```

## Important limitations

- Not flood prediction, hydrological modelling, an official warning, or emergency advice.
- Open-Meteo represents model/grid-point weather; historical data are reanalysis, not station observations.
- The initial model uses only three Indian locations and its validation/test performance differs over time.
- No external LLM is configured by default; verified template explanations are normal behavior.
- No accounts, persistence, alerts, RAG, GIS, or deployment infrastructure are included.

## Documentation

[Architecture](docs/ARCHITECTURE.md) · [project plan](docs/PROJECT_PLAN.md) · [ML design](docs/ML_DESIGN.md) · [agent design](docs/AGENT_DESIGN.md) · [handoff](docs/HANDOFF.md)
