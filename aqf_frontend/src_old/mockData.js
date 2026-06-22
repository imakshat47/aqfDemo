export const mockRuntime = {
  summary: {
    records: 75,
    node_count: 26,
    edge_count: 257,
    demographic_units: 50,
    composition_like_units: 100,
  },
  fieldStatistics: [
    {
      node_id: 'Hospitalisation__Admin_Entry:_Patient_admission__Tree__Admission_type',
      concept_name: 'Admission type',
      path: 'Hospitalisation / Admin Entry: Patient admission / Tree / Admission type',
      datatype: 'DV_CODED_TEXT',
      node_type: 'leaf',
      coverage_global: 0.3333,
      coverage_local: 1.0,
      coverage: 0.8667,
      diversity: 0.08,
      distinct_count: 3,
      distinct_values: ['Elective', 'Emergency', 'Transfer'],
      total_records: 25,
      queriability: 1.21,
      recommended_widget: 'dropdown',
    },
    {
      node_id: 'Demographic_data__Admin_Entry:_Demographic_data__components__gender',
      concept_name: 'gender',
      path: 'Demographic data / Admin Entry: Demographic data / components / gender',
      datatype: 'DV_CODED_TEXT',
      node_type: 'leaf',
      coverage_global: 0.3333,
      coverage_local: 1.0,
      coverage: 0.8667,
      diversity: 0.08,
      distinct_count: 2,
      distinct_values: ['Male', 'Female'],
      total_records: 25,
      queriability: 1.14,
      recommended_widget: 'dropdown',
    },
    {
      node_id: 'Hospitalisation__Evaluation:_Problem_Diagnosis__structure__Secondary_Diagnosis',
      concept_name: 'Secondary Diagnosis',
      path: 'Hospitalisation / Evaluation: Problem/Diagnosis / structure / Secondary Diagnosis',
      datatype: 'DV_CODED_TEXT',
      node_type: 'leaf',
      coverage_global: 0.3333,
      coverage_local: 1.0,
      coverage: 0.8667,
      diversity: 0.12,
      distinct_count: 5,
      distinct_values: ['C20', 'C509', '0000', 'C34', 'C61'],
      total_records: 25,
      queriability: 1.79,
      recommended_widget: 'autocomplete',
    },
  ],
  canonicalForm: {
    form_id: 'mock',
    groups: [
      {
        group_id: 'group_hospitalisation',
        label: 'Hospitalisation',
        fields: [
          { field_id: 'f1', label: 'Patient class', path: 'Hospitalisation / Admin Entry: Patient admission / Tree / Patient class', datatype: 'DV_TEXT', queriability: 1.0, allowed_operators: ['='], metadata: {} },
          { field_id: 'f2', label: 'Admission type', path: 'Hospitalisation / Admin Entry: Patient admission / Tree / Admission type', datatype: 'DV_CODED_TEXT', queriability: 1.2, allowed_operators: ['=', '!='], metadata: {} },
        ]
      }
    ]
  },
  adaptiveForm: {
    form_id: 'mock_form',
    title: 'AQF Adaptive Form',
    complexity: 3,
    metadata: { source: 'mock' },
    elements: [
      {
        field_id: 'f1',
        label: 'Admission type',
        path: 'Hospitalisation / Admin Entry: Patient admission / Tree / Admission type',
        datatype: 'DV_CODED_TEXT',
        allowed_operators: ['=', '!='],
        queriability: 1.2,
        role: 'filter',
        metadata: {}
      },
      {
        field_id: 'f2',
        label: 'gender',
        path: 'Demographic data / Admin Entry: Demographic data / components / gender',
        datatype: 'DV_CODED_TEXT',
        allowed_operators: ['=', '!='],
        queriability: 1.14,
        role: 'filter',
        metadata: {}
      }
    ]
  },
  previewText: `AQF Demo Preview
==================

Repository summary:
- Records: 75
- Nodes: 26
- Edges: 257
- Demographic units: 50
- Composition-like units: 100`,
}

export const emptyFieldStatistics = []
