import AQFFieldRow from './AQFFieldRow'

export default function AQFFormBuilder({
  groups,
  selectedGroups,
  selectedSections,
  fieldState,
  onChangeFieldState,
  onRunQuery
}) {
  const visibleSections = []

  groups.forEach((group) => {
    if (!selectedGroups.includes(group.label)) return
    ;(group.sections || []).forEach((section) => {
      if (!selectedSections.includes(section.key)) return
      visibleSections.push({
        groupLabel: group.displayLabel || group.label,
        sectionLabel: section.displayLabel || section.label,
        sectionKey: section.key,
        fields: section.fields || []
      })
    })
  })

  return (
    <main className="workspace">
      <div className="panel">
        <div className="panel-header">
          <div>
            <div className="eyebrow">2. Adaptive query form</div>
            <h2>Form Builder</h2>
          </div>
          <div className="muted">{visibleSections.length} active sections</div>
        </div>

        <div className="stack">
          {visibleSections.length === 0 ? (
            <div className="empty">
              Select at least one clinical domain and section to build the form.
            </div>
          ) : visibleSections.map((sectionGroup) => (
            <section key={sectionGroup.sectionKey} className="group">
              <div className="group-header">
                <div>
                  <div className="group-title">{sectionGroup.sectionLabel}</div>
                  <div className="muted">{sectionGroup.groupLabel}</div>
                </div>
                <div className="tiny">{sectionGroup.fields.length} fields</div>
              </div>

              <div className="fields">
                {sectionGroup.fields.map((field) => (
                  <AQFFieldRow
                    key={field.key}
                    field={field}
                    valueState={fieldState[field.key] || { operator: field.allowed_operators?.[0] || '=', value: '', show: false }}
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
