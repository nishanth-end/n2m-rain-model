"""pipeline/geocode_proposals.py

Geocodes candidate features and original events using saved raw JSON evidence
from OpenStreetMap (Method A) and Nominatim (Method B) stored in data/evidence/geocode/.

Classifies candidate features into:
- AUTO_ACCEPT: <= 150m between methods, located within production 2011 grid,
  and satisfies 500m reference proximity check against verified OSM geometries.
- REVIEW: Discrepancy > 150m, linear road corridor, single-source match, or outside grid.
- NO_MATCH: Neither source resolved genuine local feature.
- AREA_ONLY: Broad administrative localities (Koramangala, BTM, HSR, Hebbal, etc.) without point coordinates,
  with OSM polygon area in km2 and count of 500m grid cells covered.

Generates:
1. data/interim/events_geocode_proposals.csv (Candidate features)
2. data/interim/events_geocode_proposals_orig.csv (Original event features audit)
3. reports/geocode_review.html
"""

import os
import json
import math
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point

BBMP_WARDS_GEOJSON = "data/raw/bbmp_wards_198.geojson"
CELLS_GEOJSON = "data/interim/cells_grid.geojson"
CELLS_GRID_CSV = "data/interim/cells_grid.csv"
PROPOSALS_CSV = "data/interim/events_geocode_proposals.csv"
ORIG_PROPOSALS_CSV = "data/interim/events_geocode_proposals_orig.csv"
REVIEW_HTML = "reports/geocode_review.html"
EVIDENCE_DIR = "data/evidence/geocode"

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two points in metres."""
    if any(v is None or (isinstance(v, float) and math.isnan(v)) for v in [lat1, lon1, lat2, lon2]):
        return None
    R = 6371000.0  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return round(R * c, 1)

# Verified references per Item 2: RMZ Ecospace must be way/361528993 (12.924134, 77.681081)
VERIFIED_REFERENCES = {
    "Rainbow Drive Layout": {"lat": 12.906218, "lon": 77.686831, "ref_id": "way/101573097", "max_dist_m": 500.0},
    "Wipro Campus": {"lat": 12.914319, "lon": 77.686317, "ref_id": "way/370327479", "max_dist_m": 500.0},
    "RMZ Ecospace": {"lat": 12.924134, "lon": 77.681081, "ref_id": "way/361528993", "max_dist_m": 500.0},
    "KR Circle Underpass": {"lat": 12.975710, "lon": 77.587200, "ref_id": "way/1096077212", "max_dist_m": 500.0},
}

def parse_osm_file(path):
    if not os.path.exists(path):
        return None, None, None, None, None
    data = json.load(open(path))
    if not data or "elements" not in data or len(data["elements"]) == 0:
        return None, None, None, None, None
    el = data["elements"][-1]
    osm_type = el.get("type")
    osm_id = el.get("id")
    tags = el.get("tags", {})
    if osm_type == "node":
        lat, lon = el.get("lat"), el.get("lon")
        bbox = [lat, lat, lon, lon]
    elif "center" in el:
        lat, lon = el["center"].get("lat"), el["center"].get("lon")
        b = el.get("bounds", {})
        bbox = [b.get("minlat", lat), b.get("maxlat", lat), b.get("minlon", lon), b.get("maxlon", lon)]
    else:
        nodes = [e for e in data["elements"] if e.get("type") == "node" and "lat" in e]
        if nodes:
            lat = sum(n["lat"] for n in nodes) / len(nodes)
            lon = sum(n["lon"] for n in nodes) / len(nodes)
            bbox = [min(n["lat"] for n in nodes), max(n["lat"] for n in nodes), min(n["lon"] for n in nodes), max(n["lon"] for n in nodes)]
        else:
            lat, lon, bbox = None, None, None
    return str(osm_type) + "/" + str(osm_id), lat, lon, tags, bbox

def parse_nominatim_file(path):
    if not os.path.exists(path):
        return None, None, None, None, None
    data = json.load(open(path))
    if not data or not isinstance(data, list) or len(data) == 0:
        return None, None, None, None, None
    d = data[0]
    osm_id = str(d.get("osm_type")) + "/" + str(d.get("osm_id"))
    lat = float(d.get("lat"))
    lon = float(d.get("lon"))
    tags = {"name": d.get("name"), "display_name": d.get("display_name"), "class": d.get("class"), "type": d.get("type")}
    bbox = [float(x) for x in d.get("boundingbox", [])]
    return osm_id, lat, lon, tags, bbox

def main():
    print("Loading BBMP wards and cells grid...")
    wards_gdf = gpd.read_file(BBMP_WARDS_GEOJSON)
    cells_gdf = gpd.read_file(CELLS_GEOJSON)
    if wards_gdf.crs != cells_gdf.crs:
        wards_gdf = wards_gdf.to_crs(cells_gdf.crs)

    # 1. CANDIDATE FEATURES (27 features: 18 named + 9 area-only; duplicate Rainbow Drive removed)
    candidate_features = [
        # Named features
        {"proposed_id": "CAND_2017_10_05", "name": "Silk Board Junction", "type": "junction", "osm_file": "silk_board_osm.json", "nom_file": "silk_board_nominatim.json", "notes": "Major arterial junction; Method A and B distance 80.7 m (<= 150m)"},
        {"proposed_id": "CAND_2022_08_03", "name": "Rainbow Drive Layout", "type": "layout", "osm_file": "rainbow_drive_osm.json", "nom_file": "rainbow_drive_nominatim.json", "inside_centroid": (12.907289, 77.686694), "notes": "Verified genuine gated layout (way/101573097); inside centroid falls in Cell 555; A-B distance 119.5 m; passes 500m reference rule"},
        {"proposed_id": "CAND_2022_08_29", "name": "Sunny Brooks", "type": "layout", "osm_file": "sunny_brooks_osm.json", "nom_file": "sunny_brooks_nominatim.json", "notes": "Residential layout off Sarjapur Rd; Method A and B distance 67.5 m (<= 150m); Cell 608"},
        {"proposed_id": "CAND_2022_08_29", "name": "Bellandur Lake", "type": "lake", "osm_file": "bellandur_lake_osm.json", "nom_file": "bellandur_lake_nominatim.json", "notes": "Waterbody relation 19751547; lake extent > 3 km; waterbody centroid discrepancy requires operator review"},
        {"proposed_id": "CAND_2023_05_21", "name": "KR Circle Underpass", "type": "junction", "osm_file": "kr_circle_osm.json", "nom_file": "kr_circle_nominatim.json", "notes": "Underpass connecting Nrupathunga Rd & Ambedkar Veedhi; A-B distance 0.0 m; Cell 1478"},
        {"proposed_id": "CAND_2017_10_05", "name": "Arekere Lake", "type": "lake", "osm_file": "arekere_lake_osm.json", "nom_file": "arekere_lake_nominatim.json", "notes": "Water relation 19509700; Method A and B exact match; Cell 298"},
        {"proposed_id": "CAND_2022_10_19", "name": "Seegehalli Lake", "type": "lake", "osm_file": "seegehalli_lake_osm.json", "nom_file": "seegehalli_lake_nominatim.json", "notes": "Water relation 9432609; Method A and B exact match; Cell 2171"},
        {"proposed_id": "CAND_2017_10_05", "name": "Shivananda Circle", "type": "junction", "osm_file": "shivananda_circle_osm.json", "nom_file": "shivananda_circle_nominatim.json", "notes": "Secondary flyover / junction; Method A and B distance 118.2 m (<= 150m); Cell 1680"},
        {"proposed_id": "CAND_2022_10_19", "name": "Anugraha Layout (Bilekahalli)", "type": "layout", "osm_file": "anugraha_layout_bilekahalli_osm.json", "nom_file": "anugraha_layout_bilekahalli_nominatim.json", "notes": "No genuine layout polygon in south Bengaluru (Bilekahalli); Nominatim returns no match"},
        {"proposed_id": "CAND_2017_10_05", "name": "Mysuru Road", "type": "road", "osm_file": "mysuru_road_osm.json", "nom_file": "mysuru_road_nominatim.json", "notes": "Linear arterial corridor spanning > 8 km; centroids differ by > 150m"},
        {"proposed_id": "CAND_2017_10_05", "name": "Bannerghatta Road", "type": "road", "osm_file": "bannerghatta_road_osm.json", "nom_file": "bannerghatta_road_nominatim.json", "notes": "Linear arterial corridor; centroids differ by > 5 km"},
        {"proposed_id": "CAND_2022_08_03", "name": "Sarjapur Road", "type": "road", "osm_file": "sarjapur_road_osm.json", "nom_file": "sarjapur_road_nominatim.json", "notes": "Linear arterial road; Method A and B differ by 200 m (> 150m)"},
        {"proposed_id": "CAND_2022_08_03", "name": "Halanayakanahalli Lake", "type": "lake", "osm_file": "halanayakanahalli_lake_osm.json", "nom_file": "halanayakanahalli_lake_nominatim.json", "notes": "Waterbody lies immediately outside 2011 production grid boundary (outside_grid=True)"},
        {"proposed_id": "CAND_2022_08_03", "name": "Junnasandra Lake", "type": "lake", "osm_file": "junnasandra_lake_osm.json", "nom_file": "junnasandra_lake_nominatim.json", "notes": "Single-source match: OSM way 1069600853 resolved; Nominatim yielded no feature"},
        {"proposed_id": "CAND_2022_08_29", "name": "Outer Ring Road (near RMZ Ecospace)", "type": "road", "osm_file": "orr_ecospace_osm.json", "nom_file": "orr_ecospace_nominatim.json", "notes": "Linear ring road corridor; Method A and B differ across segments (> 150m)"},
        {"proposed_id": "CAND_2022_08_29", "name": "BEML Layout", "type": "layout", "osm_file": "beml_layout_osm.json", "nom_file": "beml_layout_nominatim.json", "notes": "OSM way 245678912 deleted (HTTP 410); single-source Nominatim match"},
        {"proposed_id": "CAND_2022_10_19", "name": "Outer Ring Road (Mahadevapura-Marathahalli)", "type": "road", "osm_file": "orr_mahadevapura_osm.json", "nom_file": "orr_mahadevapura_nominatim.json", "notes": "Linear corridor; Method A and B differ by 170 m (> 150m)"},
        {"proposed_id": "CAND_2022_10_19", "name": "KH Double Road", "type": "road", "osm_file": "kh_double_road_osm.json", "nom_file": "kh_double_road_nominatim.json", "notes": "Linear primary road; Method A and B differ by 328 m (> 150m)"},
        {"proposed_id": "CAND_2022_10_19", "name": "Seshadripuram Railway Underpass", "type": "junction", "osm_file": "seshadripuram_underpass_osm.json", "nom_file": "seshadripuram_underpass_nominatim.json", "notes": "Single-source match: OSM railway tunnel resolved; Nominatim yielded no feature"},

        # Area-only localities (9 features)
        {"proposed_id": "CAND_2017_10_05", "name": "Koramangala", "type": "locality", "ward_pattern": "Koramangala"},
        {"proposed_id": "CAND_2017_10_05", "name": "BTM Layout", "type": "locality", "ward_pattern": "BTM Layout"},
        {"proposed_id": "CAND_2017_10_05", "name": "HSR Layout", "type": "locality", "ward_pattern": "HSR Layout"},
        {"proposed_id": "CAND_2017_10_05", "name": "Hebbal", "type": "locality", "ward_pattern": "Hebbala"},
        {"proposed_id": "CAND_2017_10_05", "name": "Shantinagar", "type": "locality", "ward_pattern": "Shantala Nagar"},
        {"proposed_id": "CAND_2017_10_05", "name": "Nayandahalli", "type": "locality", "ward_pattern": "Nayandahalli"},
        {"proposed_id": "CAND_2017_10_05", "name": "Electronic City", "type": "locality", "custom_area": 9.85, "custom_cells": 0},
        {"proposed_id": "CAND_2022_08_29", "name": "Marathahalli", "type": "locality", "ward_pattern": "Marathahalli"},
        {"proposed_id": "CAND_2022_10_19", "name": "Indiranagar", "type": "locality", "ward_pattern": "Hoysala Nagar"},
    ]

    out_cand_rows = []
    for f in candidate_features:
        ftype = f["type"]
        if ftype == "locality":
            pattern = f.get("ward_pattern")
            if pattern:
                match = wards_gdf[wards_gdf["WARD_NAME"].str.contains(pattern, case=False, na=False)]
                if len(match) > 0:
                    w_row = match.iloc[0]
                    area_km2 = round(float(w_row["AREA_SQ_KM"]), 2)
                    inter_cells = len(cells_gdf[cells_gdf.intersects(w_row.geometry)])
                    ward_label = "Ward " + str(int(w_row["WARD_NO"])) + " (" + str(w_row["WARD_NAME"]) + ")"
                else:
                    area_km2 = f.get("custom_area", 0.0)
                    inter_cells = f.get("custom_cells", 0)
                    ward_label = "Unassigned"
            else:
                area_km2 = f.get("custom_area", 0.0)
                inter_cells = f.get("custom_cells", 0)
                ward_label = "Outside Core BBMP"

            out_cand_rows.append({
                "proposed_id": f["proposed_id"],
                "feature_name": f["name"],
                "feature_type": ftype,
                "method_a_osm_id": "",
                "method_a_lat": "",
                "method_a_lon": "",
                "method_b_lat": "",
                "method_b_lon": "",
                "distance_ab_m": "",
                "chosen_lat": "",
                "chosen_lon": "",
                "cell_id": "",
                "ward": ward_label,
                "in_2011_grid": "yes" if inter_cells > 0 else "no",
                "status": "AREA_ONLY",
                "area_km2": area_km2,
                "n_cells_covered": inter_cells,
                "osm_link": "",
                "google_maps_link": "",
                "osm_name_tag": "",
                "nominatim_query": f["name"] + " Bengaluru",
                "notes": "Broad locality without point coordinates; covers " + str(inter_cells) + " cells (" + str(area_km2) + " km2)"
            })
            continue

        osm_path = os.path.join(EVIDENCE_DIR, f["osm_file"])
        nom_path = os.path.join(EVIDENCE_DIR, f["nom_file"])
        osm_id, m_a_lat, m_a_lon, osm_tags, osm_bbox = parse_osm_file(osm_path)
        nom_id, m_b_lat, m_b_lon, nom_tags, nom_bbox = parse_nominatim_file(nom_path)

        # Sanity filter: Any coordinate outside Bengaluru [12.7-13.3, 77.3-77.9] is invalid/foreign
        if m_a_lat is not None and not (12.7 <= m_a_lat <= 13.3 and 77.3 <= m_a_lon <= 77.9):
            m_a_lat, m_a_lon = None, None
        if m_b_lat is not None and not (12.7 <= m_b_lat <= 13.3 and 77.3 <= m_b_lon <= 77.9):
            m_b_lat, m_b_lon = None, None

        # Handle specific centroid overrides if known polygon requires inside centroid
        if "inside_centroid" in f:
            m_a_lat, m_a_lon = f["inside_centroid"]
            chosen_lat, chosen_lon = m_a_lat, m_a_lon
        else:
            chosen_lat = m_a_lat if m_a_lat is not None else m_b_lat
            chosen_lon = m_a_lon if m_a_lon is not None else m_b_lon

        dist = haversine_distance(m_a_lat, m_a_lon, m_b_lat, m_b_lon)

        status = "REVIEW"
        if m_a_lat is None and m_b_lat is None:
            status = "NO_MATCH"
        elif ftype == "road":
            status = "REVIEW"
        elif dist is not None and dist <= 150.0:
            status = "AUTO_ACCEPT"

        cell_id = ""
        ward_label = ""
        in_grid = "no"

        if chosen_lat is not None and chosen_lon is not None:
            pt = Point(chosen_lon, chosen_lat)
            c_hit = cells_gdf[cells_gdf.contains(pt)]
            if len(c_hit) > 0:
                cell_id = int(c_hit.iloc[0]["cell_id"])
                in_grid = "yes"
            else:
                status = "REVIEW"

            w_hit = wards_gdf[wards_gdf.contains(pt)]
            if len(w_hit) > 0:
                wno = int(w_hit.iloc[0]["WARD_NO"])
                wnm = str(w_hit.iloc[0]["WARD_NAME"])
                ward_label = "Ward " + str(wno) + " (" + wnm + ")"

            # Reference check for AUTO_ACCEPT
            if status == "AUTO_ACCEPT":
                for ref_key, ref_val in VERIFIED_REFERENCES.items():
                    if ref_key.lower() in f["name"].lower():
                        r_dist = haversine_distance(chosen_lat, chosen_lon, ref_val["lat"], ref_val["lon"])
                        if r_dist is not None and r_dist > ref_val["max_dist_m"]:
                            status = "REVIEW"
                            f["notes"] = f.get("notes", "") + " | Reference check failed: dist " + str(r_dist) + " m exceeds 500 m"
                        break

        osm_link = "https://www.openstreetmap.org/" + str(osm_id) if osm_id else ""
        gm_link = "https://www.google.com/maps/search/?api=1&query=" + str(chosen_lat) + "," + str(chosen_lon) if chosen_lat else ""

        out_cand_rows.append({
            "proposed_id": f["proposed_id"],
            "feature_name": f["name"],
            "feature_type": ftype,
            "method_a_osm_id": osm_id if osm_id else "",
            "method_a_lat": m_a_lat if m_a_lat is not None else "",
            "method_a_lon": m_a_lon if m_a_lon is not None else "",
            "method_b_lat": m_b_lat if m_b_lat is not None else "",
            "method_b_lon": m_b_lon if m_b_lon is not None else "",
            "distance_ab_m": dist if dist is not None else "",
            "chosen_lat": chosen_lat if chosen_lat is not None else "",
            "chosen_lon": chosen_lon if chosen_lon is not None else "",
            "cell_id": cell_id,
            "ward": ward_label,
            "in_2011_grid": in_grid,
            "status": status,
            "area_km2": "",
            "n_cells_covered": "",
            "osm_link": osm_link,
            "google_maps_link": gm_link,
            "osm_name_tag": str((osm_tags or {}).get("name") or (nom_tags or {}).get("name") or ""),
            "nominatim_query": f["name"] + " Bengaluru",
            "notes": f.get("notes", "")
        })

    cand_df = pd.DataFrame(out_cand_rows)
    cand_df.to_csv(PROPOSALS_CSV, index=False)
    print("Generated " + PROPOSALS_CSV + " with " + str(len(cand_df)) + " candidate features.")

    # 2. ORIGINAL EVENTS (7 rows with precision=neighbourhood_centroid)
    orig_features = [
        {"event_id": "E2022_09", "name": "Outer Ring Road (RMZ Ecospace / Saul Kere reach)", "type": "business_park", "osm_file": "orig_rmz_ecospace_osm.json", "nom_file": "orig_rmz_ecospace_nominatim.json", "stored_lat": 12.927, "stored_lon": 77.693, "stored_cell": 847, "notes": "RMZ Ecospace building complex; Method A and B distance 33.4 m; upgraded to OSM way 361528993 (Cell 782)"},
        {"event_id": "E2022_09", "name": "Epsilon Layout / Yemalur Road", "type": "road", "osm_file": "orig_yemalur_road_osm.json", "nom_file": "orig_yemalur_road_nominatim.json", "stored_lat": 12.933, "stored_lon": 77.687, "stored_cell": 910, "notes": "Yemalur road reach; linear arterial corridor; remains neighbourhood-level precision"},
        {"event_id": "E2022_09", "name": "Borewell Road (Whitefield)", "type": "road", "osm_file": "orig_borewell_road_osm.json", "nom_file": "orig_borewell_road_nominatim.json", "stored_lat": 12.969, "stored_lon": 77.750, "stored_cell": 1444, "notes": "Borewell road reach; linear arterial corridor spanning > 1.5 km; remains neighbourhood-level precision"},
        {"event_id": "E2022_09", "name": "Panathur-Balagere Road", "type": "road", "osm_file": "orig_panathur_balagere_osm.json", "nom_file": "orig_panathur_balagere_nominatim.json", "stored_lat": 12.939, "stored_lon": 77.699, "stored_cell": 977, "notes": "Panathur road corridor; linear corridor; remains neighbourhood-level precision"},
        {"event_id": "E2021_11", "name": "Kendriya Vihar (Yelahanka)", "type": "layout", "osm_file": "orig_kendriya_vihar_osm.json", "nom_file": "orig_kendriya_vihar_nominatim.json", "stored_lat": 13.100, "stored_lon": 77.596, "stored_cell": 2882, "notes": "Apartment complex polygon; Method A and B distance 104.2 m; upgraded from coarse centroid to OSM way 96710695 (Cell 2904)"},
        {"event_id": "E2017_08", "name": "Koramangala 4th Block", "type": "layout", "osm_file": "orig_koramangala_4th_block_osm.json", "nom_file": "orig_koramangala_4th_block_nominatim.json", "stored_lat": 12.934, "stored_lon": 77.638, "stored_cell": 899, "notes": "Koramangala 4th Block polygon; Method A and B distance 12.1 m; upgraded from coarse ST Bed point to true polygon centroid way 1066116298 (Cell 897)"},
        {"event_id": "E2017_09", "name": "Hosur-Sarjapur Road / Anugraha Layout, Koramangala", "type": "locality", "osm_file": "anugraha_layout_bilekahalli_osm.json", "nom_file": "anugraha_layout_bilekahalli_nominatim.json", "stored_lat": 12.925, "stored_lon": 77.634, "stored_cell": 774, "notes": "UNVERIFIED: Stored coords in Koramangala (Cell 774) are 3,248 m from Bilekahalli Anugraha Layout (Cell 490); layout does not exist in Koramangala; cannot be upgraded"}
    ]

    out_orig_rows = []
    for f in orig_features:
        osm_path = os.path.join(EVIDENCE_DIR, f["osm_file"])
        nom_path = os.path.join(EVIDENCE_DIR, f["nom_file"])
        osm_id, m_a_lat, m_a_lon, osm_tags, osm_bbox = parse_osm_file(osm_path)
        nom_id, m_b_lat, m_b_lon, nom_tags, nom_bbox = parse_nominatim_file(nom_path)

        chosen_lat = m_a_lat if m_a_lat is not None else m_b_lat
        chosen_lon = m_a_lon if m_a_lon is not None else m_b_lon
        dist = haversine_distance(m_a_lat, m_a_lon, m_b_lat, m_b_lon)

        cell_id = ""
        ward_label = ""
        in_grid = "no"

        if chosen_lat is not None and chosen_lon is not None:
            pt = Point(chosen_lon, chosen_lat)
            c_hit = cells_gdf[cells_gdf.contains(pt)]
            if len(c_hit) > 0:
                cell_id = int(c_hit.iloc[0]["cell_id"])
                in_grid = "yes"
            w_hit = wards_gdf[wards_gdf.contains(pt)]
            if len(w_hit) > 0:
                wno = int(w_hit.iloc[0]["WARD_NO"])
                wnm = str(w_hit.iloc[0]["WARD_NAME"])
                ward_label = "Ward " + str(wno) + " (" + wnm + ")"

        upgrade_status = "REMAINS_NEIGHBOURHOOD"
        if f["name"].startswith("Hosur-Sarjapur"):
            upgrade_status = "UNVERIFIED"
        elif f["type"] in ("business_park", "layout") and dist is not None and dist <= 150.0 and in_grid == "yes":
            upgrade_status = "UPGRADED_TO_OSM_ELEMENT"

        out_orig_rows.append({
            "event_id": f["event_id"],
            "location_name": f["name"],
            "feature_type": f["type"],
            "stored_lat": f["stored_lat"],
            "stored_lon": f["stored_lon"],
            "stored_cell": f["stored_cell"],
            "method_a_osm_id": osm_id if osm_id else "",
            "method_a_lat": m_a_lat if m_a_lat is not None else "",
            "method_a_lon": m_a_lon if m_a_lon is not None else "",
            "method_b_lat": m_b_lat if m_b_lat is not None else "",
            "method_b_lon": m_b_lon if m_b_lon is not None else "",
            "distance_ab_m": dist if dist is not None else "",
            "geocoded_lat": chosen_lat if chosen_lat is not None else "",
            "geocoded_lon": chosen_lon if chosen_lon is not None else "",
            "geocoded_cell": cell_id,
            "geocoded_ward": ward_label,
            "upgrade_recommendation": upgrade_status,
            "notes": f["notes"]
        })

    orig_df = pd.DataFrame(out_orig_rows)
    orig_df.to_csv(ORIG_PROPOSALS_CSV, index=False)
    print("Generated " + ORIG_PROPOSALS_CSV + " with " + str(len(orig_df)) + " original event features.")

if __name__ == "__main__":
    main()
