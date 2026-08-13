import React, { useEffect, useState } from 'react'
import { getHealth } from './services/api.js'
import SearchTab from './components/SearchTab.jsx'
import DebateTab from './components/DebateTab.jsx'
import BatchTab from './components/BatchTab.jsx'
import DatasetTab from './components/DatasetTab.jsx'

export default function App() {
  const [activeTab, setActiveTab] = useState('search')
  const [theme, setTheme] = useState(() => localStorage.getItem('quotelab-theme') || 'cyber')
  const [healthStatus, setHealthStatus] = useState({ status: 'checking...', service: '', version: '' })
  const [error, setError] = useState(null)

  // Sync active theme attribute & persist in localStorage
  useEffect(() => {
    document.documentElement.setAttribute('data-theme', theme)
    localStorage.setItem('quotelab-theme', theme)
  }, [theme])

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

  const toggleTheme = () => {
    setTheme((prev) => (prev === 'cyber' ? 'comic' : 'cyber'))
  }

  // Navigation module configurations adapted to active theme
  const modules = [
    {
      id: 'search',
      code: 'SEARCH',
      title: 'Semantic Discovery',
      subtitle: theme === 'comic' ? 'Vector Vibe Scanner' : 'Semantic Similarity Engine',
      icon: '🔍',
    },
    {
      id: 'debate',
      code: 'DEBATE',
      title: theme === 'comic' ? 'Evidence Clash' : 'Evidence Arena',
      subtitle: 'RAG Debate Synthesizer',
      icon: theme === 'comic' ? '⚔️' : '⚖️',
    },
    {
      id: 'batch',
      code: 'BATCH',
      title: theme === 'comic' ? 'Token Reactor' : 'Token Optimizer',
      subtitle: 'Budget & Packing Engine',
      icon: theme === 'comic' ? '⚡' : '📦',
    },
    {
      id: 'dataset',
      code: 'DATASET',
      title: theme === 'comic' ? 'Knowledge Web' : 'Knowledge Corpus',
      subtitle: 'Corpus Archive & Grid',
      icon: theme === 'comic' ? '🕸️' : '📊',
    },
  ]

  return (
    <div className="app-container" data-theme={theme}>
      {/* Dual Theme Ambient Background System */}
      <div className="ambient-background" aria-hidden="true">
        {/* Cyber Theme Ambient Background Layers */}
        <div className="cyber-bg-layer">
          <div className="cyber-grid-overlay"></div>
          <div className="ambient-orb ambient-orb-1"></div>
          <div className="ambient-orb ambient-orb-2"></div>
          <div className="ambient-orb ambient-orb-3"></div>
        </div>

        {/* Comic Theme Ambient Background Layers */}
        <div className="comic-bg-layer">
          <div className="halftone-overlay"></div>
          <div className="speed-lines-overlay"></div>
          <div className="ambient-orb ambient-orb-1"></div>
          <div className="ambient-orb ambient-orb-2"></div>
          <div className="ambient-orb ambient-orb-3"></div>
        </div>
      </div>

      {/* Main Terminal & Laboratory Header */}
      <header className="header">
        <div className="header-left">
          <div className="logo-container">
            <div className="logo">
              <span className="logo-icon-wrap">
                <span className="logo-mark">{theme === 'comic' ? '💥' : '⚡'}</span>
                <span className="logo-glow-dot"></span>
              </span>
              <span className="logo-text">QuoteLab</span>
              <span className="badge-tag">
                {theme === 'comic' ? 'NEON COMIC LAB' : 'CYBER KNOWLEDGE LAB'}
              </span>
            </div>
            <span className="logo-tagline">Semantic Intelligence for Human Knowledge</span>
          </div>
        </div>

        <div className="header-right">
          {/* Futuristic Thematic Theme Switcher Button */}
          <button
            type="button"
            className="theme-switcher-btn"
            onClick={toggleTheme}
            title="Switch Visual Theme Universe"
            aria-label="Switch Visual Theme Universe"
          >
            <span className="theme-icon-badge">
              {theme === 'cyber' ? '🌐' : '🕸️'}
            </span>
            <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-start', lineHeight: 1.2 }}>
              <span className="theme-name">{theme === 'cyber' ? 'CYBER LAB' : 'COMIC LAB'}</span>
              <span className="theme-toggle-hint">
                Switch to {theme === 'cyber' ? 'Comic 🕸️' : 'Cyber 🌐'}
              </span>
            </div>
          </button>

          {/* Backend Status Pill */}
          {error ? (
            <div className="status-pill error">
              <span className="status-dot error"></span>
              <span>OFFLINE: {error}</span>
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

      {/* Module Navigation Control Bar */}
      <div className="module-nav-container">
        <div className="module-nav-grid" role="tablist" aria-label="QuoteLab Module Selector">
          {modules.map((mod) => {
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

      {/* Main Active Module Container */}
      <main className="main-content">
        {activeTab === 'search' && <SearchTab />}
        {activeTab === 'debate' && <DebateTab />}
        {activeTab === 'batch' && <BatchTab />}
        {activeTab === 'dataset' && <DatasetTab />}
      </main>
    </div>
  )
}
