import React, { useMemo, useState } from 'react'
import { groupFieldsByWidget } from '../lib/runtimeApi'
import { displayDatatypeLabel, displayFieldLabel, displayPathLabel } from '../utils/clinicalTerminology'

function ValueList({ values = [] }) {
  const [query, setQuery] = useState('')
  const filtered = useMemo(() => {
    const q = query.trim().toLowerCase()
    if (!q) return values
    return values.filter(v => String(v).toLowerCase().includes(q))
  }, [query, values])

  return (
    <div className="value-list">
      <input
        className="input"
        placeholder="Search values..."
        value={query}
        onChange={(e) => setQuery(e.target.value)}
      />
      <div className="chips">
        {filtered.slice(0, 12).map((v) => (
          <span key={String(v)} className="chip">{String(v)}</span>
        ))}
      </div>
    </div>
  )
}

function FieldControl({ field }) {
  const widget = field.recommended_widget || 'text_input'
  const label = field.displayLabel || displayFieldLabel(field.concept_name || field.label)
  const datatype = field.displayDatatype || displayDatatypeLabel(field.datatype)
  return (
    <div className="field-control">
      <div className="field-top">
        <div>
          <div className="field-label">{label}</div>
          <div className="field-meta">{field.displayPath || displayPathLabel(field.path)}</div>
        </div>
        <span className="badge">{widget}</span>
      </div>

      <div className="field-row">
        {widget === 'dropdown' || widget === 'autocomplete' ? (
          <select className="input">
            <option>Select value</option>
            {(field.distinct_values || []).slice(0, 40).map((v) => (
              <option key={String(v)}>{String(v)}</option>
            ))}
          </select>
        ) : widget === 'date_picker' ? (
          <input className="input" type="date" />
        ) : widget === 'number_input' ? (
          <input className="input" type="number" placeholder="Enter number" />
        ) : widget === 'checkbox' ? (
          <label className="checkbox">
            <input type="checkbox" />
            <span>{label}</span>
          </label>
        ) : (
          <input className="input" type="text" placeholder="Enter text" />
        )}
      </div>

      {field.distinct_values && field.distinct_values.length > 0 ? (
        <ValueList values={field.distinct_values} />
      ) : null}

      <div className="field-foot">
        <span>{datatype}</span>
        <span>cov {Number(field.coverage ?? 0).toFixed(2)}</span>
        <span>q {Number(field.queriability ?? 0).toFixed(2)}</span>
        <span>distinct {field.distinct_count ?? 0}</span>
      </div>
    </div>
  )
}

export default function FormPreview({ form }) {
  const grouped = useMemo(() => groupFieldsByWidget(form?.elements || []), [form])
  const total = form?.elements?.length || 0

  if (!form) {
    return <div className="empty-state">No adaptive form loaded.</div>
  }

  return (
    <div className="form-preview">
      <div className="form-summary">
        <div>
          <h3>{form.title || 'AQF Adaptive Form'}</h3>
          <p>{total} elements · complexity {form.complexity ?? 0}</p>
        </div>
        <div className="summary-tags">
          {Object.entries(grouped).map(([widget, items]) => (
            <span key={widget} className="chip">
              {widget}: {items.length}
            </span>
          ))}
        </div>
      </div>

      <div className="form-grid">
        {(form.elements || []).map((field) => (
          <FieldControl key={field.field_id || field.path} field={field} />
        ))}
      </div>
    </div>
  )
}
