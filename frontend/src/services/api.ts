import type { Analysis, Location, ReverseLocation } from "../types";

const baseUrl = import.meta.env.VITE_API_BASE_URL?.replace(/\/$/, "");

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  if (!baseUrl) throw new Error("WeatherRisk AI is missing its backend URL configuration.");
  let response: Response;
  try { response = await fetch(`${baseUrl}${path}`, init); } catch (error) { if ((error as DOMException).name === "AbortError") throw error; throw new Error("Unable to reach the WeatherRisk AI backend. Please try again."); }
  const body = await response.json().catch(() => null);
  if (!response.ok) throw new Error(body?.error?.message ?? "The request could not be completed.");
  return body as T;
}

export const searchLocations = (query: string, signal?: AbortSignal) => request<Location[]>(`/locations?query=${encodeURIComponent(query)}`, { signal });
export const reverseLocation = (latitude: number, longitude: number, signal?: AbortSignal) => request<ReverseLocation>(`/locations/reverse?latitude=${encodeURIComponent(latitude)}&longitude=${encodeURIComponent(longitude)}`, { signal });
export const getAnalysis = (location: Location, signal?: AbortSignal) => request<Analysis>("/analysis", { method: "POST", headers: { "Content-Type": "application/json" }, signal, body: JSON.stringify({ latitude: location.latitude, longitude: location.longitude, location_name: [location.name, location.admin1].filter(Boolean).join(", ") }) });
