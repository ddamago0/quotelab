import React from 'react'

export default function PlaceholderView({ title, description, icon }) {
  return (
    <div className="card placeholder-card">
      <div className="placeholder-header">
        <span className="placeholder-icon">{icon || '⚡'}</span>
        <div>
          <h2>{title}</h2>
          <p className="placeholder-description">{description}</p>
        </div>
      </div>
      <div className="placeholder-badge-container">
        <span className="placeholder-badge">Step 1 Navigation Placeholder — View Implementation Pending</span>
      </div>
    </div>
  )
}
