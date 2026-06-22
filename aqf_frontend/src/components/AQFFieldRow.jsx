import { useEffect, useMemo, useState } from 'react'
import { getSuggestions } from '../services/queryApi'
import { displayDatatypeLabel } from '../utils/clinicalTerminology'
import { humanizeOperator } from '../utils/operatorLabels'

function renderValueInput(
  field,
  valueState,
  onChange,
  suggestions
) {
  const datatype = (field.datatype || "").toUpperCase()

  const values =
    field.distinct_values ||
    suggestions.map((s) => s.value)

  const update = (v) =>
    onChange({
      ...valueState,
      value: v
    })

  // Replaced broken Tailwind classes with a clean, scoped custom class
  const inputClassName = "modern-input";

  //
  // DATE
  //
  if (datatype === "DV_DATE") {
    return (
      <input
        type="date"
        className={inputClassName}
        value={valueState.value || ""}
        onChange={(e) => update(e.target.value)}
      />
    )
  }

  //
  // DATETIME
  //
  if (
    datatype === "DV_DATE_TIME" ||
    datatype === "DV_DATETIME"
  ) {
    return (
      <input
        type="datetime-local"
        className={inputClassName}
        value={valueState.value || ""}
        onChange={(e) => update(e.target.value)}
      />
    )
  }

  //
  // NUMERIC
  //
  if (
    datatype === "DV_COUNT" ||
    datatype === "DV_QUANTITY"
  ) {
    return (
      <input
        type="number"
        className={inputClassName}
        step={datatype === "DV_QUANTITY" ? "0.01" : "1"}
        value={valueState.value || ""}
        placeholder="Enter value"
        onChange={(e) => update(e.target.value)}
      />
    )
  }

  //
  // BOOLEAN
  //
  if (
    values.length === 2 &&
    values.includes("true") &&
    values.includes("false")
  ) {
    return (
      <select
        className={inputClassName}
        value={valueState.value || ""}
        onChange={(e) => update(e.target.value)}
      >
        <option value="">Select...</option>
        <option value="true">Yes</option>
        <option value="false">No</option>
      </select>
    )
  }

  //
  // CODED TEXT / CATEGORY
  //
  if (
    datatype === "DV_CODED_TEXT" ||
    field.recommended_widget === "dropdown"
  ) {
    const listId = `${field.field_id}-options`

    return (
      <>
        <input
          list={listId}
          className={inputClassName}
          value={valueState.value || ""}
          placeholder="Select or type..."
          onChange={(e) => update(e.target.value)}
        />

        <datalist id={listId}>
          {values.map((v) => (
            <option key={v} value={v} />
          ))}
        </datalist>
      </>
    )
  }

  //
  // DEFAULT TEXT
  //
  return (
    <input
      type="text"
      className={inputClassName}
      value={valueState.value || ""}
      placeholder="Enter search text..."
      onChange={(e) => update(e.target.value)}
    />
  )
}


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
    // Custom inline styles clean up structural grid layout without needing heavy frameworks
    <div className="field-card" style={{ display: 'flex', flexDirection: 'column', gap: '8px', padding: '14px' }}>

      {/* Horizontal Alignment Control Bar */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px', width: '100%' }}>

        {/* Concept Label & Datatype Tag */}
        <div style={{ width: '30%', display: 'flex', flexDirection: 'column', gap: '4px' }}>
          <span style={{ fontSize: '14px', fontWeight: '600', color: '#1e293b' }}>{label}</span>
          <span style={{ fontSize: '10px', textTransform: 'uppercase', color: '#94a3b8', fontWeight: '700' }}>
            {datatype}
          </span>
        </div>

        {/* Condition Operator Selection */}
        <div style={{ width: '20%' }}>
          <select
            style={{ width: '100%', margin: 0, padding: '6px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px' }}
            value={valueState.operator}
            onChange={(e) => onChange({ ...valueState, operator: e.target.value })}
          >
            {operatorOptions.map((op) => (
              <option key={op} value={op}>{humanizeOperator(op)}</option>
            ))}
          </select>
        </div>

        {/* User Search Input Field */}
        <div style={{ width: '35%' }}>
          {renderValueInput(
            field,
            valueState,
            onChange,
            suggestions
          )}
        </div>
        {/* <div style={{ width: '35%' }}>
          <input
            style={{ width: '100%', margin: 0, padding: '6px 10px', borderRadius: '6px', border: '1px solid #cbd5e1', fontSize: '13px' }}
            type="text"
            placeholder="Enter search context..."
            value={valueState.value}
            onChange={(e) => onChange({ ...valueState, value: e.target.value })}
          />
        </div> */}

        {/* Selection Output Toggle switch layout */}
        <div style={{ width: '15%', display: 'flex', justifyContent: 'flex-end' }}>
          <label style={{ display: 'flex', alignItems: 'center', gap: '6px', cursor: 'pointer', fontSize: '12px', fontWeight: '500' }}>
            <input
              type="checkbox"
              checked={Boolean(valueState.show)}
              onChange={(e) => onChange({ ...valueState, show: e.target.checked })}
            />
            <span>Show as Output</span>
          </label>
        </div>
      </div>

      {/* Suggestion Chips Box (Renders cleanly under the main input line) */}
      {/* {suggestions.length > 0 && (
        <div className="suggestions" style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', marginTop: '4px' }}>
          {suggestions.map((s) => (
            <button
              type="button"
              key={String(s.value)}
              className="chip"
              style={{ fontSize: '11px', padding: '3px 8px', background: '#f1f5f9', border: 'none', borderRadius: '4px', cursor: 'pointer' }}
              onClick={() => onChange({ ...valueState, value: String(s.value) })}
            >
              {String(s.value)}
            </button>
          ))}
        </div>
      )} */}

      {/* {loading && <div style={{ fontSize: '11px', color: '#94a3b8', fontStyle: 'italic' }}>Loading local repository suggestions...</div>} */}
    </div>
  )
}