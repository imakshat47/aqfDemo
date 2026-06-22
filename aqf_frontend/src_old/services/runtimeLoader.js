import { RUNTIME_BASE_URL } from '../config'
import { displayFieldLabel, groupFieldsBySection, normalizeCanonical } from '../utils/fieldGrouping'
import {buildClinicalTerminologyMap} from '../utils/clinicalTerminology'
async function fetchJson(path) {
  const url = `${RUNTIME_BASE_URL.replace(/\/$/, '')}/${path.replace(/^\//, '')}`
  const res = await fetch(url, { cache: 'no-store' })
  if (!res.ok) {
    throw new Error(`Failed to load ${path} (${res.status})`)
  }
  return await res.json()
}

export async function loadRuntimeData() {
  const [canonical, fieldStats, adaptive] = await Promise.allSettled([
    fetchJson('canonical_form.json'),
    fetchJson('field_statistics.json'),
    fetchJson('adaptive_form.json')
  ])

  const canonicalData = canonical.status === 'fulfilled' ? canonical.value : {}
  const fieldStatsData = fieldStats.status === 'fulfilled' ? fieldStats.value : []
  const adaptiveData = adaptive.status === 'fulfilled' ? adaptive.value : {}

  const normalizedCanonical = normalizeCanonical(canonicalData)
  const groups = groupFieldsBySection(normalizedCanonical)
  const terminologyMap = buildClinicalTerminologyMap(adaptiveData)

  // merge field stats to enrich display info and ensure we preserve raw query paths
  const statsById = new Map((Array.isArray(fieldStatsData) ? fieldStatsData : fieldStatsData?.fields || []).map((r) => [r.node_id, r]))
  const enrichedGroups = groups.map((group) => ({
    ...group,
    fields: group.fields.map((field) => {
      const stat = statsById.get(field.key) || statsById.get(field.field_id) || null
      const rawDatatype = stat?.datatype || field.datatype || 'unknown'
      return {
        ...field,
        queriability: stat?.queriability ?? field.queriability,
        coverage: stat?.coverage ?? field.coverage,
        coverage_local: stat?.coverage_local ?? field.coverage_local,
        distinct_count: stat?.distinct_count ?? field.distinct_count,
        distinct_values: Array.isArray(stat?.distinct_values) ? stat.distinct_values : field.distinct_values,
        displayLabel: terminologyMap.fieldMap[field.label] || field.displayLabel || displayFieldLabel(field.label),
        displayDatatype: terminologyMap.datatypeMap[rawDatatype] || field.displayDatatype,
        displaySectionLabel: terminologyMap.sectionMap[(String(field.path || '').split(' / ')[1] || '')] || field.displaySectionLabel,
      }
    }),
    sections: group.sections.map((section) => ({
      ...section,
      displayLabel: terminologyMap.sectionMap[section.label] || section.displayLabel || section.label.split(':').pop().trim(),
      fields: section.fields.map((field) => ({
        ...field,
        displayLabel: terminologyMap.fieldMap[field.label] || field.displayLabel || displayFieldLabel(field.label),
        displayDatatype: terminologyMap.datatypeMap[field.datatype] || field.displayDatatype,
        displayPath: field.displayPath || ''
      }))
    }))
  }))

  return {
    canonical: canonicalData,
    adaptive: adaptiveData,
    terminologyMap,
    normalizedGroups: enrichedGroups,
    fieldStatistics: Array.isArray(fieldStatsData) ? fieldStatsData : fieldStatsData?.fields || [],
  }
}

export function buildFieldIndex(groups) {
  const index = new Map()
  groups.forEach((group) => {
    (group.sections || []).forEach((section) => {
      (section.fields || []).forEach((field) => {
        const entry = {
          ...field,
          groupLabel: group.label,
          groupDisplayLabel: group.displayLabel || group.label,
          sectionLabel: section.label,
          sectionDisplayLabel: section.displayLabel || section.label,
        }
        index.set(field.key, entry)
        if (field.path) index.set(field.path, entry)
      })
    })
  })
  return index
}
