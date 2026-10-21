# EcoVision

EcoVision is an environmental monitoring and learning dashboard with live air-quality data, an explicitly illustrative pollution simulator, policy comparisons, and an OpenStreetMap location view. It does not claim to have local water, soil, or noise sensors.

## Project Links

- Application: ecovision-c4umkiwfg-samrudh-ns-projects.vercel.app (available when running locally; no public deployment is configured yet)
- API documentation:  https://ecovision-api-6jve.onrender.com (available when the backend is running)
- Source repository: [github.com/samrudh-source/sample](https://github.com/samrudh-source/sample)

## What EcoVision Includes

- Environmental dashboard with Open-Meteo air-quality and weather data, pollutant units, source labels, and timestamps.
- Separate US and European AQI values, with no conversion or claim that either is Indian National AQI.
- City search, optional browser geolocation, hourly particulate trends, and an OpenStreetMap view of the queried location.
- Interactive air-pollution model with traffic, industry, dust, vegetation, weather, and policy controls; Normal and Eco modes; animated city scene; 24-hour illustrative trends; and source contributions.
- What-if policy comparison for traffic, transit, industry, construction dust, green cover, and combined interventions.
- Air, water, soil, and noise learning content, a short data-literacy quiz, and an assumption-based tree impact calculator.
- FastAPI service with input validation, API caching, SQLite snapshot storage, and structured errors.

The simulator is an educational scenario tool, not an atmospheric forecast, official air-quality index, exposure estimate, or health diagnosis. Details and equations are documented in [docs/simulation-model.md](docs/simulation-model.md).

## Architecture

- `frontend/`: React, TypeScript, and Vite interface; Recharts visualizations; Leaflet/OpenStreetMap map.
- `backend/app/`: FastAPI endpoints, Open-Meteo integration, Pydantic schemas, and simulation calculations.
- `backend/app/services/store.py`: SQLite snapshot persistence, isolated so it can be replaced with PostgreSQL for a multi-instance deployment.
- `backend/tests/` and `frontend/src/App.test.tsx`: backend API/model tests and a frontend unavailable-data test.

## Requirements

- Node.js 20 or newer and npm
- Python 3.11 or newer

## Run locally

```bash
cp .env.example .env
python3 -m venv .venv
source .venv/bin/activate
pip install -r backend/requirements.txt
uvicorn app.main:app --app-dir backend --reload --port 8000
```

In another terminal:

```bash
cd frontend
npm install
npm run dev
```

Open the Vite URL shown in the terminal (normally `http://localhost:5173`). The frontend reads `VITE_API_BASE_URL`; restart Vite after changing it. The backend reads `FRONTEND_ORIGIN`, `ECOVISION_DB_PATH`, `OPEN_METEO_TIMEOUT_SECONDS`, and `OPEN_METEO_CACHE_SECONDS`. No API key is required. Open-Meteo availability and rate limits apply.

## Checks

```bash
cd backend && PYTHONPATH=. pytest
cd frontend && npm test
npm run build
```

## Data integrity

Live measurements and weather come from Open-Meteo's Air Quality and Forecast APIs after city geocoding. Current values carry the API timestamp, units, and source. AQI is presented as US AQI and European AQI separately; neither is labeled Indian AQI. The OSM marker shows the selected query coordinate, not a monitoring station.

When the external API is unavailable, live panels show an error/unavailable state. The simulation works independently and is labeled simulated. There are no fabricated live readings. Water, soil, and noise content is educational; their sliders and scenario outputs are estimates only.

## API

- `GET /api/health`
- `GET /api/air-quality?city=New%20Delhi` (or include both `latitude` and `longitude`)
- `GET /api/environmental-summary?city=New%20Delhi`
- `GET /api/pollution-history?city=New%20Delhi`
- `POST /api/simulate`
- `POST /api/scenarios/compare`
- `GET /api/awareness/facts`
- `GET /api/awareness/quiz`
- `POST /api/awareness/quiz/submit`

Interactive API docs are available at `http://localhost:8000/docs`. Input errors use a structured `error` response. The backend caches successful live responses in memory and stores queried air snapshots in a local SQLite database (`ecovision.db` by default).

## Deployment

Deploy `frontend` as a static Vite site (for example, Vercel) with `VITE_API_BASE_URL` set to the deployed API origin. Deploy `backend` to a Python ASGI host (for example, Render) using `uvicorn app.main:app --app-dir backend --host 0.0.0.0 --port $PORT`; configure `FRONTEND_ORIGIN` and a persistent disk path for `ECOVISION_DB_PATH`. Use HTTPS origins in production. SQLite is suitable for a single development/instance deployment; replace the small snapshot store with PostgreSQL for multi-instance production.

## Limitations

See [docs/simulation-model.md](docs/simulation-model.md) for equations and limitations. Open-Meteo values are API-provided estimates/reanalysis/forecast products rather than readings from a user-selected physical sensor. There is no account system, IoT integration, or local water/soil/noise data source in this version.
