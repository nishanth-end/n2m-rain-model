"""pipeline/prototype_extended_grid.py
Option D Prototype: Evaluates extending the 500 m grid beyond the 2011 BBMP ward union
by a 1 km and 2 km spatial buffer.

Outputs (analysis only, does not overwrite production grid):
    data/interim/experimental/cells_grid_ext_1km.csv
    data/interim/experimental/cells_grid_ext_2km.csv
"""

import os
import math
import pandas as pd
import geopandas as gpd
import numpy as np
from shapely.geometry import box, Point

def build_extended_prototype(buffer_m=1000.0, output_csv=None):
    orig_cells = pd.read_csv("data/interim/cells_grid.csv")
    orig_gdf = gpd.read_file("data/interim/cells_grid.geojson").to_crs("EPSG:32643")
    wards = gpd.read_file("data/raw/bbmp_wards_198.geojson").to_crs("EPSG:32643")
    city_poly = wards.union_all()
    spacing = 500.0

    buf_poly = city_poly.buffer(buffer_m)
    minx, miny, maxx, maxy = buf_poly.bounds

    x_start = math.floor(minx / spacing) * spacing
    y_start = math.floor(miny / spacing) * spacing
    x_end = math.ceil(maxx / spacing) * spacing
    y_end = math.ceil(maxy / spacing) * spacing

    xs = np.arange(x_start, x_end, spacing)
    ys = np.arange(y_start, y_end, spacing)

    existing_centers = set(zip(orig_cells["lattice_center_x"].round(2), orig_cells["lattice_center_y"].round(2)))

    new_cells = []
    for y in ys:
        for x in xs:
            cx = round(x + spacing / 2.0, 2)
            cy = round(y + spacing / 2.0, 2)
            if (cx, cy) in existing_centers:
                continue
            cell_box = box(x, y, x + spacing, y + spacing)
            if cell_box.intersects(buf_poly):
                clipped = cell_box.intersection(buf_poly)
                if not clipped.is_empty and clipped.area > 1.0:
                    c = clipped.centroid
                    new_cells.append({
                        "lattice_center_x": cx,
                        "lattice_center_y": cy,
                        "x_utm": round(c.x, 2),
                        "y_utm": round(c.y, 2),
                        "area_km2": round(clipped.area / 1e6, 6),
                        "geometry": clipped,
                        "centroid_geom": c,
                        "in_ward_union": False,
                        "ward": pd.NA,
                        "ward_name": pd.NA,
                        "rain_pixel_id": pd.NA
                    })

    gdf_new = gpd.GeoDataFrame(new_cells, crs="EPSG:32643")
    gdf_new = gdf_new.sort_values(by=["lattice_center_y", "lattice_center_x"]).reset_index(drop=True)
    gdf_new["cell_id"] = range(len(orig_cells), len(orig_cells) + len(gdf_new))

    # Transform centroids to WGS84 for new cells
    new_centroids_wgs = gpd.GeoDataFrame(gdf_new, geometry="centroid_geom", crs="EPSG:32643").to_crs("EPSG:4326")
    gdf_new["lat"] = np.round(new_centroids_wgs.geometry.y, 6)
    gdf_new["lon"] = np.round(new_centroids_wgs.geometry.x, 6)

    # Base cells copy
    orig_copy = orig_cells.copy()
    orig_copy["in_ward_union"] = True

    combined_df = pd.concat([orig_copy, gdf_new.drop(columns=["geometry", "centroid_geom"])], ignore_index=True)

    if output_csv:
        os.makedirs(os.path.dirname(output_csv), exist_ok=True)
        combined_df.to_csv(output_csv, index=False)
        print(f"Saved extended grid ({int(buffer_m/1000)}km buffer) to {output_csv}")

    # Evaluate events matching
    events = pd.read_csv("data/events.csv")
    events_gdf = gpd.GeoDataFrame(
        events,
        geometry=gpd.points_from_xy(events["lon"], events["lat"]),
        crs="EPSG:4326"
    ).to_crs("EPSG:32643")

    combined_gdf = pd.concat([orig_gdf, gdf_new], ignore_index=True)

    matches = []
    for idx, r in events.iterrows():
        pt = events_gdf.geometry.iloc[idx]
        pip = combined_gdf[combined_gdf.geometry.contains(pt)]
        if len(pip) > 0:
            c = pip.iloc[0]
            cid = int(c["cell_id"])
            c_pt = Point(c["x_utm"], c["y_utm"])
            dist = round(pt.distance(c_pt), 1)
            is_orig = cid < len(orig_cells)
            matches.append({
                "place_name": r["place_name"],
                "cell_id": cid,
                "dist_m": dist,
                "in_ward_union": is_orig
            })
        else:
            matches.append({
                "place_name": r["place_name"],
                "cell_id": None,
                "dist_m": None,
                "in_ward_union": False
            })

    # Deduplicated yield
    neighbors = {}
    for _, r in combined_gdf.iterrows():
        c = r.geometry.centroid
        dists = combined_gdf.geometry.centroid.distance(c)
        nbr_ids = set(combined_gdf.loc[dists <= 750.0, "cell_id"])
        neighbors[int(r["cell_id"])] = nbr_ids

    daily_a = set()
    daily_b = set()
    for idx, r in events.iterrows():
        cid = matches[idx]["cell_id"]
        if cid is not None:
            dates = pd.date_range(r["start_date"], r["end_date"])
            for d in dates:
                d_str = d.strftime("%Y-%m-%d")
                daily_a.add((d_str, cid))
                for n in neighbors[cid]:
                    daily_b.add((d_str, n))

    return {
        "buffer_km": buffer_m / 1000.0,
        "existing_cells": len(orig_cells),
        "new_cells": len(gdf_new),
        "total_cells": len(combined_df),
        "extra_area_km2": round(gdf_new["area_km2"].sum(), 2),
        "total_area_km2": round(orig_cells["area_km2"].sum() + gdf_new["area_km2"].sum(), 2),
        "matches": matches,
        "yield_a": len(daily_a),
        "yield_b": len(daily_b)
    }

if __name__ == "__main__":
    res_1km = build_extended_prototype(1000.0, "data/interim/experimental/cells_grid_ext_1km.csv")
    res_2km = build_extended_prototype(2000.0, "data/interim/experimental/cells_grid_ext_2km.csv")

    print("\n=== OPTION D SUMMARY RESULTS ===")
    print(f"1 km Buffer: Total cells = {res_1km['total_cells']} (+{res_1km['new_cells']} new), Extra Area = +{res_1km['extra_area_km2']} km²")
    print(f"  Yield (a): {res_1km['yield_a']} cell-days, Yield (b): {res_1km['yield_b']} cell-days")
    print(f"2 km Buffer: Total cells = {res_2km['total_cells']} (+{res_2km['new_cells']} new), Extra Area = +{res_2km['extra_area_km2']} km²")
    print(f"  Yield (a): {res_2km['yield_a']} cell-days, Yield (b): {res_2km['yield_b']} cell-days")
