import React from 'react'

export default function JsonPanel({ title, data, compact = false }) {
  return (
    <div className={`json-panel ${compact ? 'compact' : ''}`}>
      <div className="json-panel-title">{title}</div>
      <pre>{typeof data === 'string' ? data : JSON.stringify(data, null, 2)}</pre>
    </div>
  )
}
