import { useRef, useState } from "react";
import SearchPanel from "./components/SearchPanel";
import RiskCard from "./components/RiskCard";
import RiskFactors from "./components/RiskFactors";
import Forecast from "./components/Forecast";
import Explanation from "./components/Explanation";
import { getAnalysis, reverseLocation, searchLocations } from "./services/api";
import type { Analysis, Location, ReverseLocation } from "./types";

const value = (number: number | null, unit: string, digits = 0) => number === null ? "—" : `${number.toFixed(digits)}${unit}`;

function App() {
  const [query, setQuery] = useState("");
  const [results, setResults] = useState<Location[]>([]);
  const [analysis, setAnalysis] = useState<Analysis | null>(null);
  const [deviceLocation, setDeviceLocation] = useState<ReverseLocation | null>(null);
  const [loadingSearch, setLoadingSearch] = useState(false);
  const [loadingAnalysis, setLoadingAnalysis] = useState(false);
  const [locating, setLocating] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searchMessage, setSearchMessage] = useState<string | null>(null);
  const searchRequest = useRef<AbortController | null>(null);
  const analysisRequest = useRef<AbortController | null>(null);
  const locationIdentityRequest = useRef(0);

  const search = async () => {
    const trimmed = query.trim();
    if (!trimmed) return;
    searchRequest.current?.abort();
    const controller = new AbortController();
    searchRequest.current = controller;
    setLoadingSearch(true); setError(null); setSearchMessage(null);
    try {
      const locations = await searchLocations(trimmed, controller.signal);
      if (searchRequest.current !== controller) return;
      setResults(locations);
      if (!locations.length) setSearchMessage("No matching locations found. Try a city or place name.");
    } catch (err) {
      if ((err as DOMException).name !== "AbortError") setError("Unable to search locations right now. Please try again.");
    } finally { if (searchRequest.current === controller) setLoadingSearch(false); }
  };

  const select = async (location: Location, currentDeviceLocation: ReverseLocation | null = null) => {
    locationIdentityRequest.current += 1;
    analysisRequest.current?.abort();
    const controller = new AbortController();
    analysisRequest.current = controller;
    setResults([]); setLoadingAnalysis(true); setError(null); setDeviceLocation(currentDeviceLocation);
    try {
      const result = await getAnalysis(location, controller.signal);
      if (analysisRequest.current === controller) setAnalysis(result);
    } catch (err) {
      if ((err as DOMException).name !== "AbortError") setError("Unable to analyze this location. We couldn't retrieve the latest weather data.");
    } finally { if (analysisRequest.current === controller) setLoadingAnalysis(false); }
  };

  const useMyLocation = () => {
    if (!navigator.geolocation) { setError("Location services are unavailable in this browser. Search for a city instead."); return; }
    const requestId = locationIdentityRequest.current + 1;
    locationIdentityRequest.current = requestId;
    setError(null); setLocating(true);
    navigator.geolocation.getCurrentPosition(async position => {
      try {
        const identity = await reverseLocation(position.coords.latitude, position.coords.longitude);
        if (locationIdentityRequest.current !== requestId) return;
        setLocating(false);
        await select({ id: null, name: identity.display_name, country: identity.country, admin1: identity.state, latitude: position.coords.latitude, longitude: position.coords.longitude, timezone: null }, identity);
      } catch {
        if (locationIdentityRequest.current !== requestId) return;
        setLocating(false);
        await select({ id: null, name: "Current device location", country: null, admin1: null, latitude: position.coords.latitude, longitude: position.coords.longitude, timezone: null });
      }
    }, geoError => {
      setLocating(false);
      const message = geoError.code === geoError.PERMISSION_DENIED ? "Location permission was denied. Search for a city instead." : geoError.code === geoError.TIMEOUT ? "Getting your location timed out. Please try again or search for a city." : "Your location could not be determined. Search for a city instead.";
      setError(message);
    }, { enableHighAccuracy: false, timeout: 10_000, maximumAge: 300_000 });
  };

  return <main><header><div className="brand-mark" aria-hidden="true">WR</div><div><h1>WeatherRisk <em>AI</em></h1><p>Real-time rainfall risk intelligence</p></div><p className="header-description">Decision support powered by live weather data, machine learning and deterministic risk analysis.</p><span className="public-badge">Decision support</span></header><div className="container"><SearchPanel query={query} results={results} loading={loadingSearch} locating={locating} error={error} onQueryChange={setQuery} onSearch={search} onSelect={location => void select(location)} onUseMyLocation={useMyLocation} />{searchMessage && <p className="notice" role="status">{searchMessage}</p>}{loadingAnalysis && <LoadingState />}{error && analysis && <section className="error-card" role="alert"><div><p className="eyebrow">Analysis unavailable</p><h2>Unable to analyze this location</h2><p>{error}</p></div><button onClick={() => void select(analysis.weather.location, deviceLocation)}>Try again</button></section>}{!analysis && !loadingAnalysis && <section className="empty-state"><p className="eyebrow">Environmental intelligence</p><h2>Choose a location to begin.</h2><p>Search for a city or use your current location to generate a live rainfall-risk assessment.</p></section>}{analysis && <Dashboard analysis={analysis} deviceLocation={deviceLocation} retry={() => void select(analysis.weather.location, deviceLocation)} />}</div></main>;
}

