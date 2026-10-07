"""pipeline/01_grid.py
Generates the 500 m full-city spatial grid for Bengaluru (BBMP boundary, 2011 delimitation).
Maps each cell to its administrative ward and native CHIRPS rain pixel (0.05 deg).

Usage:
    python pipeline/01_grid.py
"""

import os
import math
import yaml
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import box, Point
import json

def load_config(config_path="config/grid_config.yaml"):
    with open(config_path, "r") as f:
        return yaml.safe_load(f)

def build_grid():
    config = load_config()
    crs_utm = config["crs"]                # EPSG:32643
    spacing = float(config["spacing_m"])   # 500.0
    boundary_path = config["boundary_file"]
    pixel_size = float(config.get("rain_pixel_size_deg", 0.05))

    print(f"--- Loading BBMP Ward Boundaries: {boundary_path} ---")
    wards = gpd.read_file(boundary_path)
    print(f"Loaded {len(wards)} ward features. CRS: {wards.crs}")
    
    # Verification checks on raw boundary
    if len(wards) != config.get("boundary_expected_features", 198):
        raise ValueError(f"Expected {config.get('boundary_expected_features', 198)} wards, got {len(wards)}")
    if not wards.geometry.is_valid.all():
        print("Repairing invalid geometries in boundary...")
        wards["geometry"] = wards.geometry.make_valid()

    # Convert WARD_NO to clean integer
    wards["WARD_NO"] = wards["WARD_NO"].astype(float).astype(int)
    if wards["WARD_NO"].nunique() != 198:
        raise ValueError(f"Ward numbers are not unique: {wards['WARD_NO'].nunique()} unique values found")
    print("Ward numbers verified: 198 unique integer wards (1 to 198).")

    # Project to working UTM CRS
    wards_utm = wards.to_crs(crs_utm)
    city_boundary = wards_utm.union_all()
    total_boundary_area_km2 = city_boundary.area / 1e6
    print(f"Total BBMP boundary area: {total_boundary_area_km2:.2f} sq km")

    # Bounding box snapped to 500 m multiples
    minx, miny, maxx, maxy = city_boundary.bounds
    x_start = math.floor(minx / spacing) * spacing
    y_start = math.floor(miny / spacing) * spacing
    x_end = math.ceil(maxx / spacing) * spacing
    y_end = math.ceil(maxy / spacing) * spacing

    xs = np.arange(x_start, x_end, spacing)
    ys = np.arange(y_start, y_end, spacing)
    print(f"Snapped bounding lattice: {len(xs)} x {len(ys)} = {len(xs)*len(ys)} cells")

    # Generate cells and clip to city boundary
    cells = []
    for y in ys:
        for x in xs:
            cell_box = box(x, y, x + spacing, y + spacing)
            if cell_box.intersects(city_boundary):
                clipped = cell_box.intersection(city_boundary)
                # Keep valid intersecting parts; filter negligible numerical slivers (< 1 m^2)
                if not clipped.is_empty and clipped.area > 1.0:
                    c = clipped.centroid
                    cells.append({
                        "lattice_x": int(x),
                        "lattice_y": int(y),
                        "lattice_center_x": round(x + spacing / 2.0, 2),
                        "lattice_center_y": round(y + spacing / 2.0, 2),
                        "x_utm": round(c.x, 2),
                        "y_utm": round(c.y, 2),
                        "area_km2": round(clipped.area / 1e6, 6),
                        "geometry": clipped,
                        "centroid_geom": c
                    })

    gdf_cells = gpd.GeoDataFrame(cells, crs=crs_utm)
    print(f"Extracted {len(gdf_cells)} intersecting cells covering {gdf_cells.geometry.area.sum()/1e6:.2f} sq km.")

    # Sort deterministically: by lattice_y ascending, then lattice_x ascending
    gdf_cells = gdf_cells.sort_values(by=["lattice_y", "lattice_x"]).reset_index(drop=True)
    gdf_cells["cell_id"] = range(len(gdf_cells))

    # Transform centroids to WGS84 for lat, lon
    gdf_centroids_utm = gpd.GeoDataFrame(gdf_cells, geometry="centroid_geom", crs=crs_utm)
    gdf_centroids_wgs = gdf_centroids_utm.to_crs(config["output_crs"])
    gdf_cells["lat"] = np.round(gdf_centroids_wgs.geometry.y, 6)
    gdf_cells["lon"] = np.round(gdf_centroids_wgs.geometry.x, 6)

    # Spatial join centroid to Ward (using sjoin_nearest to robustly handle edge centroids)
    print("Joining cells to administrative wards...")
    wards_subset = wards_utm[["WARD_NO", "WARD_NAME", "geometry"]].copy()
    joined = gpd.sjoin_nearest(gdf_centroids_utm, wards_subset, how="left")
    # In case of equidistant boundary ties, keep first
    joined = joined.drop_duplicates(subset=["cell_id"]).reset_index(drop=True)

    gdf_cells["ward"] = joined["WARD_NO"].astype(int)
    gdf_cells["ward_name"] = joined["WARD_NAME"].astype(str)

    # Native CHIRPS rain pixels (0.05 degree grid)
    print(f"Mapping cells to native CHIRPS {pixel_size} degree rain pixels...")
    lats = gdf_cells["lat"].values
    lons = gdf_cells["lon"].values

    min_lats = np.round(np.floor(lats / pixel_size) * pixel_size, 4)
    min_lons = np.round(np.floor(lons / pixel_size) * pixel_size, 4)

    df_pixel_coords = pd.DataFrame({"min_lat": min_lats, "min_lon": min_lons})
    unique_pixels = df_pixel_coords.drop_duplicates().copy()
    # Row-major sort: by min_lat ascending, then min_lon ascending
    unique_pixels = unique_pixels.sort_values(by=["min_lat", "min_lon"]).reset_index(drop=True)
    unique_pixels["rain_pixel_id"] = range(len(unique_pixels))
    unique_pixels["max_lat"] = np.round(unique_pixels["min_lat"] + pixel_size, 4)
    unique_pixels["max_lon"] = np.round(unique_pixels["min_lon"] + pixel_size, 4)
    unique_pixels["center_lat"] = np.round(unique_pixels["min_lat"] + pixel_size / 2.0, 4)
    unique_pixels["center_lon"] = np.round(unique_pixels["min_lon"] + pixel_size / 2.0, 4)

    # Merge rain_pixel_id back to cells
    cell_pixel_merge = df_pixel_coords.merge(
        unique_pixels[["min_lat", "min_lon", "rain_pixel_id"]],
        on=["min_lat", "min_lon"],
        how="left"
    )
    gdf_cells["rain_pixel_id"] = cell_pixel_merge["rain_pixel_id"].astype(int)

    # Compute cell counts per rain pixel
    pixel_counts = gdf_cells.groupby("rain_pixel_id").size().rename("n_cells")
    unique_pixels = unique_pixels.merge(pixel_counts, on="rain_pixel_id", how="left")

    # Check how many cells straddle multiple 0.05 deg pixels
    gdf_wgs = gdf_cells.to_crs(config["output_crs"])
    straddle_count = 0
    for geom in gdf_wgs.geometry:
        b = geom.bounds
        lon_pixels = {math.floor(round(b[0], 6) / pixel_size), math.floor(round(b[2], 6) / pixel_size)}
        lat_pixels = {math.floor(round(b[1], 6) / pixel_size), math.floor(round(b[3], 6) / pixel_size)}
        if len(lon_pixels) > 1 or len(lat_pixels) > 1:
            straddle_count += 1
    print(f"Unique rain pixels containing cells: {len(unique_pixels)}")
    print(f"Cells straddling multiple rain pixels: {straddle_count} / {len(gdf_cells)} ({straddle_count/len(gdf_cells)*100:.1f}%)")

    # Output paths
    os.makedirs(os.path.dirname(config["output_cells_csv"]), exist_ok=True)
    os.makedirs(os.path.dirname(config["output_preview_html"]), exist_ok=True)

    # 1. Write rain_pixels.csv
    rain_pixels_cols = ["rain_pixel_id", "center_lat", "center_lon", "min_lat", "max_lat", "min_lon", "max_lon", "n_cells"]
    unique_pixels[rain_pixels_cols].to_csv(config["output_rain_pixels_csv"], index=False)
    print(f"Saved rain pixels to {config['output_rain_pixels_csv']}")

    # 2. Write cells_grid.csv
    cells_csv_cols = [
        "cell_id", "lat", "lon", "x_utm", "y_utm",
        "lattice_center_x", "lattice_center_y",
        "ward", "ward_name", "rain_pixel_id", "area_km2"
    ]
    gdf_cells[cells_csv_cols].to_csv(config["output_cells_csv"], index=False)
    print(f"Saved {len(gdf_cells)} grid cells to {config['output_cells_csv']}")

    # 3. Write cells_grid.geojson in WGS84
    geojson_gdf = gdf_wgs[["cell_id", "lat", "lon", "ward", "ward_name", "rain_pixel_id", "area_km2", "geometry"]].copy()
    geojson_gdf.to_file(config["output_cells_geojson"], driver="GeoJSON")
    print(f"Saved cells polygon GeoJSON to {config['output_cells_geojson']}")

    # 4. Generate grid preview HTML
    generate_preview_html(
        gdf_cells_wgs=geojson_gdf,
        wards_gdf=wards,
        rain_pixels_df=unique_pixels,
        events_csv_path=config["events_csv"],
        out_html_path=config["output_preview_html"],
        straddle_count=straddle_count,
        total_boundary_area_km2=total_boundary_area_km2
    )

    print("\n--- Summary of Generated Grid ---")
    print(f"Total cells: {len(gdf_cells):,}")
    print(f"Full (unclipped) cells: {(gdf_cells['area_km2'] >= 0.2499).sum():,}")
    print(f"Clipped edge cells: {(gdf_cells['area_km2'] < 0.2499).sum():,}")
    print(f"Unique wards represented: {gdf_cells['ward'].nunique()} / 198")
    print(f"Unique CHIRPS rain pixels: {len(unique_pixels)}")
    print(f"Total cell area sum: {gdf_cells['area_km2'].sum():.2f} km²")
    print("\nSample 5 rows:")
    print(gdf_cells[cells_csv_cols].head(5).to_string(index=False))

    return gdf_cells, unique_pixels

