# Development Handoff

## Project purpose

WeatherRisk AI provides real-time, explainable **significant-rainfall risk** intelligence for a selected location. It is explicitly not a flood-prediction product.

## Current phase

P0 Phase 3B complete — React dashboard.

## Status

Weather/location foundation, historical ML pipeline, deterministic risk engine, LangGraph evidence-constrained explanation, and React dashboard are implemented and tested. No external LLM provider, RAG, database, authentication, or deployment has been added.

## Completed

- Requirements analyzed; P0/P1/P2 scope set.
- Open-Meteo validated as the initial provider strategy.
- ML, deterministic risk, agent, persistence, and RAG decisions documented.
- Continuity instructions and planning documents created.
- FastAPI application, CORS configuration, request IDs, structured errors, and health endpoint implemented.
- `WeatherProvider` protocol and `OpenMeteoProvider` implemented for geocoding, live snapshot, and historical retrieval.
- Normalized location/weather schemas, freshness status, short-lived in-memory caching, and location/weather services implemented.
- Fixture-based automated tests implemented; no test calls Open-Meteo.
- Historical Open-Meteo reanalysis dataset collected for Hyderabad, Mumbai, and Bengaluru (2022–2024); 78,771 usable rows and 5.76% positive class.
- Leakage-safe shared training/runtime feature builder, chronological split, calibrated Logistic Regression and Random Forest comparison, local model artifact, and ML inference service implemented.
- Calibrated Random Forest selected with validation threshold 0.55; deterministic risk engine and `POST /analysis` implemented.
- Single-agent LangGraph workflow implemented with a typed evidence object, provider-independent explanation interface, validation, and deterministic template fallback.
- Responsive Vite + React + TypeScript dashboard implemented with centralized API client, location search, analysis display, forecast cards, explanation, provenance/freshness, loading, no-results, retry, and error states.

## Current work

Phase 3B is complete.

## Exact next task

Phase 4 — Full integration, testing, security review, performance and production polish. Do not expand product scope without an explicit decision.

## Architecture summary

React → FastAPI modular monolith → OpenMeteoProvider → normalized weather → sklearn model → deterministic risk engine → LangGraph evidence explanation. P0 is stateless; LLM use is optional and constrained to evidence explanation.

## Changed files

Phase 3B added `frontend/` Vite configuration, TypeScript types, centralized API client, React components (`SearchPanel`, `RiskCard`, `Forecast`, `Explanation`), responsive CSS, and frontend environment example. It updated this handoff. Local ignored Phase 2 data/model artifacts remain unchanged.

## API / ML / agent status

Implemented: `GET /health`, `GET /locations?query=`, `GET /weather?latitude=&longitude=`, and `POST /analysis`. The React app consumes `/locations` and `/analysis`; it never calls Open-Meteo or performs ML/risk calculations. No external LLM is configured, so the rendered explanation source is the valid deterministic template fallback.

## Environment

See `.env.example`. No secrets are required for Open-Meteo. An LLM key is optional only after a compatible adapter is implemented.

## Tests and known issues

`npm run build` succeeds in `frontend/`. Backend regression suite: 28 passed (one third-party TestClient deprecation warning). A local smoke check started backend and Vite, confirmed the frontend returned HTTP 200, and a real Open-Meteo-backed `/analysis` response was fresh with a template explanation. Manual visual/browser interaction and automated frontend component tests have not been run. Main limitations: no configured external LLM (by design), practical rather than full NLP validation, reanalysis/grid-point data, three training locations, temporal performance drop, no hydrological data, and no persistent history.

## Last completed milestone

P0 Phase 3B React dashboard, 2026-09-19.
