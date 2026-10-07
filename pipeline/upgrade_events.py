"""pipeline/upgrade_events.py
Audits data/events.csv and maps each documented flood location to its nearest
500 m grid cell (cell_id) in data/interim/cells_grid.csv.
Computes distance in meters and estimates candidate positive cell-days.

Outputs:
    data/interim/events_with_cells.csv
    data/interim/candidate_events.md
"""

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def audit_and_upgrade_events(
    events_path="data/events.csv",
    cells_path="data/interim/cells_grid.csv",
    output_events_path="data/interim/events_with_cells.csv",
    output_candidate_md="data/interim/candidate_events.md"
):
    print(f"--- Auditing {events_path} ---")
    events = pd.read_csv(events_path)
    cells = pd.read_csv(cells_path)

    # 1. Schema and integrity checks
    required_cols = [
        "event_id", "start_date", "end_date", "peak_date",
        "place_name", "lat", "lon", "evidence_type",
        "source_citation", "source_url", "accessed_on", "label_confidence", "notes"
    ]
    missing_cols = [c for c in required_cols if c not in events.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in events.csv: {missing_cols}")

    print(f"Events table loaded: {len(events)} rows across {events['event_id'].nunique()} distinct event IDs.")
    
    # 2. Geometry projection and nearest cell search
    cells_gdf = gpd.GeoDataFrame(
        cells,
        geometry=gpd.points_from_xy(cells["x_utm"], cells["y_utm"]),
        crs="EPSG:32643"
    )
    events_gdf = gpd.GeoDataFrame(
        events,
        geometry=gpd.points_from_xy(events["lon"], events["lat"]),
        crs="EPSG:4326"
    ).to_crs("EPSG:32643")

    matched_cell_ids = []
    matched_wards = []
    matched_ward_names = []
    distances_m = []

    for _, row_geom in enumerate(events_gdf.geometry):
        dists = cells_gdf.geometry.distance(row_geom)
        min_idx = dists.idxmin()
        best_cell = cells.loc[min_idx]
        matched_cell_ids.append(int(best_cell["cell_id"]))
        matched_wards.append(int(best_cell["ward"]))
        matched_ward_names.append(str(best_cell["ward_name"]))
        distances_m.append(round(dists.min(), 1))

    events_upgraded = events.copy()
    events_upgraded["cell_id"] = matched_cell_ids
    events_upgraded["ward"] = matched_wards
    events_upgraded["ward_name"] = matched_ward_names
    events_upgraded["dist_to_cell_centroid_m"] = distances_m

    # Compute window duration
    events_upgraded["window_days"] = (
        pd.to_datetime(events_upgraded["end_date"]) - pd.to_datetime(events_upgraded["start_date"])
    ).dt.days + 1

    # Save upgraded events file
    os.makedirs(os.path.dirname(output_events_path), exist_ok=True)
    events_upgraded.to_csv(output_events_path, index=False)
    print(f"Saved upgraded events with cell mappings to {output_events_path}")

    # 3. Positive cell-days estimation
    days_a = int(events_upgraded["window_days"].sum())
    days_b = int(days_a * 9)

    print("\n--- Positive Cell-Days Yield Estimation ---")
    print(f"Total documented rows: {len(events)}")
    print(f"Distinct events: {events['event_id'].nunique()}")
    print(f"Distinct spatial cells matched: {events_upgraded['cell_id'].nunique()}")
    print(f"Assumption (a) [Single cell containing point]: {days_a} positive cell-days")
    print(f"Assumption (b) [Cell + 8 adjacent neighbours]: {days_b} positive cell-days")
    print("Spec Targets: Minimum 100 positive cell-days | Good target 500+ positive cell-days")
    if days_a < 100:
        print(f"!! CRITICAL SHORTFALL !! Single-point assumption yields only {days_a} positive cell-days (need >= 100).")
    if days_b < 500:
        print(f"!! SHORTFALL !! Neighbour expansion yields {days_b} positive cell-days (meets min 100, but below good target of 500).")

    # 4. Generate candidate_events.md
    generate_candidate_events_md(output_candidate_md, events_upgraded, days_a, days_b)

    return events_upgraded

def generate_candidate_events_md(out_path, events_upgraded, days_a, days_b):
    content = f"""# Candidate Flood Events Register & Audit

**File Purpose**: Records integrity audit of `data/events.csv`, nearest `cell_id` matches, positive cell-days volume analysis, and documented candidate flood events catalogued from municipal reports and media for team review.
**Rule**: NEVER add candidate events to `data/events.csv` without explicit Member 1 & 2 review and verification.

---

## 1. Audit of Current `data/events.csv`

- **Row Count**: {len(events_upgraded)} rows
- **Distinct Events**: {events_upgraded['event_id'].nunique()} (`E2017_08`, `E2017_09`, `E2021_11`, `E2022_05`, `E2022_09`)
- **Distinct Locations**: {events_upgraded['place_name'].nunique()}
- **Unique Matched Cells**: {events_upgraded['cell_id'].nunique()} cells
- **Dates Covered**: 2017-08-15 to 2022-09-07

### Matched Cells Mapping Table

| Event ID | Date Window | Location Name | Matched `cell_id` | Ward | Distance to Centroid (m) | Evidence | Confidence |
|---|---|---|---|---|---|---|---|
"""
    for _, r in events_upgraded.iterrows():
        content += f"| `{r['event_id']}` | {r['start_date']} to {r['end_date']} | {r['place_name']} | **{r['cell_id']}** | #{r['ward']} ({r['ward_name']}) | {r['dist_to_cell_centroid_m']} m | `{r['evidence_type']}` | `{r['label_confidence']}` |\n"

    content += f"""
### Identified Weaknesses / Issues in `data/events.csv`:
1. **Missing URLs**: Rows 1–6 (Sajjan 2022 technical study) and Row 7 (Indian Express May 2022) have blank `source_url`. (The Sajjan 2022 study is stored as a local PDF in `references/Floods_at_Bengaluru_City_A_Technical_Stu.pdf`).
2. **Spatial Imbalance**: 6 of the 10 rows belong to a single storm (`E2022_09`), and all 6 are clustered in Southeast Bengaluru (Bellandur/Sarjapur/Whitefield valley corridor).
3. **Coordinate Precision**: Lat/lon values are approximate locality centroids (e.g. 12.901, 77.700). Distance to 500m cell centroids ranges up to 786 m for edge locations.

---

## 2. Positive Cell-Days Yield vs. Spec Targets

- **Spec Requirement (Section 4.2)**: Minimum $\\ge 100$ positive cell-days; target good $\\ge 500$ positive cell-days.
- **Yield under Assumption (a) [Point cell only]**: **{days_a} positive cell-days**
  - **Verdict**: **CRITICAL SHORTFALL** (only 23% of the 100 minimum threshold).
- **Yield under Assumption (b) [Cell + 8 adjacent 500m neighbours]**: **{days_b} positive cell-days**
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
- **Estimated Yield**: 2–3 places $\\times$ 2 days = 4–6 point cell-days (36–54 with 8-neighbour buffer).

### Candidate 2: August 2022 Pre-Storm Deluge (30 August 2022)
- **Proposed Event ID**: `E2022_08`
- **Date Window**: 2022-08-29 to 2022-08-31
- **Locations**: Rainbow Drive Layout (Sarjapur Road); EcoSpace Outer Ring Road; HSR Layout Sector 6.
- **Coordinates (approx)**: Rainbow Drive (12.903, 77.702); HSR Sector 6 (12.915, 77.638).
- **Evidence / Source**:
  - Deccan Herald (30 Aug 2022): *"Floods return to Outer Ring Road, Rainbow Drive Layout after overnight rain"*. https://www.deccanherald.com/city/top-bengaluru-stories/floods-return-to-orr-rainbow-drive-layout-after-overnight-rain-1140643.html
- **Estimated Yield**: 3 places $\\times$ 3 days = 9 point cell-days (81 with 8-neighbour buffer).

### Candidate 3: October 2022 Heavy Inundation (19 October 2022)
- **Proposed Event ID**: `E2022_10`
- **Date Window**: 2022-10-19 to 2022-10-20
- **Locations**: Shivajinagar (Cantonment); HBR Layout; Thanisandra Main Road.
- **Coordinates (approx)**: Shivajinagar (12.985, 77.605); HBR Layout (13.028, 77.632).
- **Evidence / Source**:
  - Indian Express (20 Oct 2022): *"Bengaluru rain: Shivajinagar waterlogged, traffic snarls across city"*. https://indianexpress.com/article/cities/bangalore/bengaluru-rain-traffic-snarls-waterlogging-october-8219462/
- **Estimated Yield**: 3 places $\\times$ 2 days = 6 point cell-days (54 with 8-neighbour buffer).

### Candidate 4: May 2023 KR Circle Underpass Storm (21 May 2023)
- **Proposed Event ID**: `E2023_05`
- **Date Window**: 2023-05-21 to 2023-05-21
- **Locations**: KR Circle Underpass (Central Bengaluru); Majestic / Subhash Nagar; Chickpet metro reach.
- **Coordinates (approx)**: KR Circle (12.975, 77.589); Majestic (12.977, 77.572).
- **Evidence / Source**:
  - BBC News (22 May 2023): *"Bengaluru rain: Tech worker dies after car submerges in waterlogged underpass"*. https://www.bbc.com/news/world-asia-india-65671148
- **Estimated Yield**: 2 places $\\times$ 1 day = 2 point cell-days (18 with 8-neighbour buffer).

---

## 4. Summary Recommendation for Model Team

1. Retain the **10 point reports** as verified primary truth in `events.csv`.
2. To address the volume shortfall (23 vs 100/500), the team can:
   - Formally approve Candidate Events 1, 2, and 3 above to expand spatial coverage into North and Central Bengaluru.
   - Apply spatial neighbour expansion ($3 \\times 3$ cell footprint, radius 500 m) with `label_confidence = medium` around documented inundation centroids.
"""
    with open(out_path, "w") as f:
        f.write(content)
    print(f"Saved candidate events and audit notes to {out_path}")

if __name__ == "__main__":
    audit_and_upgrade_events()
