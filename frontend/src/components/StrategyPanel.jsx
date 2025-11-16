import React from 'react'
import { Activity, Clock, Target } from 'lucide-react'

function StrategyPanel({ strategy, performance, currentLap }) {
  if (!performance || !strategy) return null

  const completedLaps = performance.lap_times.filter(lt => lt.lap <= currentLap)
  const avgLapTime = completedLaps.length > 0
    ? completedLaps.reduce((sum, lt) => sum + lt.lap_time_seconds, 0) / completedLaps.length
    : 0

  const bestLap = completedLaps.length > 0
    ? Math.min(...completedLaps.map(lt => lt.lap_time_seconds))
    : 0

  const lastLap = completedLaps.length > 0
    ? completedLaps[completedLaps.length - 1].lap_time_seconds
    : 0

  const lapDelta = lastLap - bestLap

  return (
    <div className="strategy-panel">
      <h2>Performance Metrics</h2>
      
      <div className="metrics-grid">
        <div className="metric-card">
          <div className="metric-icon">
            <Clock size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Best Lap</span>
            <span className="metric-value">{bestLap.toFixed(3)}s</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Activity size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Average Lap</span>
            <span className="metric-value">{avgLapTime.toFixed(3)}s</span>
          </div>
        </div>

        <div className="metric-card">
          <div className="metric-icon">
            <Target size={24} />
          </div>
          <div className="metric-content">
            <span className="metric-label">Last Lap Delta</span>
            <span className={`metric-value ${lapDelta > 1 ? 'negative' : 'positive'}`}>
              {lapDelta > 0 ? '+' : ''}{lapDelta.toFixed(3)}s
            </span>
          </div>
        </div>
      </div>

      <div className="sector-analysis">
        <h3>Sector Performance (Last 5 Laps)</h3>
        <div className="sectors-table">
          <table>
            <thead>
              <tr>
                <th>Lap</th>
                <th>S1</th>
                <th>S2</th>
                <th>S3</th>
                <th>Total</th>
              </tr>
            </thead>
            <tbody>
              {performance.sector_performance && performance.sector_performance.length > 0 ? (
                performance.sector_performance.slice(0, 5).map((sector, idx) => (
                  <tr key={`sector-${idx}-${sector[' LAP_NUMBER']}`}>
                    <td>{sector[' LAP_NUMBER'] || sector.LAP_NUMBER}</td>
                    <td>{sector.S1_SECONDS && sector.S1_SECONDS !== '' ? Number(sector.S1_SECONDS).toFixed(2) : '-'}</td>
                    <td>{sector.S2_SECONDS && sector.S2_SECONDS !== '' ? Number(sector.S2_SECONDS).toFixed(2) : '-'}</td>
                    <td>{sector.S3_SECONDS && sector.S3_SECONDS !== '' ? Number(sector.S3_SECONDS).toFixed(2) : '-'}</td>
                    <td>{sector[' LAP_TIME'] || sector.LAP_TIME || '-'}</td>
                  </tr>
                ))
              ) : (
                <tr>
                  <td colSpan="5" style={{ textAlign: 'center', color: '#888' }}>
                    No sector data available
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}

export default StrategyPanel