function LoadingState() { return <section className="loading-card" aria-live="polite"><div className="spinner" /><div><p className="eyebrow">Analyzing location</p><h2>Building your rainfall outlook</h2><p>Retrieving current weather · calculating risk assessment · assembling evidence</p></div></section>; }

function Dashboard({ analysis, deviceLocation, retry }: { analysis: Analysis; deviceLocation: ReverseLocation | null; retry: () => void }) {
  const weather = analysis.weather;
  const location = weather.location;
  const isCurrentDevice = deviceLocation !== null;
  const manualTitle = [analysis.location_name ?? location.name, location.country].filter((part, index, parts) => Boolean(part) && parts.indexOf(part) === index && !(analysis.location_name ?? location.name).includes(part ?? "")).join(", ") || location.name;
  const locationTitle = deviceLocation?.name ?? manualTitle;
  const locationDetails = deviceLocation ? [deviceLocation.city, deviceLocation.state, deviceLocation.country].filter(Boolean).filter(part => part !== deviceLocation.name).join(", ") : "Selected location";
  const retrievedAt = new Intl.DateTimeFormat(undefined, { dateStyle: "medium", timeStyle: "short", timeZone: weather.timezone }).format(new Date(weather.retrieved_at));
  return <><section className="location-bar"><div><p className="eyebrow">{isCurrentDevice ? "Current device location" : "Selected location"}</p><h2><span aria-hidden="true">⌖</span> {locationTitle}</h2>{locationDetails && <p>{locationDetails}</p>}<small><i className={`status-dot ${weather.freshness.status}`} />{weather.freshness.status === "fresh" ? "Fresh data" : "Stale data"} · Updated {Math.round(weather.freshness.age_minutes)} min ago</small></div><button className="text-button" onClick={retry}>Refresh analysis</button></section><div className="dashboard-grid"><RiskCard analysis={analysis} /><section className="panel current"><div className="section-heading"><div><p className="eyebrow">Current conditions</p><h2>Latest provider update</h2></div></div><div className="metric-grid"><Metric label="Temperature" value={value(weather.current.temperature_c, "°C")} /><Metric label="Humidity" value={value(weather.current.relative_humidity_percent, "%")} /><Metric label="Wind" value={value(weather.current.wind_speed_kmh, " km/h")} /><Metric label="Cloud cover" value={value(weather.current.cloud_cover_percent, "%")} /></div></section></div><RiskFactors analysis={analysis} /><Forecast hours={weather.hourly_forecast} timezone={weather.timezone} expectedRainfall={weather.rainfall.forecast_next_24h_mm} /><div className="lower-grid"><Explanation analysis={analysis} /><section className="panel data-info"><p className="eyebrow">Data & provenance</p><h2>Verified inputs</h2><div className="provenance-list"><div><span>Data status</span><b><i className={`status-dot ${weather.freshness.status}`} />{weather.freshness.status === "fresh" ? "Fresh data" : "Stale data"}</b><small>Updated {Math.round(weather.freshness.age_minutes)} min ago</small></div><div><span>Weather source</span><b>{weather.provider.name}</b><small>Retrieved {retrievedAt}</small></div><div><span>Risk model</span><b>{analysis.ml_prediction.model_version}</b><small>{analysis.ml_prediction.target}</small></div><div><span>Explanation</span><b>{analysis.explanation?.source ?? "Unavailable"}</b><small>Evidence-constrained output</small></div></div></section></div></>;
}

function Metric({ label, value }: { label: string; value: string }) { return <div className="metric"><b>{value}</b><span>{label}</span></div>; }
export default App;
