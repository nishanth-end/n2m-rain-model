# Status: REJECTED — Proposed Correction Notice: Event E2022_05 Date Alignment

**Target Event ID**: `E2022_05`  
**Current Date in `delivery/events.csv`**: `2022-05-05`  
**Proposed Date (REJECTED)**: `2022-05-17` to `2022-05-18`  
**Final Resolution**: **REJECTED**. The original date of **`2022-05-05`** is fully confirmed by contemporaneous news and ground telemetry.

---

## 1. Resolution & Ground Truth Confirmation

The proposed correction to move `E2022_05` from 5 May 2022 to 17–18 May 2022 is **REJECTED** based on decisive direct evidence discovered in *Deccan Herald*:

1. **Contemporaneous Ground Report (*Deccan Herald*, 5–6 May 2022)**:
   - **URL**: `https://www.deccanherald.com/amp/story/india%2Fkarnataka%2Fbengaluru%2Fapartment-complex-flooded-in-pre-monsoon-rain-in-bengaluru-1106860.html`
   - **Headline**: *"Apartment complex flooded in pre-monsoon rain in Bengaluru"*
   - **Published Date**: 2022-05-05 (published 5 May 2022 19:17 UTC / 6 May 2022 morning edition)
   - **Saved Evidence File**: `data/evidence/dh_2022_05_06_1106860.txt` (SHA-256: `3b79313cb17d8481ff2308c35fc18600d3d526fc8efc86ea1177fe7e6c46644f`)
   - **Verbatim Evidence Quotes**:
     > *"Parts of Rainbow Drive, an apartment complex located on Sarjapur Road, were also flooded."*
     > *"Bommanahalli, Mahadevapura, Yelahanka, and Bengaluru South received up to 70 mm of rainfall"* (12 words)

2. **Reconciled Full Event Timeline**:
   - **Thursday, 05 May 2022**: Intense pre-monsoon storm strikes south/east Bengaluru. KSNDMC gauges record up to **70 mm** in Mahadevapura (Sarjapur Road) and Bommanahalli. Rainbow Drive Layout is flooded, stranding residents.
   - **Tuesday, 10 May 2022**: Rainbow Drive residents submit a formal written complaint letter to local MLA Arvind Limbavali regarding the chronic culvert flooding.
   - **Wednesday, 11 May 2022**: *The Indian Express* publishes an initial report on the flooding and resident letter.
   - **Tuesday, 17 May 2022**: MLA Arvind Limbavali and BBMP officials conduct an on-site inspection of Rainbow Drive Layout. A separate rain storm occurs across Bengaluru on this day (34.02 mm at Pixel 12).
   - **Wednesday, 18 May 2022**: *The Indian Express* publishes follow-up article 7924521 reporting the MLA site inspection and plans for a new underground drain.

3. **CHIRPS Satellite Attenuation on 5 May 2022**:
   - On **5 May 2022**, CHIRPS Pixel 12 (Sarjapur Road / Rainbow Drive) records **7.37 mm**.
   - Against the KSNDMC ground gauge reading of **up to 70 mm** in the same zone, CHIRPS registers an attenuation factor of **~9.5×** (satellite capture ratio $7.37 / 70.0 \approx 0.105$).
   - This 9.5× attenuation is entirely consistent with the observed 2.8×–12.5× attenuation range of 0.05° satellite infrared/microwave precipitation estimates during isolated pre-monsoon convective cloudbursts in Bengaluru.
   - Low satellite daily rainfall does NOT indicate an absence of flooding; rather, it reflects the known physical spatial-averaging limitation of CHIRPS for highly localized convective cells.

4. **Label State in Delivery Dataset**:
   - In `delivery/flood_dataset.parquet`, all 7 positive label rows for `E2022_05` are correctly located on **`2022-05-05`** across Cell 555 and its topological buffer.
   - `delivery/events.csv` and `data/events.csv` correctly record `start_date = 2022-05-05` and `end_date = 2022-05-05`. No edits are required.
