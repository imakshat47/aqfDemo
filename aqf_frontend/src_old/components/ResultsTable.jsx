export default function ResultsTable({ results, fieldIndex }) {
  if (!results) return null

  const rows = results.rows || []
  const firstRow = rows.length ? (rows[0].fields || rows[0] || {}) : {}
  const columns = Object.keys(firstRow)

  const displayTitle = (col) => {
    const entry = fieldIndex?.get(col)
    return entry?.displayLabel || entry?.label || col.split(' / ').pop().trim()
  }

  return (
    <section className="panel results">
      <div className="panel-header">
        <div>
          <div className="eyebrow">Results</div>
          <h2>{results.total_matches || 0} matching records</h2>
        </div>
      </div>

      {rows.length === 0 ? (
        <div className="empty">No matching records yet.</div>
      ) : (
        <div className="table-wrap">
          <table>
            <thead>
              <tr>
                {columns.map((col) => <th key={col}>{displayTitle(col)}</th>)}
              </tr>
            </thead>
            <tbody>
              {rows.slice(0, 20).map((row, idx) => {
                const data = row.fields || row
                return (
                  <tr key={idx}>
                    {columns.map((col) => <td key={col}>{String(data?.[col] ?? '')}</td>)}
                  </tr>
                )
              })}
            </tbody>
          </table>
        </div>
      )}
    </section>
  )
}
