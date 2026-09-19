# Architecture Decisions

## ADR-001 — Significant-rainfall classification

- **Decision:** predict whether next-24h precipitation reaches an operating threshold, initially 20 mm.
- **Reason:** measurable with freely available historic data and defensible without hydrology.
- **Alternatives:** flood prediction; rejected because critical terrain, drainage, river and exposure data are absent. Rainfall regression; deferred because reliable, calibrated event classification is smaller for this MVP.
- **Status/date:** Accepted, 2026-09-18.

## ADR-002 — Open-Meteo behind a provider interface

- **Decision:** use Open-Meteo for geocoding, live forecast, and historical training data through a `WeatherProvider` abstraction.
- **Reason:** zero-key MVP, suitable forecast/hourly fields, compatible historical endpoint.
- **Alternatives:** direct frontend calls (rejected: leaks data boundary); provider lock-in (rejected).
- **Status/date:** Accepted, 2026-09-18.

## ADR-003 — Deterministic risk separate from ML/LLM

- **Decision:** documented weighted score and fixed bands generate the risk level.
- **Reason:** explanation, testability, and no hallucinated scoring.
- **Alternatives:** LLM scoring and ML-as-risk; rejected because neither exposes the needed policy layer.
- **Status/date:** Accepted, 2026-09-18.

## ADR-004 — Stateless P0

- **Decision:** no database for MVP.
- **Reason:** live analysis needs no user state; persistence adds setup and operations risk.
- **Alternatives:** PostgreSQL; defer until histories/alerts require it.
- **Status/date:** Accepted, 2026-09-18.

## ADR-005 — RAG is P1

- **Decision:** omit RAG from P0.
- **Reason:** it does not improve core meteorological assessment; a template/LLM explanation over evidence provides immediate value.
- **Status/date:** Accepted, 2026-09-18.

## ADR-006 — Calibrated Random Forest selected for Phase 2

- **Decision:** use sigmoid-calibrated Random Forest with a validation-selected 0.55 probability threshold.
- **Reason:** it had the best validation PR-AUC (0.61307) and F1 (0.58501) of the two required models.
- **Alternatives:** calibrated Logistic Regression; retained as baseline but had lower validation PR-AUC (0.60500).
- **Status/date:** Accepted, 2026-09-18. The held-out test PR-AUC of 0.55054 is documented as a limitation, not hidden.

## ADR-007 — Backend reverse geocoding for explicit device-location identity

- **Decision:** after an explicit browser geolocation request, use a cached Nominatim reverse lookup behind the existing provider/service boundary and return locality/city/state/country only.
- **Reason:** the UI needs a human-readable location identity without exposing street-address information or calling external services from React.
- **Alternatives:** display raw coordinates only (rejected: poor location identity); direct frontend reverse-geocoding call (rejected: bypasses the backend data boundary).
- **Status/date:** Accepted, 2026-09-19.
