import { useEffect, useMemo, useState } from 'react'
import CompositionSelector from './components/CompositionSelector'
import AQFFormBuilder from './components/AQFFormBuilder'
import QueryPreview from './components/QueryPreview'
import ResultsTable from './components/ResultsTable'
import { loadRuntimeData, buildFieldIndex } from './services/runtimeLoader'
import { runQuery } from './services/queryApi'
import { buildDefaultSelections } from './utils/fieldGrouping'
import './styles.css'

function buildInitialFieldState(groups) {
  const state = {}
  groups.forEach((group) => {
    (group.sections || []).forEach((section) => {
      (section.fields || []).forEach((field) => {
        state[field.key] = {
          operator: (field.allowed_operators || ['='])[0] || '=',
          value: '',
          show: false
        }
      })
    })
  })
  return state
}

function collectPayload(groups, selectedGroups, selectedSections, fieldState) {
  const conditions = []
  const return_fields = []

  groups.forEach((group) => {
    if (!selectedGroups.includes(group.label)) return
      ; (group.sections || []).forEach((section) => {
        if (!selectedSections.includes(section.key)) return
          ; (section.fields || []).forEach((field) => {
            const st = fieldState[field.key]
            if (st?.value) {
              conditions.push({
                field_path: field.path || field.label,
                operator: st.operator || '=',
                value: st.value
              })
            }
            if (st?.show) {
              return_fields.push(field.path || field.label)
            }
          })
      })
  })

  return {
    conditions,
    return_fields: return_fields.length ? return_fields : conditions.map((c) => c.field_path)
  }
}

export default function App() {
  const [groups, setGroups] = useState([])
  const [selectedGroups, setSelectedGroups] = useState([])
  const [selectedSections, setSelectedSections] = useState([])
  const [fieldState, setFieldState] = useState({})
  const [results, setResults] = useState(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    let alive = true
      ; (async () => {
        try {
          const data = await loadRuntimeData()
          if (!alive) return
          setGroups(data.normalizedGroups)

          const defaults = buildDefaultSelections(data.normalizedGroups)
          setSelectedGroups(defaults.selectedGroups)
          setSelectedSections(defaults.selectedSections)
          setFieldState(buildInitialFieldState(data.normalizedGroups))
        } catch (e) {
          if (!alive) return
          setError(e?.message || 'Failed to load AQF runtime.')
        } finally {
          if (alive) setLoading(false)
        }
      })()

    return () => { alive = false }
  }, [])

  const fieldIndex = useMemo(() => buildFieldIndex(groups), [groups])

  const activeFieldCount = useMemo(() => {
    let count = 0
    groups.forEach((group) => {
      if (!selectedGroups.includes(group.label)) return
        ; (group.sections || []).forEach((section) => {
          if (!selectedSections.includes(section.key)) return
          count += (section.fields || []).length
        })
    })
    return count
  }, [groups, selectedGroups, selectedSections])

  const toggleGroup = (label) => {
    setSelectedGroups((prev) => {
      const next = prev.includes(label) ? prev.filter((x) => x !== label) : [...prev, label]
      return next
    })
  }

  const toggleSection = (key) => {
    setSelectedSections((prev) => prev.includes(key) ? prev.filter((x) => x !== key) : [...prev, key])
  }

  const changeFieldState = (key, next) => {
    setFieldState((prev) => ({
      ...prev,
      [key]: next
    }))
  }

  const handleRunQuery = async () => {
    try {
      const payload = collectPayload(groups, selectedGroups, selectedSections, fieldState)
      const data = await runQuery(payload)
      setResults(data)
    } catch (e) {
      setResults({
        total_matches: 0,
        rows: [],
        error: e?.message || 'Query execution failed'
      })
    }
  }

  if (loading) {
    return <div className="loading">Loading AQF runtime…</div>
  }

  if (error && groups.length === 0) {
    return <div className="error-box">{error}</div>
  }

  return (
    <div style={{ display: 'flex', flexDirection: 'column', minHeight: '100vh', backgroundColor: 'var(--bg)' }}>
      {/* 1. Global Enterprise Top Navigation Bar */}
      <header style={{
        height: '60px',
        backgroundColor: '#ffffff',
        borderBottom: '1px solid var(--line)',
        display: 'flex',
        alignItems: 'center',
        justifyContent: 'space-between',
        padding: '0 24px',
        position: 'sticky',
        top: 0,
        zIndex: 1000,
        boxShadow: '0 1px 2px 0 rgba(0, 0, 0, 0.02)'
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
          <div style={{ fontWeight: '700', fontSize: '16px', color: 'var(--text)', letterSpacing: '-0.3px' }}>
            Adaptive Query Form <span style={{ color: 'var(--accent)', fontWeight: '500' }}> (AQF)</span>
          </div>
          <span style={{ width: '1px', height: '16px', background: 'var(--line)' }}></span>
          <nav style={{ display: 'flex', gap: '24px' }}>
            <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--accent)', cursor: 'pointer' }}>Query Workspace</span>
            <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--muted)', cursor: 'pointer' }}>Database Exploration</span>
            <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--muted)', cursor: 'pointer' }}>Query Logs</span>
          </nav>
        </div>

        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '11px', fontWeight: '600', color: '#0f766e', background: '#ccfbf1', padding: '4px 10px', borderRadius: '12px', textTransform: 'uppercase' }}>
            openEHR ORBDA Environment
          </span>
        </div>
      </header>


      <div className="app-shell">
        <CompositionSelector
          groups={groups}
          selectedGroups={selectedGroups}
          selectedSections={selectedSections}
          onToggleGroup={toggleGroup}
          onToggleSection={toggleSection}
        />

        <AQFFormBuilder
          groups={groups}
          selectedGroups={selectedGroups}
          selectedSections={selectedSections}
          fieldState={fieldState}
          onChangeFieldState={changeFieldState}
          onRunQuery={handleRunQuery}
        />

        <QueryPreview
          groups={groups}
          selectedGroups={selectedGroups}
          selectedSections={selectedSections}
          fieldState={fieldState}
          fieldIndex={fieldIndex}
        />

        <div className="results-row">
          <ResultsTable results={results} fieldIndex={fieldIndex} />
        </div>

        <div className="footer-note">
          Adaptive Query Form (AQF) · {groups.length} compositions · {activeFieldCount} active fields
        </div>
      </div>
    </div>
  )
}
