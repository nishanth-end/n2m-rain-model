/**
 * N²M Flood Prediction Model — API Client
 * Centralized fetch service for the Bengaluru Flood Susceptibility Backend.
 */

const API_BASE = import.meta.env.VITE_API_BASE_URL || 'http://127.0.0.1:8000';

async function fetchJson(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const response = await fetch(url, {
      ...options,
      headers: {
        'Accept': 'application/json',
        ...(options.headers || {}),
      },
    });

    if (!response.ok) {
      let errorDetail = `HTTP ${response.status} ${response.statusText}`;
      try {
        const errorJson = await response.json();
        if (errorJson.detail) {
          errorDetail = typeof errorJson.detail === 'string' ? errorJson.detail : JSON.stringify(errorJson.detail);
        }
      } catch {
        // Not JSON
      }
      throw new Error(errorDetail);
    }

    return await response.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

export const api = {
  getBaseUrl() {
    return API_BASE;
  },

  async getHealth() {
    return fetchJson('/');
  },

  async getAbout() {
    return fetchJson('/api/about');
  },

  async getDates() {
    return fetchJson('/api/dates');
  },

  async getRisk(date, { level = null, limit = null } = {}) {
    const params = new URLSearchParams({ date });
    if (level) params.append('level', level);
    if (limit) params.append('limit', limit);
    return fetchJson(`/api/risk?${params.toString()}`);
  },

  async getLatestRisk({ level = null, limit = null } = {}) {
    const params = new URLSearchParams();
    if (level) params.append('level', level);
    if (limit) params.append('limit', limit);
    const qs = params.toString() ? `?${params.toString()}` : '';
    return fetchJson(`/api/risk/latest${qs}`);
  },

  async getSummary(date) {
    const params = new URLSearchParams({ date });
    return fetchJson(`/api/summary?${params.toString()}`);
  },

  async getTelegramPreview(date) {
    const params = new URLSearchParams({ date });
    return fetchJson(`/api/telegram/demo-preview?${params.toString()}`);
  },

  async getPipelineStatus() {
    return fetchJson('/api/pipeline/status');
  },
};
