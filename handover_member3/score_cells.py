import json
import pandas as pd
import xgboost as xgb

def load(model_path="flood_xgb.json", features_path="features.json", rule_path="thresholds.json"):
    feats = json.load(open(features_path))
    rule = json.load(open(rule_path))
    model = xgb.XGBClassifier()
    model.load_model(model_path)
    return model, feats, rule

def score_day(df, model, feats, rule, n_ref=3026):
    """df = one row per cell for ONE date; must contain cell_id and every feature in features.json."""
    missing = [f for f in feats if f not in df.columns]
    if missing:
        raise ValueError(f"Missing feature columns: {missing}")
    keep = [c for c in ["cell_id", "ward", "lat", "lon"] if c in df.columns]
    out = df[keep].copy()
    out["score"] = model.predict_proba(df[feats])[:, 1]
    out["rank"] = out["score"].rank(ascending=False, method="first").astype(int)
    n = len(out)
    high_k = round(n * rule["high_top_k"] / n_ref)
    mod_k = round(n * rule["moderate_top_k"] / n_ref)
    out["level"] = "None"
    out.loc[out["rank"] <= mod_k, "level"] = "Moderate"
    out.loc[out["rank"] <= high_k, "level"] = "High"
    return out.sort_values("rank")