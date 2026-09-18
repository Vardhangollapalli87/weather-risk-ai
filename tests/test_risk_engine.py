import pytest

from app.risk.engine import assess_risk, rainfall_indicator


@pytest.mark.parametrize(("rainfall", "expected"), [(0, 0), (2, 20), (10, 50), (20, 80), (40, 100)])
def test_rainfall_indicator_boundaries(rainfall: float, expected: float) -> None:
    assert rainfall_indicator(rainfall)[0] == expected


def test_score_boundaries_low_moderate_high() -> None:
    # Score equals 0.45 * ML probability when all deterministic indicators are zero.
    assert assess_risk(34.99 / 45, 0, 0, 0).level == "Low"
    assert assess_risk(35 / 45, 0, 0, 0).level == "Moderate"
    assert assess_risk(1.0, 0, 100, 10).level == "High"  # 45 + 15 + 5 = 65


def test_risk_is_deterministic_and_factors_are_ranked() -> None:
    first = assess_risk(0.8, 21, 70, 5)
    second = assess_risk(0.8, 21, 70, 5)
    assert first == second
    assert [factor.indicator for factor in first.factors] == sorted([factor.indicator for factor in first.factors], reverse=True)
    assert first.score == 72.5
