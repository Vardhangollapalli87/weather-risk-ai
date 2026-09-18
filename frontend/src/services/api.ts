import type { Analysis, Location } from "../types";

const baseUrl = import.meta.env.VITE_API_BASE_URL ?? "http://localhost:8000";

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response;
  try { response = await fetch(`${baseUrl}${path}`, init); } catch (error) { if ((error as DOMException).name === "AbortError") throw error; throw new Error("Unable to reach the WeatherRisk AI backend. Please try again."); }
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(body?.error?.message ?? "The request could not be completed.");
  return body as T;
}

export const searchLocations = (query: string, signal?: AbortSignal) => request<Location[]>(`/locations?query=${encodeURIComponent(query)}`, { signal });
export const getAnalysis = (location: Location, signal?: AbortSignal) => request<Analysis>("/analysis", { method: "POST", headers: { "Content-Type": "application/json" }, signal, body: JSON.stringify({ latitude: location.latitude, longitude: location.longitude, location_name: [location.name, location.admin1].filter(Boolean).join(", ") }) });
