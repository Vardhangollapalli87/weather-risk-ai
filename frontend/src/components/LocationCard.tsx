import type { Analysis, ReverseLocation } from "../types";

export default function LocationCard({ analysis, deviceLocation, onRefresh }: { analysis: Analysis; deviceLocation: ReverseLocation | null; onRefresh: () => void }) {
  const location = analysis.weather.location;
  const isDevice = deviceLocation !== null;
  const manualTitle = [analysis.location_name ?? location.name, location.country].filter((part, index, parts) => Boolean(part) && parts.indexOf(part) === index && !(analysis.location_name ?? location.name).includes(part ?? "")).join(", ") || location.name;
  const title = deviceLocation?.name ?? manualTitle;
  const subtitle = deviceLocation ? [deviceLocation.city, deviceLocation.state, deviceLocation.country].filter(Boolean).filter(part => part !== deviceLocation.name).join(", ") : "Selected location";
  const age = Math.round(analysis.weather.freshness.age_minutes);
  return <section className="location-card"><div className="location-pin" aria-hidden="true" /><div className="location-copy"><p className="eyebrow">{isDevice ? "Current device location" : "Analysis location"}</p><h2>{title}</h2>{subtitle && <p>{subtitle}</p>}<small>{isDevice ? `${location.latitude.toFixed(4)}° N, ${location.longitude.toFixed(4)}° E` : "Live point-location analysis"}</small></div><div className="location-status"><span><i className={`status-dot ${analysis.weather.freshness.status}`} />{analysis.weather.freshness.status === "fresh" ? "Fresh data" : "Stale data"}</span><small>Updated {age} min ago</small></div><button className="refresh-button" onClick={onRefresh}><span aria-hidden="true">↻</span> Refresh</button></section>;
}