def generate_preview_html(gdf_cells_wgs, wards_gdf, rain_pixels_df, events_csv_path, out_html_path, straddle_count, total_boundary_area_km2):
    """Generates a standalone Leaflet visualizer showing cells, wards, rain pixels, and event points."""
    print(f"Generating preview HTML at {out_html_path}...")

    # Load events (prefer events_with_cells.csv if available)
    events_data = []
    events_source_file = "data/interim/events_with_cells.csv" if os.path.exists("data/interim/events_with_cells.csv") else events_csv_path
    if os.path.exists(events_source_file):
        ev_df = pd.read_csv(events_source_file)
        for _, row in ev_df.iterrows():
            events_data.append({
                "event_id": str(row.get("event_id", "")),
                "place_name": str(row.get("place_name", "")),
                "lat": float(row.get("lat", 0)),
                "lon": float(row.get("lon", 0)),
                "date": str(row.get("start_date", "")),
                "confidence": str(row.get("label_confidence", "")),
                "outside_grid": bool(row.get("outside_grid", False)),
                "cell_id": str(row.get("cell_id", "None")),
                "nearest_cell_id": str(row.get("nearest_cell_id", ""))
            })

    # Prepare simplified GeoJSON for preview
    # To keep the HTML file reasonably light while preserving visual quality, simplify geometry slightly
    wards_simplified = wards_gdf[["WARD_NO", "WARD_NAME", "geometry"]].copy()
    wards_simplified["geometry"] = wards_simplified.geometry.simplify(0.0005)
    wards_json_str = wards_simplified.to_json()

    # Rain pixels as GeoJSON boxes
    rain_pixel_features = []
    for _, r in rain_pixels_df.iterrows():
        poly = box(r["min_lon"], r["min_lat"], r["max_lon"], r["max_lat"])
        rain_pixel_features.append({
            "type": "Feature",
            "geometry": poly.__geo_interface__,
            "properties": {
                "rain_pixel_id": int(r["rain_pixel_id"]),
                "center_lat": float(r["center_lat"]),
                "center_lon": float(r["center_lon"]),
                "n_cells": int(r["n_cells"])
            }
        })
    rain_pixels_geojson = {"type": "FeatureCollection", "features": rain_pixel_features}

    # Cells GeoJSON (sample every 1st or write as clean compact GeoJSON)
    cells_simplified = gdf_cells_wgs[["cell_id", "ward", "ward_name", "rain_pixel_id", "area_km2", "geometry"]].copy()
    cells_json_str = cells_simplified.to_json()

    html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Bengaluru 500m Grid Preview — N²M Flood Model</title>
