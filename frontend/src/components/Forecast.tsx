import type { HourlyWeather } from "../types";

const formatHour = (time: string, timezone: string) => new Intl.DateTimeFormat(undefined, { timeZone: timezone, hour: "numeric", hour12: true }).format(new Date(time));
const formatWindow = (time: string, timezone: string) => `${formatHour(time, timezone)}–${formatHour(new Date(new Date(time).getTime() + 3_600_000).toISOString(), timezone)}`;

export default function Forecast({ hours, timezone, expectedRainfall }: { hours: HourlyWeather[]; timezone: string; expectedRainfall: number }) {
  const maximum = Math.max(...hours.map(hour => hour.precipitation_mm ?? 0), 0.1);
  const peak = hours.reduce((highest, hour) => (hour.precipitation_mm ?? 0) > (highest.precipitation_mm ?? 0) ? hour : highest, hours[0]);
  const chartWidth = 720;
  const chartHeight = 190;
  const baseline = 154;
  const step = chartWidth / Math.max(hours.length, 1);
  const line = hours.map((hour, index) => `${(index + .5) * step},${baseline - ((hour.precipitation_probability_percent ?? 0) / 100) * 112}`).join(" ");
  return <section className="forecast-panel"><div className="section-heading"><div><p className="eyebrow">Rainfall outlook</p><h2>Next 24 hours</h2></div><span className="muted">Local time · {timezone}</span></div><div className="forecast-summary"><span>Expected rainfall <b>{expectedRainfall.toFixed(1)} mm</b></span><span>Peak rainfall <b>{peak ? formatWindow(peak.time, timezone) : "—"}</b></span></div><div className="timeline" role="img" aria-label={`24-hour rainfall timeline. Expected rainfall ${expectedRainfall.toFixed(1)} millimetres. Peak window ${peak ? formatWindow(peak.time, timezone) : "unavailable"}.`}><svg viewBox={`0 0 ${chartWidth} ${chartHeight}`} preserveAspectRatio="none" aria-hidden="true"><line x1="0" x2={chartWidth} y1={baseline} y2={baseline} className="timeline-axis" />{hours.map((hour, index) => { const rain = hour.precipitation_mm ?? 0; const height = (rain / maximum) * 112; return <rect key={hour.time} x={index * step + 3} y={baseline - height} width={Math.max(step - 6, 2)} height={height} rx="2" className={hour === peak ? "rain-bar peak" : "rain-bar"} />; })}<polyline points={line} className="probability-line" /></svg><div className="timeline-legend"><span><i className="rain-key" /> Rainfall (mm)</span><span><i className="chance-key" /> Rain probability</span></div></div><div className="forecast-scroll">{hours.map((hour, index) => <article className={`hour-card ${index === 0 ? "next-hour" : ""}`} key={hour.time}><b>{index === 0 ? "Next" : formatHour(hour.time, timezone)}</b><span className={`hour-weather ${weatherTone(hour)}`} aria-hidden="true" /><strong>{hour.temperature_c?.toFixed(0) ?? "—"}°</strong><small>{hour.precipitation_mm?.toFixed(1) ?? "—"} mm</small><small>{hour.precipitation_probability_percent?.toFixed(0) ?? "—"}% chance</small></article>)}</div></section>;
}

function weatherTone(hour: HourlyWeather) { return (hour.precipitation_mm ?? 0) > 0 || (hour.precipitation_probability_percent ?? 0) > 50 ? "rain" : "cloud"; }
