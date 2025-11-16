import React from 'react'
import { AlertTriangle, CheckCircle, TrendingUp } from 'lucide-react'

function PitWindowCalculator({ strategy, currentLap }) {
  if (!strategy || !strategy.pit_windows) return null

  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#10b981'
    if (confidence >= 0.6) return '#f59e0b'
    return '#ef4444'
  }

  const getPositionColor = (position) => {
    if (position <= 3) return '#ffd700'
    if (position <= 8) return '#c0c0c0'
    return '#cd7f32'
  }
  
  const isWindowOpen = (window) => {
    return currentLap >= window.lap_start && currentLap <= window.lap_end
  }
  
  const isWindowPassed = (window) => {
    return currentLap > window.lap_end
  }

  return (
    <div className="pit-window-calculator">
      <h2>Pit Strategy Analysis</h2>
      
      <div className="degradation-alert">
        <TrendingUp size={20} />
        <div>
          <strong>Tire Degradation:</strong>
          <span className={Math.abs(strategy.tire_degradation_rate) > 0.3 ? 'critical' : 'normal'}>
            {Math.abs(strategy.tire_degradation_rate) > 0.01
              ? `${strategy.tire_degradation_rate > 0 ? '+' : ''}${strategy.tire_degradation_rate.toFixed(3)}s per lap`
              : 'Minimal degradation'
            }
          </span>
        </div>
      </div>

      <div className="windows-grid">
        {strategy.pit_windows.length > 0 ? (
          strategy.pit_windows.map((window, idx) => (
            <div 
              key={`window-${idx}-${window.lap_start}`} 
              className={`window-card ${isWindowOpen(window) ? 'active' : ''} ${isWindowPassed(window) ? 'passed' : ''}`}
            >
              <div className="window-header">
                <h3>{window.reason}</h3>
                <div 
                  className="confidence-badge"
                  style={{ backgroundColor: getConfidenceColor(window.confidence) }}
                >
                  {(window.confidence * 100).toFixed(0)}%
                </div>
              </div>
              
              <div className="window-details">
                <div className="detail-row">
                  <span className="label">Pit Window:</span>
                  <span className="value">Laps {window.lap_start}-{window.lap_end}</span>
                </div>
                
                <div className="detail-row">
                  <span className="label">Time Loss:</span>
                  <span className="value">{window.time_loss.toFixed(1)}s</span>
                </div>
                
                <div className="detail-row">
                  <span className="label">Predicted Position:</span>
                  <span 
                    className="value position"
                    style={{ color: getPositionColor(window.predicted_position) }}
                  >
                    P{window.predicted_position}
                  </span>
                </div>
              </div>

              {isWindowOpen(window) && (
                <div className="pit-now-alert">
                  <CheckCircle size={16} />
                  <span>WINDOW OPEN - PIT NOW!</span>
                </div>
              )}
              
              {isWindowPassed(window) && (
                <div className="window-passed">
                  Window Closed
                </div>
              )}
            </div>
          ))
        ) : (
          <div className="no-windows">
            <p>No pit windows available for current lap</p>
          </div>
        )}
      </div>
    </div>
  )
}

export default PitWindowCalculator
