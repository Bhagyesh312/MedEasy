// In production the React build is served by Flask, so /api works directly.
// In dev, Vite proxies /api → http://localhost:5000 (see vite.config.js).
const BASE = '/api'

function getToken() {
  return localStorage.getItem('medeasy_token')
}

function authHeaders(extra = {}) {
  const token = getToken()
  return {
    ...(token ? { Authorization: `Bearer ${token}` } : {}),
    ...extra,
  }
}

async function handleResponse(res) {
  const data = await res.json().catch(() => ({}))
  if (!res.ok) {
    const msg = data.error || `Request failed (${res.status})`
    const err = new Error(msg)
    err.status = res.status
    throw err
  }
  return data
}

function friendlyError(err) {
  if (!navigator.onLine) return 'No internet connection.'
  if (
    err.message?.includes('Failed to fetch') ||
    err.message?.includes('NetworkError') ||
    err.message?.includes('ERR_CONNECTION_REFUSED')
  ) {
    return 'Cannot connect to server. Make sure the Flask backend is running on port 5000.'
  }
  return err.message || 'Something went wrong.'
}

export const api = {
  async register(name, email, password) {
    const res = await fetch(`${BASE}/auth/register`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ name, email, password }),
    }).catch(e => { throw new Error(friendlyError(e)) })
    return handleResponse(res)
  },

  async login(email, password) {
    const res = await fetch(`${BASE}/auth/login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ email, password }),
    }).catch(e => { throw new Error(friendlyError(e)) })
    return handleResponse(res)
  },

  async analyse(formData) {
    const res = await fetch(`${BASE}/analyse`, {
      method: 'POST',
      headers: authHeaders(),
      body: formData,
    }).catch(e => { throw new Error(friendlyError(e)) })
    return handleResponse(res)
  },

  async getReports() {
    const res = await fetch(`${BASE}/reports`, {
      headers: authHeaders(),
    }).catch(e => { throw new Error(friendlyError(e)) })
    return handleResponse(res)
  },

  async deleteReport(id) {
    const res = await fetch(`${BASE}/reports/${id}`, {
      method: 'DELETE',
      headers: authHeaders(),
    }).catch(e => { throw new Error(friendlyError(e)) })
    return handleResponse(res)
  },

  async exportPDF(reportId) {
    const res = await fetch(`${BASE}/reports/${reportId}/export`, {
      headers: authHeaders(),
    }).catch(e => { throw new Error(friendlyError(e)) })
    if (!res.ok) {
      const d = await res.json().catch(() => ({}))
      throw new Error(d.error || 'Export failed')
    }
    const blob = await res.blob()
    return URL.createObjectURL(blob)
  },

  async compare(reportA, reportB, lang = 'en') {
    const res = await fetch(`${BASE}/compare`, {
      method: 'POST',
      headers: authHeaders({ 'Content-Type': 'application/json' }),
      body: JSON.stringify({ report_a: reportA, report_b: reportB, lang }),
    }).catch(e => { throw new Error(friendlyError(e)) })
    return handleResponse(res)
  },
}
