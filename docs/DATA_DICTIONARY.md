# Data Dictionary: Static Grid Cell Features (`data/interim/cells_static.csv`)

This document defines each feature column in `cells_static.csv`, detailing physical units, underlying open datasets, spatial aggregation rules over the 500 m cell footprint, and hydrological interpretation.

---

| Column | Type | Unit | Primary Source | Aggregation Rule | Physical / Hydrological Definition |
|---|:---:|:---:|---|---|---|
| `cell_id` | integer | dimensionless | 500 m UTM lattice (`cells_grid.csv`) | exact primary key | Unique cell identifier (0 to 3,025) matching municipal grid. |
| `elev_m` | float | metres (m above MSL) | Copernicus DEM GLO-30 (`dem_30m_utm.tif`) | **mean** across 30 m cell pixels | Mean topographic elevation above mean sea level from raw unburned DEM (EGM2008 geoid). |
| `slope_deg` | float | degrees (°) | Copernicus DEM GLO-30 (`dem_30m_utm.tif`) | **mean** across 30 m cell pixels | Mean terrain surface slope angle derived by Horn gradient operator on unburned raw DEM. |
| `flow_acc` | float | square kilometres (km²) | Copernicus DEM GLO-30 (burned) | **maximum** across 30 m cell pixels | Maximum upstream contributing drainage area routing overland flow through cell footprint. |
| `twi` | float | dimensionless | Copernicus DEM GLO-30 | **mean** across 30 m cell pixels | Topographic Wetness Index: $\ln(a / \tan\beta)$, quantifying propensity for soil saturation. |
| `hand_m` | float | metres (m) | Copernicus DEM GLO-30 | **mean** across 30 m cell pixels | Height Above Nearest Drainage: relative vertical elevation above hydrologically connected flow line. |
| `dist_drain_m` | float | metres (m) | OpenStreetMap waterways | Euclidean distance from cell centroid | Horizontal planar distance to nearest mapped natural or engineered stormwater drain / rajakaluve. |
| `dist_road_m` | float | metres (m) | OpenStreetMap highways | Euclidean distance from cell centroid | Horizontal planar distance to nearest major road (motorway, trunk, primary, secondary + links). |
| `dist_lake_m` | float | metres (m) | OpenStreetMap water | Euclidean distance from cell centroid | Horizontal planar distance to nearest mapped lake / kere / tank boundary polygon. |
| `lakes_within_1km` | integer | count | OpenStreetMap water | count intersecting 1 km radial buffer | Count of distinct lake/tank water bodies within a 1,000 m radial buffer around the cell polygon. Touching lake polygons are dissolved prior to counting. |
| `impervious_fraction`| float | dimensionless [0.0–1.0] | ESA WorldCover 10 m 2021 v200 | **mean** across 10 m / 30 m cell pixels | WorldCover built-up fraction (Class 50), serving as an open proxy for urbanization (not true engineered imperviousness). |
| `cell_area_km2` | float | square kilometres (km²) | BBMP 2011 boundary polygon clip | exact geometric polygon area | Actual clipped planar area of cell geometry (0.25 km² for interior cells; < 0.25 km² for edge cells). |
| `is_edge_cell` | boolean | boolean (True / False) | BBMP 2011 boundary clip | boolean flag (`area_km2 < 0.2499`) | Indicates whether cell intersects municipal boundary and was clipped. |

---

## Technical Specifications & Conditioning Rules

1. **Elevation & Slope Source**: `elev_m` and `slope_deg` are computed strictly from the **raw, unburned DEM** (`dem_30m_utm.tif`) to preserve true physical surface topography.
2. **Stream Burning**: Mapped OSM rajakaluves/waterways are burned into the DEM by **-2.0 metres** (`burn_depth = 2.0 m`) solely during hydrological flow routing (pysheds) to enforce flow path capture along physical urban drainage alignments.
3. **Lakes Conditioning**: Touching water body polygons (`natural=water`) are **dissolved** into single contiguous hydrologically connected water features. Sinks inside lake bodies are depression-filled and resolved during flat routing.
4. **Major Road Taxonomy**: Defined strictly as OpenStreetMap ways tagged with `highway` in `['motorway', 'trunk', 'primary', 'secondary', 'motorway_link', 'trunk_link', 'primary_link', 'secondary_link']`.
5. **Leakage & Edge Guard**: Static pipeline code computes features independently across all grid cells and **never accesses or imports event ground truth tables** (`events.csv` or `event_cells.csv`).

