import React from 'react'

export default function Panel({ title, subtitle, children, right }) {
  return (
    <section className="panel">
      <div className="panel-head">
        <div>
          <h2>{title}</h2>
          {subtitle ? <p>{subtitle}</p> : null}
        </div>
        {right ? <div className="panel-right">{right}</div> : null}
      </div>
      <div className="panel-body">{children}</div>
    </section>
  )
}
