# 4-Day Implementation Plan

## Day 1 — provider foundation (P0)

Create Python and React projects; configuration, typed domain models, health endpoint, Open-Meteo provider interface/implementation, normalization, place search, weather API, provider fixtures and tests. **Exit:** a selected location returns live, provenance-labelled conditions and forecast.

## Day 2 — historical ML and risk (P0)

Build reproducible historical collection and feature pipeline; train/evaluate baseline and candidate; persist real model metadata; implement unit-tested risk engine and analysis endpoint. **Exit:** a live analysis returns actual model output plus deterministic, traceable score.

## Day 3 — orchestration and dashboard (P0)

Implement LangGraph typed workflow, template fallback/optional adapter, explanation contract; build dashboard and integration tests. **Exit:** browser flow search → weather → analysis works with failure/loading states.

## Day 4 — hardening and optional P1 only after P0

Contract/end-to-end tests, docs, accessibility/responsive polish, Docker/deployment notes. If P0 is stable, add one P1 item: curated RAG *or* richer historical comparison, never both by default. **Exit:** documented demo, real metrics, known limitations, and reproducible setup.

Each day ends with tests, documentation/handoff update, and a reviewable milestone. Git actions remain manual.
