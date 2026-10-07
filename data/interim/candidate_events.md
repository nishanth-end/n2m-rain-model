# Candidate Flood Events Register and Audit

**File Purpose**: Records integrity audit of `data/events.csv`, strict point-in-polygon (PIP) verification, deduplicated positive cell-days volume analysis, and candidate historical events for team review.
**Rule**: NEVER add candidate events to `data/events.csv` without explicit Member 1 and Member 2 review and verification.

---

## 1. Audit of Current `data/events.csv` (Strict PIP Verification)

- **Total Rows**: 10 rows
- **Distinct Locations**: 9 unique names / 9 unique coordinates
- **Points Strictly Inside Grid Footprint**: 7 rows
- **Points Outside Grid Footprint**: 3 rows (RBD Layout and Wipro Campus)
- **Distinct Cells (Inside points)**: 7 cells
- **Dates Covered**: 2017-08-15 to 2022-09-07

### Verification Table

| Event ID | Date Window | Location Name | PIP Inside? | Cell ID | Ward | Dist to Centroid (m) | Dist to Lattice Center (m) | Dist to Cell Edge (m) | Dist to Grid Boundary (m) |
|---|---|---|---|---|---|---|---|---|---|
| `E2022_09` | 2022-09-05 to 2022-09-07 | RBD Layout (Sarjapur Road) | **NO (OUTSIDE)** | *(nearest 558)* | *(outside BBMP)* | 640.6 m | 574.6 m | n/a | 444.9 m |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Wipro Campus (Sarjapur Road) | **NO (OUTSIDE)** | *(nearest 557)* | *(outside BBMP)* | 786.1 m | 659.7 m | n/a | 665.2 m |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Outer Ring Road (RMZ Ecospace / Saul Kere reach) | YES | **847** | #150 (Bellanduru) | 153.9 m | 153.9 m | 100.1 m | n/a |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Epsilon Layout / Yemalur Road (ORR Kadubeesanahalli bridge) | YES | **910** | #150 (Bellanduru) | 193.4 m | 193.4 m | 56.7 m | n/a |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Borewell Road (Whitefield) | YES | **1444** | #84 (Hagadur) | 123.2 m | 123.2 m | 145.6 m | n/a |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Panathur-Balagere Road (near BWSSB STP/Varthur lake) | YES | **977** | #150 (Bellanduru) | 211.8 m | 211.8 m | 64.7 m | n/a |
| `E2022_05` | 2022-05-05 to 2022-05-05 | RBD Layout (Sarjapur Road) | **NO (OUTSIDE)** | *(nearest 558)* | *(outside BBMP)* | 640.6 m | 574.6 m | n/a | 444.9 m |
| `E2021_11` | 2021-11-21 to 2021-11-21 | Yelahanka / Jakkur, North Bengaluru | YES | **2882** | #1 (Kempegowda Ward) | 261.7 m | 261.7 m | 12.4 m | n/a |
| `E2017_08` | 2017-08-15 to 2017-08-15 | Koramangala 4th Block | YES | **899** | #114 (Agaram) | 64.4 m | 64.4 m | 187.3 m | n/a |
| `E2017_09` | 2017-09-27 to 2017-09-28 | Hosur-Sarjapur Road / Anugraha Layout, Koramangala | YES | **774** | #173 (Jakkasandra) | 87.2 m | 87.2 m | 188.0 m | n/a |

### Root Cause for Outside Points (RBD Layout and Wipro Campus):
- **Diagnosis**: Combination of genuine municipal boundary exclusion and hand-rounded coordinates.
- **Boundary Reality**: In the 2011 BBMP 198-ward delimitation, Ward 150 (Bellanduru) terminates along Sarjapur Road. Physical gated layouts south of Sarjapur Road (Rainbow Drive Layout, Halanayakanahalli, Junnasandra) fell in Anekal Taluk panchayat jurisdiction.
- **Coordinate Precision**: Hand-entered coordinates (12.901, 77.700) and (12.900, 77.696) place the points 444.9 m and 665.2 m south of the Ward 150 border. Independent OSM Nominatim geocoding locates the entrance of Rainbow Drive Layout at 12.9062, 77.6868, which is 5.6 m south of the BBMP border.
- **Action Taken**: Flagged with `outside_grid=True` and `cell_id=NA`. No silent snapping.

---

## 2. Positive Cell-Days Yield vs. Spec Targets (Spatially Deduplicated)

- **Spec Requirement (Section 4.2)**: Minimum at least 100 positive cell-days; target good at least 500 positive cell-days.

### Yield Matrix

