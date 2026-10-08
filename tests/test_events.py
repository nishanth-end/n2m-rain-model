"""tests/test_events.py
Test suite for event auditing and spatial linkage in pipeline/02_events.py.
Verifies data/events.csv hash integrity, strict point-in-polygon matching,
allowlist enforcement for boundary points, and spatial deduplication math.
"""

import os
import hashlib
import pandas as pd
import numpy as np
import geopandas as gpd
from shapely.geometry import Point
import pytest

RAW_EVENTS_CSV = "data/events.csv"
UPGRADED_EVENTS_CSV = "data/interim/events_with_cells.csv"
CELLS_GEOJSON = "data/interim/cells_grid.geojson"
CELLS_CSV = "data/interim/cells_grid.csv"

EXPECTED_EVENTS_SHA256 = "720a8cc7ddf3e1a0720ef0ee69e67dc5bc83de50b60378298a98b9c79bb18a81"
ALLOWED_OUTSIDE_LOCATIONS = {
    "RBD Layout (Sarjapur Road)",
    "Wipro Campus (Sarjapur Road)"
}

@pytest.fixture(scope="module")
def raw_events_df():
    assert os.path.exists(RAW_EVENTS_CSV), f"Missing {RAW_EVENTS_CSV}."
    return pd.read_csv(RAW_EVENTS_CSV)

@pytest.fixture(scope="module")
def upgraded_events_df():
    assert os.path.exists(UPGRADED_EVENTS_CSV), f"Missing {UPGRADED_EVENTS_CSV}. Run pipeline/02_events.py first."
    return pd.read_csv(UPGRADED_EVENTS_CSV)

@pytest.fixture(scope="module")
def cells_gdf():
    assert os.path.exists(CELLS_GEOJSON), f"Missing {CELLS_GEOJSON}."
    return gpd.read_file(CELLS_GEOJSON).to_crs("EPSG:32643")

def test_events_csv_hash_guard():
    """Protects data/events.csv against accidental unverified edits."""
    with open(RAW_EVENTS_CSV, "rb") as f:
        file_hash = hashlib.sha256(f.read()).hexdigest()
    assert file_hash == EXPECTED_EVENTS_SHA256, (
        f"data/events.csv hash mismatch! Expected {EXPECTED_EVENTS_SHA256}, got {file_hash}. "
        "Candidate events must NOT be committed to data/events.csv without team review."
    )

def test_events_summary_counts(upgraded_events_df):
    """Verifies expected event row counts, distinct event IDs, and inside/outside split."""
    assert len(upgraded_events_df) == 10, f"Expected 10 event rows, got {len(upgraded_events_df)}"
    assert upgraded_events_df["event_id"].nunique() == 5, (
        f"Expected 5 distinct events, got {upgraded_events_df['event_id'].nunique()}"
    )

    inside = upgraded_events_df[~upgraded_events_df["outside_grid"]]
    outside = upgraded_events_df[upgraded_events_df["outside_grid"]]

    assert len(inside) == 7, f"Expected 7 inside events, got {len(inside)}"
    assert len(outside) == 3, f"Expected 3 outside events, got {len(outside)}"

def test_events_strict_pip_and_distance_bounds(upgraded_events_df, cells_gdf):
    """Inside events must strictly satisfy Point-in-Polygon (PIP) and distance <= 353.6 m (+ epsilon)."""
    inside = upgraded_events_df[~upgraded_events_df["outside_grid"]]
    max_diag = 250.0 * np.sqrt(2.0) + 1.0  # ~354.6 m

    for _, row in inside.iterrows():
        cid = int(row["cell_id"])
        cell_geom = cells_gdf[cells_gdf["cell_id"] == cid].geometry.iloc[0]
        
        # Point in EPSG:32643
        pt_wgs = Point(row["lon"], row["lat"])
        pt_utm = gpd.GeoSeries([pt_wgs], crs="EPSG:4326").to_crs("EPSG:32643").iloc[0]

        # 1. Point must lie inside cell polygon
        assert cell_geom.contains(pt_utm), (
            f"Event {row['place_name']} does not lie inside matched cell {cid} geometry!"
        )

        # 2. Distance to centroid must not exceed maximum lattice radius
        assert row["dist_to_cell_centroid_m"] <= max_diag, (
            f"Event {row['place_name']} dist {row['dist_to_cell_centroid_m']} m exceeds max diagonal {max_diag} m"
        )

        # 3. Distance to cell edge must be positive
        assert pd.notna(row["dist_to_cell_edge_m"])
        assert float(row["dist_to_cell_edge_m"]) > 0

def test_outside_events_allowlist(upgraded_events_df):
    """Only approved peri-urban boundary sites may be marked outside_grid; no silent snapping."""
    outside = upgraded_events_df[upgraded_events_df["outside_grid"]]
    for _, row in outside.iterrows():
        assert pd.isna(row["cell_id"]), f"Outside event {row['place_name']} must have NA cell_id"
        assert pd.isna(row["ward"]), f"Outside event {row['place_name']} must have NA ward"
        assert row["dist_to_grid_boundary_m"] > 0, "Distance to grid boundary must be positive"
        assert row["place_name"] in ALLOWED_OUTSIDE_LOCATIONS, (
            f"Unexpected outside event: {row['place_name']}. Outside locations must be in allowlist."
        )

