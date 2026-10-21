import math

from .schemas import SimulationInput


def simulate(inputs: SimulationInput) -> dict:
    """Return an illustrative relative pollution scenario, not a forecast."""
    traffic = (inputs.vehicles / 10000) * (1 - inputs.traffic_restrictions / 100 * 0.65)
    traffic *= 1 - inputs.public_transport / 100 * 0.35
    industry = inputs.industrial_emissions / 100 * (1 - inputs.industrial_control / 100)
    dust = inputs.construction_dust / 100
    population = inputs.population_density / 100

    pm25_sources = {
        "Road traffic": traffic * 17,
        "Industry": industry * 15,
        "Construction dust": dust * 9,
        "Background activity": population * 5,
    }
    pm10_sources = {
        "Road traffic": traffic * 22,
        "Industry": industry * 12,
        "Construction dust": dust * 24,
        "Background activity": population * 4,
    }
    tree_effect = min(inputs.trees / 100000 * 0.06, 0.18)
    vegetation_effect = min(inputs.green_cover / 100 * 0.15 + tree_effect, 0.24)
    wind_factor = 1 / (1 + inputs.wind_speed / 18)
    rain_factor = max(0.35, 1 - inputs.rainfall / 100 * 0.55)
    dispersion = wind_factor * rain_factor * (1 - vegetation_effect)

    pm25 = round(max(2, sum(pm25_sources.values()) * dispersion + 3), 1)
    pm10 = round(max(4, sum(pm10_sources.values()) * dispersion + 7), 1)
    # This relative index is deliberately not a national or regulatory AQI.
    index = min(500, round(pm25 * 2.5))
    band = "Low" if index < 50 else "Moderate" if index < 100 else "Elevated" if index < 200 else "High"
    contributions = {
        name: round(value / max(sum(pm25_sources.values()), 0.001) * 100)
        for name, value in pm25_sources.items()
    }
    improvement_hours = round(max(1, 24 * dispersion / max(inputs.wind_speed / 20 + inputs.rainfall / 100 + 0.25, 0.25)))

    forecast = []
    for hour in range(24):
        diurnal = 1 + 0.12 * math.sin((hour - 7) * math.pi / 12)
        hourly_pm25 = round(max(2, pm25 * diurnal), 1)
        forecast.append({"hour": hour, "pm25": hourly_pm25, "pm10": round(pm10 * diurnal, 1), "index": min(500, round(hourly_pm25 * 2.5))})

    return {
        "data_status": "simulated",
        "pm25": pm25,
        "pm10": pm10,
        "index": index,
        "index_label": "Illustrative index (not an official AQI)",
        "band": band,
        "source_contributions": contributions,
        "estimated_improvement_hours": improvement_hours,
        "forecast_24h": forecast,
        "assumptions": [
            "Source terms are illustrative linear weights, not measured emissions inventories.",
            "Wind, rainfall, and vegetation apply bounded attenuation factors; local terrain and chemistry are omitted.",
            "The relative index is PM2.5 multiplied by 2.5 and is not an Indian, US, or European AQI calculation.",
        ],
    }