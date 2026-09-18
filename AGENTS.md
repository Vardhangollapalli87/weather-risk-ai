# AI Agent Instructions

1. Read `docs/HANDOFF.md`, `docs/ARCHITECTURE.md`, and the relevant design document before changing code.
2. Inspect existing code and contracts first; preserve public API schemas unless the change is documented.
3. Use live provider data at runtime. Never substitute fake weather values or claim forecasts are observations.
4. Keep the boundary explicit: provider supplies data, ML predicts, risk engine calculates, agent explains.
5. Do not let an LLM invent values, calculate risk, or override deterministic risk output.
6. Do not add authentication, a database, RAG, alerts, or new infrastructure before their planned milestone.
7. Use typed Pydantic models, validation, structured errors, logging, and tests for changed behavior.
8. Keep secrets in environment variables; never commit them.
9. Avoid unrelated rewrites and unnecessary abstractions. Do not initialize Git, commit, push, or change remotes unless explicitly asked.
10. After a completed milestone, update `docs/HANDOFF.md`, relevant API/design documents, and `docs/DECISIONS.md` when a decision changes.
