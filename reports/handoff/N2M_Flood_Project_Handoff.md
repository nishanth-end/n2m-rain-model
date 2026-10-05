# Predictive Flood Alert System — Project Handoff & Working Reference

**1BCP308 – Community Project | Team N²M | Dept. of CSE, DSCE**

| | |
|---|---|
| **Document purpose** | Full context for anyone (teammate, or a fresh AI assistant session) picking up this project from here — what it is, what's done, what's next, all sources and schemas used so far. |
| **Last updated** | October 2026, ahead of Review 2 (Oct 5–8) |
| **Team** | Mohith M (1DS25CS147), Nihal Rao (1DS25CS160), Nishanth G M (1DS25CS161) |
| **Faculty Guide** | Prof. Punith Kumar |

---

## 1. What This Project Is

A Predictive Flood Alert System for Bengaluru: instead of mapping where floods have already happened (reactive), the system forecasts flood risk 24–48 hours in advance for a defined set of flood-prone zones, using historical rainfall + satellite + terrain data to train a model, then serves live risk scores through an alert bot and a map.

**Domain** (per the Community Project guidelines): Space & Earth Observation, with secondary relevance to National Importance (disaster management).
**SDG mapping:** SDG 11 (Sustainable Cities and Communities, Target 11.5) and SDG 13 (Climate Action, Target 13.1).

### 1.1 Why this scope, and what was simplified

The original ambition (full Sentinel-1 SAR change detection + LSTM forecasting across the whole city) was deliberately scoped down for the Review 2 timeline. Current approach: pick a small number of real, documented flood zones; use a simple model (logistic regression → XGBoost) before attempting LSTM; be explicit with the guide that SAR imagery and a more sophisticated model are the Review 3/4 roadmap, not missing work.

---

## 2. System Architecture — How It Works

**Pipeline:** Data collection → Model (risk scoring) → Live pipeline (rainfall forecast feed) → Alerting (Telegram bot) → Visualization (Leaflet map, with historical replay mode).

1. **Data collection & pre-processing** (Nishanth / Member 1): historical rainfall, satellite flood-extent imagery, terrain/elevation, drain layout → cleaned structured dataset.
2. **Model** (Teammate B / Member 2): trained on rainfall + terrain features → flood risk score per zone. Starting with scikit-learn Logistic Regression → upgrading to XGBoost → stretch goal LSTM.
3. **Systems integration** (Teammate A / Member 3): live rainfall API → feeds model → Telegram bot alerts past a risk threshold → Leaflet map (reusing the Integral Geo template) shows live + historical risk.

**Output contract** agreed between data/model and frontend (so work can proceed independently):

```json
{
  "zone": "Bellandur",
  "risk_score": 0.82,
  "risk_level": "high"
}
```

---

## 3. Progress So Far

### 3.1 Completed
- Domain, title, objectives, and SDG mapping finalised.
- Full project synopsis written and exported as a Word document (institutional header, abstract, literature review with 5 real cited papers, methodology, SDG mapping table, team contribution plan, references) — see Section 6 for the source list used.
- Team roles assigned and documented (Section 4).
- Found and mined a 191-page technical study: *"Floods at Bengaluru City – A Technical Study"* by Dr. Sudhir Sajjan (Dec 2022) — extracted real catchment areas, lake names, and documented flood dates for 6 specific Bengaluru zones (RBD Layout, Wipro Campus Sarjapur Road, Outer Ring Road/RMZ Ecospace, Epsilon Layout/Yemalur Road, Borewell Road, Panathur-Balagere Road).
- Built `flood_zones_dataset.csv` — 9 rows covering the 6 documented flood zones (incl. 2 events for RBD Layout) plus 2 manually-added contrast/control zones (Malleswaram, Jayanagar) for the model to learn from non-flood examples.
- Built `bengaluru_monsoon_2022_rainfall.csv` — citywide monthly/seasonal rainfall context data for 2022.
- Compiled a full external data source list (Section 7) and a beginner Google Earth Engine walkthrough (Section 8).
- Guide contacted for Review 2 slot (Oct 5–8 window).

### 3.2 In progress / not yet done
- Model not yet trained on the real `flood_zones_dataset.csv` — last discussed step was adapting the Colab logistic regression skeleton (Section 9.2) to this real data instead of the placeholder CSV.
- `elevation_proxy` in the dataset is still just low/high labels, not real SRTM DEM numbers — placeholder, flagged for later.
- No live rainfall API integration yet.
- No Telegram bot built yet.
- No real Leaflet map wired to model output yet (frontend teammate unavailable for a few days as of last session) — fallback was a throwaway matplotlib bar chart instead.
- Sentinel-1 SAR pipeline not started — planned as a later-week / Review 3 upgrade, not needed for Review 2.

> **Keep this section updated as you go** — it's the part that tells whoever picks this up next exactly where to resume.

---

## 4. Team Roles

