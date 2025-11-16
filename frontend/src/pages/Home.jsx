import React from 'react'
import { useNavigate } from 'react-router-dom'
import { Flag, Zap, TrendingUp, Target, ArrowRight, BarChart3, MessageSquare } from 'lucide-react'
import './Home.css'

function Home() {
  const navigate = useNavigate()

  return (
    <div className="home-page">
      {/* Hero Section */}
      <section className="hero">
        <div className="hero-content">
          <div className="hero-badge">
            <Flag size={20} />
            <span>Toyota Racing Development - Hack the Track 2025</span>
          </div>
          
          <h1 className="hero-title">
            <span className="gradient-text">PitGenius</span>
            <br />
            Real-Time Race Strategy Optimizer
          </h1>
          
          <p className="hero-subtitle">
            Transform telemetry data points into winning pit stop decisions. 
            AI-powered strategy optimization for GR Cup racing teams.
          </p>
          
          <div className="hero-buttons">
            <button className="btn-primary-large" onClick={() => navigate('/dashboard')}>
              Launch Dashboard
              <ArrowRight size={20} />
            </button>
            <button className="btn-secondary-large" onClick={() => navigate('/contact')}>
              Get in Touch
            </button>
          </div>
        </div>
        
        <div className="hero-visual">
          <div className="floating-card card-1">
            <TrendingUp size={24} />
            <span>Tire Degradation Predictor</span>
          </div>
          <div className="floating-card card-2">
            <Target size={24} />
            <span>Optimal Pit Windows</span>
          </div>
          <div className="floating-card card-3">
            <Zap size={24} />
            <span>Real-Time Analytics</span>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section className="features">
        <div className="section-header">
          <h2>Winning Features</h2>
          <p>Everything you need to dominate race day</p>
        </div>
        
        <div className="features-grid">
          <div className="feature-card">
            <div className="feature-icon">
              <Target size={32} />
            </div>
            <h3>Pit Window Calculator</h3>
            <p>Analyzes 3 strategies simultaneously with confidence scoring and position prediction</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <TrendingUp size={32} />
            </div>
            <h3>Tire Degradation AI</h3>
            <p>Predicts performance drop-off before it happens using polynomial regression</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <BarChart3 size={32} />
            </div>
            <h3>Performance Analytics</h3>
            <p>Real-time lap time analysis with sector-by-sector breakdown</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <Zap size={32} />
            </div>
            <h3>Race Simulation</h3>
            <p>Test what-if scenarios and watch strategy recommendations evolve</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <MessageSquare size={32} />
            </div>
            <h3>AI Race Assistant</h3>
            <p>Chat with Gemini AI for instant race strategy insights and analysis</p>
          </div>
          
          <div className="feature-card">
            <div className="feature-icon">
              <Flag size={32} />
            </div>
            <h3>Live Weather Integration</h3>
            <p>Track conditions impact on tire strategy and performance</p>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="cta">
        <div className="cta-content">
          <h2>Ready to Win?</h2>
          <p>Join the future of data-driven racing strategy</p>
          <button className="btn-primary-large" onClick={() => navigate('/dashboard')}>
            Start Analyzing
            <ArrowRight size={20} />
          </button>
        </div>
      </section>

      {/* Footer */}
      <footer className="home-footer">
        <div className="footer-content">
          <div className="footer-brand">
            <Flag size={24} />
            <span>PitGenius</span>
          </div>
          <p>Built for Hack the Track 2025 - Toyota Racing Development</p>
        </div>
      </footer>
    </div>
  )
}

export default Home
