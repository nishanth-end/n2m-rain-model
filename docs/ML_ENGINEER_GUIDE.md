# ML Engineer Handoff Guide: Bengaluru Predictive Flood Model

**Author**: Member 1 (Data Engineer)  
**Recipient**: Member 2 (ML Engineer)  
**Project**: N²M Predictive Flood Alert System (Bengaluru, 24–48h Ahead Flood Risk)  
**Date**: 2026-11-16  
**Git Commit**: `e615b72`  
**Master ML Dataset**: `delivery/flood_dataset.parquet`  
**Dataset Acceptance**: 17 / 17 checks passed (`pipeline/validate_dataset.py`, zero failures)

---

## 1. What You Are Receiving

The `delivery/` directory contains all verified data files, lookup tables, and evaluation sequences required to train, evaluate, and benchmark flood models across Greater Bengaluru.

| Path | Format | Size | Rows | Columns | Purpose |
|---|:---:|:---:|:---:|:---:|---|
| `delivery/flood_dataset.parquet` | Parquet | 18.01 MB | 1,764,158 | 42 | Master ML dataset: all 3,026 grid cells across 583 candidate stormy days in May–Nov (2017, 2021, 2022, 2023). 240 positive cell-days across 6 events. |
| `delivery/cells_static.csv` | CSV | 0.26 MB | 3,026 | 16 | Master spatial lookup table: 10 static terrain, hydrology, and urban features per 500 m grid cell, plus ward IDs and nearest CHIRPS pixel. |
| `delivery/rainfall_daily.csv` | CSV | 1.13 MB | 36,112 | 5 | Continuous unbroken daily rainfall calendar across 37 CHIRPS pixels for April 1 – November 30 of 2017, 2021, 2022, 2023 ($976\text{ days} \times 37\text{ pixels}$). Zero nulls, `is_imputed=0`. |
| `delivery/events.csv` | CSV | 0.01 MB | 11 | 19 | Ground-truth flood event audit directory: 11 site records across 6 confirmed events with WGS84 coordinates, mapped cell IDs, citations, live URLs, and confidence grades. |
| `delivery/flood_replay_E2022_09.parquet` | Parquet | 0.90 MB | 72,624 | 42 | Held-out validation replay sequence for event `E2022_09`: 24 consecutive days (22 August – 14 September 2022 $\times$ 3,026 cells) with 188 positive labels across 4–7 September 2022. |
| `delivery/flood_dataset_event_windows.csv` | CSV | 131.29 MB | 366,146 | 42 | CSV extract containing all 3,026 cells for the 121 May–Nov candidate days within $[-14, +7]$ days of all 6 confirmed events (240 positives). |
| `delivery/flood_dataset_pilot.parquet` | Parquet | 0.30 MB | 66,572 | 31 | Lightweight subset for quick code sanity checks: 22 consecutive days (22 August – 12 September 2022 $\times$ 3,026 cells). |
| `data/evidence/manifest.csv` | CSV | 0.02 MB | 73 | 8 | Cryptographic SHA-256 provenance manifest recording requested URLs, final redirected URLs, HTTP status codes, publish timestamps, and local text hashes. |

---

## 2. How the Data Was Built

### a. Spatial Grid Skeleton
- **Source**: Bruhat Bengaluru Mahanagara Palike (BBMP) 2011 administrative ward boundary GeoJSON (198 wards, DataMeet).
- **Coverage / Scale**: Greater Bengaluru metropolitan region ($711.59\text{ km}^2$, 198 wards).
- **Method**: Reprojected boundary to EPSG:32643 (UTM Zone 43N) and overlaid a regular $500\text{ m} \times 500\text{ m}$ lattice ($0.25\text{ km}^2$ per cell). Intersected with ward polygons; cells with centroid inside the municipal boundary were retained, yielding 2,674 full cells and 352 boundary-clipped cells.
- **Output File**: `delivery/cells_static.csv` (spatial identifiers) and `data/interim/cells_grid.csv`.
- **Integrity Checks Passed**: Total cells $= 3,026$; ward coverage $= 198/198$; total area $= 711.59\text{ km}^2$; zero duplicate `cell_id`s; 14 tests passing in `tests/test_grid.py`.

