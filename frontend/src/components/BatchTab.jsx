import React, { useState } from 'react'
import { createBatches } from '../services/api.js'

export default function BatchTab() {
  const [maxUnits, setMaxUnits] = useState(500)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [validationError, setValidationError] = useState(null)
  const [receipt, setReceipt] = useState(null)
  const [hasOptimized, setHasOptimized] = useState(false)

  const handleOptimize = async (e) => {
    if (e) e.preventDefault()
    
    // Validation
    const parsedUnits = parseInt(maxUnits, 10)
    if (isNaN(parsedUnits) || parsedUnits <= 0) {
      setValidationError('Maximum units per batch must be a positive integer greater than 0.')
      return
    }

    setValidationError(null)
    setLoading(true)
    setError(null)
    setHasOptimized(true)

    try {
      const payload = {
        max_units_per_batch: parsedUnits,
      }
      const data = await createBatches(payload)
      setReceipt(data)
    } catch (err) {
      setError(err.message || 'An error occurred while optimizing quote batches.')
      setReceipt(null)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="batch-tab-container">
      <div className="tab-header">
        <h2>Budget & Batching Optimizer</h2>
        <p className="tab-description">
          Optimally pack quote items into token/unit constrained batches using a deterministic First-Fit Greedy algorithm to maximize throughput within model context limits.
        </p>
      </div>

      <form className="batch-form" onSubmit={handleOptimize}>
        <div className="form-row">
          <div className="form-group capacity-input-group">
            <label htmlFor="max-units-input" className="form-label">
              Max Units Capacity Per Batch
            </label>
            <input
              id="max-units-input"
              type="number"
              min="1"
              step="1"
              className={`batch-input ${validationError ? 'input-error' : ''}`}
              placeholder="e.g. 500"
              value={maxUnits}
              onChange={(e) => {
                setMaxUnits(e.target.value)
                if (validationError) setValidationError(null)
              }}
              disabled={loading}
            />
            {validationError && <span className="field-error-text">{validationError}</span>}
          </div>

          <button
            type="submit"
            className="btn btn-primary optimize-btn"
            disabled={loading}
          >
            {loading ? 'Optimizing...' : 'Create & Optimize Batches'}
          </button>
        </div>
      </form>

      {/* Error Banner */}
      {error && (
        <div className="error-banner">
          <div className="error-message">
            <span>⚠️ {error}</span>
          </div>
          <button type="button" className="btn btn-secondary btn-sm" onClick={handleOptimize}>
            Retry
          </button>
        </div>
      )}

      {/* Loading State */}
      {loading && (
        <div className="loading-state">
          <div className="spinner"></div>
          <p>Calculating quote unit counts and packing batches using First-Fit Greedy algorithm...</p>
        </div>
      )}

      {/* Initial Hint State */}
      {!loading && !error && !hasOptimized && (
        <div className="card hint-card">
          <h3>How Batching Optimization Works</h3>
          <p>
            Each quote's unit consumption is measured deterministically. Quotes are packed sequentially into batches without exceeding the configured unit capacity limit. Any individual item that exceeds capacity alone is moved to <code>failed_items</code>.
          </p>
        </div>
      )}

      {/* Results State */}
      {!loading && !error && hasOptimized && receipt && (
        <div className="batch-results">
          {/* Summary KPIs */}
          <div className="kpi-grid">
            <div className="card kpi-card">
              <span className="kpi-label">Items Processed</span>
              <span className="kpi-value">{receipt.total_items_processed}</span>
            </div>
            <div className="card kpi-card">
              <span className="kpi-label">Total Units Consumed</span>
              <span className="kpi-value">{receipt.total_units_consumed.toLocaleString()}</span>
            </div>
            <div className="card kpi-card">
              <span className="kpi-label">Batches Created</span>
              <span className="kpi-value">{receipt.total_batches_created}</span>
            </div>
            <div className="card kpi-card">
              <span className="kpi-label">Max Capacity / Batch</span>
              <span className="kpi-value">{receipt.max_units_per_request} units</span>
            </div>
          </div>

          {/* Failed Items Warning Banner */}
          {receipt.failed_items && receipt.failed_items.length > 0 && (
            <div className="failed-banner">
              <div className="failed-header">
                <span className="failed-icon">⚠️</span>
                <div>
                  <h3>Oversized Items Notice</h3>
                  <p>
                    {receipt.failed_items.length} {receipt.failed_items.length === 1 ? 'item' : 'items'} exceeded the batch capacity limit of {receipt.max_units_per_request} units on their own and could not be packed:
                  </p>
                </div>
              </div>
              <div className="failed-tags">
                {receipt.failed_items.map((itemId) => (
                  <span key={itemId} className="failed-chip">
                    {itemId}
                  </span>
                ))}
              </div>
            </div>
          )}

          {/* Generated Batches Visualization */}
          <div className="batches-section">
            <div className="section-meta">
              <h3>Generated Batches Summary</h3>
              <span className="badge-count">
                {receipt.batches.length} {receipt.batches.length === 1 ? 'batch' : 'batches'}
              </span>
            </div>

            <div className="batches-grid">
              {receipt.batches.map((b) => {
                const fillPercentage = Math.min(100, (b.total_units / receipt.max_units_per_request) * 100).toFixed(1)
                return (
                  <div key={b.batch_id} className="card batch-card">
                    <div className="batch-card-header">
                      <span className="batch-title">Batch #{b.batch_id}</span>
                      <span className="batch-capacity-badge">
                        {b.total_units} / {receipt.max_units_per_request} units ({fillPercentage}%)
                      </span>
                    </div>

                    <div className="progress-bar-container">
                      <div
                        className="progress-bar-fill"
                        style={{ width: `${fillPercentage}%` }}
                      ></div>
                    </div>

                    <div className="batch-items-details">
                      <span className="items-header">{b.items.length} items included:</span>
                      <div className="batch-items-chips">
                        {b.items.map((item) => (
                          <span key={item.quote_id} className="item-chip">
                            {item.quote_id} ({item.unit_count} u)
                          </span>
                        ))}
                      </div>
                    </div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
