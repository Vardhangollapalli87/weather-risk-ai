from fastapi.testclient import TestClient

from app.agent.graph import WeatherRiskAgent
from app.main import app
from tests.test_agent_graph import FakeAnalysisService, sample_weather


def test_analysis_api_includes_template_explanation() -> None:
    with TestClient(app) as client:
        app.state.weather_risk_agent = WeatherRiskAgent(FakeAnalysisService(sample_weather()))
        response = client.post("/analysis", json={"latitude": 17.385, "longitude": 78.4867, "location_name": "Hyderabad"})
    assert response.status_code == 200
    body = response.json()
    assert body["explanation"]["source"] == "template"
    assert body["explanation"]["disclaimer"] == "This is decision support, not an official warning or flood prediction."
    assert body["risk"]["score"] == 77.0
