/**
 * N²M Flood Prediction Model — API Client
 * Centralized fetch service for the Bengaluru Flood Susceptibility Backend.
 */

const rawBase = import.meta.env.VITE_API_BASE_URL;
// In production, VITE_API_BASE_URL points to the deployed backend (e.g. https://my-backend.onrender.com).
// Strip any trailing slashes to prevent malformed double-slash endpoints.
const API_BASE = rawBase ? rawBase.trim().replace(/\/+$/, '') : 'http://127.0.0.1:8000';

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

  async getTelegramStatus() {
    return fetchJson('/api/telegram/status');
  },

  async sendTelegramDemo(date, chatId = null) {
    return fetchJson('/api/telegram/send-demo', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ date, chat_id: chatId }),
    });
  },

  async getPipelineStatus() {
    return fetchJson('/api/pipeline/status');
  },

  async getLatestRainfall(forceRefresh = false) {
    const qs = forceRefresh ? '?force_refresh=true' : '';
    return fetchJson(`/api/rainfall/latest${qs}`);
  },

  async getRainfallStatus() {
    return fetchJson('/api/rainfall/status');
  },
};
