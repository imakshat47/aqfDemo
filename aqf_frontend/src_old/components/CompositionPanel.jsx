import React from 'react'

export default function CompositionPanel({
  compositions,
  selectedCompositions,
  onToggleComposition,
  selectedSections,
  onToggleSection
}) {
  return (
    <aside className="panel">
      <div className="panel-header">
        <div>
          <div className="eyebrow">1. Clinical domains</div>
          <h2>Repository Explorer</h2>
        </div>
      </div>

      <div className="stack">
        {compositions.map((composition) => {
          const isSelected = selectedCompositions.includes(composition.name)
          const sectionCount = composition.sections?.length || 0
          return (
            <div key={composition.name} className={`card ${isSelected ? 'card-selected' : ''}`}>
              <label className="row">
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => onToggleComposition(composition.name)}
                />
                <div>
                  <div className="card-title">{composition.name}</div>
                  <div className="muted">{composition.field_count || 0} fields · {sectionCount} sections</div>
                </div>
              </label>

              {isSelected ? (
                <div className="nested">
                  {(composition.sections || []).map((section) => {
                    const checked = selectedSections.includes(section.key)
                    return (
                      <label key={section.key} className={`section-chip ${checked ? 'section-chip-on' : ''}`}>
                        <input
                          type="checkbox"
                          checked={checked}
                          onChange={() => onToggleSection(section.key)}
                        />
                        <span>{section.label}</span>
                        <span className="tiny">{section.fields?.length || 0}</span>
                      </label>
                    )
                  })}
                </div>
              ) : null}
            </div>
          )
        })}
      </div>
    </aside>
  )
}
