# Candidate Flood Events Register & Audit

**File Purpose**: Records integrity audit of `data/events.csv`, strict point-in-polygon (PIP) verification, deduplicated positive cell-days volume analysis, and candidate historical events for team review.
**Rule**: NEVER add candidate events to `data/events.csv` without explicit Member 1 & 2 review and verification.

---

## 1. Audit of Current `data/events.csv` (Strict PIP Verification)

- **Total Rows**: 10 rows
- **Distinct Locations**: 9 unique names / 9 unique coordinates
- **Points Strictly Inside Grid Footprint**: 7 rows
- **Points Outside Grid Footprint**: 3 rows (`RBD Layout` and `Wipro Campus`)
- **Distinct Cells (Inside points)**: 7 cells
- **Dates Covered**: 2017-08-15 to 2022-09-07

### Verification Table

| Event ID | Date Window | Location Name | PIP Inside? | Cell ID | Ward | Dist to Centroid (m) | Dist to Lattice Center (m) | Dist to Boundary (m) |
|---|---|---|---|---|---|---|---|---|
| `E2022_09` | 2022-09-05 to 2022-09-07 | RBD Layout (Sarjapur Road) | **NO (OUTSIDE)** | *(nearest 558)* | *(outside BBMP)* | 640.6 m | 574.6 m | 444.9 m |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Wipro Campus (Sarjapur Road) | **NO (OUTSIDE)** | *(nearest 557)* | *(outside BBMP)* | 786.1 m | 659.7 m | 665.2 m |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Outer Ring Road (RMZ Ecospace / Saul Kere reach) | YES | **847** | #150 (Bellanduru) | 153.9 m | 153.9 m | 0.0 m |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Epsilon Layout / Yemalur Road (ORR Kadubeesanahalli bridge) | YES | **910** | #150 (Bellanduru) | 193.4 m | 193.4 m | 0.0 m |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Borewell Road (Whitefield) | YES | **1444** | #84 (Hagadur) | 123.2 m | 123.2 m | 0.0 m |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Panathur-Balagere Road (near BWSSB STP/Varthur lake) | YES | **977** | #150 (Bellanduru) | 211.8 m | 211.8 m | 0.0 m |
| `E2022_05` | 2022-05-05 to 2022-05-05 | RBD Layout (Sarjapur Road) | **NO (OUTSIDE)** | *(nearest 558)* | *(outside BBMP)* | 640.6 m | 574.6 m | 444.9 m |
| `E2021_11` | 2021-11-21 to 2021-11-21 | Yelahanka / Jakkur, North Bengaluru | YES | **2882** | #1 (Kempegowda Ward) | 261.7 m | 261.7 m | 0.0 m |
| `E2017_08` | 2017-08-15 to 2017-08-15 | Koramangala 4th Block | YES | **899** | #114 (Agaram) | 64.4 m | 64.4 m | 0.0 m |
| `E2017_09` | 2017-09-27 to 2017-09-28 | Hosur-Sarjapur Road / Anugraha Layout, Koramangala | YES | **774** | #173 (Jakkasandra) | 87.2 m | 87.2 m | 0.0 m |

### Root Cause for Outside Points (RBD Layout and Wipro Campus):
- **Finding**: Diagnosis (a) — Points lie outside the 2011 BBMP 198-ward administrative boundary.
- **RBD Layout (12.901, 77.700)**: Lies 444.9 m south of the Ward 150 (Bellanduru) border.
- **Wipro Campus (12.900, 77.696)**: Lies 665.2 m south of the Ward 150 border.
- **Action Taken**: Flagged with `outside_grid=True` and `cell_id=NA`. No silent snapping.

---

## 2. Positive Cell-Days Yield vs. Spec Targets (Spatially Deduplicated)

- **Spec Requirement (Section 4.2)**: Minimum $\ge 100$ positive cell-days; target good $\ge 500$ positive cell-days.

### Yield Matrix

| Evaluation Scope | Assumption (a): Single Point Cell | Assumption (b): Cell + 8 Neighbours |
|---|---|---|
| **Strict Inside Points Only (n=7)** | **16 cell-days** | **123 cell-days** |
| **All 10 Points (if outside points snapped)** | **23 cell-days** | **153 cell-days** |
| *Naive non-deduplicated arithmetic* | *23 cell-days* | *207 cell-days (INVALID: double-counted)* |

- **Note on Deduplication**: Naive arithmetic gave 207 cell-days by multiplying $9 \times \text{locations} \times \text{days}$. In reality, adjacent points (Wipro/RBD and RMZ/Epsilon) have overlapping $3 \times 3$ neighbour blocks, and edge cells have fewer than 8 interior neighbours. True deduplicated yield is **153 cell-days** (all 10 points) or **123 cell-days** (inside points only).

---

## 3. Candidate Additional Historical Flood Events (For Review Only)

1. **Kendriya Vihar / Yelahanka Lake Overflow (Nov 2021)**: 2021-11-21 to 2021-11-22 (The Hindu, 22 Nov 2021).
2. **Rainbow Drive / ORR Inundation (Aug 2022)**: 2022-08-29 to 2022-08-31 (Deccan Herald, 30 Aug 2022).
3. **Shivajinagar / Central Deluge (Oct 2022)**: 2022-10-19 to 2022-10-20 (Indian Express, 20 Oct 2022).
4. **KR Circle Underpass Flash Flood (May 2023)**: 2023-05-21 (BBC News, 22 May 2023).
