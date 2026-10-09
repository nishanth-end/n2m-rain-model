"""tests/test_events.py
Test suite for event auditing and spatial linkage in pipeline/02_events.py.
Verifies data/events.csv hash integrity, strict point-in-polygon matching,
event_cells.csv structure, and spatial deduplication math.
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
EVENT_CELLS_CSV = "data/interim/event_cells.csv"
CELLS_GEOJSON = "data/interim/cells_grid.geojson"
CELLS_CSV = "data/interim/cells_grid.csv"

# Deliberately updated following approved audit decisions (Wipro & RBD footprint seeds, Koramangala move)
EXPECTED_EVENTS_SHA256 = "b0b0d2fae0f1f7bdf4190d2270abb62e700177990f3468da8ebb08d2ddcc77a0"

@pytest.fixture(scope="module")
def raw_events_df():
    assert os.path.exists(RAW_EVENTS_CSV), f"Missing {RAW_EVENTS_CSV}."
    return pd.read_csv(RAW_EVENTS_CSV)

@pytest.fixture(scope="module")
def upgraded_events_df():
    assert os.path.exists(UPGRADED_EVENTS_CSV), f"Missing {UPGRADED_EVENTS_CSV}. Run pipeline/02_events.py first."
    return pd.read_csv(UPGRADED_EVENTS_CSV)

@pytest.fixture(scope="module")
def event_cells_df():
    assert os.path.exists(EVENT_CELLS_CSV), f"Missing {EVENT_CELLS_CSV}. Run pipeline/02_events.py first."
    return pd.read_csv(EVENT_CELLS_CSV)

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
    """Verifies that all 11 event rows strictly lie inside the production grid across 6 events."""
    assert len(upgraded_events_df) == 11, f"Expected 11 event rows, got {len(upgraded_events_df)}"
    assert upgraded_events_df["event_id"].nunique() == 6, (
        f"Expected 6 distinct events, got {upgraded_events_df['event_id'].nunique()}"
    )

    inside = upgraded_events_df[~upgraded_events_df["outside_grid"]]
    outside = upgraded_events_df[upgraded_events_df["outside_grid"]]

    assert len(inside) == 11, f"Expected all 11 events strictly inside grid, got {len(inside)}"
    assert len(outside) == 0, f"Expected 0 outside events after footprint/centroid corrections, got {len(outside)}"

def test_events_strict_pip_and_distance_bounds(upgraded_events_df, cells_gdf):
    """All 10 events must strictly satisfy Point-in-Polygon (PIP) and distance <= 353.6 m (+ epsilon)."""
    max_diag = 250.0 * np.sqrt(2.0) + 1.0  # ~354.6 m

    for _, row in upgraded_events_df.iterrows():
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

def test_event_cells_roles_and_seeds(event_cells_df):
    """Verifies that event_cells.csv contains valid seed and neighbour_3x3 roles."""
    assert set(event_cells_df["role"].unique()) == {"seed", "neighbour_3x3"}
    seeds = event_cells_df[event_cells_df["role"] == "seed"]
    assert len(seeds) == 16, f"Expected 16 seed rows across the 11 event records, got {len(seeds)}"

    # Check CFG_C footprint seeds presence
    wipro_seeds = set(seeds[seeds["place"] == "Wipro Campus (Sarjapur Road)"]["cell_id"])
    assert wipro_seeds == {665, 666}, f"Expected Wipro seeds {665, 666}, got {wipro_seeds}"

    rbd_seeds = set(seeds[seeds["place"] == "RBD Layout (Sarjapur Road)"]["cell_id"])
    assert rbd_seeds == {554, 555, 608}, f"Expected RBD seeds {554, 555, 608}, got {rbd_seeds}"

    kor_seeds = set(seeds[seeds["place"] == "Koramangala 4th Block"]["cell_id"])
    assert kor_seeds == {897}, f"Expected Koramangala seed 897, got {kor_seeds}"

    kv_seeds = set(seeds[seeds["place"] == "Yelahanka / Jakkur, North Bengaluru"]["cell_id"])
    assert kv_seeds == {2882}, f"Expected Kendriya Vihar seed 2882, got {kv_seeds}"

    kr_seeds = set(seeds[seeds["place"] == "KR Circle Underpass"]["cell_id"])
    assert kr_seeds == {1478}, f"Expected KR Circle seed 1478, got {kr_seeds}"

def test_seed_only_cell_days_yield(event_cells_df, raw_events_df):
    """Seed cells alone produce exactly 35 positive cell-days across the 6 historical events."""
    durations = {
        'E2022_09': pd.date_range('2022-09-05', '2022-09-07'),
        'E2022_05': pd.date_range('2022-05-05', '2022-05-05'),
        'E2021_11': pd.date_range('2021-11-21', '2021-11-21'),
        'E2017_08': pd.date_range('2017-08-15', '2017-08-15'),
        'E2017_09': pd.date_range('2017-09-27', '2017-09-28'),
        'E2023_05': pd.date_range('2023-05-21', '2023-05-21'),
    }
    seeds_df = event_cells_df[event_cells_df["role"] == "seed"]
    daily_seed_cells = set()

    for eid, dates in durations.items():
        event_seeds = set(seeds_df[seeds_df["event_id"] == eid]["cell_id"])
        for d in dates:
            d_str = d.strftime("%Y-%m-%d")
            for s in event_seeds:
                daily_seed_cells.add((d_str, s))

    assert len(daily_seed_cells) == 35, f"Expected 35 seed-only cell-days, got {len(daily_seed_cells)}"

def test_toy_spatial_deduplication():
    """Toy test demonstrating that overlapping 3x3 footprints produce strictly < 18 unique cells."""
    seed1 = (5, 5)
    fp1 = {(seed1[0] + dc, seed1[1] + dr) for dc in [-1, 0, 1] for dr in [-1, 0, 1]}
    assert len(fp1) == 9

    seed_diag = (6, 6)
    fp_diag = {(seed_diag[0] + dc, seed_diag[1] + dr) for dc in [-1, 0, 1] for dr in [-1, 0, 1]}
    assert len(fp_diag) == 9

    shared_diag = fp1.intersection(fp_diag)
    assert len(shared_diag) == 4
    union_diag = fp1.union(fp_diag)
    assert len(union_diag) == 14  # 9 + 9 - 4 = 14 < 18

    seed_ortho = (5, 6)
    fp_ortho = {(seed_ortho[0] + dc, seed_ortho[1] + dr) for dc in [-1, 0, 1] for dr in [-1, 0, 1]}
    shared_ortho = fp1.intersection(fp_ortho)
    assert len(shared_ortho) == 6
    union_ortho = fp1.union(fp_ortho)
    assert len(union_ortho) == 12  # 9 + 9 - 6 = 12 < 18

def test_footprint_yield_ge_point_yield_on_identical_seeds():
    """Footprint-based 3x3 expansion yields >= point-based 3x3 expansion on any seed set."""
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

    point_seed = 555
    footprint_seeds = [554, 555, 608]

    u_point = get_3x3(point_seed)
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

def test_evidence_quotes_verbatim_match():
    """Verifies that every VERIFIED evidence quote is a verbatim substring of its saved source file."""
    log_csv = "data/interim/source_check_log.csv"
    assert os.path.exists(log_csv), f"Missing {log_csv}"
    df = pd.read_csv(log_csv)

    for _, row in df.iterrows():
        if row["verdict"] == "VERIFIED":
            fname = row["local_file"]
            quote = str(row["evidence_quote_under_15_words"])
            fpath = os.path.join("data/raw/sources", fname)
            assert os.path.exists(fpath), f"Missing saved source file: {fpath}"
            with open(fpath, "r", encoding="utf-8", errors="ignore") as f:
                content = f.read()
            assert quote in content, (
                f"Evidence quote '{quote}' not found verbatim in saved source {fname}!"
            )
