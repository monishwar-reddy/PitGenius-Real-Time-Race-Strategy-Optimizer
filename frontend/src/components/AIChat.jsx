import React, { useState, useRef, useEffect } from 'react'
import { Send, Bot, User, Sparkles } from 'lucide-react'
import './AIChat.css'

function AIChat() {
  const [messages, setMessages] = useState([
    {
      role: 'assistant',
      content:
        "Hello! I'm your AI Race Assistant powered by Gemini 2.5 Flash. Ask me anything about race strategy, tire management, pit stops, or data analysis!"
    }
  ])

  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || isLoading) return

    const userMessage = input.trim()
    setInput('')

    // Add user message
    setMessages(prev => [...prev, { role: 'user', content: userMessage }])
    setIsLoading(true)

    try {
      const API_KEY = import.meta.env.VITE_GEMINI_API_KEY

      if (!API_KEY) {
        throw new Error("Gemini API key not found in environment variables")
      }

      console.log("Sending request to Gemini 2.5 Flash...")

      const response = await fetch(
        `https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key=${API_KEY}`,
        {
          method: "POST",
          headers: {
            "Content-Type": "application/json"
          },
          body: JSON.stringify({
            contents: [
              {
                parts: [
                  {
                    text: `
You are a professional race strategy assistant for GR Cup racing.
User question: ${userMessage}

Provide helpful, concise advice about race strategy, pit stops, tire management, 
or data analysis. Keep responses under 200 words.`
                  }
                ]
              }
            ]
          })
        }
      )

      const data = await response.json()
      console.log("Gemini response:", data)

      const aiResponse =
        data?.candidates?.[0]?.content?.parts?.[0]?.text ||
        "Sorry, I could not generate a response."

      setMessages(prev => [...prev, { role: "assistant", content: aiResponse }])
    } catch (error) {
      console.error("Gemini API Error:", error)
      setMessages(prev => [
        ...prev,
        {
          role: "assistant",
          content:
            "Sorry, I encountered an error while connecting to Gemini. Please try again."
        }
      ])
    } finally {
      setIsLoading(false)
    }
  }

  const handleKeyPress = e => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  const suggestedQuestions = [
    'When should I pit?',
    'Analyze tire degradation',
    "What's the optimal strategy?",
    'How does weather affect pace?'
  ]

  return (
    <div className="ai-chat">
      <div className="chat-container">
        <div className="chat-messages">
          {messages.map((message, index) => (
            <div key={index} className={`message ${message.role}`}>
              <div className="message-avatar">
                {message.role === 'assistant' ? (
                  <Bot size={20} />
                ) : (
                  <User size={20} />
                )}
              </div>
              <div className="message-content">
                <div className="message-text">{message.content}</div>
              </div>
            </div>
          ))}

          {isLoading && (
            <div className="message assistant">
              <div className="message-avatar">
                <Bot size={20} />
              </div>
              <div className="message-content">
                <div className="typing-indicator">
                  <span></span>
                  <span></span>
                  <span></span>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {messages.length === 1 && (
          <div className="suggested-questions">
            <div className="suggested-header">
              <Sparkles size={16} />
              <span>Try asking:</span>
            </div>
            <div className="suggested-grid">
              {suggestedQuestions.map((question, index) => (
                <button
                  key={index}
                  className="suggested-btn"
                  onClick={() => setInput(question)}
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        <div className="chat-input-container">
          <div className="chat-input-wrapper">
            <textarea
              className="chat-input"
              placeholder="Ask about race strategy, tire management, pit stops..."
              value={input}
              onChange={e => setInput(e.target.value)}
              onKeyPress={handleKeyPress}
              rows="1"
              disabled={isLoading}
            />
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={!input.trim() || isLoading}
            >
              <Send size={20} />
            </button>
          </div>
          <div className="chat-footer">
            <Sparkles size={14} />
            <span>Powered by Gemini 2.5 Flash</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default AIChat
