"""pipeline/geocode_proposals.py

Geocodes candidate features strictly via live Overpass API (Method A)
and structured Nominatim API (Method B).
Classifies into AUTO_ACCEPT (<=150m, in grid), REVIEW, or NO_MATCH.
Assigns cell_id and ward via point-in-polygon from data/interim/cells_grid.csv
and data/raw/bbmp_wards_198.geojson.
Generates:
1. data/interim/events_geocode_proposals.csv
2. reports/geocode_review.html
"""

import os
import time
import math
import json
import urllib.request
import urllib.parse
import pandas as pd
import geopandas as gpd
from shapely.geometry import Point, shape

BBMP_WARDS_GEOJSON = "data/raw/bbmp_wards_198.geojson"
CELLS_GRID_CSV = "data/interim/cells_grid.csv"
PROPOSALS_CSV = "data/interim/events_geocode_proposals.csv"
REVIEW_HTML = "reports/geocode_review.html"

# Bengaluru Bounding Box: [min_lat, min_lon, max_lat, max_lon]
BBOX = (12.80, 77.40, 13.20, 77.80)

HEADERS = {
    "User-Agent": "N2MBengaluruFloodAudit/2.0 (student.research.audit@gmail.com)"
}

def haversine_distance(lat1, lon1, lat2, lon2):
    """Calculate great-circle distance between two points in metres."""
    if any(v is None or math.isnan(v) for v in [lat1, lon1, lat2, lon2]):
        return None
    R = 6371000.0  # Earth radius in metres
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    delta_phi = math.radians(lat2 - lat1)
    delta_lambda = math.radians(lon2 - lon1)
    a = math.sin(delta_phi / 2.0)**2 + math.cos(phi1) * math.cos(phi2) * math.sin(delta_lambda / 2.0)**2
    c = 2.0 * math.atan2(math.sqrt(a), math.sqrt(1.0 - a))
    return R * c

def query_overpass(query_str):
    """Query Overpass API and return JSON elements."""
    overpass_urls = [
        "https://overpass-api.de/api/interpreter",
        "https://maps.mail.ru/osm/tools/overpass/api/interpreter",
        "https://overpass.kumi.systems/api/interpreter"
    ]
    data = urllib.parse.urlencode({"data": query_str}).encode("utf-8")
    for url in overpass_urls:
        try:
            req = urllib.request.Request(url, data=data, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=15) as resp:
                if resp.status == 200:
                    res = json.loads(resp.read().decode("utf-8"))
                    return res.get("elements", [])
        except Exception as e:
            print(f"Overpass failed on {url}: {e}")
            time.sleep(1)
    return []

def query_nominatim_structured(params):
    """Query Nominatim with structured parameters."""
    base_url = "https://nominatim.openstreetmap.org/search?"
    query_params = {
        "format": "json",
        "addressdetails": "1",
        "limit": "1",
        "country": "India",
        "state": "Karnataka",
        "city": "Bengaluru"
    }
    query_params.update(params)
    url = base_url + urllib.parse.urlencode(query_params)
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as resp:
            if resp.status == 200:
                res = json.loads(resp.read().decode("utf-8"))
                if res and len(res) > 0:
                    return res[0]
    except Exception as e:
        print(f"Nominatim query failed for {params}: {e}")
    return None