| Member | Role & Responsibilities |
|---|---|
| **Nishanth (You) — Member 1** | Data collection & pre-processing. Sources rainfall, satellite flood-extent, DEM, drain layout data. Also informal architecture lead (understands the full pipeline end to end, from Integral Geo experience). |
| **Teammate A — Member 3** | Systems integration: live rainfall API pipeline, Telegram alert bot, Leaflet map (reusing Integral Geo template). |
| **Teammate B — Member 2** | ML model: feature engineering (with Nishanth), train/evaluate Logistic Regression → XGBoost → stretch LSTM. |

Nishanth is separately self-learning ML basics (Kaggle Intro/Intermediate ML mini-courses) as a personal side-track, without taking over Member 2's actual deliverable — intended to feed into future projects (e.g. Integral Geo v2) rather than this semester's model work.

---

## 5. Data Schemas Used So Far

### 5.1 `flood_zones_dataset.csv`

| Column | Meaning |
|---|---|
| `zone` | Named location (the 6 documented zones + 2 contrast zones) |
| `catchment_area_sqkm` | Drainage catchment area feeding that zone, from the technical study |
| `feeding_lakes_streams` | Named lakes/streams draining into the zone |
| `elevation_proxy` | low / high — **PLACEHOLDER**, to be replaced with real SRTM DEM values |
| `flood_event_date` | Date of the documented flood event |
| `rainfall_mm_event` | Rainfall recorded for that event/date, where available |
| `flooded` | 1 = flooded, 0 = not flooded (model's target/label column) |
| `primary_cause` | Engineering root cause per the technical study (context, not a model input) |
| `source` | Citation for that row — flags the 2 contrast rows as general knowledge, not from the study |

### 5.2 `bengaluru_monsoon_2022_rainfall.csv`

| Column | Meaning |
|---|---|
| `period` | Date, date range, or month/season label |
| `rainfall_mm` | Rainfall total for that period |
| `description` | Context for the figure (e.g. "second wettest August on record") |
| `source` | Citation (IMD, KSNDMC, Deccan Herald archives, the technical study) |

### 5.3 Model output contract (JSON)

Agreed so Member 2 and Member 3 can build independently without syncing live:

```json
{
  "zone": "<zone name>",
  "risk_score": "0.0–1.0",
  "risk_level": "high | low"
}
```

---

## 6. References Used in the Project Synopsis

These are the 5 real, verifiable academic/technical sources already cited in the submitted synopsis document:

1. Ramachandra, T.V. and Aithal, B.H., 2016. *Bangalore's Reality: towards unlivable status with unplanned urban trajectory.* Current Science (Guest Editorial), 110(12), pp.2207–2208.
2. Gopinath, R., Akarsh, C.U. and Muralidhar, M.E., 2022. *Time-line based aerial analysis for impact of rampant urbanization on lakes of Bengaluru (India).* CEER Proceedings, 2022.
3. Islam, M.T. and Meng, Q., 2022. *An exploratory study of Sentinel-1 SAR for rapid urban flood mapping on Google Earth Engine.* International Journal of Applied Earth Observation and Geoinformation, 113, p.103002.
4. Moharrami, M., Javanbakht, M. and Attarchi, S., 2021. *Automatic flood detection using Sentinel-1 images on the Google Earth Engine.* Environmental Monitoring and Assessment, 193(5), pp.1–17.
5. Kratzert, F., Klotz, D., Brenner, C., Schulz, K. and Herrnegger, M., 2018. *Rainfall–runoff modelling using Long Short-Term Memory (LSTM) networks.* Hydrology and Earth System Sciences, 22(11), pp.6005–6022.

Plus the primary data source mined for the CSVs:

- Sajjan, S., 2022. *Floods at Bengaluru City – A Technical Study.* December 2022. *(Independent technical report, not peer-reviewed — used as a primary data/case-study source, not an academic citation.)*

---

## 7. External Data Sources (Full List)

### 7.1 Rainfall data
- **data.opencity.in/organization/ksndmc** — KSNDMC rainfall re-published as clean CSVs (annual, by district/taluk/hobli, 2017–2024, incl. 2022). Easiest starting point.
- **www.ksndmc.org** — official KSNDMC portal, finer time resolution (daily/real-time), Gram Panchayat level.
- **mausam.imd.gov.in/bengaluru** — IMD Bengaluru Meteorological Centre, daily rainfall stats PDFs and climatological tables.
- **openweathermap.org/api** — free-tier live/forecast rainfall API, for the live pipeline stage (not historical training data).

### 7.2 Satellite imagery
- **Google Earth Engine** (code.earthengine.google.com / Python API) — Sentinel-1 SAR and Sentinel-2 optical, easiest access route. See Section 8.
- **dataspace.copernicus.eu** — ESA's official Copernicus Data Space; direct scene download if not using Earth Engine.
- **bhuvan.nrsc.gov.in** — ISRO's Bhuvan portal; Indian-sourced satellite data (Resourcesat, Cartosat), good domestic-source citation alongside Sentinel.

### 7.3 Elevation / DEM
- **earthexplorer.usgs.gov** — USGS EarthExplorer, standard SRTM 30m DEM source, free account.
- **opentopography.org** — alternative DEM source, simpler UI.
- Also available directly inside Earth Engine's catalog as `USGS/SRTMGL1_003` — no separate download needed.

### 7.4 Lakes, drains, civic infrastructure
- **data.opencity.in** — broader civic datasets beyond rainfall (check org list for lakes/wards/drainage).
- **Bhoomi / Karnataka GIS** (landrecords.karnataka.gov.in) — referenced in the technical study for historical nalla/stream-path KMZ files.
- **openstreetmap.org** (or the Overpass API) — free mapped lakes, drains, roads for Bengaluru; usable directly in Leaflet.

---

## 8. Google Earth Engine — Beginner Walkthrough

1. Sign up at **earthengine.google.com/signup** with any Google account; choose **"Noncommercial"** use (free, instant for students). This auto-creates a Google Cloud project.
2. Optional: explore visually first at **code.earthengine.google.com** (JavaScript Code Editor, no setup needed) before writing Python.
3. Set up the Python API in Colab:

```python
!pip install earthengine-api
import ee
ee.Authenticate()
ee.Initialize(project='your-project-id')
```

4. Pull a test Sentinel-1 image for a study zone:

```python
aoi = ee.Geometry.Rectangle([77.68, 12.90, 77.72, 12.93])
collection = (ee.ImageCollection('COPERNICUS/S1_GRD')
              .filterBounds(aoi)
              .filterDate('2022-09-03', '2022-09-07')
              .filter(ee.Filter.eq('instrumentMode', 'IW')))
print(collection.size().getInfo())
```

5. Basic water detection (SAR water = low backscatter):

```python
image = collection.first()
vv = image.select('VV')
water_mask = vv.lt(-15)  # threshold needs tuning per scene
```

Official reference if stuck: search "Earth Engine Python API Colab setup notebook" (github.com/google/earthengine-community).

---

## 9. Model Development — Code So Far

### 9.1 Colab setup
No local install needed; pandas and scikit-learn are preloaded in Google Colab (colab.research.google.com).

### 9.2 Training skeleton (Logistic Regression baseline)

```python
import pandas as pd
df = pd.read_csv('flood_zones_dataset.csv')

elevation_map = {'low': 0, 'medium': 1, 'high': 2}
df['elevation_num'] = df['elevation_proxy'].map(elevation_map)

X = df[['rainfall_mm_event', 'elevation_num']]
y = df['flooded']

from sklearn.linear_model import LogisticRegression
model = LogisticRegression()
model.fit(X, y)
```

### 9.3 Reusable risk function (the output-contract implementation)

```python
def get_risk(zone, rainfall_mm, elevation_proxy):
    elevation_num = elevation_map[elevation_proxy]
    test = pd.DataFrame([{'rainfall_mm_event': rainfall_mm, 'elevation_num': elevation_num}])
    score = model.predict_proba(test)[0][1]
    return {"zone": zone, "risk_score": round(float(score), 2),
            "risk_level": "high" if score > 0.5 else "low"}
```

**Next model upgrade step (not yet done):** swap `LogisticRegression` for `XGBoost` once the Kaggle Intermediate ML course's XGBoost lesson is complete, and add `catchment_area_sqkm` as a third feature once missing values are filled in for the contrast zones.

---

## 10. Next Steps (In Order)

1. Load `flood_zones_dataset.csv` into the model notebook (Section 9.2) in place of any placeholder data — immediate next action for Teammate B.
2. Fill missing `catchment_area_sqkm` for the 2 contrast zones (Malleswaram, Jayanagar) — rough Google Maps lookup is fine for now.
3. Get a working end-to-end slice: data → model → some visible output (real Leaflet map if Teammate A is back, otherwise the matplotlib bar-chart fallback) before the Review 2 slot.
4. Write/finalise the one-page requirements note and a simple system design diagram (data → model → map boxes) — explicitly required by the Review 2 guidelines alongside the working prototype.
5. Attend Review 2 (Oct 5–8, exact slot pending guide confirmation) — be upfront that SAR imagery and a trained XGBoost/LSTM model are the Review 3 roadmap, not missing work.
6. Post-Review 2: swap in real SRTM DEM elevation values (Section 7.3), move from Logistic Regression to XGBoost, and begin the Sentinel-1 SAR water-detection pipeline (Section 8) using the 6 real documented zones as validation cases.
7. Build the Telegram bot (Member 3) and wire the live rainfall API (OpenWeatherMap) once the model is stable.

---

## 11. Files Produced So Far

| File | Contents |
|---|---|
| `Community_Project_Synopsis_Flood_Alert_System.docx` | Full submitted synopsis: abstract, intro, problem statement, objectives, literature review, methodology, SDG mapping, references, team table. |
| `N2M_Flood_Project_Role_Breakdown.xlsx` | Team role/task/timeline breakdown spreadsheet. |
| `flood_zones_dataset.csv` | 6 documented flood zones + 2 contrast zones, with catchment/lake/date/rainfall/cause data (Section 5.1). |
| `bengaluru_monsoon_2022_rainfall.csv` | Citywide monthly/seasonal 2022 rainfall context (Section 5.2). |
| `N2M_Flood_Project_Handoff.docx` / `.md` | This document, in both formats. |