### b. Static Terrain and Hydrology Features
- **Sources**: Copernicus GLO-30 Digital Elevation Model (30 m DSM), ESA WorldCover 2021 v200 (10 m land cover), and OpenStreetMap vector networks (highways, waterways, lakes).
- **Coverage / Scale**: Full city (all 3,026 grid cells).
- **Method**: Conditioned elevation rasters using `pysheds` and Horn's slope algorithm. Computed 10 static physical features per cell:
  1. `elev_m`: Mean elevation from Copernicus GLO-30 DSM ($767.1\text{ m}$ to $951.7\text{ m}$).
  2. `slope_deg`: Mean slope derived from GLO-30 DEM ($0.0^\circ$ to $12.3^\circ$).
  3. `twi`: Topographic Wetness Index: $\ln(\text{flow\_acc\_m2} / \tan(\text{slope\_rad}))$, clamped at $[4.8, 13.1]$.
  4. `hand_m`: Height Above Nearest Drainage relative to conditioned flow streams ($0.0\text{ m}$ to $58.5\text{ m}$).
  5. `flow_acc`: Maximum upstream contributing drainage area in $\text{km}^2$ ($0.0\text{ km}^2$ to $76.5\text{ km}^2$).
  6. `imperv_frac`: Fraction of cell covered by built-up surface (WorldCover 2021 Class 50 proxy, $0.0$ to $0.99$).
  7. `dist_lake_m`: Euclidean distance from cell centroid to nearest OSM waterbody polygon ($\ge 0\text{ m}$).
  8. `dist_drain_m`: Euclidean distance from centroid to nearest OSM waterway / rajakaluve ($\ge 0\text{ m}$).
  9. `dist_road_m`: Euclidean distance from centroid to nearest OSM primary / secondary / trunk road ($\ge 0\text{ m}$).
  10. `lakes_within_1km`: Count of distinct dissolved waterbodies intersecting a 1 km buffer around centroid (0 to 11).
- **Output File**: `delivery/cells_static.csv`.
- **Integrity Checks Passed**: Zero nulls across all 10 features; features constant per cell across all dates; 5 tests passing in `tests/test_static.py`.

### c. Continuous Rainfall Series
- **Source**: UCSB Climate Hazards Group InfraRed Precipitation with Stations (CHIRPS Daily v2.0 p05, $0.05^\circ$ resolution, ~5.3 km).
- **Coverage / Scale**: 37 grid pixels covering Greater Bengaluru across wet seasons (April 1 to November 30) of 2017, 2021, 2022, 2023.
- **Method**: Downloaded 976 daily GeoTIFF rasters. Mapped each 500 m grid cell to its nearest Euclidean CHIRPS pixel center (mean distance 2.12 km, max 3.84 km). Ingested continuous calendars starting April 1 (30-day buffer) and computed rolling precipitation sums (`rain_1d_mm`, `rain_3d_mm`, `rain_7d_mm`, `rain_14d_mm`, `rain_30d_mm`) and daily lags (`rain_lag1_mm` through `rain_lag14_mm`) strictly within each year prior to row filtering.
- **Output File**: `delivery/rainfall_daily.csv` ($36,112\text{ rows}$) and `data/interim/rain_timeseries.csv`.
- **Integrity Checks Passed**: Continuous unbroken dates ($976\text{ days} \times 37\text{ pixels}$); zero nulls; `is_imputed = 0`; rolling monotonic identities hold ($\text{rain\_1d} \le \text{rain\_3d} \le \text{rain\_7d}$); lag identity holds ($\text{rain\_3d} = \text{rain\_1d} + \text{lag1} + \text{lag2}$ with absolute error $< 0.02\text{ mm}$); 5 tests passing in `tests/test_rainfall.py`.

