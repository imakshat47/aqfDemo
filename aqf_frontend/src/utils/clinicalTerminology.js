const SECTION_LABEL_MAP = {
  'Admin Entry: Demographic data': 'Demographic Data',
  'Admin Entry: Patient admission': 'Patient Admission',
  'Admin Entry: Patient discharge': 'Patient Discharge',
  'Admin Entry: Authorization for hospital admission': 'Hospital Admission Authorization',
  'Admin Entry: HCPA': 'High Complexity Procedure Administration',
  'Evaluation: Problem/Diagnosis': 'Diagnosis',
  'Action: Procedure undertaken': 'Procedure',
}

const COMPOSITION_LABEL_MAP = {
  'Demographic data': 'Demographic',
  'Hospitalisation': 'Hospitalisation',
  'Outpatient high complexity procedures': 'Out-Patient Department',
}

const FIELD_LABEL_MAP = {
  'race': 'Race',
  'ethnic group': 'Ethnic Group',
  'birth date': 'Birth Date',
  'gender': 'Gender',
  'educational level': 'Educational Level',
  'nationality': 'Nationality',
  'hospital infection': 'Hospital Infection',
  'patient class': 'Patient Class',
  'claim reason': 'Claim Reason',
  'death indicator': 'Death Indicator',
  'date of discharge': 'Date of Discharge',
  'issue date': 'Issue Date',
  'ICU - Total': 'ICU Total',
  'Universal ID': 'Facility Identifier',
  'State/province': 'State',
  'Admission type': 'Admission Type',
  'Hospital service': 'Hospital Service',
  'Admit date/time': 'Admit Date/Time',
  'Problem': 'Problem',
  'Secondary Diagnosis': 'Additional Diagnosis',
  'Procedure': 'Procedure',
  'state': 'State',
  'schema': 'Treatment Schema',
  'duration of treatment': 'Treatment Duration',
  'reason for encounter': 'Reason for Encounter',
  'healthcare unit': 'Healthcare Unit',
  'patient age': 'Patient Age',
  'Clinical staging': 'Clinical Stage',
  'Histopathological grading (G)': 'Histopathological Grade (G)',
  'topography': 'Tumour Topography',
  'date of pathological identification': 'Pathological Identification Date',
  'Associated causes': 'Associated Causes',
  'Invaded regional linphonodes': 'Regional Lymph Node Involvement',
  'Assigned patient location': 'Assigned Patient Location',
  'General data': 'General Data',
  'components': 'Clinical Components',
  'structure': 'Clinical Structure',
  'tree': 'Clinical Tree',
}

const DATATYPE_LABEL_MAP = {
  DV_CODED_TEXT: 'Clinical Category',
  DV_TEXT: 'Text',
  DV_DATE: 'Date',
  DV_DATE_TIME: 'Date & Time',
  DV_QUANTITY: 'Numberic',
  DV_COUNT: 'Numberic',
  DV_BOOLEAN: 'Yes / No',
  DV_ORDINAL: 'Clinical Scale',
  DV_IDENTIFIER: 'Identifier',
  unknown: 'Clinical Value',
}

const ACRONYM_MAP = {
  HCPA: 'High Complexity Procedure Administration',
  ICU: 'Intensive Care Unit',
  TNM: 'Tumour Staging',
}

function titleCase(value = '') {
  return String(value)
    .replace(/[\/_-]+/g, ' ')
    .replace(/\s+/g, ' ')
    .trim()
    .replace(/\b\w/g, (m) => m.toUpperCase())
}

function normalizeKey(value = '') {
  return String(value).trim().toLowerCase()
}

function mapExact(map, value) {
  const hit = map[value]
  if (hit) return hit
  const lower = normalizeKey(value)
  for (const [k, v] of Object.entries(map)) {
    if (normalizeKey(k) === lower) return v
  }
  return null
}

export function displayCompositionLabel(rawLabel = '') {
  return mapExact(COMPOSITION_LABEL_MAP, rawLabel) || titleCase(rawLabel)
}

export function displaySectionLabel(rawLabel = '') {
  if (!rawLabel) return 'Section'
  const exact = mapExact(SECTION_LABEL_MAP, rawLabel)
  if (exact) return exact

  let label = String(rawLabel).trim()
  if (label.includes(':')) {
    label = label.split(':').pop().trim()
  }
  if (label.includes('/')) {
    label = label.split('/').pop().trim()
  }
  const acronym = mapExact(ACRONYM_MAP, label)
  if (acronym) return acronym

  return titleCase(label)
}

export function displayFieldLabel(rawLabel = '') {
  if (!rawLabel) return 'Field'
  const exact = mapExact(FIELD_LABEL_MAP, rawLabel)
  if (exact) return exact

  const acronym = mapExact(ACRONYM_MAP, rawLabel)
  if (acronym) return acronym

  return titleCase(rawLabel)
}

export function displayDatatypeLabel(rawDatatype = '') {
  return mapExact(DATATYPE_LABEL_MAP, rawDatatype) || titleCase(rawDatatype || 'Clinical Value')
}

export function displayPathLabel(path = '') {
  const parts = String(path).split(' / ').map((s) => s.trim()).filter(Boolean)
  if (!parts.length) return ''
  const [composition, ...rest] = parts
  const displayParts = [displayCompositionLabel(composition)]
  for (const seg of rest) {
    if (['components', 'structure', 'tree'].includes(normalizeKey(seg))) continue
    if (/^admin entry:/i.test(seg) || /^evaluation:/i.test(seg) || /^action:/i.test(seg)) {
      displayParts.push(displaySectionLabel(seg))
      continue
    }
    if (/^[a-z]/.test(seg) || seg.includes('-') || seg.includes('(') || seg.includes('/')) {
      displayParts.push(displayFieldLabel(seg))
      continue
    }
    displayParts.push(titleCase(seg))
  }
  return displayParts.join(' / ')
}

export function simplifySectionForQuery(rawLabel = '') {
  if (!rawLabel) return ''
  const exact = mapExact(SECTION_LABEL_MAP, rawLabel)
  if (exact) return exact
  let label = String(rawLabel).trim()
  if (label.includes(':')) {
    label = label.split(':').pop().trim()
  }
  if (label.includes('/')) {
    label = label.split('/').pop().trim()
  }
  return label
}

export function buildClinicalTerminologyMap(adaptiveForm = {}) {
  const sectionMap = {}
  const fieldMap = {}
  const datatypeMap = {}

  for (const el of adaptiveForm?.elements || []) {
    const path = String(el.path || '')
    const parts = path.split(' / ').map((s) => s.trim()).filter(Boolean)
    const section = parts[1] || ''
    if (section) {
      sectionMap[section] = displaySectionLabel(section)
    }
    if (el.label) {
      fieldMap[el.label] = displayFieldLabel(el.label)
    }
    if (el.datatype) {
      datatypeMap[el.datatype] = displayDatatypeLabel(el.datatype)
    }
  }

  return {
    sectionMap,
    fieldMap,
    datatypeMap,
    compositionMap: COMPOSITION_LABEL_MAP,
  }
}

export function mapClinicalPresentation(value, type = 'field') {
  if (type === 'section') return displaySectionLabel(value)
  if (type === 'datatype') return displayDatatypeLabel(value)
  if (type === 'composition') return displayCompositionLabel(value)
  return displayFieldLabel(value)
}

export function rawToDisplayPath(path = '') {
  return displayPathLabel(path)
}
