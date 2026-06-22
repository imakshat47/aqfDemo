import React, { useMemo } from 'react'
import FieldControl from './FieldControl'

export default function AdaptiveForm({
  compositions,
  selectedCompositions,
  selectedSections,
  fieldState,
  onChangeFieldState,
  onRunQuery
}) {
  const visible = useMemo(() => {
    const result = []
    compositions.forEach((composition) => {
      if (!selectedCompositions.includes(composition.name)) return
      const sections = composition.sections || []
      sections.forEach((section) => {
        if (!selectedSections.includes(section.key)) return
        result.push({
          composition: composition.name,
          sectionLabel: section.label,
          sectionKey: section.key,
          fields: section.fields || []
        })
      })
    })
    return result
  }, [compositions, selectedCompositions, selectedSections])

  return (
    <main className="workspace">
      <div className="panel">
        <div className="panel-header">
          <div>
            <div className="">2. Adaptive form</div>
            <h2>Query Builder</h2>
          </div>
          <div className="muted">{visible.length} active sections</div>
        </div>

        <div className="stack">
          {visible.length === 0 ? (
            <div className="empty">
              Select one or more clinical domains and sections to generate the query form.
            </div>
          ) : visible.map((sectionGroup) => (
            <section key={sectionGroup.sectionKey} className="group">
              <div className="group-header">
                <div>
                  <div className="group-title">{sectionGroup.sectionLabel}</div>
                  <div className="muted">{sectionGroup.composition}</div>
                </div>
                <div className="tiny">{sectionGroup.fields.length} fields</div>
              </div>

              <div className="fields">
                {sectionGroup.fields.map((field) => (
                  <FieldControl
                    key={field.key}
                    field={field}
                    valueState={fieldState[field.key] || { operator: field.recommended_operators?.[0] || 'is', value: '', show: false }}
                    onChange={(next) => onChangeFieldState(field.key, next)}
                  />
                ))}
              </div>
            </section>
          ))}
        </div>

        <div className="runbar">
          <button className="primary" onClick={onRunQuery}>
            Search records
          </button>
        </div>
      </div>
    </main>
  )
}
