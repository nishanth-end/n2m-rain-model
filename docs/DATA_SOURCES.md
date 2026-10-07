# Data Sources Register

This document records the provenance, licensing, version, and access details for all geospatial, meteorological, and ground-truth data sources used by the data pipeline.

---

## 1. BBMP Ward Boundaries (City Boundary & Spatial Partitioning)

- **Source / Publisher**: DataMeet Bangalore Community Spatial Repository & OpenCity
- **Repository URL**: `https://github.com/datameet/bangalore`
- **Direct Download URL**: `https://raw.githubusercontent.com/datameet/bangalore/master/Wards/BBMP_Wards_2011_Nov.geojson`
- **Delimitation**: BBMP 2011 Delimitation (198 wards)
- **Geometry Type**: MultiPolygon / Polygon (WGS84, EPSG:4326)
- **Feature Count**: Exactly 198 wards
- **Total Area**: ~716 km²
- **Access Date**: 2026-10-07
- **Licence**: Open Database License (ODbL) 1.0 / CC BY-SA 2.5 India
- **Role in Pipeline**: Defines the boundary for clipping the 500 m UTM lattice and supplies the `ward` identifier for spatial 5-fold cross-validation.

---

## 2. Daily Precipitation (CHIRPS Daily v2.0)

- **Product**: Climate Hazards Group InfraRed Precipitation with Station data (CHIRPS) v2.0 Daily
- **Publisher**: Climate Hazards Center, University of California, Santa Barbara (UCSB) / USGS
- **Citation**: Funk, C., Peterson, P., Landsfeld, M., et al. (2015). The climate hazards infrared precipitation with stations—a new environmental record for monitoring extremes. *Scientific Data*, 2, 150066. https://doi.org/10.1038/sdata.2015.66
- **Spatial Resolution**: 0.05° $\times$ 0.05° (~5.3 km $\times$ 5.5 km over Bengaluru)
- **Temporal Alignment**: UTC calendar day (00:00:00 UTC to 23:59:59 UTC)
- **Licence**: Public Domain (Creative Commons Zero / U.S. Government Work)
- **Role in Pipeline**: Grid cells are mapped to native 0.05° CHIRPS pixels via `rain_pixel_id`. Rolling rainfall sums (1d, 3d, 7d, 14d, 30d) and daily lags are computed continuously per pixel.

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
