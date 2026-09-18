import re
from typing import Protocol

from app.agent.evidence import Evidence
from app.models.analysis import Explanation

DISCLAIMER = "This is decision support, not an official warning or flood prediction."


class ExplanationProvider(Protocol):
    def generate(self, evidence: Evidence) -> Explanation: ...


def template_explanation(evidence: Evidence) -> Explanation:
    probability = round(evidence.ml_probability * 100, 1)
    return Explanation(summary=f"{evidence.risk_level} significant-rainfall risk for the next 24 hours.", why_this_risk=[f"The deterministic risk score is {evidence.risk_score:.1f} ({evidence.risk_level}).", f"Forecast precipitation over the next 24 hours is {evidence.forecast_24h_rain_mm:.1f} mm.", f"The ML model estimates a {probability:.1f}% probability of reaching 20 mm in the next 24 hours."], key_factors=evidence.factors[:3], what_to_watch=[f"Maximum hourly precipitation probability is {evidence.max_hourly_precipitation_probability_percent:.0f}%.", f"Recent 24-hour precipitation is {evidence.recent_24h_rain_mm:.1f} mm.", "Monitor changes in the hourly forecast."], disclaimer=DISCLAIMER, source="template")


def validate_explanation(explanation: Explanation, evidence: Evidence) -> None:
    fields = [explanation.summary, *explanation.why_this_risk, *explanation.key_factors, *explanation.what_to_watch]
    if not all(field.strip() for field in [explanation.summary, explanation.disclaimer]) or not any(field.strip() for field in explanation.why_this_risk):
        raise ValueError("Explanation has required empty fields")
    text = " ".join([*fields, explanation.disclaimer]).lower()
    factual_text = " ".join(fields).lower()
    if any(term in factual_text for term in ("flood", "official warning", "emergency")):
        raise ValueError("Explanation contains an unsupported safety claim")
    if explanation.disclaimer != DISCLAIMER:
        raise ValueError("Explanation disclaimer does not match the required safety disclaimer")
    levels = {"low", "moderate", "high"}
    mentioned = levels.intersection(set(re.findall(r"\b(?:low|moderate|high)\b", text)))
    if mentioned and mentioned != {evidence.risk_level.lower()}:
        raise ValueError("Explanation risk level conflicts with deterministic risk")
    allowed = {"20", "24", "0", "1"}
    for number in [evidence.risk_score, evidence.forecast_24h_rain_mm, evidence.recent_24h_rain_mm, evidence.max_hourly_precipitation_probability_percent, evidence.ml_probability * 100, evidence.current_temperature_c]:
        if number is not None:
            allowed.update({str(round(float(number), 1)), str(round(float(number))), str(float(number))})
    for token in re.findall(r"\b\d+(?:\.\d+)?\b", text):
        if token not in allowed:
            raise ValueError("Explanation includes an unsupported numerical value")
