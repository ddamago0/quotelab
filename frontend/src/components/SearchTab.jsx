import React, { useState } from 'react'
import { searchQuotes } from '../services/api.js'

const SAMPLE_QUERIES = [
  'Perseverance in the face of defeat and hardship',
  'Destiny vs free will and human choices',
  'The profound quiet and beauty of silence',
  'Truth, wisdom, and the search for knowledge',
]

export default function SearchTab() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e, customQuery) => {
    if (e) e.preventDefault()
    const targetQuery = (customQuery || query).trim()
    if (!targetQuery || loading) return

    if (customQuery) setQuery(customQuery)
    setLoading(true)
    setError(null)
    setHasSearched(true)

    try {
      const data = await searchQuotes({ query: targetQuery })
      setResult(data)
    } catch (err) {
      setError(err.message || 'An error occurred while executing semantic search.')
      setResult(null)
    } finally {
      setLoading(false)
    }
  }

  const formatScore = (score) => {
    const pct = (score * 100).toFixed(1)
    return `${pct}%`
  }

  return (
    <div className="search-tab-container">
      <div className="tab-header">
        <h2>[SCANNER] Semantic Discovery Engine</h2>
        <p className="tab-description">
          Search the 100-quote corpus using dense 384-dimensional vector embeddings. Describe a personal situation, emotion, or abstract concept to find quotes matching the semantic vibe.
        </p>
      </div>

      <form className="search-form" onSubmit={handleSearch}>
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder="Scan semantic concept e.g. 'Overcoming destiny', 'Silence and truth'..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !query.trim()}
          >
            {loading ? 'Scanning...' : 'Execute Scan'}
          </button>
        </div>
      </form>

      {/* Error State */}
      {error && (
        <div className="error-banner">
          <div className="error-message">
            <span>⚠️ {error}</span>
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={handleSearch}>
            Retry Scan
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>SCANNING VECTOR SPACE: Computing 384d embedding & executing cosine distance lookup...</p>
        </div>
      )}

      {/* Initial Hint State */}
      {!loading && !error && !hasSearched && (
        <div className="card hint-card">
          <h3>Search by Meaning, Not Just Words</h3>
          <p>
            QuoteLab converts your query into a dense multilingual vector representation using <code>paraphrase-multilingual-MiniLM-L12-v2</code> and ranks quotes by semantic proximity.
          </p>
          <div style={{ marginTop: '16px' }}>
            <span style={{ fontFamily: 'var(--font-mono)', fontSize: '0.8rem', color: 'var(--neon-cyan)', display: 'block', marginBottom: '10px', textTransform: 'uppercase' }}>
              ⚡ Sample Discovery Triggers:
            </span>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
              {SAMPLE_QUERIES.map((sq, i) => (
                <button
                  key={i}
                  type="button"
                  className="tag-chip"
                  style={{ cursor: 'pointer', background: 'var(--bg-surface)', border: '1px solid var(--border-neon)', color: 'var(--text-primary)' }}
                  onClick={(e) => handleSearch(e, sq)}
                >
                  "{sq}"
                </button>
              ))}
            </div>
          </div>
        </div>
      )}

      {/* Empty Results State */}
      {!loading && !error && hasSearched && result && result.matches.length === 0 && (
        <div className="card empty-card">
          <h3>No Matching Vector Nodes Found</h3>
          <p>No quotes in the corpus met the semantic similarity criteria for your query. Try describing your thought with different words.</p>
        </div>
      )}

      {/* Success Results List State */}
      {!loading && !error && hasSearched && result && result.matches.length > 0 && (
        <div className="results-section">
          <div className="results-meta">
            <h3>Top Semantic Matches</h3>
            <span className="results-count-badge">
              {result.total_found} {result.total_found === 1 ? 'NODE' : 'NODES'} MATCHED
            </span>
          </div>

          <div className="matches-list">
            {result.matches.map((match, idx) => (
              <div key={match.quote.id || idx} className="quote-card">
                <div className="quote-card-header">
                  <span className="quote-author">— {match.quote.author}</span>
                  <span className="similarity-badge">
                    {formatScore(match.similarity_score)} SEMANTIC MATCH
                  </span>
                </div>

                <blockquote className="quote-text">
                  "{match.quote.text}"
                </blockquote>

                {match.quote.tags && match.quote.tags.length > 0 && (
                  <div className="quote-tags">
                    {match.quote.tags.map((tag) => (
                      <span key={tag} className="tag-chip">
                        #{tag}
                      </span>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