<link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css" />
<script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
<style>
  :root {{
    --bg: #0b1320;
    --panel: #132238;
    --card: #192d4a;
    --border: #233c60;
    --text: #e8edf4;
    --muted: #8ea1b8;
    --accent: #38bdf8;
    --warning: #f59e0b;
    --danger: #ef4444;
  }}
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    background: var(--bg);
    color: var(--text);
    display: flex;
    flex-direction: column;
    height: 100vh;
    overflow: hidden;
  }}
  header {{
    background: var(--panel);
    border-bottom: 1px solid var(--border);
    padding: 12px 20px;
    display: flex;
    align-items: center;
    justify-content: space-between;
    flex-wrap: wrap;
    gap: 12px;
  }}
  .title-group h1 {{
    font-size: 18px;
    font-weight: 600;
    letter-spacing: -0.3px;
    color: #fff;
  }}
  .title-group p {{
    font-size: 12.5px;
    color: var(--muted);
    margin-top: 2px;
  }}
  .kpi-bar {{
    display: flex;
    gap: 12px;
    flex-wrap: wrap;
  }}
  .kpi {{
    background: var(--card);
    border: 1px solid var(--border);
    border-radius: 6px;
    padding: 6px 12px;
    font-size: 11.5px;
  }}
  .kpi strong {{
    display: block;
    font-size: 15px;
    color: var(--accent);
  }}
  #main-container {{
    display: flex;
    flex: 1;
    position: relative;
    height: calc(100vh - 65px);
  }}
  #map {{
    flex: 1;
    height: 100%;
    background: #090e17;
  }}
  #sidebar {{
    width: 320px;
    background: var(--panel);
    border-left: 1px solid var(--border);
    padding: 16px;
    overflow-y: auto;
    font-size: 13px;
    line-height: 1.5;
  }}
  .sidebar-section {{
    margin-bottom: 20px;
  }}
  .sidebar-section h3 {{
    font-size: 13px;
    text-transform: uppercase;
    letter-spacing: 0.5px;
    color: var(--muted);
    margin-bottom: 8px;
    border-bottom: 1px solid var(--border);
    padding-bottom: 4px;
  }}
  .legend-item {{
    display: flex;
    align-items: center;
    gap: 8px;
    margin: 6px 0;
  }}
  .color-swatch {{
    width: 16px;
    height: 16px;
    border-radius: 3px;
    flex-shrink: 0;
  }}
  .info-table {{
    width: 100%;
    border-collapse: collapse;
    font-size: 12px;
  }}
  .info-table td {{
    padding: 4px 0;
    border-bottom: 1px solid rgba(255,255,255,0.05);
  }}
  .info-table td.label {{
    color: var(--muted);
  }}
  .info-table td.value {{
    text-align: right;
    font-weight: 500;
  }}
  .leaflet-popup-content-wrapper {{
    background: var(--panel) !important;
    color: var(--text) !important;
    border: 1px solid var(--border) !important;
    border-radius: 8px !important;
    font-family: inherit !important;
  }}
  .leaflet-popup-tip {{
    background: var(--panel) !important;
  }}
  .popup-row {{
    font-size: 12px;
    margin: 3px 0;
  }}
  .popup-lbl {{
    color: var(--muted);
  }}
