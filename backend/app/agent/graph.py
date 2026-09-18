from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agent.evidence import Evidence, build_evidence
from app.agent.explanation import ExplanationProvider, template_explanation, validate_explanation
from app.models.analysis import AnalysisResponse, Explanation
from app.models.weather import WeatherSnapshot
from app.services.analysis_service import AnalysisService


class AgentState(TypedDict, total=False):
    latitude: float
    longitude: float
    location_name: str | None
    weather: WeatherSnapshot
    analysis: AnalysisResponse
    evidence: Evidence
    explanation: Explanation
    error: str
    use_template: bool


class WeatherRiskAgent:
    def __init__(self, analysis_service: AnalysisService, explanation_provider: ExplanationProvider | None = None) -> None:
        self.analysis_service = analysis_service
        self.explanation_provider = explanation_provider
        graph = StateGraph(AgentState)
        graph.add_node("validate_request", self.validate_request)
        graph.add_node("retrieve_weather", self.retrieve_weather)
        graph.add_node("run_analysis", self.run_analysis)
        graph.add_node("assemble_evidence", self.assemble_evidence)
        graph.add_node("generate_explanation", self.generate_explanation)
        graph.add_node("template_explanation", self.template_explanation)
        graph.add_node("validate_explanation", self.validate_explanation)
        graph.add_edge(START, "validate_request")
        graph.add_edge("validate_request", "retrieve_weather")
        graph.add_edge("retrieve_weather", "run_analysis")
        graph.add_edge("run_analysis", "assemble_evidence")
        graph.add_conditional_edges("assemble_evidence", self.route_explanation, {"provider": "generate_explanation", "template": "template_explanation"})
        graph.add_edge("generate_explanation", "validate_explanation")
        graph.add_conditional_edges("validate_explanation", self.route_validation, {"done": END, "template": "template_explanation"})
        graph.add_edge("template_explanation", END)
        self.graph = graph.compile()

    def validate_request(self, state: AgentState) -> AgentState:
        if not -90 <= state["latitude"] <= 90 or not -180 <= state["longitude"] <= 180:
            raise ValueError("Coordinates are invalid")
        return state

    async def retrieve_weather(self, state: AgentState) -> AgentState:
        state["weather"] = await self.analysis_service.weather_service.get_weather(state["latitude"], state["longitude"])
        return state

    def run_analysis(self, state: AgentState) -> AgentState:
        state["analysis"] = self.analysis_service.analyze_weather(state["weather"], state.get("location_name"))
        return state

    def assemble_evidence(self, state: AgentState) -> AgentState:
        state["evidence"] = build_evidence(state["analysis"])
        return state

    def route_explanation(self, state: AgentState) -> str:
        return "provider" if self.explanation_provider else "template"

    def generate_explanation(self, state: AgentState) -> AgentState:
        try:
            state["explanation"] = self.explanation_provider.generate(state["evidence"])  # type: ignore[union-attr]
        except Exception:
            state["use_template"] = True
        return state

    def template_explanation(self, state: AgentState) -> AgentState:
        state["explanation"] = template_explanation(state["evidence"])
        return state

    def validate_explanation(self, state: AgentState) -> AgentState:
        if state.get("use_template"):
            return state
        try:
            validate_explanation(state["explanation"], state["evidence"])
        except Exception:
            state["use_template"] = True
        return state

    def route_validation(self, state: AgentState) -> str:
        return "template" if state.get("use_template") else "done"

    async def invoke(self, latitude: float, longitude: float, location_name: str | None = None) -> AnalysisResponse:
        final = await self.graph.ainvoke({"latitude": latitude, "longitude": longitude, "location_name": location_name})
        result = final["analysis"]
        return result.model_copy(update={"explanation": final["explanation"]})
