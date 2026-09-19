import type { Analysis } from "../types";

const amount = (value: number) => `${value.toFixed(1)} mm`;

export default function RiskCard({ analysis }: { analysis: Analysis }) {
  const tone = analysis.risk.level.toLowerCase();
  return <section className={`risk-card ${tone}`}><p className="eyebrow">Significant rainfall risk</p><div className="risk-content"><div><strong>{analysis.risk.level}</strong><span>Deterministic risk assessment</span></div><div className="score"><b>{analysis.risk.score.toFixed(1)}</b><span>/ 100</span></div></div><div className="probability"><span>ML probability of ≥20 mm in the next 24 hours</span><b>{Math.round(analysis.ml_prediction.probability * 100)}%</b></div><dl className="risk-details"><div><dt>Forecast rain</dt><dd>{amount(analysis.weather.rainfall.forecast_next_24h_mm)}</dd></div><div><dt>Recent rain</dt><dd>{amount(analysis.weather.rainfall.recent_24h_mm)}</dd></div><div><dt>Max hourly chance</dt><dd>{Math.round(analysis.risk.max_hourly_precipitation_probability_percent)}%</dd></div><div><dt>Model</dt><dd>{analysis.ml_prediction.model_version}</dd></div><div><dt>Data freshness</dt><dd>{analysis.weather.freshness.status} · {Math.round(analysis.weather.freshness.age_minutes)} min</dd></div></dl></section>;
}
