from typing import Annotated

from fastapi import APIRouter, Depends, Request

from app.models.analysis import AnalysisRequest, AnalysisResponse
from app.agent.graph import WeatherRiskAgent

router = APIRouter(tags=["analysis"])


def analysis_service(request: Request) -> WeatherRiskAgent:
    return request.app.state.weather_risk_agent


@router.post("/analysis", response_model=AnalysisResponse)
async def analysis(payload: AnalysisRequest, service: Annotated[WeatherRiskAgent, Depends(analysis_service)]) -> AnalysisResponse:
    return await service.invoke(payload.latitude, payload.longitude, payload.location_name)