</style>
</head>
<body>

<header>
  <div class="title-group">
    <h1>Bengaluru 500 m Full-City Spatial Grid</h1>
    <p>Spatial Skeleton: UTM 43N (EPSG:32643) &bull; BBMP 2011 198-Ward Delimitation &bull; Native CHIRPS 0.05&deg;</p>
  </div>
  <div class="kpi-bar">
    <div class="kpi"><span>Grid Cells</span><strong>{len(gdf_cells_wgs):,}</strong></div>
    <div class="kpi"><span>Wards</span><strong>198</strong></div>
    <div class="kpi"><span>CHIRPS Pixels</span><strong>{len(rain_pixels_df)}</strong></div>
    <div class="kpi"><span>Coverage</span><strong>{total_boundary_area_km2:.1f} km²</strong></div>
  </div>
</header>

<div id="main-container">
  <div id="map"></div>
  <div id="sidebar">
    <div class="sidebar-section">
      <h3>Layer Legend</h3>
      <div class="legend-item">
        <span class="color-swatch" style="background: rgba(56, 189, 248, 0.4); border: 1px solid #38bdf8;"></span>
        <span>500 m Grid Cells (n={len(gdf_cells_wgs):,})</span>
      </div>
      <div class="legend-item">
        <span class="color-swatch" style="background: transparent; border: 2px solid #a855f7;"></span>
        <span>BBMP 198 Wards (2011)</span>
      </div>
      <div class="legend-item">
        <span class="color-swatch" style="background: rgba(245, 158, 11, 0.15); border: 2px dashed #f59e0b;"></span>
        <span>Native CHIRPS Pixels (0.05&deg;)</span>
      </div>
      <div class="legend-item">
        <span class="color-swatch" style="background: #ef4444; border-radius: 50%;"></span>
        <span>Documented Flood Events (10 points)</span>
      </div>
    </div>

    <div class="sidebar-section">
      <h3>Lattice Specification</h3>
      <table class="info-table">
        <tr><td class="label">Projected CRS</td><td class="value">EPSG:32643 (UTM 43N)</td></tr>
        <tr><td class="label">Geographic CRS</td><td class="value">EPSG:4326 (WGS84)</td></tr>
        <tr><td class="label">Spacing</td><td class="value">500 m regular lattice</td></tr>
        <tr><td class="label">Full (0.25 km²) Cells</td><td class="value">{(gdf_cells_wgs['area_km2'] >= 0.2499).sum():,}</td></tr>
        <tr><td class="label">Edge (Clipped) Cells</td><td class="value">{(gdf_cells_wgs['area_km2'] < 0.2499).sum():,}</td></tr>
        <tr><td class="label">Straddling Pixels</td><td class="value">{straddle_count} ({straddle_count/len(gdf_cells_wgs)*100:.1f}%)</td></tr>
      </table>
    </div>

    <div class="sidebar-section">
      <h3>Cell Inspector</h3>
      <p id="inspect-msg" style="color: var(--muted); font-size: 12px;">Click any grid cell, ward, or rain pixel on the map to inspect its attributes.</p>
      <div id="inspect-data" style="display:none;"></div>
    </div>
  </div>
