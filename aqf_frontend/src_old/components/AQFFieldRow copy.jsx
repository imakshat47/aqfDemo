import { useEffect, useMemo, useState } from 'react'
import { getSuggestions } from '../services/queryApi'
import { displayDatatypeLabel, rawToDisplayPath } from '../utils/clinicalTerminology'
import { humanizeOperator } from "../utils/operatorLabels";

export default function AQFFieldRow({ field, valueState, onChange }) {
  const [suggestions, setSuggestions] = useState([])
  const [loading, setLoading] = useState(false)

  useEffect(() => {
    let alive = true
      ; (async () => {
        setLoading(true)
        try {
          const data = await getSuggestions(field.path || field.label)
          if (!alive) return
          const list = Array.isArray(data?.suggestions) ? data.suggestions : []
          setSuggestions(list.slice(0, 8))
        } finally {
          if (alive) setLoading(false)
        }
      })()
    return () => { alive = false }
  }, [field.path, field.label])

  const operatorOptions = useMemo(() => {
    const ops = field.allowed_operators || ['=', '!=', 'contains', 'starts_with']
    return Array.from(new Set(ops))
  }, [field.allowed_operators])

  const label = field.displayLabel || field.label
  const datatype = field.displayDatatype || displayDatatypeLabel(field.datatype)

  return (
    <div className="field-card">
      <div className="field-head">
        <div>
          <div className="field-title">{label}</div>
          <div className="field-sub">{datatype}</div>
        </div>
        {/* <span className="pill">{field.recommended_widget || 'text_input'}</span> */}
      </div>

      <div className="muted small" style={{ marginBottom: 10, display: 'none' }}>
        {field.displayPath || rawToDisplayPath(field.path)}
      </div>

      <div className="field-grid">

        <label className="field-block">
          <span className="label">Condition</span>
          <select
            className="input"
            value={valueState.operator || operatorOptions[0] || '='}
            onChange={(e) => onChange({ ...valueState, operator: e.target.value })}
          >
            {operatorOptions.map((op) => (
              <option key={op} value={op}>
                {humanizeOperator(op)}
              </option>
            ))}
          </select>
        </label>

        <label className="field-block">
          <span className="label">Value</span>
          <input
            className="input"
            list={`values-${field.key}`}
            value={valueState.value || ''}
            placeholder="Enter value"
            onChange={(e) => onChange({ ...valueState, value: e.target.value })}
          />
          <datalist id={`values-${field.key}`}>
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

      <label
        key={label}
        className={`section-chip ${valueState.show ? 'section-chip-on' : ''}`}
      >
        <input type="checkbox" checked={Boolean(valueState.show)} onChange={(e) => onChange({ ...valueState, show: e.target.checked, })} />
        <span>Show in results</span>
      </label>
      {/* <label key={label}  className={`section-chip ${e.target.checked ? 'section-chip-on' : ''}`}>
        <input
          type="checkbox"
          checked={Boolean(valueState.show)}
          onChange={(e) => onChange({ ...valueState, show: e.target.checked, className.add(section-chip-on) })}
        />
        <span>Show in results</span>
      </label> */}
    </div>
  )
}

//  <label key={section.key} className={`section-chip ${checked ? 'section-chip-on' : ''}`}>
//                         <input
//                           type="checkbox"
//                           checked={checked}
//                           onChange={() => onToggleSection(section.key)}
//                         />
//                         <span>{section.displayLabel || section.label}</span>
//                         {/* <span className="tiny">{section.fields?.length || 0}</span> */}
//                       </label>

