# Simulation model

EcoVision's scenario engine is a small, deterministic teaching model. It is not a scientifically validated atmospheric dispersion model, an official AQI calculation, an exposure estimate, or a health diagnosis.

The user controls are normalized into source terms. Traffic is scaled by vehicle count and reduced by traffic restrictions and public-transport uptake. Industry is scaled by its activity and reduced by control efficiency. Construction dust and population density contribute separate background terms. PM2.5 and PM10 use different illustrative source weights.

The combined source terms are attenuated by a bounded dispersion factor: increasing wind speed increases dilution; rainfall removes a fraction of airborne particles; green cover and tree count apply a capped vegetation factor. A small background concentration remains. The 24-hour line adds a fixed sinusoidal activity pattern to the current simulated concentration; it does not use weather forecasts or calibrated city emissions.

The displayed relative index is `round(simulated PM2.5 × 2.5)`, capped at 500. This deliberately is not the Indian National AQI, US AQI, or European AQI. Live AQIs from Open-Meteo are separately named by standard and never converted between scales.

All coefficients are chosen for understandable directional behavior, not fitted to measurements. The model omits atmospheric chemistry, topography, street-canyon effects, source inventories, and local calibration. Treat comparisons as educational what-if scenarios only.