import type { Analysis } from "../types";

const amount = (value: number) => `${value.toFixed(1)} mm`;

export default function RiskCard({ analysis }: { analysis: Analysis }) {
  const tone = analysis.risk.level.toLowerCase();
  return <section className={`risk-card ${tone}`}><p className="eyebrow">Significant rainfall risk</p><div className="risk-topline"><strong>{analysis.risk.level}</strong><span className="risk-level-dot" aria-hidden="true" /></div><div className="risk-score"><b>{analysis.risk.score.toFixed(1)}</b><span>out of 100</span></div><div className="score-track" aria-label={`Risk score ${analysis.risk.score.toFixed(1)} out of 100`}><i style={{ width: `${analysis.risk.score}%` }} /></div><p className="risk-interpretation">{analysis.risk.level} likelihood of reaching the 20 mm significant-rainfall threshold in the next 24 hours.</p><div className="probability"><span>ML probability</span><b>{Math.round(analysis.ml_prediction.probability * 100)}%</b></div><div className="risk-summary"><span>Forecast <b>{amount(analysis.weather.rainfall.forecast_next_24h_mm)}</b></span><span>Peak chance <b>{Math.round(analysis.risk.max_hourly_precipitation_probability_percent)}%</b></span></div></section>;
}
