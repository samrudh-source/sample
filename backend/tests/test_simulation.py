from app.schemas import SimulationInput
from app.simulation import simulate


def test_more_controls_reduce_simulated_pm25():
    baseline = simulate(SimulationInput())
    eco = simulate(SimulationInput(traffic_restrictions=70, industrial_control=80, public_transport=75, green_cover=60))
    assert eco["pm25"] < baseline["pm25"]
    assert eco["data_status"] == "simulated"
    assert len(eco["forecast_24h"]) == 24


def test_simulation_reports_assumptions_and_bounded_outputs():
    result = simulate(SimulationInput(vehicles=0, wind_speed=80, rainfall=100))
    assert result["pm25"] >= 2
    assert result["index"] <= 500
    assert result["assumptions"]


def test_input_limits_are_validated():
    import pytest
    from pydantic import ValidationError

    with pytest.raises(ValidationError):
        SimulationInput(vehicles=-1)