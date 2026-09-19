import type { Analysis } from "../types";

const value = (number: number | null, unit: string, digits = 0) => number === null ? "—" : `${number.toFixed(digits)}${unit}`;

export default function CurrentConditions({ analysis }: { analysis: Analysis }) {
  const weather = analysis.weather;
  const icon = weather.current.precipitation_mm && weather.current.precipitation_mm > 0 ? "rain" : weather.current.cloud_cover_percent && weather.current.cloud_cover_percent > 65 ? "cloud" : "sun";
  return <section className="conditions-card"><div className="section-heading"><div><p className="eyebrow">Current conditions</p><h2>Live weather snapshot</h2></div><span className={`weather-symbol ${icon}`} aria-label={icon === "rain" ? "Rain conditions" : icon === "cloud" ? "Cloudy conditions" : "Clear conditions"} /></div><div className="temperature"><b>{value(weather.current.temperature_c, "°C")}</b><span>Latest provider update</span></div><div className="condition-grid"><Metric label="Humidity" value={value(weather.current.relative_humidity_percent, "%")} /><Metric label="Wind" value={value(weather.current.wind_speed_kmh, " km/h")} /><Metric label="Cloud cover" value={value(weather.current.cloud_cover_percent, "%")} /><Metric label="Recent rain" value={value(weather.rainfall.recent_24h_mm, " mm", 1)} /></div></section>;
}

function Metric({ label, value }: { label: string; value: string }) { return <div><b>{value}</b><span>{label}</span></div>; }
