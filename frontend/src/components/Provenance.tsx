import type { Analysis } from "../types";

export default function Provenance({ analysis }: { analysis: Analysis }) {
  const weather = analysis.weather;
  const retrievedAt = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short", timeZone: weather.timezone }).format(new Date(weather.retrieved_at));
  return <section className="provenance-card"><div><p className="eyebrow">Data & provenance</p><h2>Verified inputs</h2></div><div className="provenance-list"><Item label="Data status" value={weather.freshness.status === "fresh" ? "Fresh data" : "Stale data"} detail={`Updated ${Math.round(weather.freshness.age_minutes)} min ago`} fresh={weather.freshness.status === "fresh"} /><Item label="Weather source" value={weather.provider.name} detail={retrievedAt} /><Item label="Risk model" value={analysis.ml_prediction.model_version} detail={analysis.ml_prediction.target} /><Item label="Explanation" value={analysis.explanation?.source ?? "Unavailable"} detail="Evidence-constrained output" /></div></section>;
}

function Item({ label, value, detail, fresh }: { label: string; value: string; detail: string; fresh?: boolean }) { return <div><span>{label}</span><b>{fresh && <i className="status-dot fresh" />}{value}</b><small>{detail}</small></div>; }
