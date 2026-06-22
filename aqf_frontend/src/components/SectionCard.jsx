import React from 'react'

export default function SectionCard({ title, subtitle, children, actions }) {
  return (
    <div className="section-card">
      <div className="section-card-head">
        <div>
          <h3>{title}</h3>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
        {actions ? <div>{actions}</div> : null}
      </div>
      <div className="section-card-body">{children}</div>
    </div>
  )
}
