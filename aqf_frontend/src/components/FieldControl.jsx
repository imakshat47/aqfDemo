import React, { useEffect, useMemo, useState } from 'react'
import { getSuggestions } from '../services/queryApi'

const OPERATOR_LABELS = {
  'is': 'is',
  '=': 'is',
  'is not': 'is not',
  '!=': 'is not',
  'contains': 'contains text',
  'starts with': 'starts with',
  '>': 'greater than',
  '<': 'less than',
  'between': 'between'
}

export default function FieldControl({ field, valueState, onChange }) {
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let alive = true
    ;(async () => {
      setLoading(true)
      try {
        const data = await getSuggestions(field.path || field.key || field.label)
        if (!alive) return
        setSuggestions((data?.suggestions || []).slice(0, 8))
      } catch {
        if (!alive) return
      } finally {
        if (alive) setLoading(false)
      }
    })()
    return () => { alive = false }
  }, [field.path, field.key, field.label])

  const operatorOptions = useMemo(() => {
    const ops = field.recommended_operators || ['is', 'is not', 'contains', 'starts with']
    return Array.from(new Set(ops))
  }, [field.recommended_operators])

  const widget = field.recommended_widget || 'text_input'

  return (
    <div className="field-card">
      <div className="field-head">
        <div>
          <div className="field-title">{field.label}</div>
          <div className="field-sub">{field.datatype || 'unknown'}</div>
        </div>
        <span className="pill">{widget}</span>
      </div>

      <div className="field-grid">
        <label className="field-block">
          <span className="label">Condition</span>
          <select
            className="input"
            value={valueState.operator}
            onChange={(e) => onChange({ ...valueState, operator: e.target.value })}
          >
            {operatorOptions.map((op) => (
              <option key={op} value={op}>
                {OPERATOR_LABELS[op] || op}
              </option>
            ))}
          </select>
        </label>

        <label className="field-block">
          <span className="label">Value</span>
          <input
            className="input"
            list={`suggestions-${field.key}`}
            value={valueState.value}
            placeholder="Enter value"
            onChange={(e) => onChange({ ...valueState, value: e.target.value })}
          />
          <datalist id={`suggestions-${field.key}`}>
            {suggestions.map((s) => (
              <option key={String(s.value)} value={String(s.value)} />
            ))}
          </datalist>
        </label>
      </div>

      {loading ? <div className="muted small">Loading suggestions…</div> : null}

      {suggestions.length > 0 ? (
        <div className="suggestions">
          {suggestions.map((s) => (
            <button
              type="button"
              key={String(s.value)}
              className="chip"
              onClick={() => onChange({ ...valueState, value: String(s.value) })}
            >
              {String(s.value)}
            </button>
          ))}
        </div>
      ) : null}

      <label className="show-row">
        <input
          type="checkbox"
          checked={Boolean(valueState.show)}
          onChange={(e) => onChange({ ...valueState, show: e.target.checked })}
        />
        <span>Show in results</span>
      </label>
    </div>
  )
}