| Evaluation Scope | Assumption (a): Single Point Cell | Assumption (b): Cell + 8 Neighbours |
|---|---|---|
| **Strict Inside Points Only (n=7)** | **16 cell-days** | **123 cell-days** |
| **All 10 Points (if outside points snapped)** | **23 cell-days** | **153 cell-days** |
| *Naive non-deduplicated arithmetic* | *23 cell-days* | *207 cell-days (INVALID: double-counted)* |

### Deduplication Proof and Lattice Structure
- In `E2022_09`, seed cells 847 and 910 have lattice offset (d_col=-1, d_row=+1). As diagonal neighbours, their 3x3 footprints share exactly 4 cells: [846, 847, 910, 911].
- Seeds 847 and 977 share 2 cells [911, 912]; seeds 910 and 977 share 2 cells [911, 976]. Cell 911 is shared across three blocks.
- Net unique cells per day in `E2022_09` under (b) inside-only: 29 cells. Over 3 days: 29 * 3 = 87 cell-days.
- Adding outside snapped cells 557 and 558 (which share 4 cells with each other) adds 8 cells/day, totaling 37 cells/day * 3 days = 111 cell-days.

---

## 3. Candidate Additional Historical Flood Events (Audit and Status)

### Candidate 1: Kendriya Vihar / Yelahanka Lake Overflow (Nov 2021)
- **Primary Source**: The Hindu (22 Nov 2021). "Heavy rain submerges Kendriya Vihar apartments in Yelahanka; boats deployed". URL: https://www.thehindu.com/news/cities/bangalore/heavy-rain-floods-several-areas-in-bengaluru/article37628863.ece
- **Flood Date**: 2021-11-21 to 2021-11-22
- **Location**: Kendriya Vihar, Bellahalli / Kogilu Road, Yelahanka (approx 13.116, 77.587)
- **Audit Status**: **SAME-CLUSTER / DUPLICATE** of existing event `E2021_11` (Yelahanka / Jakkur, 2021-11-21). Located ~2.2 km from the stored Jakkur point in the same storm basin. Adding this would duplicate the Nov 2021 event storm signal rather than provide an independent event.

### Candidate 2: Rainbow Drive / ORR Inundation (Aug 2022)
- **Primary Source**: Deccan Herald (30 Aug 2022). "Floods return to ORR, Rainbow Drive Layout after overnight rain". URL: https://www.deccanherald.com/city/top-bengaluru-stories/floods-return-to-orr-rainbow-drive-layout-after-overnight-rain-1140643.html
- **Flood Date**: 2022-08-29 to 2022-08-31
- **Location**: Rainbow Drive Layout (12.906, 77.687) and ORR Ecospace (12.927, 77.693)
- **Audit Status**: **NEW EVENT (different date), but SAME GEOGRAPHIC CLUSTER**. Pre-monsoon downpour 6 days before the Sep 5 storm. Rainbow Drive remains outside the 2011 boundary; ORR Ecospace matches Cell 847.

### Candidate 3: Shivajinagar / Central Deluge (Oct 2022)
- **Primary Source**: Indian Express (20 Oct 2022). "Bengaluru rain: Shivajinagar waterlogged, traffic snarls across city". URL: https://indianexpress.com/article/cities/bangalore/bengaluru-rain-traffic-snarls-waterlogging-october-8219462/
- **Flood Date**: 2022-10-19 to 2022-10-20
- **Location**: Russell Market / Shivajinagar bus terminus (approx 12.985, 77.605)
- **Audit Status**: **VERIFIED NEW EVENT and NEW GEOGRAPHY**. Distinct storm in central core.
- **Grid Match**: Point-in-polygon matches **Cell 1618** (Ward 110: Sampangiram Nagar).
- **Yield Added**: +2 cell-days under (a); +18 cell-days under (b) (isolated cell, 0 overlap with Bellandur).

### Candidate 4: KR Circle Underpass Flash Flood (May 2023)
- **Primary Source**: BBC News (22 May 2023). "Bengaluru rain: Tech worker dies after car submerges in waterlogged underpass". URL: https://www.bbc.com/news/world-asia-india-65671148
- **Flood Date**: 2023-05-21
- **Location**: KR Circle Underpass (approx 12.975, 77.589)
- **Audit Status**: **VERIFIED NEW EVENT and NEW GEOGRAPHY**. Pre-monsoon flash flood in central underpass.
- **Grid Match**: Point-in-polygon matches **Cell 1478** (Ward 110: Sampangiram Nagar).
- **Yield Added**: +1 cell-day under (a); +9 cell-days under (b) (isolated cell, 0 overlap).
