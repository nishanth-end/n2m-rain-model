import sys
import numpy as np
import pandas as pd

path = sys.argv[1]
df = pd.read_parquet(path) if path.endswith(".parquet") else pd.read_csv(path)
df["date"] = pd.to_datetime(df["date"])

STATIC = ["elev_m", "slope_deg", "twi", "hand_m", "flow_acc", "imperv_frac",
          "dist_lake_m", "dist_drain_m", "lakes_within_1km"]
REQ = ["cell_id", "date", "lat", "lon", "ward", "rain_pixel_id", "rain_1d_mm",
       "rain_3d_mm", "rain_7d_mm", "flood_label", "label_source", "label_confidence",
       "event_id", "day_sampling_weight"] + STATIC
SOURCES = {"sar", "hotspot_pdf", "news", "civic_report", "none"}
CONF = {"high", "medium", "low"}
FORBIDDEN = {"elevation_proxy", "is_hotspot", "dist_to_hotspot", "hotspot_name",
             "primary_cause"}

fails = []
def check(ok, msg):
    print(("PASS  " if ok else "FAIL  ") + msg)
    if not ok:
        fails.append(msg)

missing = [c for c in REQ if c not in df.columns]
check(not missing, f"required columns present {missing if missing else ''}")
if missing:
    sys.exit("Fix the missing columns first.")

check(not df.duplicated(["cell_id", "date"]).any(), "no duplicate (cell_id, date)")
n_cells = df["cell_id"].nunique()
per_day = df.groupby("date")["cell_id"].nunique()
check((per_day == n_cells).all(), f"every date has all {n_cells} cells "
                                   f"({int((per_day != n_cells).sum())} incomplete days)")
check(df[["rain_1d_mm", "rain_3d_mm", "rain_7d_mm"]].notna().all().all(), "no missing rain")
check(df[STATIC].notna().all().all(), "no missing static features")
check(((df.rain_1d_mm <= df.rain_3d_mm + 1e-6) & (df.rain_3d_mm <= df.rain_7d_mm + 1e-6)).all(),
      "rain_1d <= rain_3d <= rain_7d")
if {"rain_lag1_mm", "rain_lag2_mm"} <= set(df.columns):
    check(np.allclose(df.rain_3d_mm, df.rain_1d_mm + df.rain_lag1_mm + df.rain_lag2_mm, atol=0.02),
          "rain_3d == rain_1d + lag1 + lag2")
check(df.groupby("cell_id")[STATIC].nunique().max().max() == 1, "static features constant per cell")
check(set(df.flood_label.unique()) <= {0, 1}, "flood_label only 0/1")
check(set(df.label_source.dropna().unique()) <= SOURCES, "label_source values allowed")
check(set(df.label_confidence.dropna().unique()) <= CONF, "label_confidence values allowed")
check((df.day_sampling_weight >= 1).all(), "day_sampling_weight >= 1")
pos = df[df.flood_label == 1]
check(len(pos) > 0, f"{len(pos)} positive rows")
check((pos.label_source != "none").all(), "every positive has a label_source")
check(pos.event_id.notna().all(), "every positive has an event_id")
n_events = pos.event_id.nunique()
check(n_events >= 3, f"at least 3 distinct events (found {n_events})")
bad = [c for c in df.columns if c.lower() in FORBIDDEN]
check(not bad, f"no forbidden columns {bad if bad else ''}")

print("\nrows:", len(df), "| cells:", n_cells, "| days:", df.date.nunique(),
      "| date range:", df.date.min().date(), "to", df.date.max().date())
print("flood rate (all rows):", round(df.flood_label.mean(), 4))
print("positives per event:")
print(pos.groupby("event_id").size().to_string())
print("\nFAILED CHECKS:", len(fails))
