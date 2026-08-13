import React, { useEffect, useMemo, useState } from 'react'
import { getQuotes } from '../services/api.js'

export default function DatasetTab() {
  const [quotes, setQuotes] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [searchTerm, setSearchTerm] = useState('')
  const [viewMode, setViewMode] = useState('table') // 'table' | 'grid'

  const fetchDataset = async () => {
    setLoading(true)
    setError(null)
    try {
      const data = await getQuotes()
      setQuotes(Array.isArray(data) ? data : [])
    } catch (err) {
      setError(err.message || 'Failed to load quote dataset.')
      setQuotes([])
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    fetchDataset()
  }, [])

  // Calculate Dataset Metadata Stats
  const stats = useMemo(() => {
    if (!quotes.length) return { total: 0, authors: 0, avgWords: 0 }
    const uniqueAuthors = new Set(quotes.map((q) => q.author)).size
    const totalWords = quotes.reduce((acc, q) => {
      const words = q.text ? q.text.trim().split(/\s+/).length : 0
      return acc + words
    }, 0)
    return {
      total: quotes.length,
      authors: uniqueAuthors,
      avgWords: (totalWords / quotes.length).toFixed(1),
    }
  }, [quotes])

  // Client-Side Filtered Quotes
  const filteredQuotes = useMemo(() => {
    const term = searchTerm.trim().toLowerCase()
    if (!term) return quotes

    return quotes.filter((q) => {
      const matchId = q.id && q.id.toLowerCase().includes(term)
      const matchAuthor = q.author && q.author.toLowerCase().includes(term)
      const matchText = q.text && q.text.toLowerCase().includes(term)
      const matchTags = q.tags && q.tags.some((tag) => tag.toLowerCase().includes(term))
      return matchId || matchAuthor || matchText || matchTags
    })
  }, [quotes, searchTerm])

  return (
    <div className="dataset-tab-container">
      <div className="tab-header">
        <h2>[CORPUS] Knowledge Archive & Dataset</h2>
        <p className="tab-description">
          Inspect, search, and filter the complete 100-quote Excel dataset repository powering QuoteLab's vector store, RAG debate engine, and batch optimizer.
        </p>
      </div>

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>FETCHING CORPUS: Loading quote nodes from repository...</p>
        </div>
      )}

      {/* Error State */}
      {!loading && error && (
        <div className="error-banner">
          <div className="error-message">
            <span>⚠️ {error}</span>
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={fetchDataset}>
            Retry Fetch
          </button>
        </div>
      )}

      {/* Main Content State */}
      {!loading && !error && (
        <div className="dataset-content">
          {/* Metadata Summary KPI Cards */}
          <div className="kpi-grid">
            <div className="card kpi-card">
              <span className="kpi-label">Total Corpus Quotes</span>
              <span className="kpi-value">{stats.total}</span>
            </div>
            <div className="card kpi-card">
              <span className="kpi-label">Unique Authors</span>
              <span className="kpi-value">{stats.authors}</span>
            </div>
            <div className="card kpi-card">
              <span className="kpi-label">Avg Words / Quote</span>
              <span className="kpi-value">{stats.avgWords}</span>
            </div>
            <div className="card kpi-card">
              <span className="kpi-label">Matching Corpus Nodes</span>
              <span className="kpi-value">{filteredQuotes.length}</span>
            </div>
          </div>

          {/* Filter Bar & Layout View Switcher */}
          <div className="dataset-controls">
            <div className="search-input-wrapper" style={{ flex: 1 }}>
              <input
                type="text"
                className="search-input"
                placeholder="Filter dataset by author, text keyword, tag, or ID (e.g. 'Nietzsche', 'destino', 'q_42')..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
              {searchTerm && (
                <button
                  type="button"
                  className="btn btn-secondary btn-sm"
                  onClick={() => setSearchTerm('')}
                >
                  Clear Filter
                </button>
              )}
            </div>

            <div className="view-toggle-btns">
              <button
                type="button"
                className={`btn btn-secondary btn-sm ${viewMode === 'table' ? 'active' : ''}`}
                style={viewMode === 'table' ? { borderColor: 'var(--neon-cyan)', color: 'var(--neon-cyan)' } : {}}
                onClick={() => setViewMode('table')}
              >
                Table View
              </button>
              <button
                type="button"
                className={`btn btn-secondary btn-sm ${viewMode === 'grid' ? 'active' : ''}`}
                style={viewMode === 'grid' ? { borderColor: 'var(--neon-cyan)', color: 'var(--neon-cyan)' } : {}}
                onClick={() => setViewMode('grid')}
              >
                Grid View
              </button>
            </div>
          </div>

          {/* No Matching Quotes State */}
          {filteredQuotes.length === 0 && (
            <div className="card empty-card">
              <h3>No Quotes Match Filter</h3>
              <p>No quote in the corpus matches your filter criteria "{searchTerm}". Try clearing or broadening your search terms.</p>
            </div>
          )}

          {/* Table View */}
          {filteredQuotes.length > 0 && viewMode === 'table' && (
            <div className="dataset-table-wrapper">
              <table className="dataset-table">
                <thead>
                  <tr>
                    <th style={{ width: '80px' }}>ID</th>
                    <th style={{ width: '180px' }}>Author</th>
                    <th>Quote Text</th>
                    <th style={{ width: '200px' }}>Tags</th>
                  </tr>
                </thead>
                <tbody>
                  {filteredQuotes.map((quote) => (
                    <tr key={quote.id}>
                      <td className="cell-id">
                        <span className="quote-id-chip">{quote.id}</span>
                      </td>
                      <td className="cell-author">{quote.author}</td>
                      <td className="cell-text">"{quote.text}"</td>
                      <td className="cell-tags">
                        <div className="table-tags-container">
                          {quote.tags && quote.tags.length > 0 ? (
                            quote.tags.map((tag) => (
                              <span key={tag} className="tag-chip">
                                #{tag}
                              </span>
                            ))
                          ) : (
                            <span className="text-muted">—</span>
                          )}
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}

          {/* Grid View */}
          {filteredQuotes.length > 0 && viewMode === 'grid' && (
            <div className="matches-list" style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: '20px' }}>
              {filteredQuotes.map((quote) => (
                <div key={quote.id} className="quote-card">
                  <div className="quote-card-header">
                    <span className="quote-id-badge">ID: {quote.id}</span>
                    <span className="quote-author">— {quote.author}</span>
                  </div>
                  <blockquote className="quote-text">
                    "{quote.text}"
                  </blockquote>
                  {quote.tags && quote.tags.length > 0 && (
                    <div className="quote-tags">
                      {quote.tags.map((tag) => (
                        <span key={tag} className="tag-chip">
                          #{tag}
                        </span>
                      ))}
                    </div>
                  )}
                </div>
              ))}
            </div>
          )}
        </div>
      )}
    </div>
  )
}
