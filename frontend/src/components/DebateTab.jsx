import React, { useState } from 'react'
import { generateDebate } from '../services/api.js'

export default function DebateTab() {
  const [topic, setTopic] = useState('')
  const [minScore, setMinScore] = useState(0.4)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [debate, setDebate] = useState(null)
  const [hasGenerated, setHasGenerated] = useState(false)

  const handleSubmit = async (e) => {
    if (e) e.preventDefault()
    const cleanedTopic = topic.trim()
    if (!cleanedTopic || loading) return

    setLoading(true)
    setError(null)
    setHasGenerated(true)

    try {
      const payload = {
        topic: cleanedTopic,
        min_evidence_score: Number(minScore),
      }
      const data = await generateDebate(payload)
      setDebate(data)
    } catch (err) {
      setError(err.message || 'An error occurred while generating the debate.')
      setDebate(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="debate-tab-container">
      <div className="tab-header">
        <h2>[ARENA] Evidence-Backed Debate Synthesizer</h2>
        <p className="tab-description">
          Synthesize multi-perspective philosophical arguments strictly grounded in verbatim quotes from the dataset. If evidence is insufficient, the system enforces a controlled refusal.
        </p>
      </div>

      {/* RAG Process Flow Visualizer */}
      <div className="debate-flow-stepper">
        <div className="flow-step active">
          <span className="flow-step-num">1</span>
          <span>Topic Input</span>
        </div>
        <span className="flow-arrow">➔</span>
        <div className="flow-step active">
          <span className="flow-step-num">2</span>
          <span>Dense Vector Retrieval</span>
        </div>
        <span className="flow-arrow">➔</span>
        <div className="flow-step active">
          <span className="flow-step-num">3</span>
          <span>Grounded Synthesis</span>
        </div>
        <span className="flow-arrow">➔</span>
        <div className="flow-step active">
          <span className="flow-step-num">4</span>
          <span>Refusal Verification</span>
        </div>
      </div>

      <form className="debate-form" onSubmit={handleSubmit}>
        <div className="form-group">
          <label htmlFor="topic-input" className="form-label">
            Debate Topic or Philosophical Question
          </label>
          <input
            id="topic-input"
            type="text"
            className="debate-input"
            placeholder="e.g. 'Is human destiny predetermined or shaped by free will?'..."
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            disabled={loading}
          />
        </div>

        <div className="form-row">
          <div className="form-group score-slider-group">
            <label htmlFor="score-slider" className="form-label">
              Minimum Evidence Relevance Threshold: <strong>{(minScore * 100).toFixed(0)}%</strong>
            </label>
            <div className="slider-wrapper">
              <input
                id="score-slider"
                type="range"
                min="0.0"
                max="0.9"
                step="0.05"
                className="score-slider"
                value={minScore}
                onChange={(e) => setMinScore(parseFloat(e.target.value))}
                disabled={loading}
              />
              <span className="slider-hint">Higher values enforce stricter evidence matching and refusal triggers</span>
            </div>
          </div>

          <button
            type="submit"
            className="btn btn-primary generate-btn"
            disabled={loading || !topic.trim()}
          >
            {loading ? 'Synthesizing...' : 'Synthesize Debate'}
          </button>
        </div>
      </form>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <div className="error-message">
            <span>⚠️ {error}</span>
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={handleSubmit}>
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>SYNTHESIZING DEBATE: Retrieving relevant quotes & generating grounded multi-perspective arguments...</p>
        </div>
      )}

      {/* Initial Hint State */}
      {!loading && !error && !hasGenerated && (
        <div className="card hint-card">
          <h3>Grounding & Anti-Hallucination Invariants</h3>
          <p>
            The debate engine uses <strong>RAG (Retrieval-Augmented Generation)</strong> to retrieve corpus quotes matching your topic. LLM-generated arguments are strictly validated against quote IDs to prevent hallucinated citations.
          </p>
        </div>
      )}

      {/* Controlled Refusal / Insufficient Evidence State */}
      {!loading && !error && hasGenerated && debate && !debate.sufficient_evidence && (
        <div className="refusal-banner">
          <div className="refusal-header">
            <span className="refusal-icon">🛑</span>
            <div>
              <h3>EVIDENCE THRESHOLD NOT REACHED</h3>
              <p className="refusal-text">
                {debate.refusal_message ||
                  `No quotes in the repository met the minimum similarity score threshold of ${(minScore * 100).toFixed(0)}% for topic "${debate.topic}".`}
              </p>
            </div>
          </div>
          <div className="refusal-suggestion">
            💡 <em>Try lowering the minimum evidence relevance threshold slider or rephrasing your debate topic.</em>
          </div>
        </div>
      )}

      {/* Generated Debate Results State */}
      {!loading && !error && hasGenerated && debate && debate.sufficient_evidence && (
        <div className="debate-results">
          {/* Multi-Perspective Arguments */}
          <div className="arguments-section">
            <div className="section-meta">
              <h3>Synthesized Perspectives</h3>
              <span className="badge-count">
                {debate.arguments.length} {debate.arguments.length === 1 ? 'PERSPECTIVE' : 'PERSPECTIVES'}
              </span>
            </div>

            <div className="arguments-grid">
              {debate.arguments.map((arg, idx) => (
                <div key={idx} className="card argument-card">
                  <div className="argument-header">
                    <span className="position-badge">{arg.position}</span>
                    {arg.evidence_quote_ids && arg.evidence_quote_ids.length > 0 && (
                      <div className="citation-badges">
                        {arg.evidence_quote_ids.map((qid) => (
                          <span key={qid} className="citation-chip">
                            CIT: {qid}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                  <p className="argument-text">{arg.argument_text}</p>
                </div>
              ))}
            </div>
          </div>

          {/* Grounding Evidence Quotes Corpus List */}
          {debate.evidence_quotes && debate.evidence_quotes.length > 0 && (
            <div className="evidence-section">
              <div className="section-meta">
                <h3>Grounding Evidence Quotes</h3>
                <span className="badge-count">
                  {debate.evidence_quotes.length} {debate.evidence_quotes.length === 1 ? 'QUOTE CITED' : 'QUOTES CITED'}
                </span>
              </div>

              <div className="evidence-list">
                {debate.evidence_quotes.map((quote) => (
                  <div key={quote.id} className="quote-card evidence-quote-card">
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
            </div>
          )}
        </div>
      )}
    </div>
  )
}
