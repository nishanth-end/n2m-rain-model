"""Train + honestly evaluate the flood model on Member 1's flood_dataset.csv.
Usage: python train_real.py flood_dataset.csv
Evaluation is by EVENT (leave-one-event-out) and by PLACE (ward-grouped CV) -- never random row splits."""
import sys, json, numpy as np, pandas as pd, xgboost as xgb
from sklearn.metrics import average_precision_score, confusion_matrix
from sklearn.model_selection import GroupKFold

CSV = sys.argv[1] if len(sys.argv) > 1 else "flood_dataset.csv"
MIN_RAIN_3D = 10          # keep only wetter days (dry days are trivially negative). 0 = keep everything
CONF_WEIGHT = {"high": 1.0, "medium": 0.7, "low": 0.4}   # how much to trust each POSITIVE label
CANDIDATES = ["rain_1d_mm", "rain_3d_mm", "rain_7d_mm", "rain_max_1h_mm", "elev_m", "slope_deg", "twi",
              "flow_acc", "imperv_frac", "dist_drain_m", "dist_road_m", "lakes_within_1km"]

df = pd.read_csv(CSV, parse_dates=["date"])
FEATURES = [c for c in CANDIDATES if c in df.columns and df[c].notna().any()]
print("features used:", FEATURES)
if MIN_RAIN_3D and "rain_3d_mm" in df: df = df[df.rain_3d_mm >= MIN_RAIN_3D].copy()
df = df.dropna(subset=["flood_label"]).reset_index(drop=True)
print(f"rows: {len(df):,} | flood rate: {df.flood_label.mean():.4f} | positives: {int(df.flood_label.sum())}")

# ---- find distinct flood EVENTS: positive dates within 3 days of each other = one storm ----
pos_dates = sorted(pd.to_datetime(df.loc[df.flood_label == 1, "date"].unique()))
events, start, prev = [], None, None
for d in pos_dates:
    if prev is None or (d - prev).days > 3:
        if start is not None: events.append((start, prev))
        start = d
    prev = d
if start is not None: events.append((start, prev))
print(f"distinct flood events found: {len(events)}")
for s, e in events: print("  ", s.date(), "->", e.date(), "| positives:", int(((df.date >= s) & (df.date <= e) & (df.flood_label == 1)).sum()))

def weights(d):
    return np.where(d.flood_label == 1, d.get("label_confidence", pd.Series("high", index=d.index)).map(CONF_WEIGHT).fillna(0.7), 1.0)

def fit(tr):
    pos = (tr.flood_label == 1).sum()
    m = xgb.XGBClassifier(n_estimators=200, max_depth=3, learning_rate=0.05, subsample=0.8, colsample_bytree=0.8,
                          min_child_weight=3, scale_pos_weight=(len(tr) - pos) / max(pos, 1), eval_metric="aucpr")
    m.fit(tr[FEATURES], tr.flood_label, sample_weight=weights(tr))
    return m

import os

OUT_DIR = os.path.dirname(os.path.abspath(__file__))

def metrics(y, p, thr):
    tn, fp, fn, tp = confusion_matrix(y, p >= thr, labels=[0, 1]).ravel()
    return dict(thr=round(float(thr), 2), POD=round(tp / max(tp + fn, 1), 2), FAR=round(fp / max(tp + fp, 1), 2),
                CSI=round(tp / max(tp + fn + fp, 1), 2), TP=int(tp), FP=int(fp), FN=int(fn))

def pooled_report(name, y, p):
    thr = max(np.arange(0.05, 0.96, 0.05), key=lambda t: metrics(y, p, t)["CSI"])
    m = metrics(y, p, thr)
    pr_auc = float(average_precision_score(y, p))
    chance = float(y.mean())
    print(f"[{name}] pooled PR-AUC {pr_auc:.3f} (chance = {chance:.3f}) | best-CSI threshold: {m}")
    print("    (threshold picked on these same predictions -> slightly optimistic; confirm on a final held-out event)")
    return {"pr_auc": round(pr_auc, 4), "chance": round(chance, 4), "best_threshold": m}

