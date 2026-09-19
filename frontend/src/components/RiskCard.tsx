import type { Analysis } from "../types";

const amount = (value: number) => `${value.toFixed(1)} mm`;

export default function RiskCard({ analysis }: { analysis: Analysis }) {
  const tone = analysis.risk.level.toLowerCase();
  return <section className={`risk-card ${tone}`}><div><p className="eyebrow">Significant rainfall risk</p><div className="risk-topline"><strong>{analysis.risk.level}</strong><span className="risk-level-dot" aria-hidden="true" /></div></div><div className="risk-center"><div className="risk-gauge" aria-label={`Risk score ${analysis.risk.score.toFixed(1)} out of 100`}><svg viewBox="0 0 120 120" aria-hidden="true"><circle cx="60" cy="60" r="51" className="gauge-track" /><circle cx="60" cy="60" r="51" className="gauge-value" pathLength="100" style={{ strokeDasharray: `${analysis.risk.score} 100` }} /></svg><div><b>{analysis.risk.score.toFixed(1)}</b><span>/ 100</span></div></div><p className="risk-interpretation">{analysis.risk.level} likelihood of reaching the 20 mm significant-rainfall threshold in the next 24 hours.</p></div><div className="risk-footer"><span><small>ML probability</small><b>{Math.round(analysis.ml_prediction.probability * 100)}%</b></span><span><small>Forecast rain</small><b>{amount(analysis.weather.rainfall.forecast_next_24h_mm)}</b></span><span><small>Peak chance</small><b>{Math.round(analysis.risk.max_hourly_precipitation_probability_percent)}%</b></span></div></section>;
}
