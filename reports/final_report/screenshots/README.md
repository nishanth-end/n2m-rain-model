# N²M Flood Prediction Model — Report Screenshots & Visual Assets

This directory stores genuine user interface screenshots captured from the working N²M Flood Prediction Model application.

---

## 1. Available Verified Screenshots

### 1. `flood_map_interface_overview.jpg`
- **Component**: Historical Flood Map Interface (`FloodMapPage.jsx`).
- **Date Rendered**: Benchmark historical flood date `2022-09-08` (Day 18 of 24).
- **Visible Elements**:
  - Top navigation bar showing project title, Replay v1 badge, active tab indicator, and API connectivity status.
  - Historical replay stepper controls: Play/Pause button, Previous/Next date controls, active date display (`2022-09-08`), and quick-jump date selector dropdown.
  - Summary metrics bar: High Priority (150 cells / 5%), Moderate Priority (150 cells / 5%), Baseline (2,726 cells), and Total (3,026 cells).
  - Spatial tier filters: `All (3,026)`, `High + Mod (300)`, `High Only (150)`, and Recenter button.
  - Interactive cell search box: `# Find Cell ID (0-3025)`.
  - Floating Cell Telemetry & Attributes inspector drawer.
  - Susceptibility Ranking Legend with clear non-emergency disclaimers.

---

## 2. Recommended Additional Screenshots for Presentation

For students wishing to capture supplementary live screenshots from the deployed Vercel app or local server (`http://localhost:5173`), recommended captures include:

1. **`homepage_hero_overview.png`**:
   - Navigate to **Home** (`/`).
   - Capture the full-page layout including the hero section, problem statement, engineering approach pillars, and research boundaries.

2. **`flood_map_cell_selected.png`**:
   - Navigate to **Flood Map** (`/map`).
   - Enter `722` in the cell search input and click **Find**.
   - Capture the map zoomed into Cell #722 (Bellandur / Mahadevapura reach) with the expanded Telemetry Inspector showing its elevation (874.2 m), HAND (4.1 m), TWI (9.8), impervious fraction (0.78), and score (0.2191).

3. **`live_simulation_weather_context.png`**:
   - Navigate to **Live & Simulation** (`/simulation`).
   - Capture the Open-Meteo meteorological feed card, 14-day rolling precipitation chart, and pipeline isolation status badge.

4. **`telegram_demo_control_panel.png`**:
   - Navigate to **Telegram** (`/telegram`).
   - Capture the operational safety boundary banner, live connection status terminal, supported slash command directory, and rendered demonstration alert payload.

5. **`telegram_mobile_bulletin.png`**:
   - Capture a screenshot on a mobile device showing the formatted susceptibility bulletin delivered by `@N2M_Flood_Bot` in the Telegram app following a `/demo` command or "Send Demo Alert" dispatch.
