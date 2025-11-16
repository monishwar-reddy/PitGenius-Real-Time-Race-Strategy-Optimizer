import React from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceLine } from 'recharts'

function TelemetryChart({ lapTimes, tireDegradation, currentLap }) {
  if (!lapTimes || lapTimes.length === 0) return null

  const chartData = lapTimes
    .filter(lt => lt.lap <= currentLap && lt.lap < 32768)
    .map(lt => ({
      lap: lt.lap,
      lapTime: lt.lap_time_seconds,
      predicted: tireDegradation.trend 
        ? tireDegradation.trend[1] + tireDegradation.trend[0] * (lt.lap - 1)
        : null
    }))

  const bestLap = Math.min(...chartData.map(d => d.lapTime))

  return (
    <div className="telemetry-chart">
      <h2>Lap Time Analysis</h2>
      
      <div className="chart-container">
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={chartData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#333" />
            <XAxis 
              dataKey="lap" 
              stroke="#888"
              label={{ value: 'Lap Number', position: 'insideBottom', offset: -5 }}
            />
            <YAxis 
              stroke="#888"
              domain={['dataMin - 2', 'dataMax + 2']}
              label={{ value: 'Lap Time (seconds)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip 
              contentStyle={{ 
                backgroundColor: '#1a1a1a', 
                border: '1px solid #333',
                borderRadius: '8px'
              }}
              formatter={(value) => value?.toFixed(3) + 's'}
            />
            <Legend />
            <ReferenceLine 
              y={bestLap} 
              stroke="#10b981" 
              strokeDasharray="3 3"
              label={{ value: 'Best Lap', fill: '#10b981' }}
            />
            <Line 
              type="monotone" 
              dataKey="lapTime" 
              stroke="#3b82f6" 
              strokeWidth={3}
              dot={{ fill: '#3b82f6', r: 4 }}
              name="Actual Lap Time"
            />
            {tireDegradation.trend && (
              <Line 
                type="monotone" 
                dataKey="predicted" 
                stroke="#f59e0b" 
                strokeWidth={2}
                strokeDasharray="5 5"
                dot={false}
                name="Degradation Trend"
              />
            )}
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="chart-insights">
        <div className="insight">
          <span className="insight-label">Consistency:</span>
          <span className="insight-value">
            {chartData.length > 1 
              ? (Math.max(...chartData.map(d => d.lapTime)) - Math.min(...chartData.map(d => d.lapTime))).toFixed(3) + 's variance'
              : 'N/A'
            }
          </span>
        </div>
        <div className="insight">
          <span className="insight-label">Trend:</span>
          <span className={`insight-value ${tireDegradation.degradation_rate > 0.3 ? 'negative' : 'positive'}`}>
            {tireDegradation.degradation_rate > 0.3 ? 'Degrading' : 'Stable'}
          </span>
        </div>
      </div>
    </div>
  )
}

export default TelemetryChart
