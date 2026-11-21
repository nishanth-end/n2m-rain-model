# Bengaluru Predictive Flood Model — Delivery Package (Member 1)

**Author**: Member 1 (Data Engineer)  
**Recipient**: Member 2 (ML Engineer)  
**Project**: N²M Predictive Flood Alert System (Bengaluru, 24–48h Ahead Flood Risk)  
**Date**: 2026-11-16  
**Git Commit**: `e615b72`  
**Dataset Specification**: Conforms strictly to *Flood Model Dataset Specification v1.0* (all 17 Section 9 checks passed)

---

## 1. Overview & Contents of `delivery/`

This delivery provides the training, evaluation, and replay datasets for XGBoost and sequential flood models across the Greater Bengaluru (BBMP) metropolitan region.

| File Name | Format | Size | Rows | Columns | Purpose |
|---|:---:|:---:|:---:|:---:|---|
| `flood_dataset.parquet` | Parquet | 18.01 MB | 1,764,158 | 42 | Primary ML training and cross-validation table: all 3,026 grid cells across 583 candidate stormy days in May–Nov (2017, 2021, 2022, 2023). 240 positive cell-days across 6 events. |
| `cells_static.csv` | CSV | 0.26 MB | 3,026 | 16 | Master static lookup table: 10 terrain, hydrology, and urban infrastructure features per 500 m grid cell, with ward IDs, coordinates, and nearest CHIRPS pixel ID. |
| `rainfall_daily.csv` | CSV | 1.13 MB | 36,112 | 5 | Continuous unbroken daily rainfall calendar for 37 CHIRPS pixels covering wet seasons (April 1 to November 30) of 2017, 2021, 2022, and 2023 ($976\text{ days} \times 37\text{ pixels}$). Zero nulls, `is_imputed=0`. |
| `events.csv` | CSV | 0.01 MB | 11 | 19 | Ground-truth flood event audit directory: 11 site records across 6 confirmed events with WGS84 coordinates, mapped cell IDs, verified citations, live URLs, and confidence grades. |
| `flood_replay_E2022_09.parquet` | Parquet | 0.90 MB | 72,624 | 42 | Continuous validation replay sequence for held-out event `E2022_09`: 24 consecutive days (22 August to 14 September 2022 $\times$ 3,026 cells) with 188 positive labels across 4–7 September 2022. |
| `flood_dataset_event_windows.csv` | CSV | 131.29 MB | 366,146 | 42 | Full CSV extract containing all 3,026 cells for the 121 May–Nov candidate days within $[-14, +7]$ days of each confirmed event (240 positives). |
| `flood_dataset_pilot.parquet` | Parquet | 0.30 MB | 66,572 | 31 | Minimum first sample for rapid pipeline testing (22 August to 12 September 2022 $\times$ 3,026 cells). |
| `data_dictionary.md` | Markdown | 0.01 MB | 66 | - | Single source of truth column reference, definitions, valid physical ranges, and units for every field. |
| `validator_output.txt` | Text | 0.001 MB | 32 | - | Unaltered terminal execution log of `pipeline/validate_dataset.py` confirming 0 failures across all 17 specification rules. |
| `handoff_stats.txt` | Text | 0.005 MB | 85 | - | Computed audit statistics generated directly from the delivery files via `pipeline/handoff_stats.py`. |

---

## 2. Effective Sample Size & Event Breakdown

### Summary Metrics (Computed from Data)
| Metric | Full Candidate Dataset (`flood_dataset.parquet`) | Event Windows (`flood_dataset_event_windows.csv`) |
|---|:---:|:---:|
| **Total Rows** | 1,764,158 | 366,146 |
| **Grid Cells** | 3,026 | 3,026 |
| **Candidate Days** | 583 | 121 |
| **Distinct Confirmed Events** | 6 (`E2017_08`, `E2017_09`, `E2021_11`, `E2022_05`, `E2022_09`, `E2023_05`) | 6 |
| **Total Positive Cell-Days** | **240** | **240** |
| **Centre-Only Positives (Seed-Days)** | **30** | **30** |
| **Buffer-Only Positives ($3\times3$)** | **210** | **210** |
| **Distinct Seed Cells** | **10** (555, 666, 774, 847, 897, 910, 977, 1444, 1478, 2882) | **10** |
| **Overall Flood Rate** | 0.0136% (0.000136) | 0.0655% (0.000655) |

### Positive Cell-Days Breakdown by Event
| Event ID | Dates | Days | Seed Positives | Buffer Positives ($3\times3$) | Total Positives | Locations Documented |
|---|:---:|:---:|:---:|:---:|:---:|---|
| **`E2017_08`** | 2017-08-15 | 1 | 1 | 8 | 9 | Cell 897 (Koramangala 4th Block) |
| **`E2017_09`** | 2017-09-27..28 | 2 | 2 | 16 | 18 | Cell 774 (Hosur-Sarjapur Rd / Koramangala $\times$ 2 days) |
| **`E2021_11`** | 2021-11-21 | 1 | 1 | 8 | 9 | Cell 2882 (Yelahanka / Kendriya Vihar) |
| **`E2022_05`** | 2022-05-05 | 1 | 1 | 6 | 7 | Cell 555 (RBD Layout, boundary clipped $3\times3$) |
| **`E2022_09`** | 2022-09-04..07 | 4 | 24 | 164 | 188 | 6 hotspots $\times$ 4 days (RBD 555, Wipro 666, Ecospace 847, Epsilon 910, Whitefield 1444, Panathur 977) |
| **`E2023_05`** | 2023-05-21 | 1 | 1 | 8 | 9 | Cell 1478 (KR Circle Underpass) |
| **TOTAL** | | **10** | **30** | **210** | **240** | **10 distinct seed cells across 6 events** |

