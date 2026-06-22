import { displayFieldLabel, displaySectionLabel } from '../utils/clinicalTerminology'

export default function QueryPreview({
  groups,
  selectedGroups,
  selectedSections,
  fieldState,
  fieldIndex
}) {
  const lines = []
  const outputLabels = []

  groups.forEach((group) => {
    if (!selectedGroups.includes(group.label)) return
    lines.push(group.displayLabel || group.label)
    ;(group.sections || []).forEach((section) => {
      if (!selectedSections.includes(section.key)) return
      lines.push(`  ${section.displayLabel || displaySectionLabel(section.label)}`)
      ;(section.fields || []).forEach((field) => {
        const state = fieldState[field.key]
        if (!state || !state.value) return
        const label = field.displayLabel || displayFieldLabel(field.label)
        lines.push(`    ${label} ${state.operator || '='} ${state.value}`)
      })
    })
  })

  Object.entries(fieldState)
    .filter(([, v]) => v?.show)
    .forEach(([key]) => {
      const entry = fieldIndex?.get(key)
      outputLabels.push(entry?.displayLabel || entry?.label || key)
    })

  return (
    <aside className="panel">
      <div className="panel-header">
        <div>
          <div className="eyebrow">3. Query preview</div>
          <h2>Current Search</h2>
        </div>
      </div>

      <div className="stack">
        <div className="preview-box">
          <pre>{lines.length ? lines.join('\n') : 'No active criteria yet.'}</pre>
        </div>

        <div>
          <div className="subhead">Show in results</div>
          <div className="muted small">Selected output fields: {outputLabels.length}</div>
          <div className="output-list">
            {outputLabels.length ? outputLabels.map((x) => (
              <div key={x} className="output-item">{x}</div>
            )) : <div className="muted small">No output fields selected.</div>}
          </div>
        </div>
      </div>
    </aside>
  )
}
