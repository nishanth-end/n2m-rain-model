"""pipeline/02_events.py
Stage 1b: Audits data/events.csv and maps each documented flood location to its 500 m grid cell.
Performs strict point-in-polygon (PIP) assignment against cell geometries:
- Inside grid: outside_grid=False, records matched cell_id, ward, and distance to cell edge/centroid.
- Generates data/interim/events_with_cells.csv.
- Generates data/interim/event_cells.csv with (event_id, place, cell_id, role) for seeds and 3x3 topological neighbours.
- Computes true seed-only positive cell-days.

Usage:
    python pipeline/02_events.py
"""

import os
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

def audit_and_upgrade_events(
    events_path="data/events.csv",
    cells_path="data/interim/cells_grid.csv",
    cells_geojson_path="data/interim/cells_grid.geojson",
    output_events_path="data/interim/events_with_cells.csv",
    output_event_cells_path="data/interim/event_cells.csv"
):
    print(f"--- Auditing {events_path} ---")
    events = pd.read_csv(events_path)
    cells = pd.read_csv(cells_path)
    cells_gdf = gpd.read_file(cells_geojson_path).to_crs("EPSG:32643")
    grid_union = cells_gdf.union_all()

    # 1. Schema check
    required_cols = [
        "event_id", "start_date", "end_date", "peak_date",
        "place_name", "lat", "lon", "cell_id", "evidence_type",
        "source_citation", "source_url", "accessed_on", "label_confidence", "notes"
    ]
    missing_cols = [c for c in required_cols if c not in events.columns]
    if missing_cols:
        raise ValueError(f"Missing required columns in events.csv: {missing_cols}")

    print(f"Events table loaded: {len(events)} rows across {events['event_id'].nunique()} distinct events.")

    # 2. Strict Point-in-Polygon check
    events_gdf = gpd.GeoDataFrame(
        events,
        geometry=gpd.points_from_xy(events["lon"], events["lat"]),
        crs="EPSG:4326"
    ).to_crs("EPSG:32643")

    records = []
    for idx, r in events.iterrows():
        pt = events_gdf.geometry.iloc[idx]
        pip = cells_gdf[cells_gdf.geometry.contains(pt)]

        if len(pip) > 0:
            c = pip.iloc[0]
            cid = int(c["cell_id"])
            cell_row = cells[cells["cell_id"] == cid].iloc[0]
            stored_c = Point(cell_row["x_utm"], cell_row["y_utm"])
            lat_c = Point(cell_row["lattice_center_x"], cell_row["lattice_center_y"])
            dist_to_edge = round(c.geometry.boundary.distance(pt), 1)

            records.append({
                "event_id": r["event_id"],
                "start_date": r["start_date"],
                "end_date": r["end_date"],
                "place_name": r["place_name"],
                "lat": r["lat"],
                "lon": r["lon"],
                "outside_grid": False,
                "cell_id": cid,
                "ward": int(cell_row["ward"]),
                "ward_name": str(cell_row["ward_name"]),
                "dist_to_cell_centroid_m": round(pt.distance(stored_c), 1),
                "dist_to_lattice_center_m": round(pt.distance(lat_c), 1),
                "dist_to_cell_edge_m": dist_to_edge,
                "dist_to_grid_boundary_m": pd.NA,
                "nearest_cell_id": cid,
                "label_confidence": r["label_confidence"],
                "evidence_type": r["evidence_type"],
                "source_citation": r["source_citation"],
                "notes": r.get("notes", "")
            })
        else:
            dists_geom = cells_gdf.geometry.distance(pt)
            nearest_idx = dists_geom.idxmin()
            nearest_c = cells_gdf.loc[nearest_idx]
            nearest_cid = int(nearest_c["cell_id"])
            cell_row = cells[cells["cell_id"] == nearest_cid].iloc[0]
            stored_c = Point(cell_row["x_utm"], cell_row["y_utm"])
            lat_c = Point(cell_row["lattice_center_x"], cell_row["lattice_center_y"])
            dist_boundary = round(grid_union.boundary.distance(pt), 1)

            records.append({
                "event_id": r["event_id"],
                "start_date": r["start_date"],
                "end_date": r["end_date"],
                "place_name": r["place_name"],
                "lat": r["lat"],
                "lon": r["lon"],
                "outside_grid": True,
                "cell_id": pd.NA,
                "ward": pd.NA,
                "ward_name": pd.NA,
                "dist_to_cell_centroid_m": round(pt.distance(stored_c), 1),
                "dist_to_lattice_center_m": round(pt.distance(lat_c), 1),
                "dist_to_cell_edge_m": pd.NA,
                "dist_to_grid_boundary_m": dist_boundary,
                "nearest_cell_id": nearest_cid,
                "label_confidence": r["label_confidence"],
                "evidence_type": r["evidence_type"],
                "source_citation": r["source_citation"],
                "notes": r.get("notes", "")
            })

    events_upgraded = pd.DataFrame(records)

    # Compute window duration
    events_upgraded["window_days"] = (
        pd.to_datetime(events_upgraded["end_date"]) - pd.to_datetime(events_upgraded["start_date"])
    ).dt.days + 1

    os.makedirs(os.path.dirname(output_events_path), exist_ok=True)
    events_upgraded.to_csv(output_events_path, index=False)
    print(f"Saved upgraded events with strict PIP status to {output_events_path}")

    # 3. Spatial neighborhood map using lattice (col, row) offsets
    id_to_pos = {int(r['cell_id']): (round(r['lattice_center_x']), round(r['lattice_center_y'])) for _, r in cells.iterrows()}
    pos_to_id = {(round(r['lattice_center_x']), round(r['lattice_center_y'])): int(r['cell_id']) for _, r in cells.iterrows()}

    def get_3x3_cells(cid):
        x, y = id_to_pos[cid]
        nbrs = set()
        for dx in [-500, 0, 500]:
            for dy in [-500, 0, 500]:
                p = (x + dx, y + dy)
                if p in pos_to_id:
                    nbrs.add(pos_to_id[p])
        return nbrs

    # Footprint / multiple seeds mapping per decision A3
    event_place_seeds = [
        ('E2022_09', 'RBD Layout (Sarjapur Road)', [554, 555, 608]),
        ('E2022_09', 'Wipro Campus (Sarjapur Road)', [665, 666]),
        ('E2022_09', 'Outer Ring Road (RMZ Ecospace / Saul Kere reach)', [847]),
        ('E2022_09', 'Epsilon Layout / Yemalur Road (ORR Kadubeesanahalli bridge)', [910]),
        ('E2022_09', 'Borewell Road (Whitefield)', [1444]),
        ('E2022_09', 'Panathur-Balagere Road (near BWSSB STP/Varthur lake)', [977]),
        ('E2022_05', 'RBD Layout (Sarjapur Road)', [554, 555, 608]),
        ('E2021_11', 'Yelahanka / Jakkur, North Bengaluru', [2882]),
        ('E2017_08', 'Koramangala 4th Block', [897]),
        ('E2017_09', 'Hosur-Sarjapur Road / Anugraha Layout, Koramangala', [774]),
    ]

    event_cells_rows = []
    for eid, place, seeds in event_place_seeds:
        all_nbrs = set()
        for s in seeds:
            event_cells_rows.append({'event_id': eid, 'place': place, 'cell_id': s, 'role': 'seed'})
            all_nbrs.update(get_3x3_cells(s))
        for n in sorted(all_nbrs - set(seeds)):
            event_cells_rows.append({'event_id': eid, 'place': place, 'cell_id': n, 'role': 'neighbour_3x3'})

    df_event_cells = pd.DataFrame(event_cells_rows)
    df_event_cells.to_csv(output_event_cells_path, index=False)
    print(f"Saved event cells with roles (seeds and neighbours) to {output_event_cells_path}")

    # Compute seed-only cell-days
    daily_seed_cells = set()
    durations = {
        'E2022_09': pd.date_range('2022-09-05', '2022-09-07'),
        'E2022_05': pd.date_range('2022-05-05', '2022-05-05'),
        'E2021_11': pd.date_range('2021-11-21', '2021-11-21'),
        'E2017_08': pd.date_range('2017-08-15', '2017-08-15'),
        'E2017_09': pd.date_range('2017-09-27', '2017-09-28'),
    }

    seeds_by_event = {}
    for eid, place, seeds in event_place_seeds:
        seeds_by_event.setdefault(eid, set()).update(seeds)

    for eid, dates in durations.items():
        seeds = seeds_by_event.get(eid, set())
        for d in dates:
            d_str = d.strftime("%Y-%m-%d")
            for s in seeds:
                daily_seed_cells.add((d_str, s))

    print("\n--- Positive Cell-Days Yield (Seed Cells Only) ---")
    print(f"Total Seed-Only Positive Cell-Days: {len(daily_seed_cells)}")
    print(f"Spec Targets: Minimum >= 100 ({len(daily_seed_cells)}/100 = {len(daily_seed_cells)/100:.1%}); Target >= 500 ({len(daily_seed_cells)}/500 = {len(daily_seed_cells)/500:.1%})")

    return events_upgraded

if __name__ == "__main__":
    audit_and_upgrade_events()
