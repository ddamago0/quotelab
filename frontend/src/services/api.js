/**
 * Centralized API client service wrapping backend REST endpoints using native Fetch API.
 * Leverages Vite proxy for '/api' paths without hardcoding hostnames.
 */

async function request(endpoint, options = {}) {
  const config = {
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
    ...options,
  }

  try {
    const response = await fetch(endpoint, config)
    const data = await response.json().catch(() => ({}))

    if (!response.ok) {
      const errorMessage = data.detail || `Request failed with HTTP ${response.status}`
      const error = new Error(errorMessage)
      error.status = response.status
      error.data = data
      throw error
    }

    return data
  } catch (err) {
    if (err.status) throw err
    const networkError = new Error('Unable to connect to QuoteLab API backend.')
    networkError.status = 0
    throw networkError
  }
}

/**
 * Health check endpoint: GET /api/health
 */
export async function getHealth() {
  return request('/api/health')
}

/**
 * Semantic quote search endpoint: POST /api/search
 * @param {Object} payload - { query: string }
 */
export async function searchQuotes(payload) {
  return request('/api/search', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

/**
 * Evidence-backed debate generation endpoint: POST /api/debate
 * @param {Object} payload - { topic: string, min_evidence_score?: number }
 */
export async function generateDebate(payload) {
  return request('/api/debate', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}

/**
 * Budget & batching optimization endpoint: POST /api/batch
 * @param {Object} payload - { quote_ids?: string[], max_units_per_batch?: number }
 */
export async function createBatches(payload = {}) {
  return request('/api/batch', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
}
