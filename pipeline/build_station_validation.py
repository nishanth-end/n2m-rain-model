"""pipeline/build_station_validation.py

Generates data/interim/station_validation.csv with exact per-row lineage:
date, station, source_file, quote, measurement_window, pid,
d_minus_2, d_minus_1, d_0, d_plus_1, best_day_ratio, two_day_ratio, station_type, notes

Strict Validation Rules:
1. All daily rainfall values sampled strictly via rain_at(pixel, date).
2. Zone-maximum and network-maximum are compared against the maximum over all 37 pixels on the same days, not a single pixel.
3. Sub-daily bursts and unsourced rows have no daily ratio computed.
4. Quotes must be verbatim from saved evidence in data/evidence/ and <= 25 words.
5. Measurement windows copied verbatim from source or 'unknown'. No inferred windows.
"""

import os
from datetime import datetime, timedelta
import pandas as pd

RAINFALL_DAILY_PATH = "delivery/rainfall_daily.csv"
OUT_CSV_PATH = "data/interim/station_validation.csv"

_RAINFALL_DF = None

def get_rainfall_df(path=RAINFALL_DAILY_PATH):
    global _RAINFALL_DF
    if _RAINFALL_DF is None or getattr(_RAINFALL_DF, "_source_path", None) != path:
        df = pd.read_csv(path)
        df["date"] = df["date"].astype(str)
        df._source_path = path
        _RAINFALL_DF = df
    return _RAINFALL_DF

def rain_at(pixel, date: str, path=RAINFALL_DAILY_PATH) -> float:
    """Returns rainfall in mm for a given rain pixel and date (YYYY-MM-DD).
    If pixel is 'ALL' or -1 or None, returns the maximum across all 37 pixels for that date.
    """
    df = get_rainfall_df(path)
    dt_str = str(date)
    if pixel in ("ALL", -1, None, "all"):
        sub = df[df["date"] == dt_str]
        if len(sub) == 0:
            return 0.0
        return float(sub["rain_mm"].max())
    else:
        pid = int(pixel)
        sub = df[(df["date"] == dt_str) & (df["rain_pixel_id"] == pid)]
        if len(sub) == 0:
            return 0.0
        return float(sub["rain_mm"].iloc[0])

