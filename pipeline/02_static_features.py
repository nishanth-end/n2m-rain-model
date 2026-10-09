"""pipeline/02_static_features.py
Stage 2: Static Terrain, Drainage, and Land-Cover Features.
Computes 12 static features for each of the 3,026 500 m grid cells:
- elev_m: unburned DEM mean elevation (m above MSL)
- slope_deg: unburned DEM mean slope (degrees)
- flow_acc: upstream contributing area in km2 (burned hybrid drainage on full mosaic)
- twi: topographic wetness index ln(a / tan(beta))
- hand_m: height above nearest drainage (m)
- dist_drain_m: distance to nearest stream / rajakaluve (m)
- dist_road_m: distance to nearest major road (motorway, trunk, primary, secondary) (m)
- dist_lake_m: distance to nearest waterbody / lake (m)
- n_lakes_1km: count of distinct lakes within 1 km buffer
- impervious_fraction: fraction of built-up area (ESA WorldCover 10 m class 50)
- cell_area_km2: cell area in km2
- is_edge_cell: whether cell is boundary-clipped (area < 0.2499 km2)

RULE: This script computes purely static physical and geospatial features and never accesses flood ground truth event tables.
"""

import os
import json
import rasterio
from rasterio.features import rasterize
from rasterio.warp import reproject, Resampling
import numpy as np
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, LineString, Polygon
from scipy.ndimage import distance_transform_edt
from pysheds.grid import Grid

