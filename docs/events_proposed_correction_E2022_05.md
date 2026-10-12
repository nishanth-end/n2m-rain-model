# Proposed Correction Notice: Event E2022_05 Date Alignment

**Target Event ID**: `E2022_05`  
**Current Date in `delivery/events.csv`**: `2022-05-05` (Start Date: 2022-05-05, End Date: 2022-05-05, Peak Date: 2022-05-05)  
**Proposed Corrected Dates**: 
- `start_date`: `2022-05-17`
- `end_date`: `2022-05-18`
- `peak_date`: `2022-05-17`

---

## 1. Justification and Evidence

1. **Current Mismatch**:
   - In `delivery/events.csv`, `E2022_05` is listed as occurring on `2022-05-05` at RBD Layout (Sarjapur Road).
   - In CHIRPS satellite observations at Pixel 12 (covering RBD Layout, Cell 555), precipitation on `2022-05-05` was only **7.37 mm** (`rain_1d_mm`), with zero flooding reported across the city.
   - The citation provided in `delivery/events.csv` is an *Indian Express* article dated 18 May 2022 titled *"Bengaluru: RBD layout to get new drain to flush out rainwater to Sarjapur culvert"* (`https://indianexpress.com/article/cities/bangalore/bengaluru-rbd-layout-new-drain-rainwater-sarjapur-culvert-7924521/`).
   - The article discusses civic action taken *following* the severe pre-monsoon storm of **17–18 May 2022**, where Bengaluru recorded heavy downpours inundating RBD Layout, Silk Board, and Hosur Road. The mention of "May 5" in earlier draft notes referred to an initial complaint letter date, not the catastrophic storm.

2. **Meteorological Reality (17–18 May 2022 Storm)**:
   - On **17 May 2022**, CHIRPS recorded **34.02 mm** at Pixel 12 (and up to **51.52 mm** city-wide peak at Pixel 23), producing a 3-day rolling accumulation of **66.86 mm** (`EP_12` in `high_rain_episodes.csv`).
   - News reports from 18 May 2022 confirm widespread inundation across Sarjapur Road and RBD Layout stranded residents and prompted the BBMP Chief Commissioner's site inspection.

3. **Current Delivery Dataset State**:
   - In `delivery/flood_dataset.parquet` and `delivery/flood_dataset_event_windows.csv`, the 7 positive labels for `E2022_05` currently sit on **`2022-05-05`** because the pipeline generated labels strictly from the dates recorded in `events.csv`.
   - On `2022-05-05`, the model sees `flood_label = 1` paired with `rain_1d_mm = 7.37 mm`, creating a false-association artifact.

---

## 2. Proposed Row Replacement for `events.csv`

*Note: Per strict project safety rules, `data/events.csv` and `delivery/events.csv` have NOT been edited. This proposed replacement is submitted for team review:*

```csv
event_id,start_date,end_date,peak_date,place_name,lat,lon,evidence_type,source_citation,source_url,accessed_on,label_confidence,notes,proposed_lat,proposed_lon,geocoding_method,audit_notes,polygon_type
E2022_05,2022-05-17,2022-05-18,2022-05-17,RBD Layout (Sarjapur Road),12.907289,77.686694,555,news,"The Indian Express, 18 May 2022, ""Bengaluru: RBD layout to get new drain to flush out rainwater to Sarjapur culvert""",https://indianexpress.com/article/cities/bangalore/bengaluru-rbd-layout-new-drain-rainwater-sarjapur-culvert-7924521/,2026-10-05,medium,"Severe pre-monsoon storm on 17-18 May 2022 flooded layout entrance; residents stranded >20h; site visit on 18 May; mapped to Cell 555",12.901,77.7,OSM way 101573097 inside centroid,"Corrected date from 5 May to 17-18 May based on storm records and IE article context; CFG_C footprint seeds: 554, 555, 608",landuse_footprint
```
