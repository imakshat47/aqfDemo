import React from 'react'
import ToggleChip from './ToggleChip'

export default function SelectionStep({ title, subtitle, items, selectedKeys, onToggleAll }) {
  return (
    <div className="step-panel">
      <div className="step-panel-head">
        <div>
          <h3>{title}</h3>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
        {onToggleAll ? <button className="ghost-btn" onClick={onToggleAll}>Toggle all</button> : null}
      </div>

      <div className="selection-grid">
        {items.map((item) => {
          const checked = selectedKeys.includes(item.key)
          return (
            <label key={item.key} className={`selection-card ${checked ? 'selected' : ''}`}>
              <input
                type="checkbox"
                checked={checked}
                onChange={() => item.onToggle(item.key)}
              />
              <div>
                <div className="selection-title">{item.label}</div>
                <div className="selection-meta">{item.meta}</div>
              </div>
            </label>
          )
        })}
      </div>
    </div>
  )
}
