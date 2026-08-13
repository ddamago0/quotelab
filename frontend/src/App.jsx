import React, { useEffect, useState } from 'react'
import { getHealth } from './services/api.js'
import SearchTab from './components/SearchTab.jsx'
import DebateTab from './components/DebateTab.jsx'
import BatchTab from './components/BatchTab.jsx'
import DatasetTab from './components/DatasetTab.jsx'

const MODULES = [
  {
    id: 'search',
    code: 'SEARCH',
    title: 'Semantic Discovery',
    subtitle: 'Vector Vibe Scanner',
    icon: '🔍',
  },
  {
    id: 'debate',
    code: 'DEBATE',
    title: 'Evidence Arena',
    subtitle: 'RAG Debate Synthesis',
    icon: '⚖️',
  },
  {
    id: 'batch',
    code: 'BATCH',
    title: 'Token Optimizer',
    subtitle: 'Budget & Packing Engine',
    icon: '📦',
  },
  {
    id: 'dataset',
    code: 'DATASET',
    title: 'Knowledge Corpus',
    subtitle: 'Corpus Archive & Grid',
    icon: '📊',
  },
]

export default function App() {
  const [activeTab, setActiveTab] = useState('search')
  const [healthStatus, setHealthStatus] = useState({ status: 'checking...', service: '', version: '' })
  const [error, setError] = useState(null)

  useEffect(() => {
    getHealth()
      .then((data) => {
        setHealthStatus(data)
        setError(null)
      })
      .catch((err) => {
        setError(err.message || 'Unable to connect to QuoteLab API backend')
      })
  }, [])

  return (
    <div className="app-container">
      {/* Cyberpunk Ambient Floating Orbs & Grid Background */}
      <div className="ambient-background" aria-hidden="true">
        <div className="cyber-grid-overlay"></div>
        <div className="ambient-orb ambient-orb-1"></div>
        <div className="ambient-orb ambient-orb-2"></div>
        <div className="ambient-orb ambient-orb-3"></div>
      </div>

      {/* Cyberpunk Terminal Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo-container">
            <div className="logo">
              <span className="logo-icon-wrap">
                <span className="logo-mark">⚡</span>
                <span className="logo-glow-dot"></span>
              </span>
              <span className="logo-text">QuoteLab</span>
              <span className="badge-tag">CYBERPUNK AI</span>
            </div>
            <span className="logo-tagline">Semantic Intelligence for Human Knowledge</span>
          </div>
        </div>

        <div className="header-right">
          {error ? (
            <div className="status-pill error">
              <span className="status-dot error"></span>
              <span>SYSTEM OFFLINE: {error}</span>
            </div>
          ) : (
            <div className="status-pill">
              <span className="status-dot"></span>
              <span>
                {healthStatus.service || 'QuoteLab API'} v{healthStatus.version || '0.1.0'} — {healthStatus.status.toUpperCase()}
              </span>
            </div>
          )}
        </div>
      </header>

      {/* Futuristic Module Navigation Grid */}
      <div className="module-nav-container">
        <div className="module-nav-grid" role="tablist" aria-label="Cyberpunk Module Selector">
          {MODULES.map((mod) => {
            const isActive = activeTab === mod.id
            return (
              <button
                key={mod.id}
                type="button"
                role="tab"
                aria-selected={isActive}
                className={`module-card ${isActive ? 'active' : ''}`}
                onClick={() => setActiveTab(mod.id)}
              >
                <span className="module-icon">{mod.icon}</span>
                <div className="module-text">
                  <span className="module-title">[{mod.code}] {mod.title}</span>
                  <span className="module-subtitle">{mod.subtitle}</span>
                </div>
              </button>
            )
          })}
        </div>
      </div>

      {/* Main Active Module Screen */}
      <main className="main-content">
        {activeTab === 'search' && <SearchTab />}
        {activeTab === 'debate' && <DebateTab />}
        {activeTab === 'batch' && <BatchTab />}
        {activeTab === 'dataset' && <DatasetTab />}
      </main>
    </div>
  )
}
