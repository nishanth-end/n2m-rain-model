/**
 * Common JavaScript for Predictive Flood Alert System
 * Handles API calls, persistent synthetic warnings, navigation, and reusable rainfall controls.
 */

// ONE constant for the API base URL. Change here if pointing at a hosted backend.
const API_BASE = "";

// 4 Standard Presets for the 10-day rainfall input (oldest Day -9 -> newest Today)
const RAINFALL_PRESETS = {
  dry: {
    label: "Dry week",
    values: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
  },
  light: {
    label: "Light rain",
    values: [2, 3, 1, 4, 2, 5, 3, 4, 6, 5]
  },
  storm: {
    label: "Heavy storm",
    values: [5, 10, 8, 15, 20, 35, 60, 85, 110, 140]
  },
  sept2022: {
    label: "Sept 2022-style storm",
    values: [0, 0, 5, 2, 8, 12, 25, 45, 131, 142]
  }
};

/**
 * Safely escape dynamic text before injecting into innerHTML
 */
function escapeHTML(str) {
  if (str === null || str === undefined) return "";
  return String(str)
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

/**
 * Standard fetch wrapper with centralized error handling
 */
async function fetchAPI(endpoint, options = {}) {
  const url = `${API_BASE}${endpoint}`;
  try {
    const res = await fetch(url, options);
    if (!res.ok) {
      let detail = `Server returned HTTP ${res.status}`;
      try {
        const errorData = await res.json();
        if (errorData && errorData.detail) {
          if (Array.isArray(errorData.detail)) {
            detail = errorData.detail.map(d => d.msg || JSON.stringify(d)).join("; ");
          } else {
            detail = errorData.detail;
          }
        }
      } catch (e) {
        // Not a JSON response
      }
      throw new Error(detail);
    }
    return await res.json();
  } catch (err) {
    console.error(`API Error on ${endpoint}:`, err);
    throw err;
  }
}

/**
 * Get visual styling parameters for a given risk band
 */
function getRiskBandMeta(band) {
  const b = (band || "").toLowerCase();
  switch (b) {
    case "low":
      return { color: "#3fae5a", label: "Low", class: "low" };
    case "moderate":
      return { color: "#e6b800", label: "Moderate", class: "moderate" };
    case "high":
      return { color: "#e67e22", label: "High", class: "high" };
    case "severe":
      return { color: "#e04545", label: "Severe", class: "severe" };
    default:
      return { color: "#9db0c4", label: "Unknown", class: "unknown" };
  }
}

/**
 * Initialize persistent banner across all pages
 */
async function initSyntheticBanner() {
  const bannerContainer = document.getElementById("synthetic-banner-container");
  if (!bannerContainer) return;

  try {
    const health = await fetchAPI("/api/health");
    if (health.is_synthetic) {
      bannerContainer.innerHTML = `
        <div class="synthetic-banner" role="alert">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
            <path d="M12 2L1 21h22L12 2zm1 14h-2v-2h2v2zm0-4h-2V8h2v4z"/>
          </svg>
          <span><strong>Notice:</strong> Demo model trained on <strong>SYNTHETIC</strong> data — predictions are not real flood forecasts and will not match the documented 2022 floods.</span>
        </div>
      `;
    }
  } catch (e) {
    console.warn("Could not check synthetic data status:", e);
    // Display banner by default as safety precaution
    bannerContainer.innerHTML = `
      <div class="synthetic-banner" role="alert">
        <svg width="18" height="18" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2L1 21h22L12 2zm1 14h-2v-2h2v2zm0-4h-2V8h2v4z"/>
        </svg>
        <span><strong>Notice:</strong> Demo model trained on <strong>SYNTHETIC</strong> data — predictions are not real flood forecasts and will not match the documented 2022 floods.</span>
      </div>
    `;
  }
}

/**
 * Setup navigation active state
 */
function highlightActiveNav() {
  const path = window.location.pathname.toLowerCase();
  const navLinks = document.querySelectorAll("nav.main-nav a");
  navLinks.forEach(link => {
    const href = link.getAttribute("href").toLowerCase();
    if (
      (path.endsWith("/") || path.endsWith("/index.html")) && (href === "/" || href === "index.html" || href === "/index.html")
    ) {
      link.classList.add("active");
    } else if (href.length > 1 && path.includes(href.replace(/^\//, ""))) {
      link.classList.add("active");
    } else {
      link.classList.remove("active");
    }
  });
}

/**
 * Render the reusable 10-day rainfall input component
 */
function renderRainfallComponent(containerId, initialValues, onChangeCallback) {
  const container = document.getElementById(containerId);
  if (!container) return;

  const currentValues = [...(initialValues || RAINFALL_PRESETS.storm.values)];

  let daysHtml = "";
  for (let i = 0; i < 10; i++) {
    const dayOffset = i - 9;
    const isToday = i === 9;
    const label = isToday ? "Today" : `Day ${dayOffset}`;
    daysHtml += `
      <div class="rain-day-cell ${isToday ? 'today' : ''}">
        <label for="rain-day-${i}">${label}</label>
        <input type="number" id="rain-day-${i}" data-index="${i}" min="0" max="500" step="1" value="${currentValues[i]}" aria-label="${label} rainfall in mm" />
      </div>
    `;
  }

  container.innerHTML = `
    <div class="rainfall-component">
      <div class="rainfall-presets">
        <span class="rainfall-presets-label">Quick Presets:</span>
        <button type="button" class="btn btn-sm" data-preset="dry">Dry week</button>
        <button type="button" class="btn btn-sm" data-preset="light">Light rain</button>
        <button type="button" class="btn btn-sm" data-preset="storm">Heavy storm</button>
        <button type="button" class="btn btn-sm" data-preset="sept2022">Sept 2022-style</button>
      </div>
      <div class="rainfall-grid">
        ${daysHtml}
      </div>
      <div class="rain-summary-bar">
        <span>1-Day: <strong id="${containerId}-sum-1d">0.0</strong> mm</span>
        <span>3-Day Sum: <strong id="${containerId}-sum-3d">0.0</strong> mm</span>
        <span>7-Day Sum: <strong id="${containerId}-sum-7d">0.0</strong> mm</span>
        <span>10-Day Total: <strong id="${containerId}-sum-10d">0.0</strong> mm</span>
      </div>
      <div id="${containerId}-warning" class="warning-callout" style="display: none;">
        <svg width="16" height="16" viewBox="0 0 24 24" fill="currentColor">
          <path d="M12 2L1 21h22L12 2zm1 14h-2v-2h2v2zm0-4h-2V8h2v4z"/>
        </svg>
        <span id="${containerId}-warning-text"></span>
      </div>
    </div>
  `;

  function updateDerivedSums() {
    const vals = getValues();
    const r1 = vals[9] || 0;
    const r3 = vals.slice(7).reduce((a, b) => a + b, 0);
    const r7 = vals.slice(3).reduce((a, b) => a + b, 0);
    const r10 = vals.reduce((a, b) => a + b, 0);

    const el1d = document.getElementById(`${containerId}-sum-1d`);
    const el3d = document.getElementById(`${containerId}-sum-3d`);
    const el7d = document.getElementById(`${containerId}-sum-7d`);
    const el10d = document.getElementById(`${containerId}-sum-10d`);
    const warnEl = document.getElementById(`${containerId}-warning`);
    const warnText = document.getElementById(`${containerId}-warning-text`);

    if (el1d) el1d.textContent = r1.toFixed(1);
    if (el3d) el3d.textContent = r3.toFixed(1);
    if (el7d) el7d.textContent = r7.toFixed(1);
    if (el10d) el10d.textContent = r10.toFixed(1);

    if (r3 < 10) {
      if (warnEl && warnText) {
        warnEl.style.display = "flex";
        warnText.textContent = `3-day rainfall (${r3.toFixed(1)} mm) is below 10 mm. Model was trained only on wet days; scoring will extrapolate.`;
      }
    } else {
      if (warnEl) warnEl.style.display = "none";
    }
  }

  function getValues() {
    const inputs = container.querySelectorAll("input[type='number']");
    const arr = [];
    inputs.forEach(inp => {
      let val = parseFloat(inp.value);
      if (isNaN(val) || val < 0) val = 0;
      if (val > 500) val = 500;
      arr.push(val);
    });
    return arr;
  }

  function setValues(newVals) {
    const inputs = container.querySelectorAll("input[type='number']");
    inputs.forEach((inp, idx) => {
      if (idx < newVals.length) {
        inp.value = newVals[idx];
      }
    });
    updateDerivedSums();
    if (onChangeCallback) onChangeCallback(getValues());
  }

  // Attach preset handlers
  container.querySelectorAll("button[data-preset]").forEach(btn => {
    btn.addEventListener("click", () => {
      const pKey = btn.getAttribute("data-preset");
      if (RAINFALL_PRESETS[pKey]) {
        setValues(RAINFALL_PRESETS[pKey].values);
      }
    });
  });

  // Debounced input handler
  let debounceTimer = null;
  container.querySelectorAll("input[type='number']").forEach(inp => {
    inp.addEventListener("input", () => {
      updateDerivedSums();
      if (debounceTimer) clearTimeout(debounceTimer);
      debounceTimer = setTimeout(() => {
        if (onChangeCallback) onChangeCallback(getValues());
      }, 300);
    });
  });

  updateDerivedSums();

  return {
    getValues,
    setValues,
    updateDerivedSums
  };
}

// Global initialization on DOM ready
document.addEventListener("DOMContentLoaded", () => {
  initSyntheticBanner();
  highlightActiveNav();
});
