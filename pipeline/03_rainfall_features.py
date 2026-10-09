"""Extract and compute rainfall features from CHIRPS Daily v2.0 GeoTIFFs.

Spec references:
- Section 4.2: Study period: May to November for event years (2017, 2021, 2022, 2023).
- Section 4.4: Definitions:
    - rain_1d_mm: Daily rainfall on day D (ending on D inclusive).
    - rain_3d_mm: Sum of rainfall on days D-2, D-1, D (3 days total).
    - rain_7d_mm: Sum of rainfall on days D-6 ... D (7 days total).
    - rain_14d_mm: Sum of rainfall on days D-13 ... D (14 days total).
    - rain_30d_mm: Sum of rainfall on days D-29 ... D (30 days total).
    - rain_lag1_mm: Daily rainfall on day D-1.
    - rain_lag2_mm: Daily rainfall on day D-2.
    - rain_lag3_mm: Daily rainfall on day D-3.

Buffer rule:
- Series starts on 1 April (30 days prior buffer) within each year.
- Rolling features are computed strictly within each year (never across years or missing days).
- Output is trimmed to the study period: 1 May to 30 November (214 days/year).
"""

import sys
from pathlib import Path
from datetime import datetime, timedelta
import yaml
import pandas as pd
import numpy as np
import rasterio

CONFIG_PATH = Path("config/grid_config.yaml")
RAW_DIR = Path("data/raw/chirps")
INTERIM_DIR = Path("data/interim")
OUTPUT_CSV = INTERIM_DIR / "rain_timeseries.csv"


def load_config():
    with open(CONFIG_PATH) as f:
        return yaml.safe_load(f)


def get_dates_for_year(year: int, start_md: str = "04-01", end_md: str = "11-30"):
    start_dt = datetime.strptime(f"{year}-{start_md}", "%Y-%m-%d")
    end_dt = datetime.strptime(f"{year}-{end_md}", "%Y-%m-%d")
    dates = []
    curr = start_dt
    while curr <= end_dt:
        dates.append(curr)
        curr += timedelta(days=1)
    return dates


def extract_daily_rain(study_years, rain_pixels):
    coords = [(lon, lat) for lat, lon in zip(rain_pixels.center_lat, rain_pixels.center_lon)]
    n_pixels = len(rain_pixels)
    records = []

    for year in study_years:
        dates = get_dates_for_year(year, "04-01", "11-30")
        print(f"Sampling CHIRPS rasters for year {year} ({len(dates)} days)...")
        for dt in dates:
            d_str = dt.strftime("%Y-%m-%d")
            tif_path = RAW_DIR / f"chirps-v2.0.{dt.strftime('%Y.%m.%d')}.tif"
            if not tif_path.exists():
                raise FileNotFoundError(f"Missing CHIRPS GeoTIFF: {tif_path}")

            with rasterio.open(tif_path) as ds:
                # rasterio sample takes (x, y) = (lon, lat)
                sample_coords = [(lon, lat) for lon, lat in zip(rain_pixels.center_lon, rain_pixels.center_lat)]
                vals = np.array([v[0] for v in ds.sample(sample_coords)], dtype=np.float64)

            # Mask -9999 as NaN
            vals[vals == -9999] = np.nan
            vals[vals < -5000] = np.nan

            for pid, val in zip(rain_pixels.rain_pixel_id, vals):
                records.append({
                    "rain_pixel_id": int(pid),
                    "date": d_str,
                    "year": year,
                    "dt": dt,
                    "rain_mm": float(val),
                })

    return pd.DataFrame(records)


def compute_rolling_features(df_daily):
    print("Computing rolling sums and lag features per pixel per year...")
    # Sort strictly by pixel, year, dt
    df_daily = df_daily.sort_values(["rain_pixel_id", "year", "dt"]).reset_index(drop=True)

    # Group by pixel and year so we never roll across years
    groups = []
    for (pid, year), grp in df_daily.groupby(["rain_pixel_id", "year"]):
        grp = grp.copy().sort_values("dt")
        rain = grp["rain_mm"]

        grp["rain_1d_mm"] = rain
        grp["rain_3d_mm"] = rain.rolling(window=3, min_periods=3).sum()
        grp["rain_7d_mm"] = rain.rolling(window=7, min_periods=7).sum()
        grp["rain_14d_mm"] = rain.rolling(window=14, min_periods=14).sum()
        grp["rain_30d_mm"] = rain.rolling(window=30, min_periods=30).sum()

        grp["rain_lag1_mm"] = rain.shift(1)
        grp["rain_lag2_mm"] = rain.shift(2)
        grp["rain_lag3_mm"] = rain.shift(3)

        groups.append(grp)

    df_featured = pd.concat(groups, ignore_index=True)

    # Filter to study period: May 1 to Nov 30 (month >= 5)
    df_study = df_featured[df_featured["dt"].dt.month >= 5].copy()

    # Drop temporary columns
    df_study = df_study.drop(columns=["dt", "year", "rain_mm"])
    df_study = df_study.sort_values(["date", "rain_pixel_id"]).reset_index(drop=True)

    return df_study


