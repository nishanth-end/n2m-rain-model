# Data Dictionary: Bengaluru Flood Predictive Model Dataset

Single source of truth reference for all delivered files per Member 2's *Flood Model Dataset Specification v1.0*.

---

## 1. Summary of Delivered Files (`delivery/`)

| File Name | Format | Rows | Columns | Meaning |
|---|:---:|:---:|:---:|---|
| `cells_static.csv` | CSV | 3,026 | 16 | One row per 500 m grid cell with static terrain, hydrology, and urban features. |
| `events.csv` | CSV | 11 | 19 | One row per documented flood report/zone; ground-truth event catalog. |
| `rainfall_daily.csv` | CSV | 36,112 | 5 | Continuous daily rainfall calendar across 37 CHIRPS pixels (Apr–Nov of 2017, 2021, 2022, 2023). |
| `flood_dataset.parquet` | Parquet | 1,809,548 | 40 | The primary model table: candidate days across all 4 study seasons for all 3,026 cells. |
| `flood_dataset_event_windows.csv` | CSV | 27,234 | 40 | CSV extraction containing all cells across the 9 documented flood event days. |
| `flood_dataset_pilot.parquet` | Parquet | 66,572 | 29 | Minimum first sample for testing (22 Aug to 12 Sep 2022). |
| `flood_replay_E2022_09.parquet` | Parquet | 72,624 | 40 | Contiguous validation replay window for held-out event E2022_09 (-14 to +7 days). |
| `validator_output.txt` | Text | 32 | - | Complete terminal output from `pipeline/validate_dataset.py`. |

---

## 2. Primary Dataset Schema (`flood_dataset.parquet`)

All numeric features are in **raw physical units** (no scaling, standardisation, or log-transforms).

| Column Name | Type | Unit | Allowed / Range | % Missing | Definition & Computation |
|---|:---:|:---:|:---:|:---:|---|
| `cell_id` | int64 | ID | 0 to 3,025 | 0.0% | Stable 500 m grid cell identifier, identical across all files. EPSG:32643 native. |
| `date` | string | ISO | YYYY-MM-DD | 0.0% | Calendar day $d$ described by the row (UTC day for CHIRPS precipitation). |
| `lat` | float64 | degrees | 12.83 to 13.14 | 0.0% | WGS84 latitude of cell centroid. |
| `lon` | float64 | degrees | 77.46 to 77.78 | 0.0% | WGS84 longitude of cell centroid. |
| `ward` | int64 | ID | 1 to 198 | 0.0% | BBMP 2011 administrative ward containing the cell centroid. Used for spatial CV. |
| `rain_pixel_id` | int64 | ID | 0 to 36 | 0.0% | ID of the CHIRPS 0.05° pixel supplying rainfall to this cell (Euclidean nearest). |
| `rain_1d_mm` | float64 | mm | 0 to 400 | 0.0% | Total rainfall on day $d$ for the cell's rain pixel. |
| `rain_3d_mm` | float64 | mm | $\ge$ `rain_1d_mm` | 0.0% | Rolling 3-day sum: $\text{rain}(d-2) + \text{rain}(d-1) + \text{rain}(d)$. |
| `rain_7d_mm` | float64 | mm | $\ge$ `rain_3d_mm` | 0.0% | Rolling 7-day sum of precipitation ending on day $d$. |
| `rain_14d_mm` | float64 | mm | $\ge$ `rain_7d_mm` | 0.0% | Rolling 14-day sum of precipitation ending on day $d$. |
| `rain_30d_mm` | float64 | mm | $\ge$ `rain_14d_mm` | 0.0% | Rolling 30-day sum (antecedent moisture proxy) ending on day $d$. |
| `rain_lag1_mm` ... `rain_lag14_mm` | float64 | mm | $\ge 0$ | 0.0% | Antecedent precipitation on day $d-k$ for $k \in [1, 14]$. |
| `elev_m` | float64 | m | 767.1 to 951.7 | 0.0% | Mean raw Copernicus GLO-30 DEM elevation in the cell. |
| `slope_deg` | float64 | degrees | 0.0 to 12.3 | 0.0% | Mean slope derived from Copernicus GLO-30 DEM via Horn's method. |
| `twi` | float64 | index | 4.8 to 13.1 | 0.0% | Topographic Wetness Index: $\ln(\text{flow\_acc\_m2} / \tan(\text{slope}))$. |
| `hand_m` | float64 | m | 0.0 to 58.5 | 0.0% | Height Above Nearest Drainage to hydrologically conditioned stream network. |
| `flow_acc` | float64 | $\text{km}^2$ | 0.0 to 76.5 | 0.0% | Maximum upstream contributing drainage area in $\text{km}^2$ within the cell. |
| `imperv_frac` | float64 | fraction | 0.0 to 0.99 | 0.0% | ESA WorldCover 2021 v200 built-up class fraction (class 50 proxy). |
| `dist_lake_m` | float64 | m | $\ge 0$ | 0.0% | Euclidean distance from cell centroid to nearest OSM water polygon. |
| `dist_drain_m` | float64 | m | $\ge 0$ | 0.0% | Euclidean distance from centroid to nearest OSM waterway / drain. |
| `dist_road_m` | float64 | m | $\ge 0$ | 0.0% | Euclidean distance from centroid to nearest OSM major road network. |
| `lakes_within_1km` | int64 | count | 0 to 11 | 0.0% | Count of distinct dissolved waterbodies intersecting a 1 km centroid buffer. |
| `flood_label` | int64 | flag | 0 or 1 | 0.0% | Binary target: 1 = documented flood/waterlogging; 0 = assumed dry. |
| `label_source` | string | category | `{sar, hotspot_pdf, news, civic_report, none}` | 0.0% | Provenance of label: `hotspot_pdf` (Sajjan 2022), `news` (media reports), or `none`. |
| `label_confidence` | string | category | `{high, medium, low}` | 0.0% | Confidence grade: `high` (verified hotspots), `medium` (named points), `low` (assumed 0 / unverified). |
| `event_id` | string | code | `E{YYYY}_{MM}` or empty | 0.0% | Non-empty inside documented flood event windows; empty string outside. |
| `day_sampling_weight` | float64 | weight | $\ge 1.0$ | 0.0% | Sampling weight: 1.0 (all 598 candidate days retained; no downsampling). |

---

## 3. Reference Tables

### `cells_static.csv`
- Contains: `cell_id`, `rain_pixel_id`, `lat`, `lon`, `ward`, `area_km2` (true clipped area in $\text{km}^2$), plus all 10 static features listed above.
- Zero missing values across all 3,026 cells.

### `rainfall_daily.csv`
- Schema: `date`, `rain_pixel_id`, `rain_mm`, `is_imputed` (integer 0/1), `rain_source` (always `chirps`).
- Complete calendar with 0 missing rows across all 37 pixels: $976\text{ days} \times 37\text{ pixels} = 36,112\text{ rows}$.
