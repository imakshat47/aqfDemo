import { displayDatatypeLabel, displayFieldLabel } from '../utils/clinicalTerminology'

export default function FieldCard({ field, onChange }) {
  return (
    <div className="field-card">
      <h4>{field.displayLabel || displayFieldLabel(field.concept_name || field.label)}</h4>
      <div className="muted small">{field.displayDatatype || displayDatatypeLabel(field.datatype)}</div>
      <select onChange={(e) => onChange(field, 'operator', e.target.value)}>
        {(field.recommended_operators || []).map((op) => (
          <option key={op}>{op}</option>
        ))}
      </select>
      <input
        placeholder="Enter value"
        onChange={(e) => onChange(field, 'value', e.target.value)}
      />
      <label>
        <input
          type="checkbox"
          onChange={(e) => onChange(field, 'output', e.target.checked)}
        />
        Show in results
      </label>
    </div>
  )
}
