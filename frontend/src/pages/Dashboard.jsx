import React, { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Flag, BarChart3, MessageSquare, Home, Mail, X } from 'lucide-react'
import PitGeniusApp from '../PitGeniusApp'
import AIChat from '../components/AIChat'
import './Dashboard.css'

function Dashboard() {
  const navigate = useNavigate()
  const [activePortal, setActivePortal] = useState(null)

  const openPortal = (portal) => {
    setActivePortal(portal)
  }

  const closePortal = () => {
    setActivePortal(null)
  }

  return (
    <div className="dashboard-page">
      {/* Navigation */}
      <nav className="dashboard-nav">
        <div className="nav-brand" onClick={() => navigate('/')}>
          <Flag size={24} />
          <span>PitGenius</span>
        </div>
        <div className="nav-links">
          <button onClick={() => navigate('/')} className="nav-link">
            <Home size={18} />
            <span>Home</span>
          </button>
          <button onClick={() => navigate('/contact')} className="nav-link">
            <Mail size={18} />
            <span>Contact</span>
          </button>
        </div>
      </nav>

      {/* Portal Selection */}
      {!activePortal && (
        <div className="portal-selection">
          <div className="portal-header">
            <h1>Choose Your Portal</h1>
            <p>Select a tool to start analyzing race data</p>
          </div>

          <div className="portals-grid">
            <div className="portal-card" onClick={() => openPortal('pitgenius')}>
              <div className="portal-icon">
                <BarChart3 size={48} />
              </div>
              <h2>Race Strategy Analyzer</h2>
              <p>Real-time pit stop optimization, tire degradation prediction, and performance analytics</p>
              <div className="portal-features">
                <span className="feature-tag">Pit Windows</span>
                <span className="feature-tag">Tire Analysis</span>
                <span className="feature-tag">Live Data</span>
              </div>
              <button className="portal-btn">
                Launch Analyzer
              </button>
            </div>

            <div className="portal-card" onClick={() => openPortal('aichat')}>
              <div className="portal-icon ai">
                <MessageSquare size={48} />
              </div>
              <h2>AI Race Assistant</h2>
              <p>Chat with Gemini AI for instant race strategy insights, data analysis, and recommendations</p>
              <div className="portal-features">
                <span className="feature-tag">Gemini AI</span>
                <span className="feature-tag">Strategy Tips</span>
                <span className="feature-tag">24/7 Support</span>
              </div>
              <button className="portal-btn ai-btn">
                Launch AI Chat
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Active Portal */}
      {activePortal && (
        <div className="active-portal">
          <div className="portal-header-bar">
            <div className="portal-title">
              {activePortal === 'pitgenius' ? (
                <>
                  <BarChart3 size={24} />
                  <span>Race Strategy Analyzer</span>
                </>
              ) : (
                <>
                  <MessageSquare size={24} />
                  <span>AI Race Assistant</span>
                </>
              )}
            </div>
            <button className="close-portal-btn" onClick={closePortal}>
              <X size={24} />
            </button>
          </div>

          <div className="portal-content">
            {activePortal === 'pitgenius' && <PitGeniusApp />}
            {activePortal === 'aichat' && <AIChat />}
          </div>
        </div>
      )}
    </div>
  )
}

export default Dashboard
