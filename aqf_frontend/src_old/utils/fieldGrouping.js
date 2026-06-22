import {
  displayCompositionLabel,
  displayDatatypeLabel,
  displayFieldLabel,
  displayPathLabel,
  displaySectionLabel,
  simplifySectionForQuery,
} from './clinicalTerminology'

export {
  displayCompositionLabel,
  displayDatatypeLabel,
  displayFieldLabel,
  displayPathLabel,
  displaySectionLabel,
  simplifySectionForQuery,
};

export function safeArray(value) {
  return Array.isArray(value) ? value : []
}

export function normalizeCanonical(canonical) {
  const groups = safeArray(canonical?.groups || canonical?.compositions || canonical?.forms)
  return groups.map((group) => {
    const rawGroupLabel = group.label || group.name || 'Unknown'
    return {
      group_id: group.group_id || group.id || `group_${String(rawGroupLabel).replace(/\s+/g, '_')}`,
      label: rawGroupLabel,
      displayLabel: displayCompositionLabel(rawGroupLabel),
      fields: safeArray(group.fields).map((field) => {
        const rawLabel = field.label || field.concept_name || field.name || 'Field'
        const rawPath = field.path || ''
        const rawDatatype = field.datatype || 'unknown'
        const allowedOperators = safeArray(field.allowed_operators || field.recommended_operators)
        const distinctValues = safeArray(field.distinct_values || field.examples)

        return {
          ...field,
          key: field.field_id || field.node_id || field.key || `${rawGroupLabel}::${rawLabel}`,
          label: rawLabel,
          displayLabel: displayFieldLabel(rawLabel),
          path: rawPath,
          displayPath: displayPathLabel(rawPath),
          datatype: rawDatatype,
          displayDatatype: displayDatatypeLabel(rawDatatype),
          allowed_operators: allowedOperators,
          distinct_values: distinctValues,
          recommended_widget: field.recommended_widget || field.widget || 'text_input',
          displaySectionLabel: displaySectionLabel((String(rawPath).split(' / ')[1] || '')),
        }
      })
    }
  })
}

export function groupFieldsBySection(groups) {
  return groups.map((group) => {
    const sections = new Map()

    safeArray(group.fields).forEach((field) => {
      const parts = String(field.path || '').split(' / ').map((x) => x.trim()).filter(Boolean)
      const sectionRaw = parts.length >= 2 ? parts[1] : 'General'
      const sectionLabel = sectionRaw
      if (!sections.has(sectionLabel)) {
        sections.set(sectionLabel, [])
      }
      sections.get(sectionLabel).push({
        ...field,
        displaySectionLabel: displaySectionLabel(sectionRaw),
        displayPath: displayPathLabel(field.path || '')
      })
    })

    const sectionList = Array.from(sections.entries()).map(([label, fields]) => ({
      key: `${group.group_id || group.label}||${label}`,
      label,
      displayLabel: simplifySectionForQuery(label),
      fields,
    }))

    return {
      ...group,
      displayLabel: displayCompositionLabel(group.label),
      sections: sectionList
    }
  })
}

export function buildDefaultSelections(groups) {
  return {
    selectedGroups: groups.map((g) => g.label),
    selectedSections: groups.flatMap((g) => (g.sections || []).map((s) => s.key))
  }
}