---

## Rainfall Temporal Alignment & Day-Alignment Rule

### 1. Definition in Plain Words
CHIRPS Daily v2.0 precipitation measures cumulative 24-hour rainfall over a UTC calendar day:
$$\text{CHIRPS day } d = \text{00:00:00 to 24:00:00 UTC} = \text{05:30:00 IST on day } d \text{ to } \text{05:30:00 IST on day } d+1$$

Rainfall recorded on date $d$ represents all precipitation that fell between 05:30 IST on day $d$ and 05:30 IST on the following morning (day $d+1$).

### 2. Worked Examples
- **Example 1: Storm at 6:00 pm IST (18:00 IST) on calendar date $d$ (e.g. 4 September 2022)**
  - Local time: 18:00 IST on day $d$
  - UTC conversion: $18:00 - 05:30 = \text{12:30 UTC on day } d$
  - Alignment: 12:30 UTC falls within 00:00:00 to 24:00:00 UTC of date $d$.
  - **Result**: This storm's precipitation lands in **`rain_1d_mm` on date $d$** (e.g. `2022-09-04`).

- **Example 2: Storm at 2:00 am IST (02:00 IST) on calendar date $d+1$ (e.g. 5 September 2022)**
  - Local time: 02:00 IST on day $d+1$
  - UTC conversion: $02:00 - 05:30 = -03:30$, which is **20:30 UTC on day $d$**
  - Alignment: 20:30 UTC falls before 24:00:00 UTC of date $d$.
  - **Result**: This storm's precipitation also lands in **`rain_1d_mm` on date $d$** (e.g. `2022-09-04`), NOT date $d+1$.

### 3. Impact on Flood Dataset Rows & Lags
Flooding observed on the morning of calendar date $d+1$ (e.g. 8:00 am IST on 5 September 2022, recorded as flood date `2022-09-05`):
- The causative overnight rainfall belongs to CHIRPS date $d$ (`2022-09-04`).
- For the flood row indexed at date $d+1$ (`2022-09-05`), this antecedent cloudburst is captured by **`rain_lag1_mm`** (which contains `rain_1d_mm` from date $d$), as well as trailing multi-day rolling sums **`rain_3d_mm`**, **`rain_7d_mm`**, **`rain_14d_mm`**, and **`rain_30d_mm`**.

---

## Rainfall Timeseries Features (`data/interim/rain_timeseries.csv`)

| Column | Type | Unit | Definition | Day Rule & Temporal Window | ends_after_ist_morning |
|---|:---:|:---:|---|---|:---:|
| `rain_pixel_id` | integer | dimensionless | Unique identifier of native 0.05° CHIRPS rain pixel (0 to 36). | Spatial key joining to `cells_grid.csv`. | false |
| `date` | text | YYYY-MM-DD | Target calendar day D of the observation row. | ISO-8601 date within study period (1 May to 30 Nov). | false |
| `rain_1d_mm` | float | mm | Daily precipitation on day D. | 24-hr sum on UTC day D (05:30 IST D to 05:30 IST D+1). | **true** |
| `rain_3d_mm` | float | mm | 3-day trailing rainfall sum. | Sum over days D-2, D-1, D (ends 05:30 IST D+1). | **true** |
| `rain_7d_mm` | float | mm | 7-day trailing rainfall sum. | Sum over days D-6 through D (ends 05:30 IST D+1). | **true** |
| `rain_14d_mm` | float | mm | 14-day trailing rainfall sum. | Sum over days D-13 through D (ends 05:30 IST D+1). | **true** |
| `rain_30d_mm` | float | mm | 30-day trailing rainfall sum. | Sum over days D-29 through D (ends 05:30 IST D+1). | **true** |
| `rain_lag1_mm` | float | mm | Antecedent daily rainfall on day D-1. | 24-hr sum on UTC day D-1 (ends 05:30 IST on D). | **false** |
| `rain_lag2_mm` | float | mm | Antecedent daily rainfall on day D-2. | 24-hr sum on UTC day D-2 (ends 05:30 IST on D-1). | **false** |
| `rain_lag3_mm` | float | mm | Antecedent daily rainfall on day D-3. | 24-hr sum on UTC day D-3 (ends 05:30 IST on D-2). | **false** |