</div>

<script>
const map = L.map('map', {{
  center: [12.9716, 77.5946],
  zoom: 11,
  preferCanvas: true
}});

L.tileLayer('https://{{s}}.basemaps.cartocdn.com/dark_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
  attribution: '&copy; <a href=\"https://www.openstreetmap.org/copyright\">OSM</a> &copy; <a href=\"https://carto.com/\">CARTO</a>',
  subdomains: 'abcd',
  maxZoom: 18
}}).addTo(map);

// Data payloads
const wardsData = {wards_json_str};
const rainPixelsData = {json.dumps(rain_pixels_geojson)};
const cellsData = {cells_json_str};
const eventsData = {json.dumps(events_data)};

// 1. Grid Cells Layer
const cellsLayer = L.geoJSON(cellsData, {{
  style: feature => ({{
    color: '#38bdf8',
    weight: 0.5,
    opacity: 0.6,
    fillColor: '#0284c7',
    fillOpacity: feature.properties.area_km2 < 0.24 ? 0.35 : 0.2
  }}),
  onEachFeature: (feature, layer) => {{
    layer.on('click', e => {{
      L.DomEvent.stopPropagation(e);
      const p = feature.properties;
      showInspector(`
        <h4 style="color:var(--accent);margin-bottom:6px;">Cell #${{p.cell_id}}</h4>
        <div class="popup-row"><span class="popup-lbl">Ward:</span> #${{p.ward}} - ${{p.ward_name}}</div>
        <div class="popup-row"><span class="popup-lbl">Area:</span> ${{p.area_km2.toFixed(4)}} km²</div>
        <div class="popup-row"><span class="popup-lbl">CHIRPS Rain Pixel:</span> #${{p.rain_pixel_id}}</div>
        <div class="popup-row"><span class="popup-lbl">Centroid:</span> ${{p.lat.toFixed(5)}}, ${{p.lon.toFixed(5)}}</div>
      `);
    }});
  }}
}}).addTo(map);

