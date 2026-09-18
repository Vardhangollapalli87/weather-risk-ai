# WeatherRisk AI

**Real-Time Weather & Rainfall Risk Intelligence Agent**

WeatherRisk AI is a public decision-support dashboard that converts live weather forecasts and recent rainfall into an explainable **short-horizon significant-rainfall risk** assessment. It is not a flood-warning system and does not predict inundation, river levels, or property damage.

## What it demonstrates

Real-time weather integration, reproducible historical-data training, an explainable ML classifier, deterministic risk calculation, and a LangGraph workflow that explains verified structured results.

## Core flow

`Open-Meteo → normalization → ML inference → deterministic risk engine → LangGraph explanation → React dashboard`

## MVP stack

- React + TypeScript + Vite
- Python 3.12 + FastAPI + Pydantic
- Open-Meteo Forecast, Geocoding, and Historical Weather APIs
- scikit-learn (logistic-regression baseline and random-forest candidate)
- LangGraph; optional provider-independent LLM adapter
- pytest, HTTPX, and Vitest

No authentication, database, paid API, or user-uploaded CSV is required for P0.

## Status

P0 weather, ML, deterministic-risk, LangGraph explanation, and React dashboard foundations are implemented. See [docs/HANDOFF.md](docs/HANDOFF.md) for the exact continuation point.

## Documentation

- [Architecture](docs/ARCHITECTURE.md)
- [Plan](docs/PROJECT_PLAN.md)
- [API contract](docs/API_CONTRACT.md)
- [ML design](docs/ML_DESIGN.md)
- [Agent design](docs/AGENT_DESIGN.md)
- [Decisions](docs/DECISIONS.md)
