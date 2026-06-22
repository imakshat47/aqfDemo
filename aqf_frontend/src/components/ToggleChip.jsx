import React from 'react'

export default function ToggleChip({ checked, onChange, children, className = '' }) {
  return (
    <button
      type="button"
      className={`toggle-chip ${checked ? 'checked' : ''} ${className}`}
      onClick={onChange}
    >
      {checked ? '✓' : '○'} {children}
    </button>
  )
}
