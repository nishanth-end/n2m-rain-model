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
EXPECTED_EVENTS_SHA256 = "0714a91edf2b154cd45b94cbd10c11b3a010472e5172888c2837d5ecbac11e62"

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
    """Verifies that all 10 event rows now strictly lie inside the production grid."""
    assert len(upgraded_events_df) == 10, f"Expected 10 event rows, got {len(upgraded_events_df)}"
    assert upgraded_events_df["event_id"].nunique() == 5, (
        f"Expected 5 distinct events, got {upgraded_events_df['event_id'].nunique()}"
    )

    inside = upgraded_events_df[~upgraded_events_df["outside_grid"]]
    outside = upgraded_events_df[upgraded_events_df["outside_grid"]]

    assert len(inside) == 10, f"Expected all 10 events strictly inside grid, got {len(inside)}"
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
    assert len(seeds) == 15, f"Expected 15 seed rows across the 10 event records, got {len(seeds)}"

    # Check CFG_C footprint seeds presence
    wipro_seeds = set(seeds[seeds["place"] == "Wipro Campus (Sarjapur Road)"]["cell_id"])
    assert wipro_seeds == {665, 666}, f"Expected Wipro seeds {665, 666}, got {wipro_seeds}"

    rbd_seeds = set(seeds[seeds["place"] == "RBD Layout (Sarjapur Road)"]["cell_id"])
    assert rbd_seeds == {554, 555, 608}, f"Expected RBD seeds {554, 555, 608}, got {rbd_seeds}"

    kor_seeds = set(seeds[seeds["place"] == "Koramangala 4th Block"]["cell_id"])
    assert kor_seeds == {897}, f"Expected Koramangala seed 897, got {kor_seeds}"

def test_seed_only_cell_days_yield(event_cells_df, raw_events_df):
    """Seed cells alone produce exactly 34 positive cell-days across the 5 historical events."""
    durations = {
        'E2022_09': pd.date_range('2022-09-05', '2022-09-07'),
        'E2022_05': pd.date_range('2022-05-05', '2022-05-05'),
        'E2021_11': pd.date_range('2021-11-21', '2021-11-21'),
        'E2017_08': pd.date_range('2017-08-15', '2017-08-15'),
        'E2017_09': pd.date_range('2017-09-27', '2017-09-28'),
    }
    seeds_df = event_cells_df[event_cells_df["role"] == "seed"]
    daily_seed_cells = set()

    for eid, dates in durations.items():
        event_seeds = set(seeds_df[seeds_df["event_id"] == eid]["cell_id"])
        for d in dates:
            d_str = d.strftime("%Y-%m-%d")
            for s in event_seeds:
                daily_seed_cells.add((d_str, s))

    assert len(daily_seed_cells) == 34, f"Expected 34 seed-only cell-days, got {len(daily_seed_cells)}"

def test_summary_numbers_match_csvs():
    """Verifies that statistics in reports/stage1_summary.md match recomputed values from CSVs."""
    cells = pd.read_csv(CELLS_CSV)
    events = pd.read_csv(UPGRADED_EVENTS_CSV)

    assert os.path.exists("reports/stage1_summary.md"), "Missing reports/stage1_summary.md"
    with open("reports/stage1_summary.md", "r") as f:
        md_text = f.read()

    assert f"Total Grid Cells**: {len(cells):,}" in md_text
    assert f"Total Event Rows**: {len(events)}" in md_text