### d. Ground-Truth Flood Catalog
- **Sources**: Technical Study by Dr. Sudhir Sajjan (*Floods at Bengaluru City: A Technical Study*, 2022) for September 2022 hotspots; contemporaneous verified media reports from *The Indian Express*, *The News Minute*, *Gulf Times*, and *Scroll.in*.
- **Coverage / Scale**: 6 confirmed flood events spanning 2017 to 2023 across 11 site records and 10 distinct seed cells.
- **Method**: Coordinates were resolved against OpenStreetMap feature polygons / centroids (e.g. Rainbow Drive OSM way 101573097, Wipro Campus way 370327479, Koramangala 4th Block way 1066116298) and mapped to grid cells via strict point-in-polygon matching. Where historical sources reported layout boundaries extending beyond the 2011 BBMP boundary, inside polygon centroids were assigned (Cell 555 for RBD Layout, Cell 666 for Wipro Campus).
- **Output File**: `delivery/events.csv`.
- **Integrity Checks Passed**: All 11 records lie strictly within the 3,026 production cells; every cited quote matches saved source text with $\le 25$ words; live URL verification verified; `pipeline/verify_quotes.py` passing with 0 errors.

### e. Master ML Dataset Assembly
- **Source**: Inner join of grid skeleton, static features, CHIRPS rainfall time series, and flood event labels.
- **Coverage / Scale**: 1,764,158 rows $\times$ 42 columns (3,026 cells $\times$ 583 candidate stormy days).
- **Method**: Assembled all cells on days meeting the candidate stormy days rule. Assigned `flood_label = 1` to report-mapped seed cells on active event days (`audit_is_buffer_cell = 0`, high/medium confidence). Applied an 8-connected Moore neighborhood ($3\times3$ lattice buffer) around seed cells, setting buffer cells to `flood_label = 1` (`audit_is_buffer_cell = 1`, `label_confidence = 'low'`). All remaining cells on candidate days received `flood_label = 0`, `label_source = 'none'`, and `label_confidence = 'low'`.
- **Output File**: `delivery/flood_dataset.parquet`.
- **Integrity Checks Passed**: Passed all 17 automated acceptance criteria of `pipeline/validate_dataset.py` with zero failures (unique compound key `(cell_id, date)`, zero missing values, zero forbidden columns).

### f. Validation and Replay Subsets
- **Source**: Sliced directly from `delivery/flood_dataset.parquet`.
- **Coverage / Scale**: 
  - `flood_replay_E2022_09.parquet`: 24 consecutive days (22 Aug – 14 Sep 2022 $\times$ 3,026 cells = 72,624 rows; 188 positive labels across 4–7 Sep 2022).
  - `flood_dataset_event_windows.csv`: All 3,026 cells across the 121 May–Nov candidate days within $[-14, +7]$ days of all 6 events (366,146 rows; 240 positive labels).
  - `flood_dataset_pilot.parquet`: 22 consecutive days (22 Aug – 12 Sep 2022 $\times$ 3,026 cells = 66,572 rows).
- **Method**: Filtered master table by date ranges. Audit columns and targets were cross-verified against the master parquet table.
- **Output Files**: `delivery/flood_replay_E2022_09.parquet`, `delivery/flood_dataset_event_windows.csv`, `delivery/flood_dataset_pilot.parquet`.
- **Integrity Checks Passed**: Replay parity achieved: `labels equal: True` between replay and master parquet across the 24-day evaluation window.

### g. Evidence Store and Quote Verification
- **Source**: 15 saved full-page texts (`data/evidence/*.txt`), Overpass / Nominatim raw JSON query responses (`data/evidence/geocode/*.json`), and publication metadata.
- **Coverage / Scale**: 73 manifest entries across all citations, geocode queries, and calibration sources.
- **Method**: Every cited quotation in documentation and interim tables is checked by `pipeline/verify_quotes.py` to ensure: (1) it exists verbatim in the saved page text, (2) length is $\le 25$ words, and (3) cited publication dates match the source page header.
- **Output Files**: `data/evidence/manifest.csv` and `data/evidence/`.
- **Integrity Checks Passed**: `python pipeline/verify_quotes.py` exits with code 0 (all quotes verified verbatim).

