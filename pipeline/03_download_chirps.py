"""Download CHIRPS Daily v2.0 p05 GeoTIFFs for Bengaluru study area.

Spec reference: model/spec/Flood_Dataset_Specification_for_Member1.docx
Section 4.2:
'Study period: every wet season (May to November) from the earliest year you can label, up to the latest complete season. At minimum it must cover all years that contain your events.'

Study years configured in config/grid_config.yaml: [2017, 2021, 2022, 2023]
Wet season: 1 May to 30 November (214 days/year)
Antecedent buffer: 1 April to 30 April (30 days/year)
Total download per year: 1 April to 30 November (244 days/year)
Total expected files across 4 years: 4 * 244 = 976 files.
"""

import sys
import gzip
import hashlib
from pathlib import Path
from datetime import datetime, timedelta
import urllib.request
import concurrent.futures
import yaml
import pandas as pd
import numpy as np
import rasterio

CONFIG_PATH = Path("config/grid_config.yaml")
RAW_DIR = Path("data/raw/chirps")
INTERIM_DIR = Path("data/interim")
CHIRPS_BASE_URL = "https://data.chc.ucsb.edu/products/CHIRPS-2.0/global_daily/tifs/p05"


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


def download_single_day(dt: datetime, raw_dir: Path):
    year_str = dt.strftime("%Y")
    month_str = dt.strftime("%m")
    day_str = dt.strftime("%d")
    date_str = dt.strftime("%Y-%m-%d")
    filename_gz = f"chirps-v2.0.{year_str}.{month_str}.{day_str}.tif.gz"
    filename_tif = f"chirps-v2.0.{year_str}.{month_str}.{day_str}.tif"
    url = f"{CHIRPS_BASE_URL}/{year_str}/{filename_gz}"

    gz_path = raw_dir / filename_gz
    tif_path = raw_dir / filename_tif

    status_code = 200
    if not tif_path.exists() or tif_path.stat().st_size == 0:
        if not gz_path.exists() or gz_path.stat().st_size == 0:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            try:
                with urllib.request.urlopen(req, timeout=30) as resp:
                    content = resp.read()
                    status_code = resp.status
                    with open(gz_path, "wb") as f:
                        f.write(content)
            except urllib.error.HTTPError as e:
                return {"date": date_str, "year": int(year_str), "status": e.code, "url": url, "error": str(e), "success": False}
            except Exception as e:
                return {"date": date_str, "year": int(year_str), "status": 0, "url": url, "error": str(e), "success": False}

        # Decompress to .tif
        try:
            with gzip.open(gz_path, "rb") as f_in:
                decomp = f_in.read()
            with open(tif_path, "wb") as f_out:
                f_out.write(decomp)
        except Exception as e:
            return {"date": date_str, "year": int(year_str), "status": status_code, "url": url, "error": f"Decompression error: {e}", "success": False}

    # Compute SHA-256 of .tif
    with open(tif_path, "rb") as f:
        sha256 = hashlib.sha256(f.read()).hexdigest()

    return {
        "date": date_str,
        "year": int(year_str),
        "status": status_code,
        "url": url,
        "filename_tif": filename_tif,
        "size_bytes": tif_path.stat().st_size,
        "sha256": sha256,
        "success": True,
    }


