import { API_BASE_URL } from '../config'

export async function runQuery(payload) {
  const res = await fetch(`${API_BASE_URL.replace(/\/$/, '')}/query/search`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    },
    body: JSON.stringify(payload)
  })

  if (!res.ok) {
    const text = await res.text()
    throw new Error(text || `Query failed (${res.status})`)
  }

  return await res.json()
}

export async function getSuggestions(fieldPath) {
  try {
    const res = await fetch(
      `${API_BASE_URL.replace(/\/$/, '')}/query/suggestions/${encodeURIComponent(fieldPath)}`,
      { cache: 'no-store' }
    )
    if (!res.ok) return { suggestions: [] }
    return await res.json()
  } catch {
    return { suggestions: [] }
  }
}
