import React from 'react'

const steps = [
  'Composition Selection',
  'Section Selection',
  'Form Builder',
  'Query Preview',
  'Results',
]

export default function Sidebar({ activeStep, onJump, compositions }) {
  return (
    <aside className="sidebar">
      <div>
        <div className="brand">AQF</div>
        <div className="brand-sub">Adaptive Query Forms</div>
      </div>

      <div className="side-card">
        <div className="side-card-title">Workflow</div>
        <div className="step-list">
          {steps.map((step, idx) => (
            <button
              key={step}
              className={`step-item ${activeStep === idx ? 'active' : ''}`}
              onClick={() => onJump(idx)}
            >
              <span className="step-index">{idx + 1}</span>
              <span>{step}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="side-card">
        <div className="side-card-title">Detected Compositions</div>
        <ul className="mini-list">
          {compositions.slice(0, 6).map((c) => (
            <li key={c.name}>{c.name}</li>
          ))}
        </ul>
      </div>

      <div className="sidebar-note">
        AQF UI reads runtime JSON from <code>public/runtime/</code>
      </div>
    </aside>
  )
}