def compute_static_features():
    print("--- Stage 2: Computing Static Features ---")
    cells_geojson_path = "data/interim/cells_grid.geojson"
    dem_pad_path = "data/interim/dem_30m_utm.tif"
    worldcover_path = "data/raw/worldcover/ESA_WorldCover_10m_2021_v200_N12E075_Map.tif"
    osm_path = "data/raw/osm/bengaluru_padded_waterways_roads.json"
    output_csv = "data/interim/cells_static.csv"

    # 1. Load cells
    cells_gdf = gpd.read_file(cells_geojson_path).to_crs("EPSG:32643")
    n_cells = len(cells_gdf)
    print(f"Loaded {n_cells} grid cells.")

    # 2. Load padded DEM (30 m)
    with rasterio.open(dem_pad_path) as src:
        dem_pad = src.read(1)
        dem_trans = src.transform
        dem_crs = src.crs
        res = src.res[0]

    # Compute unburned slope
    dy, dx = np.gradient(dem_pad, res, res)
    slope_rad = np.arctan(np.sqrt(dx**2 + dy**2))
    slope_deg = np.degrees(slope_rad)

    # 3. Load OSM vectors
    with open(osm_path) as f:
        osm_data = json.load(f)
    elems = osm_data.get("elements", [])
    nodes = {e["id"]: (e["lon"], e["lat"]) for e in elems if e.get("type") == "node"}
    ways = [e for e in elems if e.get("type") == "way"]

    waterway_lines = []
    for w in ways:
        if "waterway" in w.get("tags", {}):
            coords = [nodes[nid] for nid in w.get("nodes", []) if nid in nodes]
            if len(coords) >= 2:
                waterway_lines.append(LineString(coords))
    gdf_waterways = gpd.GeoDataFrame(geometry=waterway_lines, crs="EPSG:4326").to_crs("EPSG:32643")

    road_lines = []
    for w in ways:
        hw = w.get("tags", {}).get("highway", "")
        if hw in ["motorway", "trunk", "primary", "secondary", "motorway_link", "trunk_link", "primary_link", "secondary_link"]:
            coords = [nodes[nid] for nid in w.get("nodes", []) if nid in nodes]
            if len(coords) >= 2:
                road_lines.append(LineString(coords))
    gdf_roads = gpd.GeoDataFrame(geometry=road_lines, crs="EPSG:4326").to_crs("EPSG:32643")

    lake_polys = []
    for w in ways:
        if w.get("tags", {}).get("natural") == "water":
            coords = [nodes[nid] for nid in w.get("nodes", []) if nid in nodes]
            if len(coords) >= 4 and coords[0] == coords[-1]:
                lake_polys.append(Polygon(coords))
    gdf_lakes = gpd.GeoDataFrame(geometry=lake_polys, crs="EPSG:4326").to_crs("EPSG:32643")
    # Dissolve touching lakes
    if not gdf_lakes.empty:
        lakes_dissolved = gdf_lakes.union_all()
        gdf_lakes_clean = gpd.GeoDataFrame(geometry=[lakes_dissolved], crs="EPSG:32643").explode(index_parts=False)
    else:
        gdf_lakes_clean = gdf_lakes

    print(f"OSM parsed: {len(gdf_waterways)} waterways, {len(gdf_roads)} major roads, {len(gdf_lakes_clean)} dissolved lakes.")

    # 4. Burn waterways (-2.0 m) into DEM for hydrological routing
    shapes_burn = [(geom, 2.0) for geom in gdf_waterways.geometry if geom.is_valid]
    burn_mask = rasterize(shapes_burn, out_shape=dem_pad.shape, transform=dem_trans, fill=0.0, dtype=np.float32)
    dem_burned = dem_pad - burn_mask

    # 5. Hydrological routing via pysheds on padded burned DEM
    pg_grid = Grid.from_raster(dem_pad_path)
    dem_view = pg_grid.read_raster(dem_pad_path)
    # Apply burn mask
    dem_view -= burn_mask

    pit_filled = pg_grid.fill_pits(dem_view)
    flooded = pg_grid.fill_depressions(pit_filled)
    inflated = pg_grid.resolve_flats(flooded)
    fdir = pg_grid.flowdir(inflated)
    acc = pg_grid.accumulation(fdir)

    # Accumulation in km2
    cell_area_km2_pixel = (res * res) / 1e6
    acc_km2 = acc * cell_area_km2_pixel

    # Stream network threshold: chosen from hydrology (500 pixels = 0.45 km2 contributing area)
    # 0.45 km2 corresponds to typical headwater initiation of secondary urban rajakaluves in Bengaluru
    stream_mask = (acc >= 500) | (burn_mask > 0)
    hand = pg_grid.compute_hand(fdir, inflated, stream_mask)

    # Impute any unrouted edge pixels in HAND using nearest valid neighbor
    if np.any(np.isnan(hand)):
        invalid_hand = np.isnan(hand)
        indices = distance_transform_edt(invalid_hand, return_distances=False, return_indices=True)
        hand = hand[tuple(indices)]

    # Topographic Wetness Index: ln(sca / tan(beta))
    # specific catchment area sca = acc * res
    sca = acc * res
    tan_slope = np.tan(slope_rad)
    tan_slope = np.maximum(tan_slope, 0.001) # epsilon to avoid div by zero
    twi = np.log(np.maximum(sca, res) / tan_slope)

    # 6. Distance rasters via EDT
    waterway_mask = rasterize([(geom, 1) for geom in gdf_waterways.geometry if geom.is_valid],
                              out_shape=dem_pad.shape, transform=dem_trans, fill=0, dtype=np.uint8)
    dist_drain_grid = distance_transform_edt(waterway_mask == 0) * res

    road_mask = rasterize([(geom, 1) for geom in gdf_roads.geometry if geom.is_valid],
                          out_shape=dem_pad.shape, transform=dem_trans, fill=0, dtype=np.uint8)
    dist_road_grid = distance_transform_edt(road_mask == 0) * res

    if not gdf_lakes_clean.empty:
        lake_mask = rasterize([(geom, 1) for geom in gdf_lakes_clean.geometry if geom.is_valid],
                              out_shape=dem_pad.shape, transform=dem_trans, fill=0, dtype=np.uint8)
        dist_lake_grid = distance_transform_edt(lake_mask == 0) * res
    else:
        dist_lake_grid = np.full(dem_pad.shape, 99999.0, dtype=np.float32)

    # 7. WorldCover impervious surface fraction (Class 50) reprojected to padded 30 m grid
    with rasterio.open(worldcover_path) as wc_src:
        wc_arr = np.empty((1, dem_pad.shape[0], dem_pad.shape[1]), dtype=np.uint8)
        reproject(
            source=rasterio.band(wc_src, 1),
            destination=wc_arr,
            src_transform=wc_src.transform,
            src_crs=wc_src.crs,
            dst_transform=dem_trans,
            dst_crs=dem_crs,
            resampling=Resampling.nearest
        )
    built_mask_30m = (wc_arr[0] == 50).astype(np.float32)

    # 8. Sample / aggregate features per cell
    records = []
    lake_sindex = gdf_lakes_clean.sindex if not gdf_lakes_clean.empty else None

    # Pre-build coordinate grids
    cols, rows = np.meshgrid(np.arange(dem_pad.shape[1]), np.arange(dem_pad.shape[0]))
    xs, ys = rasterio.transform.xy(dem_trans, rows, cols)
    xs = np.array(xs)
    ys = np.array(ys)

    for idx, row in cells_gdf.iterrows():
        cid = int(row["cell_id"])
        geom = row.geometry
        minx, miny, maxx, maxy = geom.bounds

        # Cell bounding box window in raster indices
        col_min = max(0, int(np.floor((minx - dem_trans.c) / dem_trans.a)))
        col_max = min(dem_pad.shape[1], int(np.ceil((maxx - dem_trans.c) / dem_trans.a)))
        row_min = max(0, int(np.floor((maxy - dem_trans.f) / dem_trans.e)))
        row_max = min(dem_pad.shape[0], int(np.ceil((miny - dem_trans.f) / dem_trans.e)))

        # Sub-window arrays
        sub_elev = dem_pad[row_min:row_max, col_min:col_max]
        sub_slope = slope_deg[row_min:row_max, col_min:col_max]
        sub_acc = acc_km2[row_min:row_max, col_min:col_max]
        sub_twi = twi[row_min:row_max, col_min:col_max]
        sub_hand = hand[row_min:row_max, col_min:col_max]
        sub_built = built_mask_30m[row_min:row_max, col_min:col_max]

        # Aggregation: mean for elev_m, slope_deg, twi, hand_m; max for flow_acc
        elev_val = float(np.nanmean(sub_elev))
        slope_val = float(np.nanmean(sub_slope))
        acc_val = float(np.nanmax(sub_acc))
        twi_val = float(np.nanmean(sub_twi))
        hand_val = float(np.nanmean(sub_hand))
        imp_val = float(np.nanmean(sub_built))

        # Centroid pixel for Euclidean distance fields
        cx, cy = geom.centroid.x, geom.centroid.y
        col_c = max(0, min(dem_pad.shape[1] - 1, int(round((cx - dem_trans.c) / dem_trans.a))))
        row_c = max(0, min(dem_pad.shape[0] - 1, int(round((cy - dem_trans.f) / dem_trans.e))))

        dist_drain_val = float(dist_drain_grid[row_c, col_c])
        dist_road_val = float(dist_road_grid[row_c, col_c])
        dist_lake_val = float(dist_lake_grid[row_c, col_c])

        # Count of distinct dissolved lakes within 1 km buffer
        if lake_sindex is not None:
            buf_1km = geom.buffer(1000.0)
            possible_lakes = list(lake_sindex.intersection(buf_1km.bounds))
            actual_lakes = sum(1 for l_idx in possible_lakes if gdf_lakes_clean.geometry.iloc[l_idx].intersects(buf_1km))
        else:
            actual_lakes = 0

        area_km2 = float(row["area_km2"])
        is_edge = bool(area_km2 < 0.2499)

        records.append({
            "cell_id": cid,
            "elev_m": round(elev_val, 2),
            "slope_deg": round(slope_val, 2),
            "flow_acc": round(acc_val, 4),
            "twi": round(twi_val, 2),
            "hand_m": round(hand_val, 2),
            "dist_drain_m": round(dist_drain_val, 1),
            "dist_road_m": round(dist_road_val, 1),
            "dist_lake_m": round(dist_lake_val, 1),
            "lakes_within_1km": int(actual_lakes),
            "impervious_fraction": round(imp_val, 3),
            "cell_area_km2": round(area_km2, 4),
            "is_edge_cell": is_edge
        })

    df_static = pd.DataFrame(records)
    os.makedirs(os.path.dirname(output_csv), exist_ok=True)
    df_static.to_csv(output_csv, index=False)
    print(f"Saved {len(df_static)} static feature rows to {output_csv}")

    # Summary checks
    print("\n--- Static Feature Summary ---")
    print(df_static.describe().to_string())
    missing_count = df_static.isna().sum().sum()
    print(f"\nMissing value count: {missing_count}")
    assert missing_count == 0, f"Found {missing_count} missing values in static features!"

    return df_static

if __name__ == "__main__":
    compute_static_features()
