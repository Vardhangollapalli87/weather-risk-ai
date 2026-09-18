# WeatherRisk AI instructions

This is a public, architecture-first FastAPI + React project. Read `docs/HANDOFF.md` and the relevant docs before editing.

- Runtime weather must come from the configured provider; no mock values in production paths.
- Distinguish observed weather, forecast, ML prediction, deterministic risk, and AI explanation in models and UI.
- The MVP predicts significant rainfall exposure, **not flooding**.
- The risk score belongs only in the deterministic risk engine. An LLM may summarize structured results only.
- Use Pydantic, type hints, validation, structured errors, logging, and tests.
- Preserve API contracts and update documentation/handoff after milestones.
- Do not add authentication, persistent database storage, RAG, Telegram, or paid-provider coupling to P0.