def main():
    stations = [
        {
            "date": "2022-05-06",
            "station": "KSNDMC Mahadevapura / Bommanahalli Gauges",
            "source_file": "dh_2022_05_06_1106860.txt",
            "quote": "Bommanahalli, Mahadevapura, Yelahanka, and Bengaluru South received up to 70 mm of rainfall",
            "measurement_window": "unknown",
            "pid": "ALL",
            "station_mm": 70.0,
            "station_type": "zone-maximum",
            "notes": "Zonal maximum across eastern/southern zones; compared against 37-pixel city-wide max"
        },
        {
            "date": "2022-09-05",
            "station": "KSNDMC Varthur Gauge",
            "source_file": "tnm_2022_09_05_167538.txt",
            "quote": "Natural Disaster Monitoring Centre (KSNDMC), Bellandur, Hallenayakanahalli, Varthur recorded 67.5 mm, 74mm, 83.5 mm of rain, respectively, over the past 24 hours.",
            "measurement_window": "over the past 24 hours",
            "pid": 13,
            "station_mm": 83.5,
            "station_type": "point-gauge",
            "notes": "Point-gauge at Varthur; source KSNDMC reported in TNM 167538"
        },
        {
            "date": "2022-09-05",
            "station": "KSNDMC Bellandur Gauge",
            "source_file": "tnm_2022_09_05_167538.txt",
            "quote": "Natural Disaster Monitoring Centre (KSNDMC), Bellandur, Hallenayakanahalli, Varthur recorded 67.5 mm, 74mm, 83.5 mm of rain, respectively, over the past 24 hours.",
            "measurement_window": "over the past 24 hours",
            "pid": 12,
            "station_mm": 67.5,
            "station_type": "point-gauge",
            "notes": "Point-gauge at Bellandur; source KSNDMC reported in TNM 167538"
        },
        {
            "date": "2022-09-05",
            "station": "IMD Sampangiramanagar (Sajjan 2022 p. 132)",
            "source_file": "sajjan_2022_p132.txt",
            "quote": "The Sampangiramanagar area in Bengaluru reported a rainfall of 148mm on Sunday night, according to IMD data.",
            "measurement_window": "Sunday night",
            "pid": 17,
            "station_mm": 148.0,
            "station_type": "point-gauge",
            "notes": "Point gauge cited in Sajjan 2022 p. 132 from IMD; CHIRPS Px 17 D0: 18.99 mm (ratio 5.19x vs 4 Sept D-1 28.49 mm)"
        },
        {
            "date": "2022-09-05",
            "station": "IMD City-wide (Sajjan 2022 p. 56)",
            "source_file": "sajjan_2022_p056.txt",
            "quote": "the city recorded 13.16 cm (131.6 mm) of rainfall, most of which fell in less than 12 hours on Sunday night.",
            "measurement_window": "less than 12 hours on Sunday night",
            "pid": "ALL",
            "station_mm": 131.6,
            "station_type": "network-maximum",
            "notes": "City-wide <12h total cited in Sajjan 2022 p. 56 from IMD; compared against 37-pixel city-wide max"
        },
        {
            "date": "2022-09-05",
            "station": "Eastern Zone Mahadevapura/Varthur (Sajjan 2022 p. 132)",
            "source_file": "sajjan_2022_p132_varthur.txt",
            "quote": "Areas like Mahadevapura, Marathahalli, Doddenakundi, Varthur and HAL road in the city reported more than 100mm rainfall during the same period.",
            "measurement_window": "during the same period",
            "pid": "ALL",
            "station_mm": 100.0,
            "station_type": "zone-maximum",
            "notes": "Regional zonal total for eastern flood corridor cited in Sajjan 2022 p. 132; compared against 37-pixel max"
        },
        {
            "date": "2022-10-20",
            "station": "KSNDMC Seegehalli Gauge",
            "source_file": "tnm_2022_10_20_169062.txt",
            "quote": "Seegehalli received 81.5 mm of rainfall on Wenesday, October 19, while Doddabanahalli received 78 mm.",
            "measurement_window": "unknown",
            "pid": 20,
            "station_mm": 81.5,
            "station_type": "point-gauge",
            "notes": "Point-gauge at Seegehalli; source KSNDMC reported in TNM 169062"
        },
        {
            "date": "2017-10-05",
            "station": "IMD Bengaluru City Obs (Afternoon Cloudburst)",
            "source_file": "quint_2017_10_05.txt",
            "quote": "According to the India Meteorological Department, the city received 42 mm rainfall between 1 pm and 2.30 pm on 5 October.",
            "measurement_window": "between 1 pm and 2.30 pm on 5 October",
            "pid": 17,
            "station_mm": 42.0,
            "station_type": "sub-daily-burst",
            "notes": "90-minute sub-daily burst; cannot be compared to daily CHIRPS, no ratio computed"
        },
        {
            "date": "2017-09-27",
            "station": "KSNDMC City Maximum ('a few areas, maximum 196 mm')",
            "source_file": "gt_2017_09_27_565360.txt",
            "quote": "with a few areas receiving a maximum of 196mm as recorded at 8.30am",
            "measurement_window": "as recorded at 8.30am",
            "pid": "ALL",
            "station_mm": 196.0,
            "station_type": "network-maximum",
            "notes": "City-wide telemetry maximum across network; compared against 37-pixel city-wide max"
        },
        {
            "date": "2017-08-15",
            "station": "IMD Bengaluru City Obs (Palace Road)",
            "source_file": "NOT VERIFIABLE",
            "quote": "NOT VERIFIABLE",
            "measurement_window": "unknown",
            "pid": 17,
            "station_mm": 128.7,
            "station_type": "unsourced",
            "notes": "Unverified station record; excluded from calibration"
        },
        {
            "date": "2021-11-22",
            "station": "KSNDMC Yelahanka / Jakkur Gauge",
            "source_file": "NOT VERIFIABLE",
            "quote": "NOT VERIFIABLE",
            "measurement_window": "unknown",
            "pid": 32,
            "station_mm": 153.0,
            "station_type": "unsourced",
            "notes": "Unverified station record; complete satellite miss in CHIRPS (0.0 mm); excluded"
        }
    ]

    rows = []
    for s in stations:
        m_dt = datetime.strptime(s["date"], "%Y-%m-%d")
        d_m2 = (m_dt - timedelta(days=2)).strftime("%Y-%m-%d")
        d_m1 = (m_dt - timedelta(days=1)).strftime("%Y-%m-%d")
        d_0 = (m_dt).strftime("%Y-%m-%d")
        d_p1 = (m_dt + timedelta(days=1)).strftime("%Y-%m-%d")

        val_m2 = rain_at(s["pid"], d_m2)
        val_m1 = rain_at(s["pid"], d_m1)
        val_0 = rain_at(s["pid"], d_0)
        val_p1 = rain_at(s["pid"], d_p1)

        # Ratios are computed only for point-gauge, zone-maximum, and network-maximum
        # Sub-daily bursts and unsourced rows have no daily ratio
        if s["station_type"] in ("point-gauge", "zone-maximum", "network-maximum"):
            best_day_val = max(val_m1, val_0)
            two_day_sum = val_m1 + val_0
            best_day_ratio = round(best_day_val / s["station_mm"], 4)
            two_day_ratio = round(two_day_sum / s["station_mm"], 4)
        else:
            best_day_ratio = None
            two_day_ratio = None

        rows.append({
            "date": s["date"],
            "station": s["station"],
            "source_file": s["source_file"],
            "quote": s["quote"],
            "measurement_window": s["measurement_window"],
            "pid": s["pid"],
            "station_mm": s["station_mm"],
            "d_minus_2": round(val_m2, 2),
            "d_minus_1": round(val_m1, 2),
            "d_0": round(val_0, 2),
            "d_plus_1": round(val_p1, 2),
            "best_day_ratio": best_day_ratio if best_day_ratio is not None else "",
            "two_day_ratio": two_day_ratio if two_day_ratio is not None else "",
            "station_type": s["station_type"],
            "notes": s["notes"]
        })

    out_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_CSV_PATH), exist_ok=True)
    out_df.to_csv(OUT_CSV_PATH, index=False)
    print(f"Wrote {len(out_df)} rows to {OUT_CSV_PATH}")

    # Summary of point-gauge range
    pg = out_df[out_df["station_type"] == "point-gauge"].copy()
    pg["best_day_ratio"] = pd.to_numeric(pg["best_day_ratio"])
    pg["two_day_ratio"] = pd.to_numeric(pg["two_day_ratio"])

    min_pg_best = pg["best_day_ratio"].min()
    max_pg_best = pg["best_day_ratio"].max()
    min_pg_sum = pg["two_day_ratio"].min()
    max_pg_sum = pg["two_day_ratio"].max()

    print(f"\n--- Point-Gauge Calibration Range ({len(pg)} verified rows) ---")
    print(f"Best-day ratio range: {min_pg_best:.4f} to {max_pg_best:.4f} ({1/max_pg_best:.1f}x to {1/min_pg_best:.1f}x attenuation)")
    print(f"2-day sum ratio range: {min_pg_sum:.4f} to {max_pg_sum:.4f} ({1/max_pg_sum:.1f}x to {1/min_pg_sum:.1f}x attenuation)")

if __name__ == "__main__":
    main()
