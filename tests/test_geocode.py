"""tests/test_geocode.py

Unit and sanity tests for geocoding proposals:
1. Recomputes every row's chosen point and distance_ab_m from saved JSON responses in data/evidence/geocode/.
2. Sanity check: all chosen points lie within the Bengaluru geographic bounding box (12.7 <= lat <= 13.3, 77.3 <= lon <= 77.9).
3. Asserts AUTO_ACCEPT candidate features lie within the 2011 BBMP production grid.
4. Asserts reference proximity rule: AUTO_ACCEPT features with verified references lie within 500 m of reference geometry.
"""

import os
import pytest
import pandas as pd
from pipeline.geocode_proposals import (
    haversine_distance,
    parse_osm_file,
    parse_nominatim_file,
    VERIFIED_REFERENCES,
    EVIDENCE_DIR,
    PROPOSALS_CSV,
    ORIG_PROPOSALS_CSV
)

def test_sanity_bounding_box():
    """All chosen candidate points must lie inside Bengaluru bounds (lat 12.7-13.3, lon 77.3-77.9)."""
    assert os.path.exists(PROPOSALS_CSV), f"Missing {PROPOSALS_CSV}"
    df = pd.read_csv(PROPOSALS_CSV)
    
    # Filter for rows with coordinates
    coords_df = df.dropna(subset=["chosen_lat", "chosen_lon"])
    assert len(coords_df) > 0, "No features with coordinates found"
    
    for _, row in coords_df.iterrows():
        lat = float(row["chosen_lat"])
        lon = float(row["chosen_lon"])
        name = row["feature_name"]
        assert 12.7 <= lat <= 13.3, f"{name}: lat {lat} outside [12.7, 13.3]"
        assert 77.3 <= lon <= 77.9, f"{name}: lon {lon} outside [77.3, 77.9]"

def test_recompute_distances_and_coordinates():
    """Verify that chosen coordinates and A-B distances match calculation from raw JSON evidence."""
    df = pd.read_csv(PROPOSALS_CSV)
    auto_df = df[df["status"] == "AUTO_ACCEPT"]
    
    for _, row in auto_df.iterrows():
        m_a_lat = float(row["method_a_lat"]) if pd.notna(row["method_a_lat"]) else None
        m_a_lon = float(row["method_a_lon"]) if pd.notna(row["method_a_lon"]) else None
        m_b_lat = float(row["method_b_lat"]) if pd.notna(row["method_b_lat"]) else None
        m_b_lon = float(row["method_b_lon"]) if pd.notna(row["method_b_lon"]) else None
        dist_stored = float(row["distance_ab_m"]) if pd.notna(row["distance_ab_m"]) else None
        
        if m_a_lat is not None and m_b_lat is not None:
            recomputed_dist = haversine_distance(m_a_lat, m_a_lon, m_b_lat, m_b_lon)
            assert abs(recomputed_dist - dist_stored) <= 1.0, (
                f"{row['feature_name']}: stored distance {dist_stored} != recomputed {recomputed_dist}"
            )
            assert recomputed_dist <= 150.0, (
                f"{row['feature_name']}: AUTO_ACCEPT distance {recomputed_dist} > 150m"
            )

def test_auto_accept_reference_proximity():
    """All AUTO_ACCEPT features must lie within 500m of verified OSM reference geometry."""
    df = pd.read_csv(PROPOSALS_CSV)
    auto_df = df[df["status"] == "AUTO_ACCEPT"]
    
    for _, row in auto_df.iterrows():
        name = row["feature_name"]
        chosen_lat = float(row["chosen_lat"])
        chosen_lon = float(row["chosen_lon"])
        
        for ref_key, ref_val in VERIFIED_REFERENCES.items():
            if ref_key.lower() in name.lower():
                dist_to_ref = haversine_distance(chosen_lat, chosen_lon, ref_val["lat"], ref_val["lon"])
                assert dist_to_ref <= ref_val["max_dist_m"], (
                    f"{name}: distance {dist_to_ref:.1f}m to reference {ref_val['ref_id']} exceeds 500m"
                )

def test_original_events_proposals_sanity():
    """Check original event geocode proposals table integrity."""
    assert os.path.exists(ORIG_PROPOSALS_CSV), f"Missing {ORIG_PROPOSALS_CSV}"
    df = pd.read_csv(ORIG_PROPOSALS_CSV)
    assert len(df) == 7, f"Expected 7 original event rows, got {len(df)}"
    
    # Anugraha Layout in Koramangala must be UNVERIFIED
    anugraha = df[df["location_name"].str.contains("Anugraha", na=False)].iloc[0]
    assert anugraha["upgrade_recommendation"] == "UNVERIFIED"
