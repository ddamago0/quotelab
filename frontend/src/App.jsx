import React, { useEffect, useState } from 'react'

export default function App() {
  const [healthStatus, setHealthStatus] = useState({ status: 'checking...', service: '', version: '' })
  const [error, setError] = useState(null)

  useEffect(() => {
    fetch('/api/health')
      .then((res) => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`)
        return res.json()
      })
      .then((data) => setHealthStatus(data))
      .catch((err) => setError(err.message))
  }, [])

  return (
    <div className="app-container">
      <header className="header">
        <div className="logo">
          QuoteLab <span className="badge-tag">Phase 1 Foundation</span>
        </div>
      </header>

      <main className="main-content">
        <div className="card">
          <h2>Backend Health Status</h2>
          {error ? (
            <p style={{ color: '#f85149' }}>Backend connection error: {error}</p>
          ) : (
            <div className="status-pill">
              <span className="status-dot"></span>
              <span>{healthStatus.service || 'QuoteLab API'} v{healthStatus.version || '0.1.0'} - Status: {healthStatus.status}</span>
            </div>
          )}
        </div>

        <div className="card">
          <h2>Architecture Foundation Ready</h2>
          <p style={{ color: 'var(--text-secondary)', lineHeight: 1.6 }}>
            Phase 1 project skeleton and domain interfaces established.
            Domain ports created for QuoteRepository, VectorStore, Embedder, LLMProvider, and Tokenizer.
          </p>
        </div>
      </main>
    </div>
  )
}
