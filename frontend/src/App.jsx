import React, { useEffect, useState } from 'react'
import { getHealth } from './services/api.js'
import SearchTab from './components/SearchTab.jsx'
import DebateTab from './components/DebateTab.jsx'
import BatchTab from './components/BatchTab.jsx'
import DatasetTab from './components/DatasetTab.jsx'

const TABS = [
  {
    id: 'search',
    label: 'Semantic Search',
    title: 'Semantic Vibe Search (Desafío 1)',
    description: 'Explore quotes using dense vector embedding similarity search based on personal situations, emotions, or abstract thoughts.',
    icon: '🔍',
  },
  {
    id: 'debate',
    label: 'Evidence-Backed Debate',
    title: 'Evidence-Backed Debate (Desafío 2)',
    description: 'Generate structured philosophical and argumentative debates grounded strictly in quotes from the corpus, with controlled refusal handling.',
    icon: '⚖️',
  },
  {
    id: 'batch',
    label: 'Budget & Batching',
    title: 'Budget & Batching Optimizer (Desafío 3)',
    description: 'Pack quote items into batches respecting unit capacity limits using a deterministic First-Fit Greedy algorithm.',
    icon: '📦',
  },
  {
    id: 'dataset',
    label: 'Dataset Inspection',
    title: 'Dataset Inspection',
    description: 'Browse, filter, and inspect the complete 100-quote corpus loaded from the Excel dataset repository.',
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
        setError(err.message || 'Unable to reach backend API')
      })
  }, [])

  return (
    <div className="app-container">
      <header className="header">
        <div className="header-left">
          <div className="logo">
            QuoteLab <span className="badge-tag">Phase 6 SPA</span>
          </div>
          <nav className="nav-tabs" aria-label="Main Navigation">
            {TABS.map((tab) => (
              <button
                key={tab.id}
                type="button"
                className={`tab-button ${activeTab === tab.id ? 'active' : ''}`}
                onClick={() => setActiveTab(tab.id)}
              >
                {tab.label}
              </button>
            ))}
          </nav>
        </div>

        <div className="header-right">
          {error ? (
            <div className="status-pill error">
              <span className="status-dot error"></span>
              <span>Backend Offline: {error}</span>
            </div>
          ) : (
            <div className="status-pill">
              <span className="status-dot"></span>
              <span>
                {healthStatus.service || 'QuoteLab API'} v{healthStatus.version || '0.1.0'} — {healthStatus.status}
              </span>
            </div>
          )}
        </div>
      </header>

      <main className="main-content">
        {activeTab === 'search' && <SearchTab />}
        {activeTab === 'debate' && <DebateTab />}
        {activeTab === 'batch' && <BatchTab />}
        {activeTab === 'dataset' && <DatasetTab />}
      </main>
    </div>
  )
}
