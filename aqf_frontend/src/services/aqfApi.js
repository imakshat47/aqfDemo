
import { API_BASE_URL } from "../config";

export const api = {
  getForms: async () => fetch(`${API_BASE_URL}/forms`).then(r=>r.json()),
  getSuggestions: async (field) =>
    fetch(`${API_BASE_URL}/query/suggestions/${encodeURIComponent(field)}`).then(r=>r.json()),
  runQuery: async (payload) =>
    fetch(`${API_BASE_URL}/search`,{
      method:"POST",
      headers:{"Content-Type":"application/json"},
      body:JSON.stringify(payload)
    }).then(r=>r.json())
};
