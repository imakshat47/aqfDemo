import React from 'react'

export default function CompositionSelector({
  groups,
  selectedGroups,
  selectedSections,
  onToggleGroup,
  onToggleSection
}) {
  return (
    <aside className="panel" style={{ height: '100%', margin: 0, display: 'flex', flexDirection: 'column' }}>
      <div className="panel-header" style={{ marginBottom: '16px' }}>


        <h2>1. Clinical Domains</h2>


      </div>

      <div className="stack" style={{ display: 'flex', flexDirection: 'column', gap: '8px', flex: 1, overflowY: 'auto' }}>
        {groups.map((group) => {
          const isSelected = selectedGroups.includes(group.label)
          const sectionCount = group.sections?.length || 0

          return (
            <div
              key={group.group_id}
              style={{
                border: '1px solid #e2e8f0',
                borderRadius: '8px',
                background: isSelected ? '#f8fafc' : '#ffffff',
                padding: '12px',
                transition: 'all 0.15s ease'
              }}
            >
              {/* Category Root Node */}
              <label style={{ display: 'flex', alignItems: 'flex-start', gap: '10px', cursor: 'pointer' }}>
                <input
                  type="checkbox"
                  checked={isSelected}
                  onChange={() => onToggleGroup(group.label)}
                  style={{ marginTop: '3px', accentColor: 'var(--accent)' }}
                />
                <div style={{ flex: 1 }}>
                  <div style={{ fontSize: '13px', fontWeight: '600', color: '#0f172a' }}>
                    {group.displayLabel || group.label}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--muted)', marginTop: '2px' }}>
                    {group.fields?.length || 0} form elements · {sectionCount} clinical section
                  </div>
                </div>
              </label>

              {/* Nested Child Indentation Structure */}
              {isSelected && group.sections?.length > 0 && (
                <div style={{
                  marginLeft: '8px',
                  marginTop: '10px',
                  paddingLeft: '12px',
                  borderLeft: '2px solid #e2e8f0',
                  display: 'flex',
                  flexDirection: 'column',
                  gap: '6px'
                }}>
                  {group.sections.map((section) => {
                    const isSectionChecked = selectedSections.includes(section.key)
                    return (
                      <label
                        key={section.key}
                        style={{
                          display: 'flex',
                          alignItems: 'center',
                          gap: '8px',
                          cursor: 'pointer',
                          padding: '4px 6px',
                          borderRadius: '4px',
                          background: isSectionChecked ? '#eef2f6' : 'transparent',
                          transition: 'background 0.1s ease'
                        }}
                      >
                        <input
                          type="checkbox"
                          checked={isSectionChecked}
                          onChange={() => onToggleSection(section.key)}
                          style={{ accentColor: 'var(--accent)' }}
                        />
                        <span style={{ fontSize: '12px', fontWeight: '500', color: isSectionChecked ? 'var(--accent)' : '#475569' }}>
                          {section.displayLabel || section.label}
                        </span>
                      </label>
                    )
                  })}
                </div>
              )}
            </div>
          )
        })}
      </div>
    </aside>
  )
}