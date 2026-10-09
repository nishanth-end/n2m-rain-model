# Bengaluru Predictive Flood Model — Delivery Package (Member 1)

Prepared for Member 2 (Model Developer) according to the specifications in `Flood Model Dataset Specification v1.0`.

---

## 1. Overview & Contents of `delivery/`

This delivery provides the training, evaluation, and replay datasets for XGBoost and sequential flood models across the Greater Bengaluru (BBMP) metropolitan region.

- **`cells_static.csv`**: Master static lookup table containing 3,026 grid cells at 500 m spacing. Includes true clipped polygon areas, ward IDs, nearest CHIRPS pixel mapping, and 10 topography/hydrology/urban features.
- **`events.csv`**: Ground-truth event audit log with 10 rows across 5 confirmed flood events (2017 to 2023). Contains exact coordinates, mapped cell IDs, verified citations, live URLs, and confidence grades.
- **`rainfall_daily.csv`**: Continuous daily rainfall time series for 37 CHIRPS pixels covering the wet seasons (April 1 to November 30) of 2017, 2021, 2022, and 2023 ($976 \times 37 = 36,112$ rows, 0 nulls, `is_imputed=0`).
- **`flood_dataset.parquet`**: The primary machine learning dataset containing **1,764,158 rows** (583 May–Nov candidate days $\times$ 3,026 cells) across 42 columns (including `audit_is_buffer_cell` and `audit_geocode_precision`). Zero April rows included.
- **`flood_dataset_event_windows.csv`**: CSV containing all 3,026 cells for the 102 May–Nov event window days ($-14$ to $+7$ days around each confirmed event; **308,652 rows**).
- **`flood_dataset_pilot.parquet`**: Minimum first sample for testing (22 Aug to 12 Sep 2022; 66,572 rows).
- **`flood_replay_E2022_09.parquet`**: Continuous replay sequence for held-out event `E2022_09` from 22 August to 14 September 2022 (24 contiguous days $\times$ 3,026 cells = **72,624 rows**).
- **`data_dictionary.md`**: Complete schema, definitions, valid ranges, and units for every column.
- **`validator_output.txt`**: Unaltered execution report of `pipeline/validate_dataset.py` confirming 0 failures.

---

## 2. Effective Sample Size & Event Breakdown

### Summary Metrics
| Metric | Full Candidate Dataset | Event Windows (`flood_dataset_event_windows.csv`) |
|---|:---:|:---:|
| **Total Rows** | 1,764,158 | 308,652 |
| **Grid Cells** | 3,026 | 3,026 |
| **Unique Days** | 583 | 102 |
| **Distinct Confirmed Events** | 5 (`E2017_08`, `E2021_11`, `E2022_05`, `E2022_09`, `E2023_05`) | 5 |
| **Total Positive Cell-Days** | **175** | **175** |
| **Centre-Cells-Only Positives** | **22** | **22** |
| **Buffer-Cells-Only Positives** | **153** | **153** |
| **Flood Rate (All Rows)** | 0.0099% (0.000099) | 0.0567% (0.000567) |

### Positive Cell-Days Breakdown by Event
- **`E2017_08`** (15 Aug 2017): Total = 9 | Centre-only = 1 (Cell 897 Koramangala 4th Block) | Buffer-only = 8
- **`E2021_11`** (21 Nov 2021): Total = 9 | Centre-only = 1 (Cell 2882 Yelahanka Kendriya Vihar) | Buffer-only = 8
- **`E2022_05`** (05 May 2022): Total = 7 | Centre-only = 1 (Cell 555 Rainbow Drive Layout) | Buffer-only = 6 ($3\times3$ lattice in BBMP)
- **`E2022_09`** (05–07 Sep 2022): Total = 141 | Centre-only = 18 (6 hotspots $\times$ 3 days) | Buffer-only = 123
- **`E2023_05`** (21 May 2023): Total = 9 | Centre-only = 1 (Cell 1478 KR Circle Underpass) | Buffer-only = 8

### Training Sample Size if `E2022_09` is Held Out
When holding out the September 2022 catastrophic flood (`E2022_09`) for validation:
- **Total Positives for Training**: **34 positive cell-days**
- **Centre-Only Positives for Training**: **4 positive cell-days**
- **Buffer-Only Positives for Training**: **30 positive cell-days**

*Recommendation for Member 2*: Due to extreme positive scarcity when holding out `E2022_09`, sample weighting via `day_sampling_weight` and setting `scale_pos_weight` in XGBoost is strongly required.

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

### Dataset Regeneration
To validate the delivered datasets:
```bash
python pipeline/validate_dataset.py delivery/flood_dataset.parquet
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

## 6. Known Weaknesses & Deviations (For Member 2)

1. **CHIRPS Spatial Smoothing**: CHIRPS has ~5 km resolution (37 pixels cover the entire city). Extreme localized cloudbursts are smoothed across 5 km grid cells. Models should rely heavily on cumulative features (`rain_3d_mm`, `rain_7d_mm`, `rain_30d_mm`).
2. **`E2022_05` Pre-Monsoon Window Truncation**: `E2022_05` (5 May 2022) occurred early in the pre-monsoon. The study season dataset begins on May 1 (with April 1–30 downloaded as the 30-day antecedent buffer). Because March 2022 CHIRPS data was not in the original seasonal download archive, the $-14$ day window (21–30 April 2022) is omitted from `flood_dataset.parquet` to guarantee that all rows strictly conform to the May–November study definition and feature non-null 30-day rolling sums.
3. **Reporting Bias in Ground Truth**: High-confidence positive labels cluster along major IT corridors (ORR, Whitefield, Sarjapur, Yelahanka) and arterial underpasses. Unlabelled cells (`flood_label=0`, `label_confidence=low`) represent *unreported* locations rather than proven dry ground.
4. **UTC vs IST Offset**: A storm occurring between 00:00 and 05:30 IST falls into the preceding UTC calendar day. Using `rain_lag1_mm` and `rain_3d_mm` accounts for this offset.