// 2. Wards Layer
const wardsLayer = L.geoJSON(wardsData, {{
  style: {{
    color: '#a855f7',
    weight: 1.5,
    fillOpacity: 0.02,
    dashArray: '2, 3'
  }},
  onEachFeature: (feature, layer) => {{
    layer.on('click', e => {{
      L.DomEvent.stopPropagation(e);
      const p = feature.properties;
      showInspector(`
        <h4 style="color:#c084fc;margin-bottom:6px;">Ward #${{p.WARD_NO}}</h4>
        <div class="popup-row"><span class="popup-lbl">Name:</span> ${{p.WARD_NAME}}</div>
      `);
    }});
  }}
}}).addTo(map);

// 3. Rain Pixels Layer
const rainPixelsLayer = L.geoJSON(rainPixelsData, {{
  style: {{
    color: '#f59e0b',
    weight: 2,
    dashArray: '6, 6',
    fillColor: '#f59e0b',
    fillOpacity: 0.08
  }},
  onEachFeature: (feature, layer) => {{
    const p = feature.properties;
    layer.bindTooltip(`CHIRPS Pixel #${{p.rain_pixel_id}} (${{p.n_cells}} cells)`, {{
      permanent: false,
      direction: 'center',
      className: 'pixel-tooltip'
    }});
    layer.on('click', e => {{
      L.DomEvent.stopPropagation(e);
      showInspector(`
        <h4 style="color:var(--warning);margin-bottom:6px;">CHIRPS Native Pixel #${{p.rain_pixel_id}}</h4>
        <div class="popup-row"><span class="popup-lbl">Grid size:</span> 0.05&deg; (~5.5 km)</div>
        <div class="popup-row"><span class="popup-lbl">Cells contained:</span> ${{p.n_cells}}</div>
        <div class="popup-row"><span class="popup-lbl">Center Lat/Lon:</span> ${{p.center_lat}}, ${{p.center_lon}}</div>
      `);
    }});
  }}
}}).addTo(map);

// 4. Events Layer
const eventsLayer = L.layerGroup();
eventsData.forEach(ev => {{
  const isOutside = ev.outside_grid;
  const color = isOutside ? '#f97316' : '#ef4444';
  const marker = L.circleMarker([ev.lat, ev.lon], {{
    radius: 7,
    color: color,
    fillColor: color,
    fillOpacity: 0.9,
    weight: isOutside ? 2 : 2,
    dashArray: isOutside ? '3, 3' : null
  }}).addTo(eventsLayer);

  const statusTxt = isOutside
    ? '<b style=\"color:#f97316;\">Outside 2011 BBMP Grid</b>'
    : '<b style=\"color:#38bdf8;\">Matched to Cell #' + ev.cell_id + '</b>';
  const nearestTxt = isOutside
    ? '<div class=\"popup-row\" style=\"color:var(--muted);font-size:11px;\">Nearest cell: #' + ev.nearest_cell_id + '</div>'
    : '';

  marker.bindPopup(`
    <strong style=\"color:${{isOutside ? '#fb923c' : '#f87171'}};\">${{ev.place_name}}</strong><br>
    <div class=\"popup-row\"><span class=\"popup-lbl\">Status:</span> ${{statusTxt}}</div>
    <div class=\"popup-row\"><span class=\"popup-lbl\">Event:</span> ${{ev.event_id}} (${{ev.date}})</div>
    <div class=\"popup-row\"><span class=\"popup-lbl\">Confidence:</span> ${{ev.confidence}}</div>
    <div class=\"popup-row\"><span class=\"popup-lbl\">Coord:</span> ${{ev.lat}}, ${{ev.lon}}</div>
    ${{nearestTxt}}
  `);
}});
eventsLayer.addTo(map);

// Layer Control
L.control.layers(null, {{
  "500 m Cells": cellsLayer,
  "BBMP 198 Wards": wardsLayer,
  "CHIRPS Rain Pixels": rainPixelsLayer,
  "Documented Events": eventsLayer
}}, {{ position: 'topright', collapsed: false }}).addTo(map);

function showInspector(content) {{
  document.getElementById('inspect-msg').style.display = 'none';
  const el = document.getElementById('inspect-data');
  el.style.display = 'block';
  el.innerHTML = content;
}}
</script>
</body>
</html>
"""
    with open(out_html_path, "w") as f:
        f.write(html_content)
    print(f"Saved interactive preview HTML to {out_html_path}")

if __name__ == "__main__":
    build_grid()
