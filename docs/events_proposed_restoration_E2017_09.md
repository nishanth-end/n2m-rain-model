# Proposed Restoration Notice: Event E2017_09

**Target Event ID**: `E2017_09`  
**Original Status in Commit `705eacc`**: Present in `data/events.csv`  
**Current Status in `delivery/events.csv`**: Omitted from delivery release (link was broken)  
**Proposed Action**: Restore `E2017_09` to event register with `label_confidence = low` based on independent live verification in *Gulf Times* (27 Sept 2017).

---

## 1. Original Sourcing and Link Status Audit

In commit `705eacc` (`Mon Oct 5 17:44:42 2026`), `data/events.csv` originally included `E2017_09`:

```csv
E2017_09,2017-09-27,2017-09-28,2017-09-27,"Hosur-Sarjapur Road / Anugraha Layout, Koramangala",12.925,77.634,news,"Garda World Crisis24, 27 Sep 2017",https://crisis24.garda.com/fr/product/222601,2026-10-05,medium,"295mm month-to-date vs 148mm normal for September; one death reported; approximate locality centroid"
```

### Original Citation Link Status
- **Original Citation**: GardaWorld Crisis24, 27 Sep 2017
- **Original URL**: `https://crisis24.garda.com/fr/product/222601` (also tested variant `https://crisis24.garda.com/fr/product/223626`)
- **HTTP Status**: **HTTP 302 Redirect / Broken** (redirects to generic corporate authentication/product portal `https://crisis24.garda.com/`)
- **Audit Outcome**: Because the primary citation link was inaccessible, `E2017_09` was conservatively omitted during generation of `delivery/flood_dataset.parquet`.

---

## 2. Independent Verification (*Gulf Times*, 27 Sept 2017)

Contemporaneous news coverage has been retrieved and verified:

- **Source**: *Gulf Times*
- **URL**: `https://www.gulf-times.com/story/565360/heavy-rains-paralyse-bengaluru-mysuru`
- **Headline**: *"Heavy rains paralyse Bengaluru, Mysuru"*
- **Publish Date**: **2017-09-27** (23:03 AST)
- **Saved Evidence File**: `data/evidence/gt_2017_09_27_565360.txt` (SHA-256: `955833aa3b1a1ddf4fa6e191316f7358b1ee3fdf9b76e27e8080f339f40fe3fc`)
- **Verbatim Evidence Quotes**:
  > *"Even upscale suburbs like Koramangala and Jayanagar witnessed flash floods as the drains, filled with silt and filth, failed to cope with the huge amounts of water. Rainwater also entered homes in many areas."* (27 words total; verbatim sentence: *"Even upscale suburbs like Koramangala and Jayanagar witnessed flash floods as the drains, filled with silt and filth, failed to cope"*, 21 words)
  > *"The heavy rains which began on Tuesday night led to drains overflowing onto roads in several places, leading to water-logging."* (20 words)
  > *"“The city received heavy rainfall, with a few areas receiving a maximum of 196mm as recorded at 8.30am,” an official from the Karnataka State Natural Disaster Monitoring Centre (KSNDMC) said."* (26 words; station context: *"with a few areas receiving a maximum of 196mm as recorded at 8.30am"*, 14 words)
  > *"Fifty-five-year-old Meenamma, a resident of Krishnarajapuram, a suburb in the eastern part of the city, died yesterday after a night of incessant rain, police said. “Her house was inundated after the rainfall.”"*

---

## 3. Label Confidence and Spatial Precision

- **Storm Timing**: Began Tuesday night (26 Sept 2017) and continued into Wednesday (27 Sept 2017). Measurement window ending 08:30 IST on 27 Sept 2017 captured up to 196 mm city-wide maximum.
- **Location**: Flooding occurred across Koramangala, Jayanagar, and Krishnarajapuram. The stored coordinate `(12.925, 77.634)` (Cell 774, Ward 173) is a coarse locality centroid for Hosur-Sarjapur Road / Anugraha Layout.
- **Proposed Confidence**: **`label_confidence = low`** (broad neighbourhood centroid; specific street-level flood extents not delineated by building polygons).

---

## 4. Dataset Yield Comparison (With vs. Without `E2017_09`)

| Metric | Without `E2017_09` (Current `delivery/flood_dataset.parquet`) | With `E2017_09` Restored (Proposed) | Net Difference |
|---|:---:|:---:|:---:|
| **Positive Seed Cells** | 16 seed-days | **18 seed-days** (+2 days at Cell 774) | +2 seed-days |
| **Parquet Positive Rows (CFG_A / Actual)** | **175 cell-days** | **193 cell-days** (175 + 18) | +18 cell-days |
| **Uniform Config (CFG_UNIFORM_FOOTPRINT)** | **181 cell-days** | **199 cell-days** (181 + 18) | +18 cell-days |
| **Active Events Count** | 5 events (`E2017_08`, `E2021_11`, `E2022_05`, `E2022_09`, `E2023_05`) | **6 events** (adds `E2017_09`) | +1 event |

---

## 5. Proposed Row for Future Event Registry Update

*Per strict project safety rules, `delivery/events.csv` and `data/events.csv` have NOT been modified. This row is proposed for the next release cycle:*

```csv
event_id,start_date,end_date,peak_date,place_name,lat,lon,cell_id,evidence_type,source_citation,source_url,accessed_on,label_confidence,notes,audit_stored_lat,audit_stored_lon,audit_coord_source,audit_coord_note,coord_precision
E2017_09,2017-09-27,2017-09-28,2017-09-27,"Hosur-Sarjapur Road / Koramangala",12.925,77.634,774,news,"Gulf Times, 27 Sep 2017, 'Heavy rains paralyse Bengaluru, Mysuru'",https://www.gulf-times.com/story/565360/heavy-rains-paralyse-bengaluru-mysuru,2026-10-14,low,"Heavy storm 26-27 Sept 2017; flash floods in Koramangala & Jayanagar; KSNDMC reported 196 mm max; coarse centroid (Cell 774); restored with label_confidence=low",12.925,77.634,Stored (GardaWorld / Gulf Times),"Original Crisis24 link broken; verified live via Gulf Times 27 Sept 2017; restored at low confidence",neighbourhood_centroid
```
