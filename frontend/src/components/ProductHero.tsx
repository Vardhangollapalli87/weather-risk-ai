import type { ReactNode } from "react";
import type { Analysis, ReverseLocation } from "../types";

export default function ProductHero({ children, analysis, deviceLocation }: { children: ReactNode; analysis: Analysis | null; deviceLocation: ReverseLocation | null }) {
  const location = analysis?.weather.location;
  const title = deviceLocation?.display_name ?? analysis?.location_name ?? location?.name;
  const subtitle = deviceLocation ? "" : [location?.admin1, location?.country].filter(Boolean).join(", ");
  const temperature = analysis?.weather.current.temperature_c;
  const cloud = analysis?.weather.current.cloud_cover_percent;
  const rain = analysis?.weather.current.precipitation_mm;
  const weatherState = rain && rain > 0 ? "rain" : cloud && cloud > 65 ? "cloud" : "sun";
  return <section className={`product-hero ${weatherState}`}><div className="cloud cloud-one" /><div className="cloud cloud-two" /><header className="product-header"><div className="brand"><span className="brand-mark" aria-hidden="true"><i /><i /><i /></span><span>WeatherRisk <em>AI</em></span></div><span className="hero-status">Live decision support</span></header>{analysis ? <div className="weather-hero"><div className="weather-location"><p>{deviceLocation ? "Current location" : "Selected location"}</p><h1>{title}</h1><span className="place-line"><i aria-hidden="true" />{subtitle || "Live point-location analysis"}</span></div><div className="weather-primary"><span className={`weather-illustration ${weatherState}`} aria-hidden="true" /><strong>{temperature == null ? "—" : `${temperature.toFixed(0)}°`}</strong><p>Live provider update</p></div><div className="weather-glance"><span>Humidity <b>{analysis.weather.current.relative_humidity_percent ?? "—"}%</b></span><span>Wind <b>{analysis.weather.current.wind_speed_kmh ?? "—"} km/h</b></span><span>Cloud cover <b>{analysis.weather.current.cloud_cover_percent ?? "—"}%</b></span></div></div> : <div className="hero-copy"><p>Rainfall risk intelligence</p><h1>Weather-aware decisions,<br />grounded in evidence.</h1><span>Live weather data, machine learning and deterministic risk analysis for the next 24 hours.</span></div>}<div className="hero-search">{children}</div></section>;
}
