# Agent Design

## Implemented Phase 3A agent

`WeatherRiskAgent` is a single typed LangGraph orchestration layer. It invokes existing services; it does not query Open-Meteo directly beyond the existing weather service, build ML features, predict, or calculate risk itself.

```text
START → validate_request → retrieve_weather → run_analysis → assemble_evidence
      ├─ no ExplanationProvider → template_explanation → END
      └─ provider → generate_explanation → validate_explanation
                                      ├─ valid → END
                                      └─ failed/unsafe → template_explanation → END
```

State contains coordinates, optional location label, normalized weather, deterministic analysis, verified `Evidence`, explanation, and fallback status—never raw provider JSON. `run_analysis` reuses `AnalysisService.analyze_weather`, which remains the single authority for ML inference and the risk engine.

## Evidence and explanation boundary

Evidence includes selected location/coordinates, current temperature, recent and forecast 24-hour rain, maximum hourly precipitation probability, ML probability/target/model version, risk score/level/factors, freshness, and retrieval timestamp. The `ExplanationProvider` protocol receives only this typed object.

The response schema is `summary`, `why_this_risk`, `key_factors`, `what_to_watch`, `disclaimer`, and `source`. Validation requires non-empty required content, the exact disclaimer, risk-level consistency, numeric claims matching evidence, and no flood, official-warning, or emergency claim outside the disclaimer. A missing provider, timeout/error, malformed explanation, or failed validation yields the deterministic template, built exclusively from evidence. `LLM_PROVIDER`, `LLM_API_KEY`, and `LLM_MODEL` are environment configuration placeholders; no paid provider or credentials are required or configured in P0.

Weather/provider, missing-model, stale-data, and risk errors remain structured backend errors from the pre-agent pipeline; the graph does not fabricate recovery data. RAG remains omitted.
