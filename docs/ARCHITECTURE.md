# Architecture

## 1. Problem, users, and boundary

People need more than a raw forecast: they need a transparent indication of whether upcoming rain merits attention. The primary user is a resident, student, field worker, or operations trainee selecting a place and assessing the next 24 hours.

The product estimates **significant-rainfall risk** for a selected point location over the next 24 hours. It is decision support, not an official warning, flood model, or safety guarantee. Flood prediction needs terrain, drainage, river gauge, catchment and vulnerability data that P0 does not possess.

## 2. MVP requirements and boundaries

P0: place search; current conditions; hourly forecast; recent accumulation; normalized schema; trained classifier inference; deterministic Low/Moderate/High risk; structured explanation; React dashboard.

Excluded from P0: accounts, persistence, alerts, GIS, hydrology, RAG, and advanced charts. The app is publicly usable with no authentication.

## 3. High-level architecture

```text
React dashboard
     │ HTTPS
FastAPI modular monolith
 ├─ WeatherProvider interface ──> Open-Meteo geocoding/forecast/archive
 ├─ normalization + freshness validation
 ├─ ML model artifact + feature builder
 ├─ deterministic risk engine
 └─ LangGraph explanation workflow ──> optional LLM adapter
```

The frontend never calls weather providers directly. Backend services own provider calls, timeouts, retries, validation, caching (in-memory, short TTL), and normalized contracts.

## 4. Weather data strategy

`OpenMeteoProvider` implements a small `WeatherProvider` protocol: `search_locations`, `reverse_geocode`, `get_weather_snapshot`, and `get_historical_hourly`. Forecast calls request current and hourly temperature, relative humidity, sea-level pressure, wind speed, cloud cover, precipitation, precipitation probability, and weather code; request `past_hours=24` for recent accumulation. Open-Meteo geocoding resolves a user query to coordinates/timezone. An explicit browser-device-location request may use the backend's cached Nominatim reverse lookup to return locality/city/state/country only; it never returns or displays street-address fields.

Historical training uses Open-Meteo `/v1/archive` with ERA5 hourly data, selecting the same feasible meteorological variables but never pretending reanalysis is station observation. The service records provider generation time, retrieval time, source/model metadata, and the requested location. If data is older than the configured freshness threshold, analysis is labelled stale; provider failure returns a structured 502/503 and no invented fallback values.

Open-Meteo documentation confirms forecast hourly fields including precipitation probability and its archive endpoint with hourly precipitation, temperature, humidity, pressure, cloud cover and wind. See [Forecast docs](https://open-meteo.com/en/docs) and [Historical Weather API docs](https://open-meteo.com/en/docs/historical-weather-api).

## 5. ML pipeline

The defensible target is binary classification: **will total precipitation in the next 24 hours be at least 20 mm?** This is measurable from historical hourly series and avoids a false claim of flood prediction. Features are forecast-available or derived from trailing observed/reanalysis history: temperature, relative humidity, pressure, wind, cloud cover, current/previous precipitation, 6h/24h accumulated rain, hour, month, and location-independent calendar encodings.

Offline pipeline: fetch pinned date ranges and locations → validate/null handling → chronological split → feature engineering without future leakage → logistic baseline and random-forest candidate → select by validation PR-AUC, recall, calibration and confusion matrix → persist model plus feature schema, training period, threshold, metrics, and version. Metrics are recorded only after training. Runtime produces probability and uncertainty/status, never a fabricated rainfall amount.

## 6. Deterministic risk engine

Risk is a transparent exposure index, not ML output. It combines (a) calibrated ML probability, (b) next-24h forecast total, (c) maximum hourly precipitation probability, and (d) observed/recent 24h accumulation:

```text
score = 0.45*P_ml + 0.30*I(forecast_24h) + 0.15*I(max_pop) + 0.10*I(recent_24h)
```

`P_ml` is 0–100. Each indicator is a documented 0–100 piecewise band (forecast: 0/20/50/80/100 at <2, <10, <20, <40, ≥40 mm; probability: max hourly POP; recent rain: same bands). Low `<35`, Moderate `35–64`, High `≥65`. The engine returns score, level, every input, triggered threshold, ranked factors, and calculation version. Thresholds are configurable, tested, and clearly labelled as MVP decision-support policy.

## 7. Agent and RAG

LangGraph orchestrates fixed tools in a single graph: validate request → retrieve normalized snapshot → build features/run model → calculate risk → assemble evidence → explain. Tools produce typed results and the graph stops if a dependency fails. The optional LLM receives only this evidence object and must output a schema-constrained explanation; a deterministic renderer is used if no provider is configured. It may clarify factors and cautious recommendations, but cannot fetch values, score risk, or make emergency claims.

RAG is P1 only. If added, it will retrieve a tiny curated, versioned set of authoritative public rain/flood-safety guidance and cite document title/section. It never supplies meteorological facts or affects scores.

## 8. Frontend and API

React state is limited to selected location, loading/error state, and analysis response. The dashboard renders data provenance/time, current conditions, 24-hour outlook, ML probability, risk card, factors, and explanation. API schemas are defined in `API_CONTRACT.md`; endpoint groups are `/locations` (including `/locations/reverse` for explicit device-location identity), `/weather`, `/analysis`, and `/health`.

## 9. Persistence, resilience, security, and operations

No database is necessary for P0: historical training files and model artifacts are local/versioned outside Git; live analysis is stateless. In-memory TTL caching reduces provider calls but is not source of truth. Add PostgreSQL only for an explicit history/alert feature.

Validate query length and coordinate ranges; configure CORS; keep secrets in environment; use timeouts, bounded retries only for transient provider failures, request IDs, structured logs, and no secret/raw-key logging. Tests cover provider normalization with recorded fixtures, feature leakage rules, risk thresholds, agent failure paths, API contracts, and frontend rendering. Docker and a single-host deployment are P1 after the local MVP.

## 10. Future extensions

P1: safety-guidance RAG, historical comparison, richer charts, optional Telegram alert. P2: accounts, saved locations, GIS, station/river/reservoir/satellite data, and purpose-built hydrological modelling.
