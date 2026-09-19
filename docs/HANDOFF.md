# Development Handoff

## Project purpose

WeatherRisk AI provides real-time, explainable **significant-rainfall risk** intelligence for a selected location. It is explicitly not a flood-prediction product.

## Current phase

Phase 5A complete — decision-support dashboard enhancement.

## Status

The complete local vertical slice is implemented and hardened: React dashboard, FastAPI, Open-Meteo, ML inference, deterministic risk, and LangGraph template explanation. Phase 5A adds opt-in browser geolocation, richer backend-evidence presentation, and a lightweight forecast timeline. No external LLM provider, RAG, database, authentication, or deployment has been added.

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
- Phase 5A adds user-initiated browser geolocation with permission/unavailable/timeout handling and no coordinate persistence; backend-derived risk details/factors; an SVG rainfall/probability timeline; and responsive/accessibility refinements. The frontend does not calculate risk.
- Phase 4 audit fixed browser CORS for JSON `POST /analysis`, whitespace-only location validation, corrupt/invalid ML artifact handling, safe request logging, frontend request race cancellation, and generated TypeScript artifact ignores.

## Current work

Phase 5A is complete.

## Exact next task

Phase 5 — Deployment + final project packaging. Do not implement it without explicit direction.

## Architecture summary

React → FastAPI modular monolith → OpenMeteoProvider → normalized weather → sklearn model → deterministic risk engine → LangGraph evidence explanation. P0 is stateless; LLM use is optional and constrained to evidence explanation.

## Changed files

Phase 4 updated backend exception/CORS/request logging logic, ML artifact validation, frontend abortable API requests, root/frontend build configuration, `.gitignore`, targeted hardening tests, README, and this handoff. The tracked generated TypeScript build-info files were removed from the Git index while retained locally and ignored going forward. Unnecessary `.gitkeep` placeholders were removed from populated source directories; the empty `rag/.gitkeep` remains intentional. Local Phase 2 data/model artifacts remain unchanged and ignored.

## API / ML / agent status

Implemented: `GET /health`, `GET /locations?query=`, `GET /weather?latitude=&longitude=`, and `POST /analysis`. The React app consumes `/locations` and `/analysis`; it never calls Open-Meteo or performs ML/risk calculations. No external LLM is configured, so the rendered explanation source is the valid deterministic template fallback.

## Environment

See `.env.example`. No secrets are required for Open-Meteo. An LLM key is optional only after a compatible adapter is implemented.

## Tests and known issues

Audit results: `pytest -q` has 30 passing tests and one third-party TestClient deprecation warning; `npm run build` succeeds and `npm audit --omit=dev --audit-level=high` found zero production dependency vulnerabilities. New tests cover CORS POST preflight, whitespace queries, coordinate bounds, and an invalid ML artifact. `.gitignore` was validated against local environments, dependencies, generated datasets/models, Vite output, and TypeScript build products; source, docs, `.github/copilot-instructions.md`, and configuration examples remain trackable. No secrets or absolute machine paths were found in source/configuration (only empty optional LLM placeholders). Local end-to-end verification started FastAPI and Vite; frontend served HTTP 200, `/health` was OK, geocoding returned 10 Hyderabad results, and real Open-Meteo-backed analyses returned Hyderabad Low and Mumbai Moderate with the valid template explanation. Browser visual interaction, device-browser accessibility testing, and automated frontend component tests have not been run. Main limitations: no configured external LLM (by design), practical rather than full NLP validation, reanalysis/grid-point data, three training locations, temporal performance drop, no hydrological data, and no persistent history.

## Last completed milestone

Phase 5A dashboard enhancement, 2026-09-19.
