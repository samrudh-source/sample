const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export type SimulationInput = {
  vehicles: number
  industrial_emissions: number
  construction_dust: number
  population_density: number
  green_cover: number
  trees: number
  wind_speed: number
  wind_direction: number
  rainfall: number
  traffic_restrictions: number
  industrial_control: number
  public_transport: number
}

export type SimulationResult = {
  data_status: 'simulated'
  pm25: number
  pm10: number
  index: number
  index_label: string
  band: string
  source_contributions: Record<string, number>
  estimated_improvement_hours: number
  forecast_24h: { hour: number; pm25: number; pm10: number; index: number }[]
  assumptions: string[]
}

export type EnvironmentalData = {
  status: 'live'
  city: string
  coordinates: { latitude: number; longitude: number }
  updated_at: string | null
  source: string
  aqi: Record<string, { value: number | null; unit: string; status: string }>
  pollutants: { key: string; label: string; value: number | null; unit: string; status: string }[]
  weather: Record<string, { value: number | null; unit: string; status: string }>
  hourly: { time: string[]; pm2_5: (number | null)[]; pm10: (number | null)[]; us_aqi: (number | null)[]; european_aqi: (number | null)[] }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const response = await fetch(`${API_BASE}${path}`, {
    ...init,
    headers: { 'Content-Type': 'application/json', ...init?.headers },
  })
  if (!response.ok) {
    const body = await response.json().catch(() => null)
    throw new Error(body?.detail?.message || body?.error?.code || `Request failed (${response.status})`)
  }
  return response.json() as Promise<T>
}

export const getEnvironment = (city: string, coordinates?: { latitude: number; longitude: number }) => {
  const query = coordinates
    ? `city=${encodeURIComponent(city)}&latitude=${coordinates.latitude}&longitude=${coordinates.longitude}`
    : `city=${encodeURIComponent(city)}`
  return request<EnvironmentalData>(`/api/air-quality?${query}`)
}

export const getHistory = async (city: string) => {
  const result = await request<{ points: { time: string; pm25: number | null; pm10: number | null; us_aqi: number | null }[] }>(`/api/pollution-history?city=${encodeURIComponent(city)}`)
  return result.points
}

export const runSimulation = (input: SimulationInput) => request<SimulationResult>('/api/simulate', { method: 'POST', body: JSON.stringify(input) })

export const compareScenarios = (baseline: SimulationInput) => request<{
  baseline: SimulationResult
  comparisons: { name: string; result: SimulationResult; pm25_change: number; index_change: number }[]
}>('/api/scenarios/compare', {
  method: 'POST',
  body: JSON.stringify({ baseline, scenarios: [
    { name: '30% less private traffic', traffic_restrictions: 30 },
    { name: 'Public transport +40%', public_transport: Math.min(100, baseline.public_transport + 40) },
    { name: 'Industry controls +50%', industrial_control: Math.min(100, baseline.industrial_control + 50) },
    { name: 'Green cover +20%', green_cover: Math.min(100, baseline.green_cover + 20) },
    { name: 'Construction dust controls', construction_dust: baseline.construction_dust * 0.5 },
    { name: 'Combined interventions', traffic_restrictions: 30, public_transport: Math.min(100, baseline.public_transport + 40), industrial_control: Math.min(100, baseline.industrial_control + 50), green_cover: Math.min(100, baseline.green_cover + 20), construction_dust: baseline.construction_dust * 0.5 },
  ] }),
})

export const getAwareness = () => request<{ facts: { category: string; title: string; body: string; source: string }[] }>('/api/awareness/facts')
export const submitQuiz = (answers: number[]) => request<{ score: number; total: number; complete: boolean }>('/api/awareness/quiz/submit', { method: 'POST', body: JSON.stringify({ answers }) })