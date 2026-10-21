from typing import Optional

from pydantic import BaseModel, Field


class SimulationInput(BaseModel):
    vehicles: int = Field(default=6500, ge=0, le=100000)
    industrial_emissions: float = Field(default=55, ge=0, le=100)
    construction_dust: float = Field(default=30, ge=0, le=100)
    population_density: float = Field(default=55, ge=0, le=100)
    green_cover: float = Field(default=24, ge=0, le=100)
    trees: int = Field(default=12000, ge=0, le=1000000)
    wind_speed: float = Field(default=8, ge=0, le=80)
    wind_direction: float = Field(default=225, ge=0, le=360)
    rainfall: float = Field(default=0, ge=0, le=100)
    traffic_restrictions: float = Field(default=0, ge=0, le=100)
    industrial_control: float = Field(default=10, ge=0, le=100)
    public_transport: float = Field(default=35, ge=0, le=100)


class ScenarioChange(BaseModel):
    name: str = Field(min_length=1, max_length=80)
    vehicles: Optional[int] = Field(default=None, ge=0, le=100000)
    industrial_emissions: Optional[float] = Field(default=None, ge=0, le=100)
    construction_dust: Optional[float] = Field(default=None, ge=0, le=100)
    population_density: Optional[float] = Field(default=None, ge=0, le=100)
    green_cover: Optional[float] = Field(default=None, ge=0, le=100)
    trees: Optional[int] = Field(default=None, ge=0, le=1000000)
    wind_speed: Optional[float] = Field(default=None, ge=0, le=80)
    wind_direction: Optional[float] = Field(default=None, ge=0, le=360)
    rainfall: Optional[float] = Field(default=None, ge=0, le=100)
    traffic_restrictions: Optional[float] = Field(default=None, ge=0, le=100)
    industrial_control: Optional[float] = Field(default=None, ge=0, le=100)
    public_transport: Optional[float] = Field(default=None, ge=0, le=100)


class ScenarioCompareRequest(BaseModel):
    baseline: SimulationInput = Field(default_factory=SimulationInput)
    scenarios: list[ScenarioChange] = Field(min_length=1, max_length=8)


class QuizSubmission(BaseModel):
    answers: list[int] = Field(min_length=1, max_length=10)
