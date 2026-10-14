"""pipeline/build_station_validation.py

Generates data/interim/station_validation.csv with exact per-row lineage:
date, station, source_file, quote, measurement_window, pid,
d_minus_2, d_minus_1, d_0, d_plus_1, best_day_ratio, two_day_ratio, station_type

Flags:
- point-gauge: single localized ground station
- zone-maximum: aggregated zonal maximum ("up to 70 mm")
- network-maximum: city-wide telemetry network maximum ("196 mm")
- sub-daily-burst: convective burst over < 2 hours (e.g. 42 mm in 1.5 h)
- unsourced: no contemporaneous verification document
"""

import os
from datetime import datetime, timedelta
import pandas as pd

RAINFALL_DAILY_PATH = "delivery/rainfall_daily.csv"
OUT_CSV_PATH = "data/interim/station_validation.csv"

def main():
    rd = pd.read_csv(RAINFALL_DAILY_PATH)
    
    stations = [
        {
            "date": "2022-05-06",
            "station": "KSNDMC Mahadevapura / Bommanahalli Gauges",
            "source_file": "dh_2022_05_06_1106860.txt",
            "quote": "Bommanahalli, Mahadevapura, Yelahanka, and Bengaluru South received up to 70 mm of rainfall",
            "measurement_window": "24 h ending Thursday evening 5 May 2022",
            "pid": 12,
            "station_mm": 70.0,
            "station_type": "zone-maximum",
            "notes": "Zonal maximum across eastern/southern zones; excluded from point-gauge range"
        },
        {
            "date": "2022-09-05",
            "station": "KSNDMC Varthur Gauge",
            "source_file": "references/Floods_at_Bengaluru_City_A_Technical_Stu.pdf (Ch. 11)",
            "quote": "Varthur Lake catchment gauge recorded 83.5 mm on 5 Sept 2022",
            "measurement_window": "24 h ending 08:30 IST on 5 Sept 2022",
            "pid": 13,
            "station_mm": 83.5,
            "station_type": "point-gauge",
            "notes": "IISc technical report (Sajjan et al. 2022, Table 11.2); offline engineering document"
        },
        {
            "date": "2022-09-05",
            "station": "KSNDMC Bellandur Gauge",
            "source_file": "references/Floods_at_Bengaluru_City_A_Technical_Stu.pdf (Ch. 6)",
            "quote": "Bellandur Lake catchment gauge recorded 67.5 mm on 5 Sept 2022",
            "measurement_window": "24 h ending 08:30 IST on 5 Sept 2022",
            "pid": 12,
            "station_mm": 67.5,
            "station_type": "point-gauge",
            "notes": "IISc technical report (Sajjan et al. 2022, Table 6.1); offline engineering document"
        },
        {
            "date": "2022-10-20",
            "station": "KSNDMC Seegehalli Gauge",
            "source_file": "tnm_2022_10_20_169062.txt",
            "quote": "Seegehalli received 81.5 mm of rainfall on Wenesday, October 19, while Doddabanahalli received 78 mm.",
            "measurement_window": "24 h ending night of Wednesday 19 Oct 2022",
            "pid": 20,
            "station_mm": 81.5,
            "station_type": "point-gauge",
            "notes": "Best-day ratio 0.080 (6.49 mm vs 81.5 mm = 12.6x attenuation); 2-day sum ratio 0.119 (8.4x)"
        },
        {
            "date": "2017-10-05",
            "station": "IMD Bengaluru City Obs (Afternoon Cloudburst)",
            "source_file": "quint_2017_10_05.txt",
            "quote": "According to the India Meteorological Department, the city received 42 mm rainfall between 1 pm and 2.30 pm on 5 October.",
            "measurement_window": "1:00 PM to 2:30 PM (90-minute sub-daily burst)",
            "pid": 17,
            "station_mm": 42.0,
            "station_type": "sub-daily-burst",
            "notes": "90-minute convective burst, not a 24h daily station total; cannot be compared to daily CHIRPS"
        },
        {
            "date": "2017-09-27",
            "station": "KSNDMC City Maximum ('a few areas, maximum 196 mm')",
            "source_file": "gt_2017_09_27_565360.txt",
            "quote": "with a few areas receiving a maximum of 196mm as recorded at 8.30am",
            "measurement_window": "24 h ending 08:30 IST on 27 Sept 2017",
            "pid": 26,
            "station_mm": 196.0,
            "station_type": "network-maximum",
            "notes": "City-wide telemetry maximum across entire network; excluded from point-gauge range"
        },
        {
            "date": "2017-08-15",
            "station": "IMD Bengaluru City Obs (Palace Road)",
            "source_file": "UNSOURCED",
            "quote": "UNSOURCED (128.7 mm reported in secondary blogs)",
            "measurement_window": "24 h ending 08:30 IST on 15 Aug 2017",
            "pid": 17,
            "station_mm": 128.7,
            "station_type": "unsourced",
            "notes": "Unverified station record; excluded from calibration"
        },
        {
            "date": "2021-11-22",
            "station": "KSNDMC Yelahanka / Jakkur Gauge",
            "source_file": "UNSOURCED",
            "quote": "UNSOURCED (153.0 mm reported in secondary tweets)",
            "measurement_window": "24 h ending 08:30 IST on 22 Nov 2021",
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

        def get_val(dt_str):
            v = rd[(rd["date"] == dt_str) & (rd["rain_pixel_id"] == s["pid"])]["rain_mm"].values
            return float(v[0]) if len(v) > 0 else 0.0

        val_m2 = get_val(d_m2)
        val_m1 = get_val(d_m1)
        val_0 = get_val(d_0)
        val_p1 = get_val(d_p1)

        # For morning readings (08:30 IST), storm occurs on D-1 night (captured partly in D-1 and partly in D0)
        best_day_val = max(val_m1, val_0)
        two_day_sum = val_m1 + val_0

        best_day_ratio = best_day_val / s["station_mm"]
        two_day_ratio = two_day_sum / s["station_mm"]

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
            "best_day_ratio": round(best_day_ratio, 4),
            "two_day_ratio": round(two_day_ratio, 4),
            "station_type": s["station_type"],
            "notes": s["notes"]
        })

    out_df = pd.DataFrame(rows)
    os.makedirs(os.path.dirname(OUT_CSV_PATH), exist_ok=True)
    out_df.to_csv(OUT_CSV_PATH, index=False)
    print(f"Wrote {len(out_df)} rows to {OUT_CSV_PATH}")

    # Summary of point-gauge range
    pg = out_df[out_df["station_type"] == "point-gauge"]
    min_pg_best = pg["best_day_ratio"].min()
    max_pg_best = pg["best_day_ratio"].max()
    min_pg_sum = pg["two_day_ratio"].min()
    max_pg_sum = pg["two_day_ratio"].max()

    print("\n--- Point-Gauge Calibration Range ---")
    print(f"Best-day ratio range: {min_pg_best:.4f} to {max_pg_best:.4f} ({1/max_pg_best:.1f}x to {1/min_pg_best:.1f}x attenuation)")
    print(f"2-day sum ratio range: {min_pg_sum:.4f} to {max_pg_sum:.4f} ({1/max_pg_sum:.1f}x to {1/min_pg_sum:.1f}x attenuation)")

if __name__ == "__main__":
    main()