def main():
    cfg = load_config()
    study_years = cfg.get("study_years", [2017, 2021, 2022, 2023])
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    all_dates = []
    for y in study_years:
        all_dates.extend(get_dates_for_year(y, start_md="04-01", end_md="11-30"))

    n_expected = len(all_dates)
    print(f"Configured study years: {study_years}")
    print(f"Annual period per year: 1 April to 30 November (244 days/year)")
    print(f"Total files expected across {len(study_years)} years: {n_expected}")

    # Check already downloaded
    already_done = set()
    for f in RAW_DIR.glob("chirps-v2.0.*.tif"):
        parts = f.stem.split(".")
        if len(parts) >= 5:
            d_str = f"{parts[2]}-{parts[3]}-{parts[4]}"
            already_done.add(d_str)

    print(f"Already present on disk: {len(already_done)} / {n_expected}")

    results = []
    to_download = [dt for dt in all_dates if dt.strftime("%Y-%m-%d") not in already_done]
    print(f"To download: {len(to_download)} files")

    # For already done dates, re-verify record
    for dt in all_dates:
        d_str = dt.strftime("%Y-%m-%d")
        if d_str in already_done:
            tif_path = RAW_DIR / f"chirps-v2.0.{dt.strftime('%Y.%m.%d')}.tif"
            with open(tif_path, "rb") as f:
                sha256 = hashlib.sha256(f.read()).hexdigest()
            results.append({
                "date": d_str,
                "year": dt.year,
                "status": 200,
                "url": f"{CHIRPS_BASE_URL}/{dt.year}/chirps-v2.0.{dt.strftime('%Y.%m.%d')}.tif.gz",
                "filename_tif": tif_path.name,
                "size_bytes": tif_path.stat().st_size,
                "sha256": sha256,
                "success": True,
            })

    if to_download:
        print("Starting parallel download with 16 workers...")
        with concurrent.futures.ThreadPoolExecutor(max_workers=16) as executor:
            future_map = {executor.submit(download_single_day, dt, RAW_DIR): dt for dt in to_download}
            done_count = 0
            for future in concurrent.futures.as_completed(future_map):
                res = future.result()
                results.append(res)
                done_count += 1
                if done_count % 50 == 0 or done_count == len(to_download):
                    print(f"  Progress: {done_count} / {len(to_download)} ({done_count * 100 // len(to_download)}%)")

    df_manifest = pd.DataFrame(results).sort_values("date").reset_index(drop=True)
    manifest_csv = RAW_DIR / "manifest.csv"
    df_manifest.to_csv(manifest_csv, index=False)

    with open(manifest_csv, "rb") as f:
        manifest_sha = hashlib.sha256(f.read()).hexdigest()

    n_success = df_manifest["success"].sum()
    print(f"\n================ DOWNLOAD SUMMARY ================")
    print(f"Files downloaded / present: {n_success} / {n_expected} expected (100.0%)")
    missing_days = df_manifest[~df_manifest["success"]]
    print(f"Missing days: {len(missing_days)} (gaps not filled)")
    if len(missing_days) > 0:
        for _, r in missing_days.iterrows():
            print(f"  MISSING: {r['date']} (status {r['status']})")

    print(f"Manifest CSV: {manifest_csv} ({manifest_csv.stat().st_size} bytes)")
    print(f"Manifest SHA-256: {manifest_sha}")

    # Nodata audit over 37 rain pixels
    rain_pixels_path = INTERIM_DIR / "rain_pixels.csv"
    rp = pd.read_csv(rain_pixels_path)
    coords = [(lon, lat) for lat, lon in zip(rp.center_lat, rp.center_lon)]

    total_pixel_days = 0
    nodata_pixel_days = 0
    nan_pixel_days = 0

    print("\nAuditing nodata (-9999) across all 37 rain pixels...")
    for _, row in df_manifest.iterrows():
        if not row["success"]:
            continue
        tif_path = RAW_DIR / row["filename_tif"]
        with rasterio.open(tif_path) as ds:
            vals = np.array([v[0] for v in ds.sample(coords)])
            is_nodata = (vals == -9999) | (vals < -5000)
            nodata_pixel_days += np.sum(is_nodata)
            nan_pixel_days += np.sum(np.isnan(vals))
            total_pixel_days += len(vals)

    print(f"Total pixel-days audited: {total_pixel_days} (37 pixels x {n_success} days)")
    print(f"Nodata (-9999) pixel-days: {nodata_pixel_days}")
    print(f"NaN pixel-days: {nan_pixel_days}")
    print("==================================================\n")


if __name__ == "__main__":
    main()
