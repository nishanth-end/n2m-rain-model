import pandas as pd
from score_cells import load, score_day

model, feats, rule = load(model_path="flood_xgb_holdout_E2022_09.json")
df = pd.read_parquet("flood_replay_E2022_09.parquet")
df["date"] = pd.to_datetime(df["date"])

d = df[df["date"] == "2022-09-08"]
out = score_day(d, model, feats, rule).set_index("cell_id")
print(out.loc[[555, 666, 847, 910, 977, 1444], ["rank", "level"]])
print(out["level"].value_counts())