import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Flag, Gauge, TrendingUp, AlertTriangle, CheckCircle } from 'lucide-react'
import StrategyPanel from './components/StrategyPanel'
import TelemetryChart from './components/TelemetryChart'
import PitWindowCalculator from './components/PitWindowCalculator'
import './App.css'

const API_BASE = '/api'

function App() {
  const [drivers, setDrivers] = useState([])
  const [selectedDriver, setSelectedDriver] = useState(null)
  const [currentLap, setCurrentLap] = useState(5)
  const [driverPerformance, setDriverPerformance] = useState(null)
  const [strategy, setStrategy] = useState(null)
  const [raceSummary, setRaceSummary] = useState(null)
  const [loading, setLoading] = useState(true)
  const [simulating, setSimulating] = useState(false)

  useEffect(() => {
    loadInitialData()
  }, [])

  useEffect(() => {
    if (selectedDriver) {
      loadDriverData()
    }
  }, [selectedDriver])
  
  useEffect(() => {
    if (selectedDriver && driverPerformance) {
      loadStrategy()
    }
  }, [currentLap])

  const loadInitialData = async () => {
    try {
      const [driversRes, summaryRes] = await Promise.all([
        axios.get(`${API_BASE}/drivers`),
        axios.get(`${API_BASE}/race/summary`)
      ])
      
      setDrivers(driversRes.data.drivers)
      setRaceSummary(summaryRes.data)
      
      if (driversRes.data.drivers.length > 0) {
        setSelectedDriver(driversRes.data.drivers[0].number)
      }
      
      setLoading(false)
    } catch (error) {
      console.error('Error loading data:', error)
      setLoading(false)
    }
  }

  const loadDriverData = async () => {
    try {
      const perfRes = await axios.get(`${API_BASE}/driver/${selectedDriver}/performance`)
      setDriverPerformance(perfRes.data)
      
      const vehicleId = perfRes.data.vehicle_id
      const strategyRes = await axios.post(`${API_BASE}/strategy/calculate`, {
        vehicle_id: vehicleId,
        current_lap: currentLap,
        total_laps: 17
      })
      
      setStrategy(strategyRes.data)
    } catch (error) {
      console.error('Error loading driver data:', error)
    }
  }
  
  const loadStrategy = async () => {
    if (!driverPerformance) return
    
    try {
      const vehicleId = driverPerformance.vehicle_id
      const strategyRes = await axios.post(`${API_BASE}/strategy/calculate`, {
        vehicle_id: vehicleId,
        current_lap: currentLap,
        total_laps: 17
      })
      
      setStrategy(strategyRes.data)
    } catch (error) {
      console.error('Error loading strategy:', error)
    }
  }

  const simulateRace = () => {
    setSimulating(true)
    let lap = 1
    
    const interval = setInterval(() => {
      lap++
      setCurrentLap(lap)
      
      if (lap >= 17) {
        clearInterval(interval)
        setSimulating(false)
      }
    }, 2000)
  }

  if (loading) {
    return (
      <div className="loading-screen">
        <Flag size={48} className="spin" />
        <h2>Loading Race Data...</h2>
      </div>
    )
  }

  return (
    <div className="app pitgenius-embedded">
      <div className="embedded-header">
        <div className="race-info-compact">
          <span className="track-name">Circuit of the Americas</span>
          <span className="lap-counter">Lap {currentLap} / 17</span>
        </div>
      </div>

      <div className="main-content">
        <aside className="sidebar">
          <div className="section">
            <h3>Race Control</h3>
            <div className="controls">
              <label>
                Current Lap
                <input 
                  type="range" 
                  min="1" 
                  max="17" 
                  value={currentLap}
                  onChange={(e) => setCurrentLap(parseInt(e.target.value))}
                  disabled={simulating}
                />
                <span>{currentLap}</span>
              </label>
              <button 
                className="btn-primary"
                onClick={simulateRace}
                disabled={simulating}
              >
                {simulating ? 'Simulating...' : 'Simulate Race'}
              </button>
            </div>
          </div>

          <div className="section">
            <h3>Select Driver</h3>
            <div className="driver-list">
              {drivers
                .filter((driver, index, self) => 
                  index === self.findIndex(d => d.number === driver.number)
                )
                .filter(driver => driver.total_laps > 1)
                .sort((a, b) => a.number - b.number)
                .map(driver => (
                  <button
                    key={`driver-${driver.number}`}
                    className={`driver-card ${selectedDriver === driver.number ? 'active' : ''}`}
                    onClick={() => setSelectedDriver(driver.number)}
                  >
                    <span className="driver-number">#{driver.number}</span>
                    <div className="driver-info">
                      <span className="driver-class">{driver.class}</span>
                      {driver.best_lap && (
                        <span className="best-lap">{driver.best_lap.toFixed(1)}s</span>
                      )}
                    </div>
                  </button>
                ))
              }
            </div>
          </div>

          {raceSummary && (
            <div className="section">
              <h3>Track Conditions</h3>
              <div className="weather-info">
                <div className="weather-item">
                  <Gauge size={16} />
                  <span>Air: {raceSummary.weather?.air_temp?.toFixed(1)}°C</span>
                </div>
                <div className="weather-item">
                  <TrendingUp size={16} />
                  <span>Track: {(raceSummary.weather?.track_temp + (currentLap * 0.2))?.toFixed(1)}°C</span>
                </div>
                <div className={`status ${(raceSummary.weather?.track_temp + (currentLap * 0.2)) < 45 ? 'green' : 'hot'}`}>
                  {(raceSummary.weather?.track_temp + (currentLap * 0.2)) < 45 ? 'GREEN' : 'HOT'}
                </div>
              </div>
            </div>
          )}
        </aside>

        <main className="content">
          {!driverPerformance && !loading && (
            <div className="empty-state">
              <h2>Select a driver to view strategy analysis</h2>
              <p>Choose a driver from the list to see pit windows, performance metrics, and lap time analysis</p>
            </div>
          )}
          
          {driverPerformance && !strategy && (
            <div className="loading-content">
              <h2>Loading strategy data...</h2>
            </div>
          )}
          
          {driverPerformance && strategy && (
            <>
              <PitWindowCalculator 
                strategy={strategy}
                currentLap={currentLap}
              />
              
              <StrategyPanel 
                strategy={strategy}
                performance={driverPerformance}
                currentLap={currentLap}
              />
              
              <TelemetryChart 
                lapTimes={driverPerformance.lap_times}
                tireDegradation={driverPerformance.tire_degradation}
                currentLap={currentLap}
              />
            </>
          )}
        </main>
      </div>
    </div>
  )
}

export default App