def main():
    print("Loading BBMP wards and cells grid...")
    wards_gdf = gpd.read_file(BBMP_WARDS_GEOJSON)
    if wards_gdf.crs != "EPSG:4326":
        wards_gdf = wards_gdf.to_crs("EPSG:4326")
    
    cells_df = pd.read_csv(CELLS_GRID_CSV)
    
    # Candidate features literally named in saved source texts
    features_to_geocode = [
        # CAND_2017_10_05
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "Silk Board Junction",
            "type": "junction",
            "source_sentence": "Mysuru Road and Silk Board Junction are also flooded as per recent reports.",
            "overpass": """[out:json][timeout:15];
(
  node["highway"~"traffic_signals|motorway_junction|junction"]["name"~"Silk Board",i](12.85,77.55,12.98,77.68);
  node["junction"="roundabout"]["name"~"Silk Board",i](12.85,77.55,12.98,77.68);
  node["name"~"Central Silk Board",i](12.90,77.60,12.93,77.64);
);
out body 1;""",
            "nominatim": {"street": "Central Silk Board Junction"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "Arekera Lake",
            "type": "lake",
            "source_sentence": "The Arekera Lake is overflowing and all roads in the Koramangala, BMT Layout...",
            "overpass": """[out:json][timeout:15];
(
  relation["natural"="water"]["name"~"Arakere|Arekere",i](12.85,77.55,12.92,77.62);
  way["natural"="water"]["name"~"Arakere|Arekere",i](12.85,77.55,12.92,77.62);
);
out center 1;""",
            "nominatim": {"amenity": "Arekere Lake", "county": "Bangalore South"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "Koramangala",
            "type": "layout",
            "source_sentence": "all roads in the Koramangala, BMT Layout, HSR Layout, Hebbal, Shantinagar... have reported flooding",
            "overpass": """[out:json][timeout:15];
(
  relation["boundary"="administrative"]["name"="Koramangala",i](12.90,77.60,12.96,77.66);
  node["place"="suburb"]["name"="Koramangala",i](12.90,77.60,12.96,77.66);
);
out center 1;""",
            "nominatim": {"suburb": "Koramangala"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "HSR Layout",
            "type": "layout",
            "source_sentence": "all roads in the Koramangala, BMT Layout, HSR Layout, Hebbal... have reported flooding",
            "overpass": """[out:json][timeout:15];
(
  relation["boundary"="administrative"]["name"~"HSR Layout",i](12.88,77.61,12.93,77.67);
  node["place"="suburb"]["name"~"HSR Layout",i](12.88,77.61,12.93,77.67);
);
out center 1;""",
            "nominatim": {"suburb": "HSR Layout"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "BTM Layout",
            "type": "layout",
            "source_sentence": "Electronic City, BTM layout, Koramangala, Shantinagar, Madiwala... have reportedly been water-logged",
            "overpass": """[out:json][timeout:15];
(
  relation["boundary"="administrative"]["name"~"BTM Layout",i](12.88,77.58,12.94,77.64);
  node["place"="suburb"]["name"~"BTM Layout",i](12.88,77.58,12.94,77.64);
);
out center 1;""",
            "nominatim": {"suburb": "BTM Layout"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "Electronic City",
            "type": "layout",
            "source_sentence": "Electronic City, BTM layout, Koramangala, Shantinagar, Madiwala... have reportedly been water-logged",
            "overpass": """[out:json][timeout:15];
(
  relation["boundary"="administrative"]["name"~"Electronics City|Electronic City",i](12.80,77.64,12.88,77.70);
  node["place"~"suburb|town"]["name"~"Electronic City",i](12.80,77.64,12.88,77.70);
);
out center 1;""",
            "nominatim": {"suburb": "Electronic City"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "Shantinagar",
            "type": "layout",
            "source_sentence": "Electronic City, BTM layout, Koramangala, Shantinagar, Madiwala... have reportedly been water-logged",
            "overpass": """[out:json][timeout:15];
(
  relation["boundary"="administrative"]["name"="Shanti Nagar",i](12.94,77.57,12.98,77.62);
  node["place"="suburb"]["name"~"Shanti Nagar|Shantinagar",i](12.94,77.57,12.98,77.62);
);
out center 1;""",
            "nominatim": {"suburb": "Shanti Nagar"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "Nayandahalli",
            "type": "layout",
            "source_sentence": "Electronic City, BTM layout, Koramangala, Shantinagar, Madiwala. Nayandahalli... water-logged",
            "overpass": """[out:json][timeout:15];
(
  relation["boundary"="administrative"]["name"~"Nayandahalli",i](12.92,77.50,12.96,77.55);
  node["place"="suburb"]["name"~"Nayandahalli",i](12.92,77.50,12.96,77.55);
);
out center 1;""",
            "nominatim": {"suburb": "Nayandahalli"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "Mysuru Road",
            "type": "road",
            "source_sentence": "Mysuru Road and Silk Board Junction are also flooded as per recent reports.",
            "overpass": """[out:json][timeout:15];
way["highway"]["name"~"Mysore Road|Mysuru Road",i](12.92,77.50,12.96,77.56);
out center 1;""",
            "nominatim": {"street": "Mysore Road"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "Bannerghatta Road",
            "type": "road",
            "source_sentence": "Nikhil Vijayapura, a regular commuter along the Bannerghatta road stated that a journey from his office...",
            "overpass": """[out:json][timeout:15];
way["highway"]["name"~"Bannerghatta Road|Bannerghatta Main Road",i](12.87,77.58,12.93,77.61);
out center 1;""",
            "nominatim": {"street": "Bannerghatta Main Road"}
        },
        {
            "proposed_id": "CAND_2017_10_05",
            "feature_name": "Shivananda Circle",
            "type": "junction",
            "source_sentence": "Vehicles have been stranded on either sides of the road for about 4 hours at the underpass on Shivananda Circle",
            "overpass": """[out:json][timeout:15];
(
  node["name"~"Shivananda Circle",i](12.97,77.56,13.01,77.60);
  node["junction"]["name"~"Shivananda",i](12.97,77.56,13.01,77.60);
);
out body 1;""",
            "nominatim": {"street": "Shivananda Circle"}
        },

        # CAND_2022_08_03
        {
            "proposed_id": "CAND_2022_08_03",
            "feature_name": "Rainbow Drive Layout",
            "type": "layout",
            "source_sentence": "The torrential rainfall on the intervening night of Tuesday and Wednesday filled the 300-metre stretch with at least three-feet of water.",
            "overpass": """[out:json][timeout:15];
(
  way["landuse"="residential"]["name"~"Rainbow Drive",i](12.88,77.69,12.93,77.74);
  node["place"~"neighbourhood|suburb"]["name"~"Rainbow Drive",i](12.88,77.69,12.93,77.74);
  way["highway"]["name"~"Rainbow Drive",i](12.88,77.69,12.93,77.74);
);
out center 1;""",
            "nominatim": {"street": "Rainbow Drive"}
        },
        {
            "proposed_id": "CAND_2022_08_03",
            "feature_name": "Sarjapur Road",
            "type": "road",
            "source_sentence": "Rainbow Drive Layout in Bengaluru’s Sarjapur, was also affected in the downpour and as a result, the streets of the layout were flooded",
            "overpass": """[out:json][timeout:15];
way["highway"]["name"~"Sarjapur Road|Sarjapur Main Road",i](12.90,77.65,12.93,77.72);
out center 1;""",
            "nominatim": {"street": "Sarjapur Main Road"}
        },
        {
            "proposed_id": "CAND_2022_08_03",
            "feature_name": "Halanayakanahalli Lake",
            "type": "lake",
            "source_sentence": "water is still flowing into Rainbow Drive because two lakes — Halanayakanahalli and Junnnasandra — are overflowing",
            "overpass": """[out:json][timeout:15];
(
  relation["natural"="water"]["name"~"Halanayakanahalli",i](12.88,77.67,12.93,77.72);
  way["natural"="water"]["name"~"Halanayakanahalli",i](12.88,77.67,12.93,77.72);
);
out center 1;""",
            "nominatim": {"amenity": "Halanayakanahalli Lake"}
        },
        {
            "proposed_id": "CAND_2022_08_03",
            "feature_name": "Junnasandra Lake",
            "type": "lake",
            "source_sentence": "water is still flowing into Rainbow Drive because two lakes — Halanayakanahalli and Junnnasandra — are overflowing",
            "overpass": """[out:json][timeout:15];
(
  relation["natural"="water"]["name"~"Junnasandra",i](12.88,77.66,12.93,77.71);
  way["natural"="water"]["name"~"Junnasandra",i](12.88,77.66,12.93,77.71);
);
out center 1;""",
            "nominatim": {"amenity": "Junnasandra Lake"}
        },

        # CAND_2022_08_29
        {
            "proposed_id": "CAND_2022_08_29",
            "feature_name": "Rainbow Drive Layout",
            "type": "layout",
            "source_sentence": "On 30th August, a resident of Rainbow Drive, a layout on Sarjapur Road, passed away as he could not get to a hospital in time.",
            "overpass": """[out:json][timeout:15];
(
  way["landuse"="residential"]["name"~"Rainbow Drive",i](12.88,77.69,12.93,77.74);
  node["place"~"neighbourhood|suburb"]["name"~"Rainbow Drive",i](12.88,77.69,12.93,77.74);
);
out center 1;""",
            "nominatim": {"street": "Rainbow Drive"}
        },
        {
            "proposed_id": "CAND_2022_08_29",
            "feature_name": "Sunny Brooks",
            "type": "layout",
            "source_sentence": "Visuals from Sunny Brooks layout area showed trees, shops and houses partially submerged in rain water.",
            "overpass": """[out:json][timeout:15];
(
  way["landuse"="residential"]["name"~"Sunny Brooks",i](12.89,77.68,12.93,77.73);
  node["name"~"Sunny Brooks",i](12.89,77.68,12.93,77.73);
);
out center 1;""",
            "nominatim": {"street": "Sunny Brooks Community"}
        },
        {
            "proposed_id": "CAND_2022_08_29",
            "feature_name": "Outer Ring Road (near RMZ Ecospace)",
            "type": "road",
            "source_sentence": "ORR Bellandur near Eco Space saw major flooding as rainwater overflowed from stormwater drains onto the street.",
            "overpass": """[out:json][timeout:15];
way["highway"]["name"~"Outer Ring Road",i](12.91,77.67,12.94,77.70);
out center 1;""",
            "nominatim": {"street": "Outer Ring Road", "suburb": "Bellandur"}
        },
        {
            "proposed_id": "CAND_2022_08_29",
            "feature_name": "Bellandur Lake",
            "type": "lake",
            "source_sentence": "In Bellandur too, it was reported that the Bellandur lake overflowed and water gushed onto the streets",
            "overpass": """[out:json][timeout:15];
(
  relation["natural"="water"]["name"~"Bellandur",i](12.91,77.64,12.96,77.69);
  way["natural"="water"]["name"~"Bellandur",i](12.91,77.64,12.96,77.69);
);
out center 1;""",
            "nominatim": {"amenity": "Bellandur Lake"}
        },
        {
            "proposed_id": "CAND_2022_08_29",
            "feature_name": "BEML Layout",
            "type": "layout",
            "source_sentence": "In the Thubrahalli Palaya area near BEML Layout, multiple tin shed houses were submerged in around 3 feet of rainwater",
            "overpass": """[out:json][timeout:15];
(
  relation["boundary"="administrative"]["name"~"BEML Layout",i](12.95,77.70,12.99,77.74);
  node["place"="suburb"]["name"~"BEML Layout",i](12.95,77.70,12.99,77.74);
);
out center 1;""",
            "nominatim": {"suburb": "BEML Layout"}
        },

        # CAND_2022_10_19
        {
            "proposed_id": "CAND_2022_10_19",
            "feature_name": "Seegehalli Lake / Gauge",
            "type": "lake",
            "source_sentence": "Seegehalli received 81.5 mm of rainfall on Wenesday, October 19, while Doddabanahalli received 78 mm.",
            "overpass": """[out:json][timeout:15];
(
  relation["natural"="water"]["name"~"Seegehalli",i](12.98,77.72,13.04,77.77);
  way["natural"="water"]["name"~"Seegehalli",i](12.98,77.72,13.04,77.77);
);
out center 1;""",
            "nominatim": {"amenity": "Seegehalli Lake"}
        },
        {
            "proposed_id": "CAND_2022_10_19",
            "feature_name": "Seshadripuram Railway Underpass",
            "type": "junction",
            "source_sentence": "BBMP control room received complaints of waterlogging from the railway underpass near Seshadripuram",
            "overpass": """[out:json][timeout:15];
(
  node["name"~"Seshadripuram",i]["railway"](12.97,77.56,13.00,77.59);
  way["highway"]["name"~"Seshadripuram",i](12.97,77.56,13.00,77.59);
  node["place"="suburb"]["name"~"Seshadripuram",i](12.97,77.56,13.00,77.59);
);
out center 1;""",
            "nominatim": {"street": "Seshadripuram Railway Underpass"}
        },
        {
            "proposed_id": "CAND_2022_10_19",
            "feature_name": "Outer Ring Road (Mahadevapura-Marathahalli)",
            "type": "road",
            "source_sentence": "Waterlogging was seen in Outer Ring Road, between Mahadevapura and Marathahalli, Koramangala, Indiranagar",
            "overpass": """[out:json][timeout:15];
way["highway"]["name"~"Outer Ring Road",i](12.94,77.68,12.99,77.72);
out center 1;""",
            "nominatim": {"street": "Outer Ring Road", "suburb": "Mahadevapura"}
        },
        {
            "proposed_id": "CAND_2022_10_19",
            "feature_name": "Indiranagar",
            "type": "layout",
            "source_sentence": "Waterlogging was seen in Outer Ring Road, between Mahadevapura and Marathahalli, Koramangala, Indiranagar",
            "overpass": """[out:json][timeout:15];
(
  relation["boundary"="administrative"]["name"="Indiranagar",i](12.96,77.62,13.00,77.66);
  node["place"="suburb"]["name"="Indiranagar",i](12.96,77.62,13.00,77.66);
);
out center 1;""",
            "nominatim": {"suburb": "Indiranagar"}
        },
        {
            "proposed_id": "CAND_2022_10_19",
            "feature_name": "KH Double Road",
            "type": "road",
            "source_sentence": "Waterlogging was seen in Outer Ring Road... and KH (Double) Road among other areas",
            "overpass": """[out:json][timeout:15];
way["highway"]["name"~"Kengal Hanumanthaiah|KH Road|Double Road",i](12.94,77.58,12.97,77.61);
out center 1;""",
            "nominatim": {"street": "KH Road"}
        },
        {
            "proposed_id": "CAND_2022_10_19",
            "feature_name": "Anugraha Layout (Bommanahalli)",
            "type": "layout",
            "source_sentence": "In Bommanahalli's Anugaha Layout, water entered several houses on the night of 19 October",
            "overpass": """[out:json][timeout:15];
(
  way["landuse"="residential"]["name"~"Anugraha",i](12.89,77.60,12.93,77.64);
  node["name"~"Anugraha Layout",i](12.89,77.60,12.93,77.64);
);
out center 1;""",
            "nominatim": {"street": "Anugraha Layout", "suburb": "Bommanahalli"}
        }
    ]

    results = []

    print(f"Beginning geocoding for {len(features_to_geocode)} candidate features...")
    for idx, item in enumerate(features_to_geocode):
        print(f"\n[{idx+1}/{len(features_to_geocode)}] Geocoding {item['feature_name']} ({item['proposed_id']})...")
        
        # Method A: Overpass
        elements = query_overpass(item["overpass"])
        osm_id = None
        a_lat, a_lon = None, None
        matched_name = None
        
        if elements:
            el = elements[0]
            osm_type = el.get("type", "node")
            osm_num = el.get("id")
            osm_id = f"{osm_type}/{osm_num}"
            tags = el.get("tags", {})
            matched_name = tags.get("name", item["feature_name"])
            
            if "center" in el:
                a_lat, a_lon = el["center"]["lat"], el["center"]["lon"]
            elif "lat" in el and "lon" in el:
                a_lat, a_lon = el["lat"], el["lon"]
            elif "geometry" in el:
                # compute average of geometry nodes
                lats = [pt["lat"] for pt in el["geometry"]]
                lons = [pt["lon"] for pt in el["geometry"]]
                a_lat, a_lon = sum(lats)/len(lats), sum(lons)/len(lons)
            print(f"  Overpass matched: {osm_id} ({matched_name}) -> ({a_lat:.5f}, {a_lon:.5f})")
        else:
            print("  Overpass: No match returned")

        time.sleep(1.0) # Polite pause for Nominatim
        
        # Method B: Structured Nominatim
        nom = query_nominatim_structured(item["nominatim"])
        b_lat, b_lon = None, None
        b_name = None
        if nom:
            b_lat, b_lon = float(nom["lat"]), float(nom["lon"])
            b_name = nom.get("display_name", "")
            print(f"  Nominatim matched: ({b_lat:.5f}, {b_lon:.5f}) -> {b_name[:60]}...")
        else:
            print("  Nominatim: No match returned")

        # Distance calculation
        dist_m = None
        if a_lat is not None and b_lat is not None:
            dist_m = haversine_distance(a_lat, a_lon, b_lat, b_lon)
            print(f"  Distance between Method A & B: {dist_m:.1f} m")

        # Coordinate selection & status determination
        chosen_lat, chosen_lon = None, None
        status = "NO_MATCH"
        note = ""

        if a_lat is not None and b_lat is not None:
            if dist_m <= 150.0:
                chosen_lat, chosen_lon = a_lat, a_lon
                status = "AUTO_ACCEPT"
                note = f"Overpass and Nominatim agree within {dist_m:.1f} m (<=150 m)"
            else:
                chosen_lat, chosen_lon = a_lat, a_lon # default to Overpass exact OSM feature
                status = "REVIEW"
                note = f"Discrepancy: Overpass and Nominatim differ by {dist_m:.1f} m (>150 m)"
        elif a_lat is not None:
            chosen_lat, chosen_lon = a_lat, a_lon
            status = "REVIEW"
            note = "Single source match: Overpass returned OSM feature; Nominatim yielded no structured result"
        elif b_lat is not None:
            chosen_lat, chosen_lon = b_lat, b_lon
            status = "REVIEW"
            note = "Single source match: Nominatim returned coordinate; Overpass query yielded no element"
        else:
            status = "NO_MATCH"
            note = "Neither Overpass nor Nominatim returned a location"

        # Spatial join: Ward and 2011 Grid Cell
        matched_cell_id = None
        matched_ward = None
        in_grid = "no"

        if chosen_lat is not None and chosen_lon is not None:
            pt = Point(chosen_lon, chosen_lat)
            # 1. Ward PIP
            w_matches = wards_gdf[wards_gdf.contains(pt)]
            if not w_matches.empty:
                w_row = w_matches.iloc[0]
                matched_ward = w_row.get("ward_no", w_row.get("ward_id", w_row.get("name", "Unknown")))
                in_grid = "yes"
            else:
                # check boundary buffer (100m)
                w_near = wards_gdf[wards_gdf.distance(pt) < 0.005]
                if not w_near.empty:
                    w_row = w_near.iloc[0]
                    matched_ward = f"Near Ward {w_row.get('ward_no', 'boundary')}"
                    in_grid = "boundary_buffer"

            # 2. Cell ID match (nearest centroid in cells_grid)
            # Find nearest 500m cell
            dists = ((cells_df["lat"] - chosen_lat)**2 + (cells_df["lon"] - chosen_lon)**2)**0.5
            nearest_idx = dists.idxmin()
            min_deg_dist = dists.loc[nearest_idx]
            # 500m is ~0.0045 degrees
            if min_deg_dist < 0.006:
                matched_cell_id = int(cells_df.loc[nearest_idx, "cell_id"])
                if matched_ward is None:
                    matched_ward = str(cells_df.loc[nearest_idx, "ward"])
                in_grid = "yes"

            if in_grid != "yes" and status == "AUTO_ACCEPT":
                status = "REVIEW"
                note += " (Downgraded to REVIEW: feature outside BBMP 2011 grid)"

        osm_link = f"https://www.openstreetmap.org/{osm_id}" if osm_id else ""
        gmaps_link = f"https://www.google.com/maps/search/?api=1&query={chosen_lat},{chosen_lon}" if chosen_lat else ""

        results.append({
            "proposed_id": item["proposed_id"],
            "feature_name": item["feature_name"],
            "method_a_osm_id": osm_id if osm_id else "",
            "method_a_lat": round(a_lat, 6) if a_lat else "",
            "method_a_lon": round(a_lon, 6) if a_lon else "",
            "method_b_lat": round(b_lat, 6) if b_lat else "",
            "method_b_lon": round(b_lon, 6) if b_lon else "",
            "distance_ab_m": round(dist_m, 1) if dist_m is not None else "",
            "chosen_lat": round(chosen_lat, 6) if chosen_lat else "",
            "chosen_lon": round(chosen_lon, 6) if chosen_lon else "",
            "cell_id": matched_cell_id if matched_cell_id is not None else "",
            "ward": matched_ward if matched_ward is not None else "",
            "in_2011_grid": in_grid,
            "status": status,
            "osm_link": osm_link,
            "google_maps_link": gmaps_link,
            "notes": note,
            "source_sentence": item["source_sentence"]
        })

    out_df = pd.DataFrame(results)
    # Save CSV
    os.makedirs(os.path.dirname(PROPOSALS_CSV), exist_ok=True)
    out_df.drop(columns=["source_sentence"]).to_csv(PROPOSALS_CSV, index=False)
    print(f"\nWrote {len(out_df)} proposals to {PROPOSALS_CSV}")

    # Generate HTML Leaflet map
    generate_leaflet_map(out_df, wards_gdf)

def generate_leaflet_map(df, wards_gdf):
    """Generate standalone Leaflet map with colored points and ward polygons."""
    markers = []
    for _, row in df.iterrows():
        if not row["chosen_lat"] or not row["chosen_lon"]:
            continue
        color = "#28a745" if row["status"] == "AUTO_ACCEPT" else ("#ffc107" if row["status"] == "REVIEW" else "#dc3545")
        popup_html = f"""
        <div style='font-family:sans-serif; font-size:12px; max-width:280px;'>
            <b style='font-size:14px;'>{row['feature_name']}</b><br/>
            <span style='color:#666;'>Event: {row['proposed_id']}</span><br/>
            <b>Status:</b> <span style='color:{color}; font-weight:bold;'>{row['status']}</span><br/>
            <b>Cell ID:</b> {row['cell_id']} | <b>Ward:</b> {row['ward']}<br/>
            <b>In 2011 Grid:</b> {row['in_2011_grid']}<br/>
            <b>Method Distance:</b> {row['distance_ab_m']} m<br/>
            <p style='margin:6px 0; font-style:italic; background:#f8f9fa; padding:4px; border-left:2px solid {color};'>
                "{row['source_sentence']}"
            </p>
            <b>Links:</b><br/>
            {"<a href='" + str(row['osm_link']) + "' target='_blank'>OSM Element</a> | " if row['osm_link'] else ""}
            <a href='{row['google_maps_link']}' target='_blank'>Google Maps</a>
        </div>
        """
        markers.append({
            "lat": float(row["chosen_lat"]),
            "lon": float(row["chosen_lon"]),
            "color": color,
            "status": row["status"],
            "name": row["feature_name"],
            "popup": popup_html
        })

    html_content = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8"/>
    <title>Bengaluru Flood Feature Geocoding Review</title>
    <link rel="stylesheet" href="https://unpkg.com/leaflet@1.9.4/dist/leaflet.css"/>
    <script src="https://unpkg.com/leaflet@1.9.4/dist/leaflet.js"></script>
    <style>
        body {{ margin: 0; padding: 0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif; }}
        #map {{ width: 100vw; height: 100vh; }}
        .legend {{ background: white; padding: 12px; border-radius: 6px; box-shadow: 0 0 15px rgba(0,0,0,0.2); font-size: 13px; line-height: 1.6; }}
        .legend-dot {{ display: inline-block; width: 12px; height: 12px; border-radius: 50%; margin-right: 6px; }}
        .header-box {{ position: absolute; top: 10px; left: 60px; z-index: 1000; background: white; padding: 10px 16px; border-radius: 6px; box-shadow: 0 0 15px rgba(0,0,0,0.2); }}
        .header-box h2 {{ margin: 0 0 4px 0; font-size: 16px; }}
        .header-box p {{ margin: 0; font-size: 12px; color: #666; }}
    </style>
</head>
<body>
    <div class="header-box">
        <h2>Bengaluru Flood Audit: Feature Geocode Review</h2>
        <p>Ground-truth verification: Overpass API (Method A) vs Structured Nominatim (Method B)</p>
    </div>
    <div id="map"></div>
    <script>
        var map = L.map('map').setView([12.94, 77.62], 12);
        L.tileLayer('https://{{s}}.basemaps.cartocdn.com/light_all/{{z}}/{{x}}/{{y}}{{r}}.png', {{
            attribution: '&copy; OpenStreetMap contributors &copy; CARTO'
        }}).addTo(map);

        var markers = {json.dumps(markers)};
        markers.forEach(function(m) {{
            L.circleMarker([m.lat, m.lon], {{
                radius: 8,
                fillColor: m.color,
                color: "#000",
                weight: 1.5,
                opacity: 1,
                fillOpacity: 0.85
            }}).bindPopup(m.popup).addTo(map);
        }});

        var legend = L.control({{ position: 'bottomright' }});
        legend.onAdd = function() {{
            var div = L.DomUtil.create('div', 'legend');
            div.innerHTML = '<b>Geocode Audit Status</b><br/>' +
                '<span class="legend-dot" style="background:#28a745;"></span> AUTO_ACCEPT (&le; 150m & inside grid)<br/>' +
                '<span class="legend-dot" style="background:#ffc107;"></span> REVIEW (discrepancy / single source)<br/>' +
                '<span class="legend-dot" style="background:#dc3545;"></span> NO_MATCH (unresolved)<br/>' +
                '<hr style="margin:6px 0;"/>' +
                'Total Features Evaluated: ' + markers.length;
            return div;
        }};
        legend.addTo(map);
    </script>
</body>
</html>
"""
    os.makedirs(os.path.dirname(REVIEW_HTML), exist_ok=True)
    with open(REVIEW_HTML, "w", encoding="utf-8") as f:
        f.write(html_content)
    print(f"Generated Leaflet map review at {REVIEW_HTML}")

if __name__ == "__main__":
    main()
