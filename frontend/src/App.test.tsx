import { render, screen } from '@testing-library/react'
import { describe, expect, it, vi } from 'vitest'
import App from './App'

vi.mock('react-leaflet', () => ({
  MapContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Marker: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Popup: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  TileLayer: () => <div />,
  useMap: () => ({ invalidateSize: () => undefined, setView: () => undefined, getZoom: () => 10 }),
}))

describe('EcoVision dashboard', () => {
  it('keeps live readings unavailable when the public API is unreachable', async () => {
    vi.stubGlobal('fetch', vi.fn().mockRejectedValue(new Error('Public API unavailable')))
    render(<App />)
    expect(screen.getByRole('heading', { name: 'Know your air. Shape what comes next.' })).toBeInTheDocument()
    expect(await screen.findByText(/Live readings unavailable/)).toBeInTheDocument()
    expect(screen.getAllByText('—').length).toBeGreaterThan(0)
  })
})