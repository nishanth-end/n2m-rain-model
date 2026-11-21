# Flood risk model: handover to Member 3

## What this is
An experimental susceptibility ranking for 3,026 Bengaluru grid cells. It ranks cells each day by relative flood risk. It is NOT a validated forecast and the scores are NOT probabilities.

## Alert levels (rank-based, per day)
- High: top 150 cells (5%)
- Moderate: top 300 cells (10%)
- Everything else: None
Do not use absolute score thresholds. Always rank all cells for one date first.

## Models
- flood_xgb.json: final model for any new/live date.
- flood_xgb_holdout_E2022_09.json: ONLY for the September 2022 replay demo (it never saw that event).

## How to score a day
1. Build one row per cell for that date with the 18 features in features.json (same names).
   - Static features (elev_m, slope_deg, twi, hand_m, flow_acc, imperv_frac, dist_lake_m, dist_drain_m, dist_road_m, lakes_within_1km) come from cells_static.csv.
   - Rain features come from daily CHIRPS rain per rain pixel (cell_pixel_map.csv links cell to pixel):
     rain_1d = rain that day; rain_lag1/2/3 = rain 1, 2, 3 days earlier;
     rain_3d / 7d / 14d = sum of that day and the previous 2 / 6 / 13 days; rain_30d = same pattern over 30 days.
2. Call score_day(df, model, feats, rule) from score_cells.py.
3. Show the ranked table and map using the 'level' column.

## Dashboard wording (please use)
- Title: "Experimental flood susceptibility ranking"
- Show: "Relative priority, not predicted flood probability."
- Do not say "forecast", "prediction of flooding", or "3 days warning".

## Known limits (show on an About page)
- About 10 labelled places across 6 events; most positives are assumed neighbour cells.
- Daily 5 km rain data misses short cloudbursts.
- Strict validation on Sept 2022: PR-AUC 0.0026 vs chance 0.0013 (about 2x chance). Hit rate on flood days: High 8.3% (random 5.0%), Moderate+ 25% (random 9.9%). Treat as indicative only.

## Demo data
flood_replay_E2022_09.parquet holds 2022-08-22 to 2022-09-14 (24 days, 3,026 cells). Use the holdout model with it. Run test_handover.py to check the setup.
## Setup
Python packages: xgboost==3.4.1, pandas, pyarrow