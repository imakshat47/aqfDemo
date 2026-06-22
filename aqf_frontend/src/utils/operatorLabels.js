export const OPERATOR_LABELS = {
  '=': 'is',
  '!=': 'is not',
  'contains': 'contains text',
  'starts_with': 'starts with',
  'starts with': 'starts with',
  '>': 'greater than',
  '<': 'less than',
  '>=': 'greater than or equal',
  '<=': 'less than or equal',
  'between': 'between',
  'before': 'before',
  'after': 'after'
}

export function humanizeOperator(op) {
  return OPERATOR_LABELS[op] || op || 'is'
}