def main():
    cfg = load_config()
    study_years = cfg.get("study_years", [2017, 2021, 2022, 2023])

    rain_pixels_path = INTERIM_DIR / "rain_pixels.csv"
    if not rain_pixels_path.exists():
        raise FileNotFoundError(f"{rain_pixels_path} not found")
    rain_pixels = pd.read_csv(rain_pixels_path).sort_values("rain_pixel_id")

    df_daily = extract_daily_rain(study_years, rain_pixels)
    df_study = compute_rolling_features(df_daily)

    # Write output
    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df_study.to_csv(OUTPUT_CSV, index=False)
    print(f"\nWrote {OUTPUT_CSV} ({len(df_study)} rows, {OUTPUT_CSV.stat().st_size} bytes)")

    # Assertions and Summary Statistics
    print("\n================ SUMMARY STATISTICS ================")
    print(f"Total rows: {len(df_study)}")
    print(f"Unique pixels: {df_study['rain_pixel_id'].nunique()} (expected 37)")
    print(f"Unique dates: {df_study['date'].nunique()} (expected {214 * len(study_years)} = {214 * 4})")

    feature_cols = [
        "rain_1d_mm", "rain_3d_mm", "rain_7d_mm", "rain_14d_mm", "rain_30d_mm",
        "rain_lag1_mm", "rain_lag2_mm", "rain_lag3_mm"
    ]

    print("\nNull Counts per feature:")
    null_counts = df_study[feature_cols].isnull().sum()
    print(null_counts)
    assert (null_counts == 0).all(), "Found null values in feature columns!"

    print("\nFeature Summary Statistics:")
    stats_df = df_study[feature_cols].describe().T[["min", "mean", "50%", "max", "std"]]
    stats_df.columns = ["min", "mean", "median", "max", "std"]
    print(stats_df.to_string())

    # Check for extreme values (> 300 mm/day)
    extreme_1d = df_study[df_study["rain_1d_mm"] > 300]
    print(f"\nValues above 300 mm/day in rain_1d_mm: {len(extreme_1d)}")
    if len(extreme_1d) > 0:
        print("Flagged extreme values:")
        print(extreme_1d[["rain_pixel_id", "date", "rain_1d_mm"]])
    else:
        print("None found (max daily rain is within plausible physical range).")

    # Monotonicity check: rain_1d <= rain_3d <= rain_7d <= rain_14d <= rain_30d
    mono_violations = (
        (df_study["rain_3d_mm"] < df_study["rain_1d_mm"] - 1e-5) |
        (df_study["rain_7d_mm"] < df_study["rain_3d_mm"] - 1e-5) |
        (df_study["rain_14d_mm"] < df_study["rain_7d_mm"] - 1e-5) |
        (df_study["rain_30d_mm"] < df_study["rain_14d_mm"] - 1e-5)
    ).sum()
    print(f"\nMonotonic window violations (rain_1d <= rain_3d <= ... <= rain_30d): {mono_violations}")
    assert mono_violations == 0, "Monotonic window check failed!"

    # Lag identity check: rain_3d == rain_1d + rain_lag1 + rain_lag2
    lag_diff = (df_study["rain_3d_mm"] - (df_study["rain_1d_mm"] + df_study["rain_lag1_mm"] + df_study["rain_lag2_mm"])).abs()
    max_lag_err = lag_diff.max()
    print(f"Max absolute error in (rain_3d == rain_1d + lag1 + lag2): {max_lag_err:.6e}")
    assert max_lag_err < 1e-4, "Lag identity check failed!"

    print("All validation checks passed successfully.")


if __name__ == "__main__":
    main()