### Training Sample Size if `E2022_09` is Held Out
When holding out the September 2022 catastrophic flood (`E2022_09`) for validation:
- **Total Positives for Training**: **52 positive cell-days**
- **Centre-Only Positives for Training**: **6 positive cell-days**
- **Buffer-Only Positives for Training**: **46 positive cell-days**

*Recommendation for Member 2*: Due to extreme positive scarcity when holding out `E2022_09`, sample weighting via `day_sampling_weight` and setting `scale_pos_weight` in XGBoost is strongly required. Use Leave-One-Event-Out cross-validation across all 6 events rather than testing on `E2022_09` alone.

---

## 3. Spatial, Hydrologic, and Temporal Specifications

1. **Spatial Framework**:
   - Projected Grid: EPSG:32643 (WGS 84 / UTM Zone 43N), 500 m resolution.
   - Geographic Coordinates: WGS 84 (EPSG:4326) cell centroids.
   - Boundaries: 2011 BBMP delimitation covering 198 wards and 711.59 $\text{km}^2$.
2. **Rainfall Definition & Alignment**:
   - Product: CHIRPS Daily v2.0 p05 GeoTIFFs (UCSB Climate Hazards Center).
   - "Day $d$" Convention: **UTC calendar day** (00:00 to 23:59 UTC, corresponding to 05:30 IST on day $d$ to 05:30 IST on day $d+1$).
   - Storm-to-Flood Alignment: The intense storm on the night of 4 September 2022 (IST) peaked after 21:00 IST (15:30 UTC), registering in CHIRPS on UTC day 4 September. The widespread inundation observed on the morning of 5 September aligns with `rain_1d_mm` from day 5 coupled with `rain_lag1_mm` (day 4 peak) and rolling sums.
3. **Terrain & Static Sources**:
   - DEM: Copernicus GLO-30 DSM (30 m).
   - TWI Formula: $\ln(\text{flow\_acc} / \tan(\text{slope\_rad}))$.
   - Built-up Fraction: ESA WorldCover 2021 v200 (Class 50 built-up proxy).
   - Infrastructure & Waterbodies: OpenStreetMap Overpass vector extracts (waterways, lakes, trunk/primary/secondary roads).

---

## 4. Software Environment, Seeds, and Regeneration

### Software Package Versions
- **Python**: `3.9.6`
- **`pandas`**: `2.3.3`
- **`numpy`**: `2.0.2`
- **`pyarrow`**: `21.0.0`
- **`scipy`**: `1.13.1`
- **`rasterio`**: `1.4.3`
- **`geopandas`**: `1.0.1`
- **`shapely`**: `2.0.7`

### Random Seeds & Determinism
- Random Seed: Fixed at `42` for all row filtering and partitioning.

### Dataset Verification & Reproduction
To validate the delivered datasets:
```bash
# Verify acceptance checks
python pipeline/validate_dataset.py delivery/flood_dataset.parquet

# Run unit tests
pytest tests/test_rainfall.py tests/test_geocode.py tests/test_static.py tests/test_grid.py

# Verify evidence quotations
python pipeline/verify_quotes.py

# Print handoff audit stats
python pipeline/handoff_stats.py
```

---

## 5. Source Licences & Access Dates

| Source | Dataset / Product | Licence | Access Date | URL / Reference |
|---|---|---|:---:|---|
| **UCSB CHC** | CHIRPS Daily v2.0 p05 | Public Domain / CC BY 4.0 | 2026-10-08 | https://data.chc.ucsb.edu/products/CHIRPS-2.0/ |
| **Copernicus** | GLO-30 Digital Elevation Model | Open Access (Copernicus Licence) | 2026-10-07 | https://spacedata.copernicus.eu/collections/copernicus-digital-elevation-model |
| **ESA** | WorldCover 2021 v200 (10 m) | CC BY 4.0 | 2026-10-07 | https://esa-worldcover.org/ |
| **OpenStreetMap** | Waterways, Waterbodies, Roads | ODbL 1.0 | 2026-10-08 | Overpass API |
| **BBMP** | 2011 198 Ward Delimitation | Open Data (OpenCity) | 2026-10-05 | https://data.opencity.in/ |

---

## 6. Critical Operational Limitations (Blunt Summary)

1. **Tiny Effective Sample Size**: The 240 positive rows represent only **30 centre seed-days** across **6 historical events**.
2. **Leave-One-Event-Out Validation Scarcity**: Holding out `E2022_09` leaves only **52 positives (6 seed-days)** for training citywide.
3. **Coarse Spatial Rainfall Resolution**: Greater Bengaluru maps to only **37 CHIRPS pixels**, and all positive cells map to only **8 pixels**. Rainfall cannot separate neighbouring cells under the same pixel; static terrain features will dominate spatial predictions.
4. **Severe Negative Label Noise**: In `flood_dataset.parquet`, **1,012 out of 1,019 pixel-days with 3-day rainfall $\ge 60\text{ mm}$ carry `flood_label == 0`**. Negatives represent unobserved/unreported cells, not verified dry ground.
5. **Temporal Leakage vs. 24–48h Forecast Goal**: The label is same-day concurrent with `rain_1d_mm`. For a true 24–48h predictive early warning model, `rain_1d_mm` must be excluded (using antecedent lags only) or substituted with an NWP rainfall forecast.
6. **Rain-Gated Sampling**: The dataset contains only 583 candidate stormy days ($\max(\text{rain\_3d}) \ge 10\text{ mm}$ or event windows). The production inference API must apply the identical filter.
