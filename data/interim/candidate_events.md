# Candidate Flood Events Register & Audit

**File Purpose**: Records integrity audit of `data/events.csv`, nearest `cell_id` matches, positive cell-days volume analysis, and documented candidate flood events catalogued from municipal reports and media for team review.
**Rule**: NEVER add candidate events to `data/events.csv` without explicit Member 1 & 2 review and verification.

---

## 1. Audit of Current `data/events.csv`

- **Row Count**: 10 rows
- **Distinct Events**: 5 (`E2017_08`, `E2017_09`, `E2021_11`, `E2022_05`, `E2022_09`)
- **Distinct Locations**: 9
- **Unique Matched Cells**: 9 cells
- **Dates Covered**: 2017-08-15 to 2022-09-07

### Matched Cells Mapping Table

| Event ID | Date Window | Location Name | Matched `cell_id` | Ward | Distance to Centroid (m) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
| `E2022_09` | 2022-09-05 to 2022-09-07 | RBD Layout (Sarjapur Road) | **558** | #150 (Bellanduru) | 640.6 m | `hotspot_pdf` | `high` |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Wipro Campus (Sarjapur Road) | **557** | #150 (Bellanduru) | 786.1 m | `hotspot_pdf` | `high` |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Outer Ring Road (RMZ Ecospace / Saul Kere reach) | **847** | #150 (Bellanduru) | 153.9 m | `hotspot_pdf` | `high` |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Epsilon Layout / Yemalur Road (ORR Kadubeesanahalli bridge) | **910** | #150 (Bellanduru) | 193.4 m | `hotspot_pdf` | `high` |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Borewell Road (Whitefield) | **1444** | #84 (Hagadur) | 123.2 m | `hotspot_pdf` | `high` |
| `E2022_09` | 2022-09-05 to 2022-09-07 | Panathur-Balagere Road (near BWSSB STP/Varthur lake) | **977** | #150 (Bellanduru) | 211.8 m | `hotspot_pdf` | `high` |
| `E2022_05` | 2022-05-05 to 2022-05-05 | RBD Layout (Sarjapur Road) | **558** | #150 (Bellanduru) | 640.6 m | `news` | `medium` |
| `E2021_11` | 2021-11-21 to 2021-11-21 | Yelahanka / Jakkur, North Bengaluru | **2882** | #1 (Kempegowda Ward) | 261.7 m | `news` | `medium` |
| `E2017_08` | 2017-08-15 to 2017-08-15 | Koramangala 4th Block | **899** | #114 (Agaram) | 64.4 m | `news` | `medium` |
| `E2017_09` | 2017-09-27 to 2017-09-28 | Hosur-Sarjapur Road / Anugraha Layout, Koramangala | **774** | #173 (Jakkasandra) | 87.2 m | `news` | `medium` |

### Identified Weaknesses / Issues in `data/events.csv`:
1. **Missing URLs**: Rows 1–6 (Sajjan 2022 technical study) and Row 7 (Indian Express May 2022) have blank `source_url`. (The Sajjan 2022 study is stored as a local PDF in `references/Floods_at_Bengaluru_City_A_Technical_Stu.pdf`).
2. **Spatial Imbalance**: 6 of the 10 rows belong to a single storm (`E2022_09`), and all 6 are clustered in Southeast Bengaluru (Bellandur/Sarjapur/Whitefield valley corridor).
3. **Coordinate Precision**: Lat/lon values are approximate locality centroids (e.g. 12.901, 77.700). Distance to 500m cell centroids ranges up to 786 m for edge locations.

---

## 2. Positive Cell-Days Yield vs. Spec Targets

- **Spec Requirement (Section 4.2)**: Minimum $\ge 100$ positive cell-days; target good $\ge 500$ positive cell-days.
- **Yield under Assumption (a) [Point cell only]**: **23 positive cell-days**
  - **Verdict**: **CRITICAL SHORTFALL** (only 23% of the 100 minimum threshold).
- **Yield under Assumption (b) [Cell + 8 adjacent 500m neighbours]**: **207 positive cell-days**
  - **Verdict**: Exceeds minimum threshold (207 > 100), but falls well short of the recommended target of 500+ cell-days.

---

