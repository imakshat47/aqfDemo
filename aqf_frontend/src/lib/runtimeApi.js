export async function loadJson(url) {
  const res = await fetch(url, { cache: 'no-store' })
  if (!res.ok) throw new Error(`Failed to load ${url}`)
  return await res.json()
}

export async function loadText(url) {
  const res = await fetch(url, { cache: 'no-store' })
  if (!res.ok) throw new Error(`Failed to load ${url}`)
  return await res.text()
}

export async function loadRuntimeBundle() {
  const base = '/runtime'
  const files = {
    summary: `${base}/schema_graph_summary.json`,
    topNodes: `${base}/top_nodes.json`,
    nodeScores: `${base}/node_scores.json`,
    topCandidates: `${base}/top_candidates.json`,
    canonicalForm: `${base}/canonical_form.json`,
    adaptiveForm: `${base}/adaptive_form.json`,
    fieldStatistics: `${base}/field_statistics.json`,
    previewText: `${base}/demo_preview.txt`,
    previewJson: `${base}/demo_preview.json`,
    tree: `${base}/schema_graph_tree.txt`,
  }

  const keys = Object.keys(files)
  const results = await Promise.allSettled(keys.map((k) =>
    (k === 'previewText' || k === 'tree') ? loadText(files[k]) : loadJson(files[k])
  ))

  const out = {}
  for (let i = 0; i < keys.length; i++) {
    out[keys[i]] = results[i].status === 'fulfilled' ? results[i].value : null
  }
  return out
}

export function splitPath(path = '') {
  return String(path).split(' / ').map(s => s.trim()).filter(Boolean)
}

export function deriveCatalog(fieldStatistics = []) {
  const compositions = new Map()

  for (const row of fieldStatistics) {
    const parts = splitPath(row.path)
    const composition = parts[0] || 'Unknown'
    const section = parts[1] || composition
    if (!compositions.has(composition)) {
      compositions.set(composition, {
        name: composition,
        sections: new Map(),
        fieldCount: 0,
      })
    }
    const comp = compositions.get(composition)
    const sectionKey = `${composition}||${section}`
    if (!comp.sections.has(sectionKey)) {
      comp.sections.set(sectionKey, {
        key: sectionKey,
        composition,
        label: section,
        fields: [],
      })
    }
    comp.sections.get(sectionKey).fields.push(row)
    comp.fieldCount += 1
  }

  return {
    compositions: [...compositions.values()].map((c) => ({
      ...c,
      sections: [...c.sections.values()],
    })),
  }
}

export function groupFieldsByWidget(fields = []) {
  return fields.reduce((acc, field) => {
    const widget = field.recommended_widget || 'text_input'
    if (!acc[widget]) acc[widget] = []
    acc[widget].push(field)
    return acc
  }, {})
}

export function inferDefaultFieldMode(field) {
  const widget = field.recommended_widget || 'text_input'
  const hasDistinct = Number(field.distinct_count || 0) > 0
  if (widget === 'dropdown' || widget === 'autocomplete') return { filter: true, output: true }
  if (widget === 'date_picker' || widget === 'number_input' || widget === 'checkbox') return { filter: true, output: true }
  return { filter: hasDistinct, output: true }
}

export function initialFormState(fieldStatistics = []) {
  const state = {}
  for (const f of fieldStatistics) {
    state[f.node_id] = {
      filterEnabled: inferDefaultFieldMode(f).filter,
      outputEnabled: inferDefaultFieldMode(f).output,
      operator: (f.recommended_operators && f.recommended_operators[0]) || '=',
      value: Array.isArray(f.distinct_values) && f.distinct_values.length === 1 ? f.distinct_values[0] : '',
    }
  }
  return state
}

export function buildQueryPayload({ selectedCompositions, selectedSections, fields, fieldState }) {
  const selectedSet = new Set(selectedSections)
  const compositionSet = new Set(selectedCompositions)

  const selectedFields = fields.filter((f) => {
    const parts = splitPath(f.path)
    const comp = parts[0] || 'Unknown'
    const section = parts[1] || comp
    return compositionSet.has(comp) && selectedSet.has(`${comp}||${section}`)
  })

  const filters = []
  const outputs = []
  const relations = []

  for (const field of selectedFields) {
    const state = fieldState[field.node_id] || {}
    if (state.filterEnabled) {
      filters.push({
        field_id: field.node_id,
        label: field.concept_name,
        path: field.path,
        operator: state.operator || '=',
        value: state.value,
        datatype: field.datatype,
      })
    }
    if (state.outputEnabled) {
      outputs.push({
        field_id: field.node_id,
        label: field.concept_name,
        path: field.path,
        datatype: field.datatype,
      })
    }
    relations.push({
      composition: splitPath(field.path)[0] || 'Unknown',
      section: splitPath(field.path)[1] || (splitPath(field.path)[0] || 'Unknown'),
      field: field.concept_name,
    })
  }

  return {
    selected_compositions: [...compositionSet],
    selected_sections: [...selectedSet],
    filters,
    outputs,
    relations,
  }
}

export function queryToAql(payload) {
  const filters = payload.filters || []
  const outputs = payload.outputs || []

  const select = outputs.length
    ? outputs.map((o) => `e/${o.path.replaceAll(' / ', '/')}`).join(', ')
    : 'e'

  const where = filters.length
    ? filters.map((f, idx) => `e/${f.path.replaceAll(' / ', '/')} ${f.operator || '='} $p${idx}`).join(' AND ')
    : ''

  if (!where) return `SELECT ${select} FROM EHR e`
  return `SELECT ${select} FROM EHR e WHERE ${where}`
}

export function resultColumnsFromPayload(payload) {
  return (payload.outputs || []).slice(0, 6).map((o) => ({
    key: o.field_id,
    title: o.label,
  }))
}
