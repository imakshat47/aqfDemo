import React, { useState, useMemo, useEffect } from 'react'

export default function ResultsTable({ results, fieldIndex }) {
  const [viewMode, setViewMode] = useState('table') // 'table' or 'card'
  const [currentPage, setCurrentPage] = useState(1)
  // 1. New Sort State
  const [sortConfig, setSortConfig] = useState({ key: null, direction: 'ascending' }) 
  const rowsPerPage = 10

  const rows = results?.rows || []
  const totalRows = rows.length
  const totalPages = Math.ceil(totalRows / rowsPerPage)

  // 2. Reset pagination AND sorting if a completely new query is run
  useEffect(() => {
    setCurrentPage(1)
    setSortConfig({ key: null, direction: 'ascending' })
  }, [results])

  const firstRow = rows.length ? (rows[0].fields || rows[0] || {}) : {}
  const columns = Object.keys(firstRow)

  const displayTitle = (col) => {
    const entry = fieldIndex?.get(col)
    return entry?.displayLabel || entry?.label || col.split(' / ').pop().trim()
  }

  // 3. Sorting Handler
  const handleSort = (key) => {
    let direction = 'ascending'
    if (sortConfig.key === key && sortConfig.direction === 'ascending') {
      direction = 'descending'
    }
    setSortConfig({ key, direction })
    setCurrentPage(1) // Return to first page when sorting changes
  }

  // 4. Memoize the Sorted AND Sliced data for the current page
  const currentData = useMemo(() => {
    let sortableRows = [...rows]

    // Apply sorting first
    if (sortConfig.key !== null) {
      sortableRows.sort((a, b) => {
        const valA = (a.fields || a)[sortConfig.key] ?? ''
        const valB = (b.fields || b)[sortConfig.key] ?? ''
        
        // Handle numeric sorting gracefully if the strings are actually numbers
        const numA = Number(valA);
        const numB = Number(valB);
        if (!isNaN(numA) && !isNaN(numB)) {
          return sortConfig.direction === 'ascending' ? numA - numB : numB - numA;
        }

        // Standard string sorting
        if (valA < valB) return sortConfig.direction === 'ascending' ? -1 : 1
        if (valA > valB) return sortConfig.direction === 'ascending' ? 1 : -1
        return 0
      })
    }

    // Then slice for pagination
    const start = (currentPage - 1) * rowsPerPage
    return sortableRows.slice(start, start + rowsPerPage)
  }, [rows, sortConfig, currentPage, rowsPerPage])

  if (!results) return null

  return (
    <section className="panel results-panel" style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
      
      {/* Header & Controls */}
      <div className="panel-header" style={{ marginBottom: 0, display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
        <div>
          <h2>4. Query Output</h2>
          {/* <div className="eyebrow" style={{ color: 'var(--accent)', fontWeight: '700', fontSize: '11px', textTransform: 'uppercase', letterSpacing: '0.5px' }}>
            Query Output
          </div> */}
          <h4 style={{ margin: '4px 0 0 24px', color: 'var(--accent)'}}>
            {results.total_matches || totalRows} matches found
          </h4>
        </div>

        {/* View Toggle Group */}
        {totalRows > 0 && (
          <div className="view-toggle">
            <button 
              className={viewMode === 'table' ? 'active' : ''} 
              onClick={() => setViewMode('table')}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="3" y1="12" x2="21" y2="12"></line><line x1="3" y1="6" x2="21" y2="6"></line><line x1="3" y1="18" x2="21" y2="18"></line></svg>
              Table
            </button>
            <button 
              className={viewMode === 'card' ? 'active' : ''} 
              onClick={() => setViewMode('card')}
            >
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><rect x="3" y="3" width="7" height="7"></rect><rect x="14" y="3" width="7" height="7"></rect><rect x="14" y="14" width="7" height="7"></rect><rect x="3" y="14" width="7" height="7"></rect></svg>
              Cards
            </button>
          </div>
        )}
      </div>

      {totalRows === 0 ? (
        <div style={{ padding: '32px', textAlign: 'center', color: '#94a3b8', fontStyle: 'italic', background: '#f8fafc', borderRadius: '8px', border: '1px dashed #cbd5e1' }}>
          No matching records found for the current criteria.
        </div>
      ) : (
        <>
          {/* Main Content Area */}
          {viewMode === 'table' ? (
            <div className="modern-table-wrap">
              <table className="modern-table">
                <thead>
                  <tr>
                    {/* 5. Update Table Headers to be Clickable with Arrows */}
                    {columns.map((col) => (
                      <th 
                        key={col} 
                        onClick={() => handleSort(col)}
                        className="sortable-header"
                        title={`Sort by ${displayTitle(col)}`}
                      >
                        <div style={{ display: 'flex', alignItems: 'center', gap: '6px' }}>
                          {displayTitle(col)}
                          <span className="sort-icon" style={{ opacity: sortConfig.key === col ? 1 : 0.2 }}>
                            {sortConfig.key === col && sortConfig.direction === 'descending' ? '↓' : '↑'}
                          </span>
                        </div>
                      </th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {currentData.map((row, idx) => {
                    const data = row.fields || row
                    return (
                      <tr key={idx}>
                        {columns.map((col) => <td key={col}>{String(data?.[col] ?? '-')}</td>)}
                      </tr>
                    )
                  })}
                </tbody>
              </table>
            </div>
          ) : (
            <div className="modern-card-grid">
              {currentData.map((row, idx) => {
                const data = row.fields || row
                return (
                  <div key={idx} className="modern-data-card">
                    {columns.map((col) => (
                      <div key={col} className="card-field-row">
                        <span className="card-label">{displayTitle(col)}</span>
                        <span className="card-value">{String(data?.[col] ?? '-')}</span>
                      </div>
                    ))}
                  </div>
                )
              })}
            </div>
          )}

          {/* Pagination Controls */}
          {totalPages > 1 && (
            <div className="pagination-bar">
              <span className="page-info">
                Showing <strong style={{ color: '#0f172a' }}>{((currentPage - 1) * rowsPerPage) + 1}</strong> to <strong style={{ color: '#0f172a' }}>{Math.min(currentPage * rowsPerPage, totalRows)}</strong> of <strong style={{ color: '#0f172a' }}>{totalRows}</strong> records
              </span>
              
              <div className="page-controls">
                <button 
                  onClick={() => setCurrentPage(p => Math.max(1, p - 1))} 
                  disabled={currentPage === 1}
                >
                  Previous
                </button>
                <span className="page-tracker">Page {currentPage} of {totalPages}</span>
                <button 
                  onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))} 
                  disabled={currentPage === totalPages}
                >
                  Next
                </button>
              </div>
            </div>
          )}
        </>
      )}
    </section>
  )
}