def test_toy_spatial_deduplication():
    """Toy test demonstrating that overlapping 3x3 footprints produce strictly < 18 unique cells."""
    # Build 3x3 footprint for seed at (col=5, row=5)
    seed1 = (5, 5)
    fp1 = {(seed1[0] + dc, seed1[1] + dr) for dc in [-1, 0, 1] for dr in [-1, 0, 1]}
    assert len(fp1) == 9

    # Diagonal neighbor seed at (col=6, row=6)
    seed_diag = (6, 6)
    fp_diag = {(seed_diag[0] + dc, seed_diag[1] + dr) for dc in [-1, 0, 1] for dr in [-1, 0, 1]}
    assert len(fp_diag) == 9

    # Diagonal neighbors share exactly 4 cells: (5,5), (5,6), (6,5), (6,6)
    shared_diag = fp1.intersection(fp_diag)
    assert len(shared_diag) == 4
    union_diag = fp1.union(fp_diag)
    assert len(union_diag) == 14  # 9 + 9 - 4 = 14 < 18

    # Orthogonal neighbor seed at (col=5, row=6)
    seed_ortho = (5, 6)
    fp_ortho = {(seed_ortho[0] + dc, seed_ortho[1] + dr) for dc in [-1, 0, 1] for dr in [-1, 0, 1]}
    shared_ortho = fp1.intersection(fp_ortho)
    assert len(shared_ortho) == 6
    union_ortho = fp1.union(fp_ortho)
    assert len(union_ortho) == 12  # 9 + 9 - 6 = 12 < 18

def test_pip_vs_nearest_centroid_failure_demo(cells_gdf):
    """Proves that naive nearest-centroid snapping fails for outside points (demonstrating Bug 1 fix)."""
    # RBD Layout coordinate
    rbd_pt_wgs = Point(77.700, 12.901)
    rbd_pt_utm = gpd.GeoSeries([rbd_pt_wgs], crs="EPSG:4326").to_crs("EPSG:32643").iloc[0]

    # Check whether RBD layout lies inside grid polygon
    grid_union = cells_gdf.union_all()
    assert not grid_union.contains(rbd_pt_utm), "RBD Layout is outside grid union polygon"

    # Nearest centroid distance
    cells_df = pd.read_csv(CELLS_CSV)
    cells_coords = cells_df[["x_utm", "y_utm"]].values
    dists = np.sqrt((cells_coords[:, 0] - rbd_pt_utm.x)**2 + (cells_coords[:, 1] - rbd_pt_utm.y)**2)
    min_dist = dists.min()

    # Min distance is ~640.6 m, which exceeds maximum possible inside distance (353.6 m)
    max_inside_radius = 250.0 * np.sqrt(2.0)
    assert min_dist > max_inside_radius, (
        f"Nearest distance {min_dist:.1f} m should exceed {max_inside_radius:.1f} m"
    )

def test_footprint_yield_ge_point_yield_on_identical_seeds():
    """Asserts that expanding seeds with a footprint produces >= daily yield under identical base seeds."""
    cells = pd.read_csv(CELLS_CSV)
    id_to_pos = {int(r['cell_id']): (round(r['lattice_center_x']), round(r['lattice_center_y'])) for _, r in cells.iterrows()}
    pos_to_id = {(round(r['lattice_center_x']), round(r['lattice_center_y'])): int(r['cell_id']) for _, r in cells.iterrows()}

    def get_3x3(cid):
        x, y = id_to_pos[cid]
        nbrs = set()
        for dx in [-500, 0, 500]:
            for dy in [-500, 0, 500]:
                p = (x + dx, y + dy)
                if p in pos_to_id:
                    nbrs.add(pos_to_id[p])
        return nbrs

    # Point seeds (CFG_A):
    point_seeds = [555, 666, 847, 910, 977, 1444]
    # Footprint seeds (CFG_B, superset containing point seeds):
    footprint_seeds = [554, 555, 608, 607, 665, 666, 847, 910, 977, 1444]

    u_point = set()
    for s in point_seeds:
        u_point.update(get_3x3(s))

    u_footprint = set()
    for s in footprint_seeds:
        u_footprint.update(get_3x3(s))

    assert len(u_footprint) >= len(u_point), (
        f"Footprint yield {len(u_footprint)} is smaller than point yield {len(u_point)}!"
    )
    assert u_point.issubset(u_footprint), "Point cells set must be a subset of footprint cells set"

def test_summary_numbers_match_csvs():
    """Verifies that statistics in reports/stage1_summary.md match recomputed values from CSVs."""
    cells = pd.read_csv(CELLS_CSV)
    events = pd.read_csv(UPGRADED_EVENTS_CSV)

    assert os.path.exists("reports/stage1_summary.md"), "Missing reports/stage1_summary.md"
    with open("reports/stage1_summary.md", "r") as f:
        md_text = f.read()

    assert f"Total Grid Cells**: {len(cells):,}" in md_text
    assert f"Total Event Rows**: {len(events)}" in md_text

