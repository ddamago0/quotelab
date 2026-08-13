import React, { useState } from 'react'
import { searchQuotes } from '../services/api.js'

export default function SearchTab() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)
  const [hasSearched, setHasSearched] = useState(false)

  const handleSearch = async (e) => {
    if (e) e.preventDefault()
    const cleaned = query.trim()
    if (!cleaned || loading) return

    setLoading(true)
    setError(null)
    setHasSearched(true)

    try {
      const data = await searchQuotes({ query: cleaned })
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
        <h2>Semantic Vibe Search</h2>
        <p className="tab-description">
          Search the 100-quote corpus using dense multilingual vector embeddings. Describe a personal situation, emotion, or abstract concept to find quotes matching the semantic vibe.
        </p>
      </div>

      <form className="search-form" onSubmit={handleSearch}>
        <div className="search-input-wrapper">
          <input
            type="text"
            className="search-input"
            placeholder="e.g. 'Overcoming failure and perseverance', 'El tiempo y el destino'..."
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            disabled={loading}
          />
          <button
            type="submit"
            className="btn btn-primary"
            disabled={loading || !query.trim()}
          >
            {loading ? 'Searching...' : 'Search Quotes'}
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
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Computing dense vector embedding and searching in-memory vector store...</p>
        </div>
      )}

      {/* Initial Hint State */}
      {!loading && !error && !hasSearched && (
        <div className="card hint-card">
          <h3>How Semantic Search Works</h3>
          <p>
            Unlike keyword search, semantic search converts your query into a dense 384-dimensional vector representation using <code>paraphrase-multilingual-MiniLM-L12-v2</code> and ranks quotes via cosine similarity.
          </p>
        </div>
      )}

      {/* Empty Results State */}
      {!loading && !error && hasSearched && result && result.matches.length === 0 && (
        <div className="card empty-card">
          <h3>No Semantically Similar Quotes Found</h3>
          <p>No quotes in the corpus met the search criteria for your query. Try describing your thought with different words.</p>
        </div>
      )}

      {/* Success Results List State */}
      {!loading && !error && hasSearched && result && result.matches.length > 0 && (
        <div className="results-section">
          <div className="results-meta">
            <h3>Top Matches</h3>
            <span className="results-count-badge">
              {result.total_found} {result.total_found === 1 ? 'quote' : 'quotes'} found
            </span>
          </div>

          <div className="matches-list">
            {result.matches.map((match, idx) => (
              <div key={match.quote.id || idx} className="card quote-card">
                <div className="quote-card-header">
                  <span className="quote-author">— {match.quote.author}</span>
                  <span className="similarity-badge">
                    {formatScore(match.similarity_score)} semantic match
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