---

## 3. Column Reference

The master table `delivery/flood_dataset.parquet` contains **42 columns**. Numeric features are provided in **raw physical units** (no scaling, standardisation, or log transforms). For complete definitions and allowed ranges, see [`delivery/data_dictionary.md`](file:///Users/nishanthgm/Documents/n2m-rain-predictive-model/delivery/data_dictionary.md).

```text
delivery/flood_dataset.parquet (42 Columns)
├── 1. Identifiers & Coordinates (6 columns)
│   ├── cell_id                      int64       Planar grid cell index (0 to 3,025)
│   ├── date                         object      UTC calendar date (YYYY-MM-DD)
│   ├── lat                          float64     Cell centroid latitude (WGS84, degrees N)
│   ├── lon                          float64     Cell centroid longitude (WGS84, degrees E)
│   ├── ward                         int64       BBMP 2011 administrative ward number (1 to 198)
│   └── rain_pixel_id                int64       Nearest CHIRPS 0.05° pixel ID (0 to 36)
├── 2. Static Terrain & Hydrology (10 columns)
│   ├── elev_m                       float64     Copernicus GLO-30 DEM mean elevation (meters)
│   ├── slope_deg                    float64     Mean slope derived from DEM (degrees)
│   ├── twi                          float64     Topographic Wetness Index (dimensionless)
│   ├── hand_m                       float64     Height Above Nearest Drainage (meters)
│   ├── flow_acc                     float64     Upstream contributing drainage area (km²)
│   ├── imperv_frac                  float64     ESA WorldCover built-up fraction (0.0 to 1.0)
│   ├── dist_lake_m                  float64     Distance to nearest OSM waterbody (meters)
│   ├── dist_drain_m                 float64     Distance to nearest OSM drain / rajakaluve (meters)
│   ├── dist_road_m                  float64     Distance to nearest OSM arterial road (meters)
│   └── lakes_within_1km             int64       Count of waterbodies intersecting 1 km buffer
├── 3. Cumulative Precipitation Sums (5 columns)
│   ├── rain_1d_mm                   float64     Rainfall on day d (ending day d inclusive, mm)
│   ├── rain_3d_mm                   float64     3-day rolling sum: rain(d-2) + rain(d-1) + rain(d) (mm)
│   ├── rain_7d_mm                   float64     7-day rolling precipitation sum (mm)
│   ├── rain_14d_mm                  float64     14-day rolling precipitation sum (mm)
│   └── rain_30d_mm                  float64     30-day antecedent moisture sum (mm)
├── 4. Antecedent Daily Precipitation Lags (14 columns)
│   ├── rain_lag1_mm ... rain_lag14_mm float64   Daily precipitation on day d-k for k in [1, 14] (mm)
├── 5. Target & Sampling Weight (4 columns)
│   ├── flood_label                  int64       Binary classification target: 1 = flooded, 0 = dry
│   ├── label_source                 object      Provenance: 'reported', 'buffered', 'restored', 'none'
│   ├── label_confidence             object      Confidence grade: 'high', 'medium', 'low'
│   └── day_sampling_weight          float64     Sampling weight: uniformly 1.0 (no subsampling)
└── 6. Audit & Provenance Columns (3 columns)
    ├── event_id                     object      Confirmed event identifier (e.g. 'E2022_09') or empty
    ├── audit_is_buffer_cell         int64       1 = 3x3 topological buffer cell; 0 = report seed
    └── audit_geocode_precision      object      'landuse_footprint', 'neighbourhood_centroid', etc.
```

---

## 4. KNOWN LIMITATIONS

> [!WARNING]
> This section is mandatory for any team member building or deploying models on this dataset. These physical, statistical, and operational constraints must be factored into model design.

### 1. Tiny Effective Sample Size
While the dataset has **1,764,158 rows**, the headline count of **240 positive cell-days** is misleading:
- **30 positives** are report-mapped centre seed-days (10 distinct seed cells $\times$ active event days).
- **210 positives (87.5%)** are topological $3\times3$ buffer cells surrounding those seeds.
- The true number of independent flood events is **6**, and the number of independent storm episodes is **5** (since May 2022 and September 2022 occurred in the same season).
- Treating 240 positive rows as independent observations will cause severe overfitting. Effective degrees of freedom are governed by the **30 seed-days**, not the 240 expanded rows.

### 2. Extreme Positive Scarcity in Leave-One-Event-Out Validation
If event `E2022_09` (September 2022) is held out as the test set:
- **188 positive cell-days** are removed from training.
- Exactly **52 positive cell-days** remain for training across the entire city:
  - **6 centre seed-days** (`E2017_08`: 1, `E2017_09`: 2, `E2021_11`: 1, `E2022_05`: 1, `E2023_05`: 1).
  - **46 buffer cell-days**.
- *Recommendation*: Use Leave-One-Event-Out Cross-Validation (LOEO-CV) across all 6 events to evaluate variance. The file `delivery/flood_replay_E2022_09.parquet` should be kept as a demonstration replay, not the sole validation benchmark.

### 3. Coarse Spatial Rainfall Resolution
- Greater Bengaluru's 3,026 grid cells map to only **37 CHIRPS pixels** (mean 81.8 cells per pixel).
- Positive cells map to only **8 distinct CHIRPS pixels**:
  - Pixel 11: 121 city cells map to it (16 positive cells).
  - Pixel 12: 118 city cells map to it (35 positive cells, including RBD Layout and Wipro Campus).
  - Pixel 17: 121 city cells map to it (9 positive cells, including Koramangala and KR Circle).
  - Pixel 20: 121 city cells map to it (6 positive cells).
- Because all cells under the same pixel receive identical rainfall values on any given day, **rainfall features cannot separate neighbouring flooded cells from dry cells within the same pixel**. The classifier will inevitably rely on static terrain features (`hand_m`, `twi`, `elev_m`, `dist_drain_m`) for spatial discrimination, using rainfall primarily as an on/off temporal trigger.

### 4. Severe Label Noise in Negatives (False Negative Ambiguity)
A label of `flood_label == 0` does **NOT** denote verified dry ground; it means **no verified media or civic flood report was indexed**.
- In `flood_dataset.parquet`, there are **1,019 pixel-days where 3-day rainfall reaches $\ge 60\text{ mm}$**.
- Of those 1,019 heavy rain pixel-days, **only 7 coincide with a positive label (`flood_label == 1`)**.
- The remaining **1,012 pixel-days with 3-day rain $\ge 60\text{ mm}$ carry `flood_label == 0`**.
- Status of label enrichment tasks:
  1. *Rainiest unlabelled dates (11 Oct 2017, 7–8 Sep 2017, 26–27 Aug 2022)*: **STILL OPEN**. No independent media or civic reports were verified in `delivery/events.csv`; these dates remain unlabelled.
  2. *2024–2025 flood events*: **STILL OPEN**. News articles for October 2024 floods exist in `data/evidence/`, but lie outside the 2017/2021–2023 study period and have not been ingested into the master dataset.
  3. *KSNDMC / IMD ground rain-gauge data*: **STILL OPEN**. A formal request draft was prepared in `docs/request_formal_ksndmc_telemetry.md`, but no official gauge telemetry has been acquired or merged.
- *Modeling Implication*: Do not apply high penalty cross-entropy to negatives in low-lying valley bottoms. Consider Positive-Unlabeled (PU) learning or focal loss.

### 5. Label Timing vs. 24–48h Forecast Horizon (Temporal Leakage Risk)
- **Finding**: At row $(c, d)$, `flood_label` represents flooding observed on day $d$. The feature `rain_1d_mm` is the **realized 24-hour precipitation on day $d$ inclusive** (00:00 to 24:00 UTC).
- **Leakage Risk**: The label is **same-day concurrent (diagnostic / nowcast)** with the rainfall features, NOT shifted ahead.
- In an operational 24–48h early warning setting, day $d$'s realized rainfall is unknown at the morning of day $d$. Training a model that relies on `rain_1d_mm` to predict flooding on day $d$ constitutes **temporal leakage** relative to the 24–48h alert goal.
- *Remediation for Member 2*: To evaluate a true 24h ahead alert system, you must either:
  1. Drop `rain_1d_mm` and predict day $d$ flooding strictly from antecedent lags (`rain_lag1_mm` through `rain_lag14_mm`), or
  2. Substitute `rain_1d_mm` with a 24-hour Numerical Weather Prediction (NWP) quantitative precipitation forecast.

### 6. Rain-Gated Sampling
- The master dataset is **not a continuous calendar**. It retains only **583 candidate stormy days** selected by the rule:
  > *"Captures days where the maximum rain_3d_mm across the city reaches at least 10 mm, PLUS all calendar days from 14 days before to 7 days after each confirmed flood event."*
- Trivial dry days outside flood windows were omitted during construction.
- *Operational Implication*: An operational serving pipeline cannot run this model on completely dry days without an upstream rain gate. Member 3's backend must implement the identical pre-filter ($\max(\text{rain\_3d}) \ge 10\text{ mm}$) before invoking model inference.

### 7. Event Catalogue Source Limits
- The 6 confirmed events originate from a single civil engineering technical study (Sajjan 2022) supplemented by mainstream English media articles.
- High-income commercial tech corridors (ORR Ecospace, Whitefield, Sarjapur Road) receive extensive reporting; low-income valley informal settlements flood regularly but lack media coverage. The catalog has high precision but low recall.

### 8. Satellite-Derived vs. Gauge Rainfall
- CHIRPS is a satellite infrared product blended with sparse stations. Convective cloudburst cells in Bengaluru are hyper-local ($< 2\text{ km}$ across).
- On 4 September 2022, KSNDMC local rain gauges recorded **131.6 mm to 148.0 mm**, but CHIRPS Pixel 12 smoothed this down to **30.85 mm** (a $4.3\times$ areal attenuation).
- Hard rule: **Never apply absolute rain thresholds (e.g. $> 70\text{ mm}$) to CHIRPS features.** A 30 mm CHIRPS daily total indicates an extreme, catastrophic rainstorm.

---

## 5. Recommended Modelling Protocol

These are engineering recommendations based on dataset properties, not rigid requirements:

1. **Model Progression**:
   - Establish a simple baseline first: Logistic Regression with $L_2$ regularization on standard scaled features.
   - Train an XGBoost classifier with shallow depth (`max_depth = 3` to `5`) and strong column subsampling (`colsample_bytree = 0.7`) to prevent tree splits from memorizing specific pixel-cell combinations.
2. **Evaluation Protocol (Leave-One-Event-Out CV)**:
   - Perform 6-fold cross-validation, holding out one event at a time.
   - Purge candidate days within $\pm 7$ days of the test event from the training fold to prevent leakage from antecedent soil moisture.
   - Report performance metrics across all 6 folds; do not rely solely on the September 2022 held-out replay.
3. **Class Imbalance & Sample Weighting**:
   - Set XGBoost `scale_pos_weight = (len(neg) / len(pos)) \approx 7,350`, or train with sample weights:
     ```python
     CONF_WEIGHTS = {"high": 1.0, "medium": 0.7, "low": 0.4}
     sample_weight = np.where(
         df["flood_label"] == 1,
         df["label_confidence"].map(CONF_WEIGHTS).fillna(0.4) * 100.0,
         1.0
     )
     ```
4. **Metrics**:
   - **Do NOT report accuracy or ROC-AUC** (which are inflated by $99.98\%$ true negatives).
   - Report **Precision-Recall AUC (PR-AUC)** against the base rate ($0.0136\%$).
   - Report **Recall at Fixed Alert Rate**: What fraction of true flooded cells are captured when issuing alerts to the top 1%, 2%, or 5% highest-risk cells in the city?
   - Report Critical Success Index (CSI / Threat Score) at threshold: $\text{CSI} = \frac{\text{TP}}{\text{TP} + \text{FP} + \text{FN}}$.
5. **Reporting Confidence Honestly**:
   - Because only 6 historical events are available, provide standard deviations across CV folds and state error bars transparently.

---

## 6. Reproducibility

### Exact Build & Verification Commands
To reproduce all outputs, run from the repository root:
```bash
# 1. Activate environment
source .venv/bin/activate

# 2. Run Section 9 Acceptance Checks
python pipeline/validate_dataset.py delivery/flood_dataset.parquet

# 3. Run Pipeline Unit Tests
pytest tests/test_rainfall.py tests/test_geocode.py tests/test_static.py tests/test_grid.py

# 4. Verify Evidence Quotes & Publication Dates
python pipeline/verify_quotes.py

# 5. Compute Ground-Truth Summary Statistics
python pipeline/handoff_stats.py
```

### Verification Outputs (Recorded on 2026-11-16)

```text
============================= TEST SUITE EXECUTION =============================
$ python pipeline/validate_dataset.py delivery/flood_dataset.parquet
PASS  required columns present 
PASS  no duplicate (cell_id, date)
PASS  every date has all 3026 cells (0 incomplete days)
PASS  no missing rain
PASS  no missing static features
PASS  rain_1d <= rain_3d <= rain_7d
PASS  rain_3d == rain_1d + lag1 + lag2
PASS  static features constant per cell
PASS  flood_label only 0/1
PASS  label_source values allowed
PASS  label_confidence values allowed
PASS  day_sampling_weight >= 1
PASS  240 positive rows
PASS  every positive has a label_source
PASS  every positive has an event_id
PASS  at least 3 distinct events (found 6)
PASS  no forbidden columns 

rows: 1764158 | cells: 3026 | days: 583 | date range: 2017-05-07 to 2023-11-09
flood rate (all rows): 0.0001
positives per event:
event_id
E2017_08      9
E2017_09     18
E2021_11      9
E2022_05      7
E2022_09    188
E2023_05      9

FAILED CHECKS: 0
================================================================================
$ pytest tests/test_rainfall.py tests/test_geocode.py tests/test_static.py tests/test_grid.py
============================== 28 passed in 2.58s ==============================
================================================================================
$ python pipeline/verify_quotes.py
All cited quotes verified verbatim against data/evidence/ files (0 errors).
================================================================================
```

- **Git Commit Hash**: `e615b72`
- **SHA-256 Provenance Manifest**: `data/evidence/manifest.csv`

---

## 7. Open Items for the Team

The following items are documented as open, with assigned placeholders for follow-up:

| Item | Description | Current State | Assigned Owner Placeholder |
|---|---|:---:|:---:|
| **1. Unlabelled Heavy Rain Dates** | Ingest media or civic corroboration for 11 Oct 2017, 7–8 Sep 2017, and 26–27 Aug 2022 ($>60\text{ mm}$ rain). | STILL OPEN | `[Owner: Data Engineering / Member 1]` |
| **2. 2024–2025 Event Ingestion** | Acquire CHIRPS GeoTIFFs for 2024 and process Oct 2024 flood reports into `events.csv`. | STILL OPEN | `[Owner: Data Engineering / Member 1]` |
| **3. KSNDMC Telemetry Access** | Follow up on formal RTI / academic data request for automated rain gauge telemetry. | STILL OPEN | `[Owner: Project Lead]` |
| **4. 24h Ahead Feature Split** | Construct dedicated 24h lag-only feature set (`rain_lag1_mm`..`14_mm`) to prevent temporal nowcast leakage. | READY FOR ML | `[Owner: ML Engineering / Member 2]` |
| **5. Pre-Inference Rain Gate** | Implement candidate day threshold ($\max(\text{rain\_3d}) \ge 10\text{ mm}$) in FastAPI backend before model scoring. | READY FOR BACKEND | `[Owner: Backend / Member 3]` |
