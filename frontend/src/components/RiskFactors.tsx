import type { Analysis } from "../types";

export default function RiskFactors({ analysis }: { analysis: Analysis }) {
  return <section className="panel risk-factors"><div className="section-heading"><div><p className="eyebrow">Risk signals</p><h2>Why this risk?</h2></div><span className="section-note">Backend-evaluated inputs</span></div><div className="factor-list">{analysis.risk.factors.map(factor => <article className="factor" key={factor.name}><p className="factor-value">{formatFactorValue(factor.name, factor.value)}</p><h3>{factorLabel(factor.name)}</h3><p className="factor-support">Included in the deterministic risk assessment</p></article>)}</div><p className="factor-footnote">These signals are combined by the deterministic risk engine to produce the final risk score.</p></section>;
}

function factorLabel(name: string) {
  if (name.startsWith("Maximum hourly")) return "Maximum hourly rain chance";
  if (name.startsWith("Forecast")) return "Forecast rainfall";
  if (name.startsWith("ML probability")) return "ML rainfall probability";
  if (name.startsWith("Recent")) return "Recent rainfall";
  return name;
}

function formatFactorValue(name: string, value: number) {
  return name.includes("probability") ? `${value.toFixed(1)}%` : `${value.toFixed(1)} mm`;
}
