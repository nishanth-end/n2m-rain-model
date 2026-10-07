# Data Sources Register

This document records the provenance, licensing, version, and access details for all geospatial, meteorological, and ground-truth data sources used by the data pipeline.

---

## 1. BBMP Ward Boundaries (City Boundary & Spatial Partitioning)

- **Source / Publisher**: DataMeet Municipal Spatial Data Repository
- **Repository URL**: `https://github.com/datameet/Municipal_Spatial_Data`
- **Final Download URL**: `https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Bangalore/BBMP_oldWards.geojson`
- **Local Path**: `data/raw/bbmp_wards_198.geojson`
- **Delimitation**: BBMP 2011 Delimitation (198 wards)
- **Geometry Type**: MultiPolygon / Polygon (WGS84, EPSG:4326)
- **Feature Count**: Exactly 198 wards
- **Total Area**: 711.59 km²
- **Fields Used**: `WARD_NO` (converted from float 1.0–198.0 to integer 1–198), `WARD_NAME`
- **Access Date**: 2026-10-07
- **Licence**: Creative Commons Attribution-ShareAlike 2.5 India (http://creativecommons.org/licenses/by-sa/2.5/in/) as stated in `Bangalore/Readme.md` of the DataMeet repository.
- **Attribution String**: "DataMeet Municipal Spatial Data contributors (CC BY-SA 2.5 IN), retrieved from https://raw.githubusercontent.com/datameet/Municipal_Spatial_Data/master/Bangalore/BBMP_oldWards.geojson"
- **Raw Checksum**: Recorded in `data/raw/CHECKSUMS.txt` (SHA-256: `06263e1a1e72fc58844a635c0b95e490962321e8489b476f2379771ce5128633`, size: 1,881,095 bytes).
- **History of 404 URL**: The originally proposed URL (`https://raw.githubusercontent.com/datameet/bangalore/master/Wards/BBMP_Wards_2011_Nov.geojson`) returned HTTP 404 due to repository restructuring in the DataMeet project. With explicit user approval, `BBMP_oldWards.geojson` from `datameet/Municipal_Spatial_Data` was audited, verified, and adopted.
- **Role in Pipeline**: Defines the boundary for clipping the 500 m UTM lattice and supplies the `ward` identifier for spatial 5-fold cross-validation.

### Area and Topology Verification
1. **Zero Ward Overlap**: Pairwise spatial intersection area across all 198 ward polygons is exactly 0.000000 km² (no sliver overlaps; clean topological partition).
2. **Boundary Conservation**: Total dissolved boundary polygon area in EPSG:32643 is 711.594263 km² (711.59 km²). The sum of all 3,026 clipped 500 m cell polygons is 711.594264 km², demonstrating exact conservation of municipal area (< 1 m² residual rounding).
3. **Census 2011 Comparison**: The District Census Handbook (Census of India 2011, Bangalore) records the BBMP municipal area as 709.49 km². The DataMeet vector boundary of 711.59 km² shows a negligible difference of +2.10 km² (+0.30%), resulting from detailed digitisation of peri-urban lake, valley, and road boundaries in outer zones.

---

## 2. Daily Precipitation (CHIRPS Daily v2.0)

- **Product**: Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS) v2.0 Daily
- **Publisher**: Climate Hazards Center, University of California, Santa Barbara (UCSB) / USGS
- **Citation**: Funk, C., Peterson, P., Landsfeld, M., et al. (2015). The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes. *Scientific Data*, 2, 150066. https://doi.org/10.1038/sdata.2015.66
- **Spatial Resolution**: 0.05° x 0.05° (~5.3 km x 5.5 km over Bengaluru)
- **Temporal Alignment**: UTC calendar day (00:00:00 UTC to 23:59:59 UTC)
- **Licence**: Public Domain (Creative Commons Zero / U.S. Government Work)
- **Role in Pipeline**: Grid cells are mapped to native 0.05° CHIRPS pixels via `rain_pixel_id`. Rolling rainfall sums (1d, 3d, 7d, 14d, 30d) and daily lags are computed continuously per pixel.

### CHIRPS Grid Statistics & Known Limitations
- **Pixel Distribution**: Bengaluru's 3,026 grid cells map to 37 unique 0.05° CHIRPS rain pixels:
  - Minimum cells per pixel: 2 (marginal sliver on outer border)
  - Median cells per pixel: 96
  - Mean cells per pixel: 81.8
  - Maximum cells per pixel: 121 (central interior pixel)
  - Straddling cells: 513 cells (17.0%) cross 0.05° pixel boundaries and are assigned to the pixel containing their centroid.
- **Spatial Coarseness**: One CHIRPS pixel encompasses 80 to 120 of our 500 m grid cells. Consequently, rainfall features are spatially smooth across neighborhoods and cannot alone resolve micro-catchment spatial variance without terrain and drainage features.
- **Sub-Daily Extreme Smoothing**: CHIRPS Daily is an aggregated 24-hour product aligned to the UTC day. Most Bengaluru flash flood events result from short-duration, high-intensity convective cloudbursts (e.g. 50–90 mm in 1–2 hours during evening storms). CHIRPS captures total daily volume but smooths peak rainfall intensity.
- **Satellite-Gauge Interpolation**: CHIRPS blends satellite infrared cold-cloud duration with sparse surface rain gauges. In areas lacking dense telemetric rain gauges, local convective storm cores can be slightly smoothed or displaced.

---

## 3. Documented Flood Events & Hotspots

- **Primary Technical Study**:
  - Sajjan, S. (2022). *Floods at Bengaluru City – A Technical Study*. Technical Report, Bengaluru, December 2022.
  - Covers 6 critical catchment flood zones (RBD Layout, Wipro Sarjapur, RMZ Ecospace/Saul Kere, Epsilon Layout/Kadubeesanahalli, Borewell Road Whitefield, Panathur-Balagere).
- **Secondary News & Incident Records**:
  - The News Minute (15 Aug 2017): Koramangala 4th Block flooding.
  - GardaWorld Crisis24 (27 Sep 2017): Hosur-Sarjapur Road / Anugraha Layout flooding.
  - The News Minute (21 Nov 2021): Yelahanka / Jakkur 153 mm deluge.
  - Indian Express (11 May 2022): RBD Layout pre-monsoon shower waterlogging.
- **Role in Pipeline**: Ground truth observations catalogued in `data/events.csv`.

### TODO: Hydrological Conditioning for Spatial Label Propagation
- **Context**: In Stage 1b, Assumption (b) expands the positive flood label from the matched 500 m cell to its 8 immediate topological neighbours (3x3 footprint of ~1.5 km x 1.5 km).
- **Requirement for Stage 2**: Direct topological 3x3 expansion assumes isotropic flood spread across all adjacent terrain. In Stage 2 (static feature integration), this expansion must be conditioned on Digital Elevation Model (DEM) hydrological connectivity:
  1. Cells with elevated ridge or upstream topography relative to the event point should be excluded.
  2. Only contiguous valley/depression cells with high Topographic Wetness Index (TWI) or flow accumulation within the catchment should inherit positive labels.