# ---- A) leave-one-event-out: train without the storm (+/-7 days buffer), test on that storm ----
per_event_results = []
leave_one_out_report = None
if len(events) >= 2:
    ys, ps = [], []
    for s, e in events:
        test = df[(df.date >= s - pd.Timedelta(days=1)) & (df.date <= e + pd.Timedelta(days=1))]
        train = df[(df.date < s - pd.Timedelta(days=7)) | (df.date > e + pd.Timedelta(days=7))]
        if test.flood_label.sum() == 0 or train.flood_label.sum() == 0: continue
        p = fit(train).predict_proba(test[FEATURES])[:, 1]
        ev_prauc = float(average_precision_score(test.flood_label, p))
        ev_chance = float(test.flood_label.mean())
        print(f"event {s.date()}: PR-AUC {ev_prauc:.3f} (chance {ev_chance:.3f})")
        per_event_results.append({
            "event_start": s.date().isoformat(),
            "event_end": e.date().isoformat(),
            "pr_auc": round(ev_prauc, 4),
            "chance": round(ev_chance, 4)
        })
        ys.append(test.flood_label.values); ps.append(p)
    if ys: leave_one_out_report = pooled_report("leave-one-event-out", np.concatenate(ys), np.concatenate(ps))
else:
    print("!! Fewer than 2 events: cannot test on a NEW storm. Ask Member 1 for more dated events.")

# ---- B) spatial CV: test on wards the model never saw ----
groups = df["ward"] if "ward" in df else df["cell_id"]
oof = np.zeros(len(df))
for tr_i, te_i in GroupKFold(n_splits=5).split(df, groups=groups):
    oof[te_i] = fit(df.iloc[tr_i]).predict_proba(df.iloc[te_i][FEATURES])[:, 1]
spatial_cv_report = pooled_report("spatial ward-grouped CV", df.flood_label.values, oof)

# ---- final model on everything (for the live pipeline), only after you trust the numbers above ----
final = fit(df)
final.save_model(os.path.join(OUT_DIR, "flood_xgb_real.json"))
json.dump(FEATURES, open(os.path.join(OUT_DIR, "features.json"), "w"), indent=2)

detected_events = [
    {
        "start": s.date().isoformat(),
        "end": e.date().isoformat(),
        "positives": int(((df.date >= s) & (df.date <= e) & (df.flood_label == 1)).sum())
    }
    for s, e in events
]

all_fi = pd.Series(final.feature_importances_, index=FEATURES).sort_values(ascending=False).round(4).to_dict()

model_report = {
    "row_count": int(len(df)),
    "flood_rate": round(float(df.flood_label.mean()), 4),
    "positives": int(df.flood_label.sum()),
    "features_used": FEATURES,
    "min_rain_3d": MIN_RAIN_3D,
    "conf_weight": CONF_WEIGHT,
    "xgboost_hyperparameters": {
        "n_estimators": 200,
        "max_depth": 3,
        "learning_rate": 0.05,
        "subsample": 0.8,
        "colsample_bytree": 0.8,
        "min_child_weight": 3,
        "scale_pos_weight_formula": "(len(tr) - pos) / max(pos, 1)",
        "eval_metric": "aucpr"
    },
    "detected_events": detected_events,
    "per_event": per_event_results,
    "leave_one_event_out": leave_one_out_report,
    "spatial_cv": spatial_cv_report,
    "feature_importances": all_fi
}

with open(os.path.join(OUT_DIR, "model_report.json"), "w") as f:
    json.dump(model_report, f, indent=2)

print(pd.Series(final.feature_importances_, FEATURES).sort_values(ascending=False).round(3).head(8))
print(f"Model artifacts and model_report.json saved to {OUT_DIR}")

