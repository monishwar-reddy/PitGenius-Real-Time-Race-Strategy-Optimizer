import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { Flag, Send, CheckCircle, Home, LayoutDashboard } from 'lucide-react'
import './Contact.css'

function Contact() {
  const navigate = useNavigate()

  const [formData, setFormData] = useState({
    name: '',
    email: '',
    subject: '',
    message: ''
  })

  const [isSubmitting, setIsSubmitting] = useState(false)
  const [isSubmitted, setIsSubmitted] = useState(false)
  const [error, setError] = useState('')

  // input handler
  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    })
  }

  // submit handler
  const handleSubmit = async (e) => {
    e.preventDefault()
    setIsSubmitting(true)
    setError('')

    const data = new FormData(e.target)

    try {
      const FORMSPREE_ENDPOINT = import.meta.env.VITE_FORMSPREE_ENDPOINT

      if (!FORMSPREE_ENDPOINT) {
        throw new Error("Formspree endpoint not found in environment variables")
      }

      const res = await fetch(FORMSPREE_ENDPOINT, {
        method: "POST",
        body: data,
        headers: {
          "Accept": "application/json"
        }
      })

      if (res.ok) {
        setIsSubmitted(true)
        setFormData({ name: '', email: '', subject: '', message: '' })
        setTimeout(() => setIsSubmitted(false), 5000)
      } else {
        setError('Failed: ' + res.status)
      }
    } catch (err) {
      setError('Network error. Please try again.')
      console.error('Form error:', err)
    } finally {
      setIsSubmitting(false)
    }
  }

  return (
    <div className="contact-page">

      {/* Navigation */}
      <nav className="contact-nav">
        <div className="nav-brand" onClick={() => navigate('/')}>
          <Flag size={24} />
          <span>PitGenius</span>
        </div>

        <div className="nav-links">
          <button onClick={() => navigate('/')} className="nav-link">
            <Home size={18} />
            Home
          </button>

          <button onClick={() => navigate('/dashboard')} className="nav-link">
            <LayoutDashboard size={18} />
            Dashboard
          </button>
        </div>
      </nav>

      <div className="contact-container">
        <div className="contact-content">
          <div className="contact-form-container">

            {!isSubmitted ? (
              <form className="contact-form" onSubmit={handleSubmit}>
                <h2>Send us a Message</h2>

                {error && (
                  <div style={{
                    padding: '12px',
                    marginBottom: '20px',
                    backgroundColor: '#fee',
                    border: '1px solid #fcc',
                    borderRadius: '8px',
                    color: '#c33'
                  }}>
                    {error}
                  </div>
                )}

                <div className="form-group">
                  <label>Name</label>
                  <input
                    type="text"
                    name="name"
                    required
                    value={formData.name}
                    onChange={handleChange}
                    placeholder="Your name"
                  />
                </div>

                <div className="form-group">
                  <label>Email</label>
                  <input
                    type="email"
                    name="email"
                    required
                    value={formData.email}
                    onChange={handleChange}
                    placeholder="your.email@example.com"
                  />
                </div>

                <div className="form-group">
                  <label>Subject</label>
                  <select
                    name="subject"
                    required
                    value={formData.subject}
                    onChange={handleChange}
                  >
                    <option value="">Select a subject</option>
                    <option value="General Inquiry">General Inquiry</option>
                    <option value="Technical Support">Technical Support</option>
                    <option value="Request Demo">Request Demo</option>
                    <option value="Feedback">Feedback</option>
                  </select>
                </div>

                <div className="form-group">
                  <label>Message</label>
                  <textarea
                    name="message"
                    rows="6"
                    required
                    value={formData.message}
                    onChange={handleChange}
                    placeholder="Tell us more about your inquiry..."
                  />
                </div>

                <button type="submit" className="submit-btn" disabled={isSubmitting}>
                  {isSubmitting ? (
                    <>
                      <span className="spinner" />
                      Sending...
                    </>
                  ) : (
                    <>
                      <Send size={20} />
                      Send Message
                    </>
                  )}
                </button>
              </form>
            ) : (
              <div className="success-message">
                <CheckCircle size={64} />
                <h2>Message Sent!</h2>
                <p>Thank you for reaching out. We'll get back to you soon.</p>
              </div>
            )}

          </div>
        </div>
      </div>

      <footer className="contact-footer">
        © 2025 PitGenius - Built for Hack the Track by Toyota Racing Development
      </footer>

    </div>
  )
}

export default Contact
