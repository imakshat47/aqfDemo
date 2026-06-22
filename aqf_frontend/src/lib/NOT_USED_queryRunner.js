export async function runQueryAgainstBackend(payload) {
  const base = import.meta.env.VITE_AQF_API_BASE
  if (!base) return null

  const res = await fetch(`${base.replace(/\/$/, '')}/query/run`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload),
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || 'Query execution failed')
  }

  return await res.json()
}
