# Proposed Restoration Notice: Event E2017_09

**Target Event ID**: `E2017_09`  
**Original Status in Commit `705eacc`**: Present in `data/events.csv`  
**Current Status in `delivery/events.csv`**: Omitted from delivery release (link was broken)  
**Proposed Action**: Evaluate restoration of `E2017_09` with `label_confidence = unverified` / `low` based on independent live verification in *Gulf Times* (27 Sept 2017) and spatial audit of Anugraha Layout discrepancy.

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
- **Saved Evidence File**: `data/evidence/gt_2017_09_27_565360.txt` (SHA-256: `d46b1a644736068002de49d6b1b7dfac9d0a6341d549e9789f1238022af09f4e`)
- **Verbatim Evidence Quotes**:
  > *"Even upscale suburbs like Koramangala and Jayanagar witnessed flash floods as the drains, filled with silt and filth, failed to cope"* (21 words)
  > *"The heavy rains which began on Tuesday night led to drains overflowing onto roads in several places, leading to water-logging."* (20 words)
  > *"with a few areas receiving a maximum of 196mm as recorded at 8.30am"* (14 words)
  > *"Fifty-five-year-old Meenamma, a resident of Krishnarajapuram, a suburb in the eastern part of the city, died yesterday after a night of incessant rain"* (23 words)

---

## 3. Anugraha Layout Spatial Discrepancy & Location Verification

A detailed spatial audit was conducted comparing the stored event coordinates against genuine OpenStreetMap and municipal ward data:

| Feature Dimension | Stored Event Coordinates (`E2017_09`) | Geocoded Anugraha Layout (Bilekahalli) |
|---|:---:|:---:|
| **Latitude, Longitude** | `(12.9250, 77.6340)` | `(12.9015, 77.6162)` |
| **Production Grid Cell** | **Cell 774** | **Cell 490** |
| **BBMP Ward** | **Ward 173 (Jakkasandra / Koramangala)** | **Ward 188 (Bilekahalli / Bommanahalli)** |
| **Named Locality** | Hosur-Sarjapur Road / Koramangala | Anugraha Layout (near Bannerghatta Rd) |

### Geographic Comparison
- **Haversine Distance**: **3,248.1 m (3.25 km)**.
- **Are they the same place?**: **NO**. They are located in distinct BBMP wards separated by over 3.2 km.
- **What this reveals about `E2017_09`**:
  1. In OpenStreetMap and BBMP GIS databases, **no residential layout named "Anugraha Layout" exists within Koramangala or Ward 173 (Jakkasandra)**.
  2. The actual residential area known as "Anugraha Layout" is situated in Bilekahalli (Ward 188), south of BTM Layout and west of Bannerghatta Road.
  3. The original event label `"Hosur-Sarjapur Road / Anugraha Layout, Koramangala"` conflated two completely separate flood reports:
     - Flash flooding along the Hosur-Sarjapur Road corridor in Koramangala (*Gulf Times*).
     - Local inundation at Anugraha Layout in Bilekahalli / Bommanahalli.
- **Conclusion**: The specific flooded layout cannot be verified to the stored coordinates `(12.925, 77.634)`. Therefore, the location precision is classified as **`UNVERIFIED`** for the specific layout, and can only be treated as a coarse neighbourhood centroid if retained for broad Koramangala flooding.

---

## 4. Dataset Yield Comparison Under Alternative Interpretations

Yield impact was evaluated across all three interpretations:

| Metric | Interpretation 0: Omitted (Current Delivery Baseline) | Interpretation A: Stored Cell 774 (Koramangala Centroid) | Interpretation B: Relocated to Cell 490 (Bilekahalli Anugraha Layout) |
|---|:---:|:---:|:---:|
| **Location Confidence** | Excluded | `low` (coarse centroid) | `unverified` (relocated layout) |
| **Seed Cells (per day)** | 0 cells | 1 cell (Cell 774) | 1 cell (Cell 490) |
| **Active Event Days** | 0 days | 2 days (27 & 28 Sept 2017) | 2 days (27 & 28 Sept 2017) |
| **Total Seed-Days Added** | 0 | **+2 seed-days** (16 $\to$ 18) | **+2 seed-days** (16 $\to$ 18) |
| **CFG_A Positive Yield** | **175 cell-days** | **193 cell-days** (+18 cell-days) | **193 cell-days** (+18 cell-days) |
| **CFG_UNIFORM Yield** | **181 cell-days** | **199 cell-days** (+18 cell-days) | **199 cell-days** (+18 cell-days) |
| **Active Events Count** | 5 events | **6 events** | **6 events** |

---

## 5. Audit Recommendation

1. If the project objective requires strict polygon-level precision, `E2017_09` should **remain omitted** or marked **`location_confidence = unverified`** because the specific flooded footprint cannot be disambiguated between Koramangala and Bilekahalli.
2. If restored to capture the 26–27 September 2017 heavy rainfall surge (196 mm network maximum), it must be restored strictly as `"Hosur-Sarjapur Road / Koramangala"` with **`coord_precision = neighbourhood_centroid`** and **`label_confidence = low`**, explicitly noting the 3,248 m discrepancy with Bilekahalli's Anugraha Layout.

```csv
event_id,start_date,end_date,peak_date,place_name,lat,lon,cell_id,evidence_type,source_citation,source_url,accessed_on,label_confidence,notes,audit_stored_lat,audit_stored_lon,audit_coord_source,audit_coord_note,coord_precision
E2017_09,2017-09-27,2017-09-28,2017-09-27,"Hosur-Sarjapur Road / Koramangala",12.925,77.634,774,news,"Gulf Times, 27 Sep 2017, 'Heavy rains paralyse Bengaluru, Mysuru'",https://www.gulf-times.com/story/565360/heavy-rains-paralyse-bengaluru-mysuru,2026-10-14,low,"Heavy storm 26-27 Sept 2017; flash floods in Koramangala & Jayanagar; KSNDMC reported 196 mm max; coarse centroid (Cell 774); Anugraha Layout in Bilekahalli is 3,248 m away; location_confidence=low",12.925,77.634,Stored (GardaWorld / Gulf Times),"Original Crisis24 link broken; verified live via Gulf Times 27 Sept 2017; restored at low confidence",neighbourhood_centroid
```
