import { useEffect, useMemo, useState } from 'react'
import CompositionSelector from './components/CompositionSelector'
import AQFFormBuilder from './components/AQFFormBuilder'
import QueryPreview from './components/QueryPreview'
import ResultsTable from './components/ResultsTable'
import { loadRuntimeData, buildFieldIndex } from './services/runtimeLoader'
import { runQuery } from './services/queryApi'
import { buildDefaultSelections } from './utils/fieldGrouping'
import './styles.css'

// Helper function to establish initial form state values
function buildInitialFieldState(groups) {
  const state = {}
  const safeGroups = Array.isArray(groups) ? groups : []
  safeGroups.forEach((group) => {
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

// Helper function to assemble JSON payloads for openEHR queries
function collectPayload(groups, selectedGroups, selectedSections, fieldState) {
  const conditions = []
  const return_fields = []
  const safeGroups = Array.isArray(groups) ? groups : []

  safeGroups.forEach((group) => {
    if (!selectedGroups.includes(group.label)) return
    ;(group.sections || []).forEach((section) => {
      if (!selectedSections.includes(section.key)) return
      ;(section.fields || []).forEach((field) => {
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
  return { conditions, return_fields }
}

export default function App() {
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [groups, setGroups] = useState([])
  const [selectedGroups, setSelectedGroups] = useState([])
  const [selectedSections, setSelectedSections] = useState([])
  const [fieldState, setFieldState] = useState({})
  const [results, setResults] = useState(null)

  // Guarded tracking index to ensure buildFieldIndex ALWAYS receives an array
  const fieldIndex = useMemo(() => {
    const safeGroups = Array.isArray(groups) ? groups : []
    return buildFieldIndex(safeGroups)
  }, [groups])

  // Lifecycle initialization logic with defensive structure normalization
  useEffect(() => {
    async function init() {
      try {
        setLoading(true)
        const data = await loadRuntimeData()
        
        // Extract the nested array safely regardless of how the backend packages it
        const groupsArray = Array.isArray(data)
          ? data
          : (data?.groups || data?.compositions || data?.forms || [])

        setGroups(groupsArray)
        
        const defaults = buildDefaultSelections(groupsArray)
        setSelectedGroups(defaults.selectedGroups || [])
        setSelectedSections(defaults.selectedSections || [])
        setFieldState(buildInitialFieldState(groupsArray))
      } catch (err) {
        setError(err.message || 'Failed to load configuration data.')
      } window.setTimeout(() => setLoading(false), 50)
    }
    init()
  }, [])

  const activeFieldCount = useMemo(() => {
    return Object.values(fieldState).filter(f => f.value || f.show).length
  }, [fieldState])

  const toggleGroup = (groupLabel) => {
    setSelectedGroups(prev =>
      prev.includes(groupLabel) ? prev.filter(g => g !== groupLabel) : [...prev, groupLabel]
    )
  }

  const toggleSection = (sectionKey) => {
    setSelectedSections(prev =>
      prev.includes(sectionKey) ? prev.filter(s => s !== sectionKey) : [...prev, sectionKey]
    )
  }

  const changeFieldState = (fieldKey, nextState) => {
    setFieldState(prev => ({
      ...prev,
      [fieldKey]: nextState
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
    return (
      <div style={{ display: 'flex', justifyContent: 'center', alignItems: 'center', height: '100vh', fontFamily: 'sans-serif', color: 'var(--muted)', background: 'var(--bg)' }}>
        Loading AQF runtime workspace…
      </div>
    )
  }

  if (error && groups.length === 0) {
    return (
      <div style={{ padding: '24px', margin: '24px', background: '#fef2f2', border: '1px solid #fecaca', color: '#991b1b', borderRadius: '8px', fontFamily: 'sans-serif' }}>
        <strong>Initialization Error:</strong> {error}
      </div>
    )
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
            AQF <span style={{ color: 'var(--accent)', fontWeight: '500' }}>Console</span>
          </div>
          <span style={{ width: '1px', height: '16px', background: 'var(--line)' }}></span>
          <nav style={{ display: 'flex', gap: '24px' }}>
            <span style={{ fontSize: '13px', fontWeight: '600', color: 'var(--accent)', cursor: 'pointer' }}>Query Workspace</span>
            <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--muted)', cursor: 'pointer' }}>Data Dictionary</span>
            <span style={{ fontSize: '13px', fontWeight: '500', color: 'var(--muted)', cursor: 'pointer' }}>Query Logs</span>
          </nav>
        </div>
        
        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
          <span style={{ fontSize: '11px', fontWeight: '600', color: '#0f766e', background: '#ccfbf1', padding: '4px 10px', borderRadius: '12px', textTransform: 'uppercase' }}>
            openEHR Production Environment
          </span>
        </div>
      </header>

      {/* 2. Responsive Layout Shell */}
      <div className="app-shell" style={{ display: 'grid', gridTemplateColumns: '320px 1fr 340px', gap: '16px', padding: '16px', flex: 1 }}>
        
        {/* Left Explorer Column */}
        <div style={{ position: 'sticky', top: '76px', maxHeight: 'calc(100vh - 92px)', overflowY: 'auto' }}>
          <CompositionSelector
            groups={groups}
            selectedGroups={selectedGroups}
            selectedSections={selectedSections}
            onToggleGroup={toggleGroup}
            onToggleSection={toggleSection}
          />
        </div>

        {/* Middle Builder Workspace Column */}
        <div>
          <AQFFormBuilder
            groups={groups}
            selectedGroups={selectedGroups}
            selectedSections={selectedSections}
            fieldState={fieldState}
            onChangeFieldState={changeFieldState}
            onRunQuery={handleRunQuery}
          />
        </div>

        {/* Right JSON Criteria Column */}
        <div style={{ position: 'sticky', top: '76px', maxHeight: 'calc(100vh - 92px)', overflowY: 'auto' }}>
          <QueryPreview
            groups={groups}
            selectedGroups={selectedGroups}
            selectedSections={selectedSections}
            fieldState={fieldState}
            fieldIndex={fieldIndex}
          />
        </div>

        {/* Full-width Search Matches Runway */}
        <div className="results-row" style={{ gridColumn: '1 / -1', marginTop: '8px' }}>
          <ResultsTable results={results} fieldIndex={fieldIndex} />
        </div>

        {/* Workspace Stats Footer */}
        <div className="footer-note" style={{ gridColumn: '1 / -1', textAlign: 'center', color: 'var(--muted)', fontSize: '12px', padding: '16px 0' }}>
          AQF Runtime Platform · {groups.length} compositions · {activeFieldCount} active fields
        </div>

      </div>
    </div>
  )
}