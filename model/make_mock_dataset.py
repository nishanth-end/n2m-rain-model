"""Makes a FAKE flood_dataset.csv with Member 1's exact column schema, so you can test train_real.py
before the real file arrives. Delete/ignore once you have the real CSV."""
import numpy as np, pandas as pd
rng = np.random.default_rng(1)
n_cells = 600
cells = pd.DataFrame({
    "cell_id": range(n_cells), "ward": rng.integers(0, 12, n_cells),
    "lat": rng.uniform(12.85, 13.15, n_cells), "lon": rng.uniform(77.45, 77.80, n_cells),
    "elev_m": rng.normal(900, 25, n_cells), "slope_deg": rng.gamma(1.5, 1.2, n_cells),
    "twi": rng.uniform(4, 14, n_cells), "hand_m": rng.gamma(2, 3, n_cells),
    "flow_acc": rng.lognormal(3, 1.5, n_cells), "imperv_frac": rng.uniform(0.1, 0.95, n_cells),
    "dist_lake_m": rng.gamma(2, 400, n_cells), "dist_drain_m": rng.gamma(2, 150, n_cells),
    "dist_road_m": rng.gamma(1.5, 80, n_cells), "lakes_within_1km": rng.integers(0, 5, n_cells)})
# 3 storms (dates) + random ordinary days
events = pd.to_datetime(["2020-10-20", "2021-11-18", "2022-09-05"])
days = list(events) + list(pd.to_datetime("2020-06-01") + pd.to_timedelta(rng.integers(0, 1100, 40), "D"))
rows = []
for d in days:
    big = d in events
    r1 = rng.gamma(2, 25) if big else rng.gamma(1, 6)
    r3, r7 = r1 + rng.gamma(2, 15 if big else 4), r1 + rng.gamma(3, 25 if big else 8)
    c = cells.copy(); c["date"] = d
    c["rain_1d_mm"], c["rain_3d_mm"], c["rain_7d_mm"] = r1, r3, r7
    z = (0.05*r3 + 0.25*c.twi - 0.35*c.hand_m - 0.002*c.dist_lake_m + 1.5*c.imperv_frac - 5.5)
    c["flood_label"] = (rng.random(len(c)) < 1/(1+np.exp(-z))).astype(int)
    rows.append(c)
df = pd.concat(rows, ignore_index=True)
df["label_source"] = np.where(df.flood_label == 1, "sar", "none")
df["label_confidence"] = np.where(df.flood_label == 1, rng.choice(["high", "medium", "low"], len(df)), "low")
df.to_csv("flood_dataset.csv", index=False)
print(df.shape, "flood rate:", round(df.flood_label.mean(), 4))