## 3. Candidate Additional Historical Flood Events (For Review Only)

The following events are documented in open municipal, IMD, and news archives. They are compiled here for Member 1/2 review and must **not** be merged into `events.csv` without formal approval.

### Candidate 1: Kendriya Vihar / Yelahanka Lake Overflow (November 2021)
- **Proposed Event ID**: `E2021_11_YEL`
- **Date Window**: 2021-11-21 to 2021-11-22
- **Locations**: Kendriya Vihar Apartment Complex, Yelahanka; Manyata Embassy Business Park, Nagavara; Kogilu Cross.
- **Coordinates (approx)**: Kendriya Vihar (13.116, 77.587); Manyata Tech Park (13.047, 77.620).
- **Evidence / Source**:
  - The Hindu (22 Nov 2021): *"Heavy rain submerges Kendriya Vihar apartments in Yelahanka; boats deployed"*. https://www.thehindu.com/news/cities/bangalore/heavy-rain-floods-several-areas-in-bengaluru/article37628863.ece
  - KSNDMC Alert: 153 mm rainfall recorded at Jakkur gauge within 24 hours.
- **Estimated Yield**: 2–3 places $\times$ 2 days = 4–6 point cell-days (36–54 with 8-neighbour buffer).

### Candidate 2: August 2022 Pre-Storm Deluge (30 August 2022)
- **Proposed Event ID**: `E2022_08`
- **Date Window**: 2022-08-29 to 2022-08-31
- **Locations**: Rainbow Drive Layout (Sarjapur Road); EcoSpace Outer Ring Road; HSR Layout Sector 6.
- **Coordinates (approx)**: Rainbow Drive (12.903, 77.702); HSR Sector 6 (12.915, 77.638).
- **Evidence / Source**:
  - Deccan Herald (30 Aug 2022): *"Floods return to Outer Ring Road, Rainbow Drive Layout after overnight rain"*. https://www.deccanherald.com/city/top-bengaluru-stories/floods-return-to-orr-rainbow-drive-layout-after-overnight-rain-1140643.html
- **Estimated Yield**: 3 places $\times$ 3 days = 9 point cell-days (81 with 8-neighbour buffer).

### Candidate 3: October 2022 Heavy Inundation (19 October 2022)
- **Proposed Event ID**: `E2022_10`
- **Date Window**: 2022-10-19 to 2022-10-20
- **Locations**: Shivajinagar (Cantonment); HBR Layout; Thanisandra Main Road.
- **Coordinates (approx)**: Shivajinagar (12.985, 77.605); HBR Layout (13.028, 77.632).
- **Evidence / Source**:
  - Indian Express (20 Oct 2022): *"Bengaluru rain: Shivajinagar waterlogged, traffic snarls across city"*. https://indianexpress.com/article/cities/bangalore/bengaluru-rain-traffic-snarls-waterlogging-october-8219462/
- **Estimated Yield**: 3 places $\times$ 2 days = 6 point cell-days (54 with 8-neighbour buffer).

### Candidate 4: May 2023 KR Circle Underpass Storm (21 May 2023)
- **Proposed Event ID**: `E2023_05`
- **Date Window**: 2023-05-21 to 2023-05-21
- **Locations**: KR Circle Underpass (Central Bengaluru); Majestic / Subhash Nagar; Chickpet metro reach.
- **Coordinates (approx)**: KR Circle (12.975, 77.589); Majestic (12.977, 77.572).
- **Evidence / Source**:
  - BBC News (22 May 2023): *"Bengaluru rain: Tech worker dies after car submerges in waterlogged underpass"*. https://www.bbc.com/news/world-asia-india-65671148
- **Estimated Yield**: 2 places $\times$ 1 day = 2 point cell-days (18 with 8-neighbour buffer).

---

## 4. Summary Recommendation for Model Team

1. Retain the **10 point reports** as verified primary truth in `events.csv`.
2. To address the volume shortfall (23 vs 100/500), the team can:
   - Formally approve Candidate Events 1, 2, and 3 above to expand spatial coverage into North and Central Bengaluru.
   - Apply spatial neighbour expansion ($3 \times 3$ cell footprint, radius 500 m) with `label_confidence = medium` around documented inundation centroids.