---

## Label-Date Convention & Leakage Note

1. **Specification Requirement**: The specification formally requires features for date D to use rain through day D inclusive (`rain_1d_mm` on day D; `rain_3d_mm` = sum over D-2, D-1, D), so all features are kept as defined.
2. **Timing and Leakage Definition**:
   - `rain_1d_mm` ... `rain_30d_mm` include rain from 05:30 IST on D to 05:30 IST on D+1, i.e. after the IST morning and also after IST day D ends.
   - `rain_lag1_mm` ... `rain_lag3_mm` end at 05:30 IST on D and still include 00:00–05:30 IST of day D.
3. **Training Decision**: Which feature set to train on is the model owner's decision, not ours.

---

## Cell-to-Pixel Mapping (`data/interim/cell_pixel_map.csv`)

| Column | Type | Unit | Definition |
|---|:---:|:---:|---|
| `cell_id` | integer | dimensionless | Unique grid cell identifier (0 to 3,025). |
| `rain_pixel_id` | integer | dimensionless | ID of enclosing native 0.05° CHIRPS rain pixel (0 to 36). |
| `lon` | float | degrees E | WGS84 longitude (EPSG:4326) of clipped cell centroid. |
| `lat` | float | degrees N | WGS84 latitude (EPSG:4326) of clipped cell centroid. |
| `pixel_center_lon` | float | degrees E | WGS84 longitude of 0.05° CHIRPS pixel center. |
| `pixel_center_lat` | float | degrees N | WGS84 latitude of 0.05° CHIRPS pixel center. |
| `distance_km` | float | kilometres (km) | WGS84 geodetic distance from cell centroid to rain pixel center. |
| `area_km2` | float | square kilometres (km²) | Surface area of clipped cell geometry. |

### Mapping Specifications
- **Centroid Definition**: The geometric centroid (center of mass) of the clipped cell geometry in EPSG:4326 (`cells_grid.csv`).
- **Mapping Rule**: A cell centroid belongs to a pixel if `min_lon <= lon < max_lon` and `min_lat <= lat < max_lat`. Points within $10^{-9}$ deg of a shared edge tie to the lower `rain_pixel_id`.
- **Spatial Resolution Limitation**: Cells within the same 0.05° pixel share identical rainfall values on every date. Rainfall has zero spatial variation inside a pixel (~5.5 km).

---

## Daily Rainfall Series (`data/interim/rainfall_daily.csv`)

| Column | Type | Unit | Definition |
|---|:---:|:---:|---|
| `date` | text | YYYY-MM-DD | Calendar date D of the observation (includes April buffer + May–Nov study period). |
| `rain_pixel_id` | integer | dimensionless | ID of native 0.05° CHIRPS rain pixel (0 to 36). |
| `rain_mm` | float | mm | Daily rainfall on UTC day D (00:00:00 to 24:00:00 UTC = 05:30 IST D to 05:30 IST D+1). 0.0 on dry days. |
| `is_imputed` | boolean | dimensionless | `false` on all rows (100% complete source series; zero missing days; no gap-filling applied). |
| `rain_source` | text | dimensionless | `chirps` (CHIRPS Daily v2.0 p05). |

### Temporal Constraints & Quantisation Diagnostic
1. **No Cross-Year Windows**: Rolling sums and lags are computed strictly within each calendar year and never roll across year boundaries. *(Note: This is a **project rule** established for pipeline safety, not a formal spec rule).*
2. **Quantisation Diagnostic & Intra-Pentad Timing**:
   - Within calendar pentads (5-day blocks), 91.99% of nonzero daily values are exact integer multiples (1x, 2x, 3x, 4x) of the pentad's minimum nonzero value (cause not verified in CHIRPS documentation).
   - In 3.97% of rainy pentads, all 37 pixels share an identical normalized daily distribution vector.
   - Consequently, daily timing inside a pentad may not reflect completely independent daily observations, making `rain_1d_mm` and `rain_lag1..3_mm` inherently noisier than aggregated multi-day totals (`rain_7d_mm` to `rain_30d_mm`).


