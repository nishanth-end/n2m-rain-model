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

- **Product**: Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS) v2.0 p05 daily
- **Publisher**: Climate Hazards Center, University of California, Santa Barbara (UCSB) / USGS
- **Download Base URL**: `https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05/`
- **Access Date**: 2026-10-08
- **Files Downloaded vs Expected**: 976 / 976 files downloaded (100% complete across 4 configured study years: 2017, 2021, 2022, 2023)
- **Downloaded Window**: 1 April to 30 November (244 days per year; 30-day pre-buffer in April + 214-day May-Nov wet season)
- **Missing Days**: 0 missing days (zero gaps; no gap-filling applied)
- **Local Path**: `data/raw/chirps/`
- **Manifest Checksum**: SHA-256 `073a36c1ad0d31f7b20ecc0da05e5f5a50a573cbc3583719ef86faad53fa69e7` (`data/raw/chirps/manifest.csv`, recorded in `data/raw/CHECKSUMS.txt`)
- **Nodata Sentinel**: None in metadata; -9999 treated as nodata, masked as NaN (never 0); 0 nodata pixel-days observed over the 37 rain pixels across all 36,112 pixel-days (37 pixels x 976 days)
- **Data Type**: `float32`
- **Nominal Resolution**: 0.05° (as read: `0.05000000074505806`)
- **Internal TIFF Document Folder**: `/home/chc-sandbox/chirps/v2.0/daily_downscaled_by_monthly/global_full_rescale_again/{year}` (2021, 2022, 2023) and `/home/sandbox/chirps/v2.0/daily_downscaled_by_monthly/global_full_rescale_again/2017` (2017) (path consistent with the final daily product; not verified against CHIRPS documentation)
- **Temporal Alignment**: UTC calendar day (00:00:00 UTC to 23:59:59 UTC = 05:30 IST day d to 05:30 IST day d+1)
- **Licence**: Public Domain (Creative Commons Zero / U.S. Government Work; https://data.chc.ucsb.edu/products/CHIRPS-2.0/)
- **Citation**: Funk, C., Peterson, P., Landsfeld, M., et al. (2015). The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes. *Scientific Data*, 2, 150066. https://doi.org/10.1038/sdata.2015.66
- **Role in Pipeline**: Grid cells are mapped to native 0.05° CHIRPS pixels via `rain_pixel_id`. Rolling rainfall sums (1d, 3d, 7d, 14d, 30d) and daily lags are computed continuously per pixel.

### CHIRPS Grid Statistics & Known Limitations
- **Pixel Distribution**: Bengaluru's 3,026 grid cells map to 37 unique 0.05° CHIRPS rain pixels:
  - Minimum cells per pixel: 2 (marginal sliver on outer border)
  - Median cells per pixel: 96
  - Mean cells per pixel: 81.8
  - Maximum cells per pixel: 121 (central interior pixel)
  - Straddling cells: 513 cells (17.0%) cross 0.05° pixel boundaries and are assigned to the pixel containing their centroid.
- **Value Stepping / Quantisation Artifact**: In calendar pentads (5-day blocks), 91.99% of nonzero daily values are exact integer multiples (1x: 54.98%, 2x: 19.37%, 3x: 11.65%, 4x: 4.41%) of the pentad's minimum nonzero value. In 3.97% of rainy pentads, all 37 pixels share an identical normalized daily timing vector. They are passed through untouched from the raw files and come directly from the upstream product (cause not verified). Daily timing inside a pentad may not reflect independent daily information, so `rain_1d_mm` and `rain_lag1..3_mm` are noisier than multi-day totals (`rain_7d_mm`..`rain_30d_mm`).
- **Spatial and Temporal Smoothing**: CHIRPS 0.05° daily smooths intense local rain and has no sub-daily timing; raw physical values are not modified. One CHIRPS pixel encompasses 80 to 120 grid cells, meaning rainfall features are spatially uniform within each 5.5 km pixel and cannot alone resolve micro-catchment spatial variance without terrain and drainage features.
- **Sub-Daily Extreme Smoothing**: CHIRPS Daily is an aggregated 24-hour product aligned to the UTC day. Flash floods often result from short-duration, high-intensity convective cloudbursts. CHIRPS captures total daily volume but smooths peak rainfall intensity.
- **Satellite-Gauge Interpolation**: CHIRPS blends satellite infrared cold-cloud duration with sparse surface rain gauges. In areas lacking dense telemetric rain gauges, local convective storm cores can be slightly smoothed or displaced.
- **Legacy UI Mock Dataset Note (`data/flood_dataset.csv`)**: Git log shows commit `49250cb40403f87f58b42cd95cb42e29cad1e97f` (Mon Oct 5 2026); no evidence of delivery found. It is a legacy UI mock (600 cells x 43 dates, 2020-06-26 to 2023-04-09, outside the study years), not the spec deliverable and not for training. The spec deliverable goes to `data/deliverables/` later.

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

### Neighbour Expansion Note
- **Rule**: Per project specification, positive labels are strictly SEED cells × event days. Topological 3x3 neighbours are retained solely as an audit flag and never conditioned on DEM, elevation, or model features.

---

## 4. Digital Elevation Model (Copernicus DEM GLO-30)

- **Product**: Copernicus DEM Global 30m (GLO-30), 2021 release
- **Provider**: European Space Agency (ESA) / Airbus Defence and Space
- **Access Route**: Public AWS Open Data Registry (`https://copernicus-dem-30m.s3.amazonaws.com/` / `s3://copernicus-dem-30m/`), free HTTP Cloud-Optimized GeoTIFF (COG) access without authentication.
  - Relevant 1°x1° tiles covering Bengaluru:
    - `Copernicus_DSM_COG_10_N12_00_E077_00_DEM` (Southern Bengaluru, 12°N–13°N, 77°E–78°E; SHA-256: `a58736cc901e3baca38721d0dd4b1048bf2a67328592e93420c7413d5012ae02`)
    - `Copernicus_DSM_COG_10_N13_00_E077_00_DEM` (Northern Bengaluru, 13°N–14°N, 77°E–78°E; SHA-256: `3bacdbc63c1a0b95f570893578ed4a6b93c9e5ed2d6783f9caf6fc5bdd43c1f1`)
- **Access Date**: 2026-10-08
- **Licence**: Worldwide free, full and open access under the Copernicus Sentinel Data Policy / Copernicus DEM Policy (attribution: "Copernicus DEM 2021, © Airbus DS / European Space Agency").
- **Vertical Datum & Native CRS**:
  - Horizontal CRS: WGS84 (EPSG:4326).
  - Vertical Datum: Earth Gravitational Model 2008 (EGM2008) geoid heights (orthometric height in metres above mean sea level).
- **Reprojection & Resampling Specification**:
  - Target CRS: EPSG:32643 (UTM Zone 43N) at 30.0 m × 30.0 m pixel resolution.
  - Resampling Algorithm: **Bilinear interpolation** (`Resampling.bilinear` in rasterio/GDAL), preserving continuous topographic slopes without the stair-step artifacts of nearest-neighbor.
  - Domain: Full 2° mosaic (N12 + N13) covering 12°N–14°N, 77°E–78°E, reprojected to EPSG:32643. Flow routing will execute across the full regional catchment mosaic to eliminate artificial boundary truncation at the municipal border.
- **Nature of Product**: Digital Surface Model (DSM). Captures reflective top surfaces (canopy, rooflines, road overpasses) rather than bare-earth terrain (DTM).

---

## 5. Land Cover & Built-Up Fraction (ESA WorldCover 10 m 2021 v200)

- **Product**: ESA WorldCover 10 m 2021 v200
- **Provider**: European Space Agency (ESA) / VITO Remote Sensing consortium
- **Final Download URL**: `https://esa-worldcover.s3.eu-central-1.amazonaws.com/v200/2021/map/ESA_WorldCover_10m_2021_v200_N12E075_Map.tif`
- **Local Path**: `data/raw/worldcover/ESA_WorldCover_10m_2021_v200_N12E075_Map.tif`
- **Access Date**: 2026-10-08
- **File Size**: 127,650,362 bytes (121.74 MB)
- **SHA-256**: `f9269901e07d86c2e180d661d0e8924e3ee57dd589f7433b9874861b3c65a978`
- **Licence**: Creative Commons Attribution 4.0 International (CC BY 4.0) (https://creativecommons.org/licenses/by/4.0/).
- **Attribution String**: "ESA WorldCover project 2021 / contains modified Copernicus Sentinel data (2021) processed by ESA WorldCover consortium."
- **Class of Interest**: Built-up / impervious surfaces (Class value `50`), mapped at 10 m resolution to compute each 500 m grid cell's impervious fraction (`impervious_fraction`).

---

## 6. OpenStreetMap Hydrography & Road Network

- **Source / Publisher**: OpenStreetMap contributors
- **Query Endpoint**: Overpass API (`https://overpass-api.de/api/interpreter`)
- **Query Bounds**: 5 km padded bounding box in WGS84 (`[12.786°N, 77.412°E, 13.191°N, 77.833°E]`)
- **Local Path**: `data/raw/osm/bengaluru_padded_waterways_roads.json`
- **Access Date**: 2026-10-08
- **OSM Database Timestamp (`timestamp_osm_base`)**: `2026-10-08T14:01:24Z`
- **File Size**: 20,703,136 bytes (19.74 MB)
- **SHA-256**: `e46fcedc7e96bf0a3457a0be05f16c86748b1431d183dd174d27497449c2dfaf`
- **Licence**: Open Database License 1.0 (ODbL 1.0) (http://opendatacommons.org/licenses/odbl/1-0/).
- **Attribution String**: "Data © OpenStreetMap contributors, ODbL 1.0. http://osm.org/copyright"
- **Features Extracted**:
  - Waterways (`waterway=*`): Rajakaluves, canals, streams, ditches for hybrid DEM stream burning (-2.0 m).
  - Water bodies (`natural=water` ways and multipolygon relations): Lakes/tanks, dissolved across touching boundaries for lake distance and count features.
  - Major road network: Motorway, trunk, primary, secondary roads and their link ramps for `dist_road_m`.
