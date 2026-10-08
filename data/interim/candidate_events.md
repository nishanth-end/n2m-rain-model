# Candidate Flood Events Register and Audit

**File Purpose**: Records integrity audit of historical flood events, strict Point-in-Polygon (PIP) verification, source check log results, and candidate historical events for team review.
**Rule**: NEVER add candidate events to `data/events.csv` without explicit Member 1 and Member 2 review and verification.

---

## 1. Candidate Events Audit and Status

### Candidate 1: Kendriya Vihar / Yelahanka Lake Overflow (Nov 2021)
- **Cited Source**: The Hindu (22 Nov 2021), `https://www.thehindu.com/news/cities/bangalore/heavy-rain-floods-several-areas-in-bengaluru/article37628863.ece` (HTTP 404: **UNVERIFIED**)
- **Verified Primary Source**: The News Minute (22 Nov 2021), `https://www.thenewsminute.com/karnataka/bengaluru-sees-very-heavy-rains-severe-waterlogging-reported-157884` (HTTP 200: **VERIFIED**)
- **Flood Date**: 2021-11-21
- **Location**: Kendriya Vihar, Bellary Road / Kogilu, Yelahanka (OSM way 1180658023, node 11473102401; 13.106967, 77.600144; Cell 2904, Ward 1 Kempegowda Ward)
- **Audit Verdict**: **DUPLICATE / SAME-STORM CLUSTER** of existing event `E2021_11`. Located ~890 m from the stored centroid (Cell 2882). Stored coordinates retained pending Member 1 approval.

### Candidate 2: Rainbow Drive / ORR Inundation (Aug 2022)
- **Cited Source**: Deccan Herald (30 Aug 2022), `https://www.deccanherald.com/city/top-bengaluru-stories/floods-return-to-orr-rainbow-drive-layout-after-overnight-rain-1140643.html`
- **Audit Verdict**: **UNVERIFIED / WRONG SOURCE**. Article ID 1140643 resolves to a NASA Moon rocket launch article ("Explained | Why did NASA cancel the Moon rocket launch?"). This candidate currently has NO valid source.

### Candidate 3: Shivajinagar / Central Deluge (Oct 2022)
- **Cited Source**: Indian Express (20 Oct 2022), `https://indianexpress.com/article/cities/bangalore/bengaluru-rain-traffic-snarls-waterlogging-october-8219462/`
- **Audit Verdict**: **UNVERIFIED** (HTTP 404 Not Found).

### Candidate 4: KR Circle Underpass Flash Flood (May 2023)
- **Previous Source**: BBC News (22 May 2023), `https://www.bbc.com/news/world-asia-india-65671148` (HTTP 404: UNVERIFIED)
- **Verified Replacement Sources**:
  1. Scroll.in (22 May 2023), `https://scroll.in/latest/1049516/techie-dies-in-bengaluru-as-car-gets-submerged-in-flooded-underpass` (HTTP 200: **VERIFIED**)
  2. The South First (21 May 2023), `https://thesouthfirst.com/karnataka/woman-dies-after-car-with-andhra-pradesh-family-zooms-into-rain-flooded-bengaluru-underpass` (HTTP 200: **VERIFIED**)
- **Flood Date**: 2023-05-21
- **Location**: KR Circle Underpass (approx 12.975, 77.589; Cell 1478, Ward 110 Sampangiram Nagar)
- **Audit Verdict**: **VERIFIED REAL EVENT**. Flash flood in central underpass. Kept in candidate register; not added to `data/events.csv`.
