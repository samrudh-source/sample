import json
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Query, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .schemas import QuizSubmission, ScenarioCompareRequest, SimulationInput
from .services.environment import fetch_environment
from .services.store import initialize, record_snapshot
from .simulation import simulate


FACTS = [
    {"category": "Air", "title": "Fine particles travel deep", "body": "PM2.5 particles are small enough to reach deep into the lungs. Open-Meteo provides modeled/reanalysis-backed estimates, not a neighborhood sensor reading.", "source": "WHO air quality guidance; Open-Meteo metadata"},
    {"category": "Water", "title": "Dissolved oxygen matters", "body": "Aquatic organisms depend on dissolved oxygen. This demo does not have a connected water-quality feed, so it does not report local water measurements.", "source": "USGS Water Science School"},
    {"category": "Soil", "title": "Soil supports urban resilience", "body": "Healthy urban soils retain water and support vegetation. Soil contamination requires site sampling; citywide values cannot be inferred from air data.", "source": "FAO soil resources"},
    {"category": "Noise", "title": "Exposure depends on time", "body": "Sound exposure is commonly described in dB(A), but duration and context matter. This platform's noise values are scenario estimates only.", "source": "WHO Environmental Noise Guidelines"},
]
QUIZ = [
    {"question": "Which statement best describes the map marker?", "options": ["A government sensor", "The selected queried location, not a sensor", "A predicted pollution hotspot"]},
    {"question": "Which AQI scales are returned by Open-Meteo?", "options": ["US and European AQI, separately labeled", "Indian AQI only", "A universal AQI"]},
    {"question": "How should the simulation be interpreted?", "options": ["An official forecast", "A simplified, illustrative scenario", "A health diagnosis"]},
]
QUIZ_ANSWERS = [1, 0, 1]


@asynccontextmanager
async def lifespan(_: FastAPI):
    initialize()
    yield


app = FastAPI(title="EcoVision API", version="1.0.0", lifespan=lifespan)
origins = os.getenv("FRONTEND_ORIGIN", "http://localhost:5173").split(",")
app.add_middleware(CORSMiddleware, allow_origins=origins, allow_credentials=False, allow_methods=["GET", "POST"], allow_headers=["*"])


@app.exception_handler(RequestValidationError)
async def validation_error_handler(_: Request, error: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": {"code": "validation_error", "details": error.errors()}})


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "ecovision-api"}


@app.get("/api/air-quality")
async def air_quality(city: str = Query(default="New Delhi", min_length=2, max_length=80), latitude: float | None = Query(default=None, ge=-90, le=90), longitude: float | None = Query(default=None, ge=-180, le=180)):
    if (latitude is None) != (longitude is None):
        raise HTTPException(status_code=422, detail={"code": "coordinate_pair_required", "message": "Provide both latitude and longitude."})
    result = await fetch_environment(city, latitude, longitude)
    record_snapshot(result["city"], json.dumps({"aqi": result["aqi"], "pollutants": result["pollutants"]}))
    return result


@app.get("/api/environmental-summary")
async def environmental_summary(city: str = Query(default="New Delhi", min_length=2, max_length=80)):
    return await fetch_environment(city)


@app.get("/api/pollution-history")
async def pollution_history(city: str = Query(default="New Delhi", min_length=2, max_length=80)):
    result = await fetch_environment(city)
    hourly = result["hourly"]
    points = [
        {"time": timestamp, "pm25": pm25, "pm10": pm10, "us_aqi": aqi}
        for timestamp, pm25, pm10, aqi in zip(hourly.get("time", []), hourly.get("pm2_5", []), hourly.get("pm10", []), hourly.get("us_aqi", []))
        if pm25 is not None or pm10 is not None
    ]
    return {"status": "live", "city": result["city"], "source": result["source"], "points": points, "data_status": "Open-Meteo hourly history and forecast"}


@app.post("/api/simulate")
def simulate_endpoint(inputs: SimulationInput):
    return simulate(inputs)


@app.post("/api/scenarios/compare")
def compare_scenarios(request: ScenarioCompareRequest):
    baseline = simulate(request.baseline)
    comparisons = []
    for scenario in request.scenarios:
        changes = scenario.model_dump(exclude={"name"}, exclude_none=True)
        variant = SimulationInput(**{**request.baseline.model_dump(), **changes})
        result = simulate(variant)
        comparisons.append({"name": scenario.name, "result": result, "pm25_change": round(result["pm25"] - baseline["pm25"], 1), "index_change": result["index"] - baseline["index"]})
    return {"baseline": baseline, "comparisons": comparisons}


@app.get("/api/awareness/facts")
def awareness_facts():
    return {"facts": FACTS}


@app.get("/api/awareness/quiz")
def awareness_quiz():
    return {"questions": QUIZ}


@app.post("/api/awareness/quiz/submit")
def submit_quiz(submission: QuizSubmission):
    correct = sum(index < len(QUIZ_ANSWERS) and answer == QUIZ_ANSWERS[index] for index, answer in enumerate(submission.answers))
    return {"score": correct, "total": len(QUIZ_ANSWERS), "complete": len(submission.answers) == len(QUIZ_ANSWERS)}