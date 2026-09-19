import type { ReactNode } from "react";

export default function ProductHero({ children }: { children: ReactNode }) {
  return <section className="product-hero"><div className="hero-orb hero-orb-one" /><div className="hero-orb hero-orb-two" /><header className="product-header"><div className="brand"><span className="brand-mark" aria-hidden="true"><i /><i /><i /></span><div><h1>WeatherRisk <em>AI</em></h1><p>Real-time rainfall risk intelligence</p></div></div><span className="public-badge">Decision support</span></header><div className="hero-copy"><p className="hero-kicker">Environmental intelligence platform</p><h2>Weather-aware decisions,<br />grounded in evidence.</h2><p>Live weather data, machine learning and deterministic risk analysis for the next 24 hours.</p></div><div className="hero-search">{children}</div><div className="hero-horizon" aria-hidden="true"><i /><i /><i /></div></section>;
}
