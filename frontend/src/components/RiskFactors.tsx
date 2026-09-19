import type { Analysis } from "../types";

export default function RiskFactors({ analysis }: { analysis: Analysis }) {
  return <section className="panel risk-factors"><div className="section-heading"><div><p className="eyebrow">Backend evidence</p><h2>Why this risk?</h2></div></div><div className="factor-list">{analysis.risk.factors.map(factor => <article className="factor" key={factor.name}><h3>{factor.name}</h3><p>Value: {factor.value.toFixed(1)}</p><p>Indicator: {factor.indicator.toFixed(0)} / 100</p><p>Threshold: {factor.threshold}</p></article>)}</div></section>;
}
