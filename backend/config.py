import os
from pathlib import Path
from pydantic import BaseModel

BASE_DIR = Path(__file__).resolve().parent.parent
HANDOVER_DIR = BASE_DIR / "handover_member3"

class Settings(BaseModel):
    # App
    PROJECT_NAME: str = "Bengaluru Flood Susceptibility Model (Historical Replay API)"
    API_VERSION: str = "1.0.0"
    MODE: str = "historical_replay"
    
    # Handover ML & Data Assets
    HANDOVER_DIR: Path = HANDOVER_DIR
    PARQUET_PATH: Path = HANDOVER_DIR / "flood_replay_E2022_09.parquet"
    STATIC_CELLS_PATH: Path = HANDOVER_DIR / "cells_static.csv"
    PIXEL_MAP_PATH: Path = HANDOVER_DIR / "cell_pixel_map.csv"
    FEATURES_PATH: Path = HANDOVER_DIR / "features.json"
    THRESHOLDS_PATH: Path = HANDOVER_DIR / "thresholds.json"
    
    # Replay Holdout Model (Strictly for Sept 2022 replay)
    HOLDOUT_MODEL_PATH: Path = HANDOVER_DIR / "flood_xgb_holdout_E2022_09.json"
    FINAL_MODEL_PATH: Path = HANDOVER_DIR / "flood_xgb.json"
    
    # Reference cell count for Bengaluru grid
    N_REFERENCE_CELLS: int = 3026
    
    # Experimental Live Pipeline Scaffolding (Disabled by default)
    ENABLE_EXPERIMENTAL_LIVE_PIPELINE: bool = False
    
    # Optional Telegram Integration (Demo/Sandbox only, disabled by default)
    TELEGRAM_ENABLED: bool = False
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""

def get_settings() -> Settings:
    return Settings(
        PARQUET_PATH=Path(os.getenv("REPLAY_PARQUET_PATH", str(HANDOVER_DIR / "flood_replay_E2022_09.parquet"))),
        STATIC_CELLS_PATH=Path(os.getenv("STATIC_CELLS_PATH", str(HANDOVER_DIR / "cells_static.csv"))),
        PIXEL_MAP_PATH=Path(os.getenv("PIXEL_MAP_PATH", str(HANDOVER_DIR / "cell_pixel_map.csv"))),
        FEATURES_PATH=Path(os.getenv("FEATURES_PATH", str(HANDOVER_DIR / "features.json"))),
        THRESHOLDS_PATH=Path(os.getenv("THRESHOLDS_PATH", str(HANDOVER_DIR / "thresholds.json"))),
        HOLDOUT_MODEL_PATH=Path(os.getenv("HOLDOUT_MODEL_PATH", str(HANDOVER_DIR / "flood_xgb_holdout_E2022_09.json"))),
        FINAL_MODEL_PATH=Path(os.getenv("FINAL_MODEL_PATH", str(HANDOVER_DIR / "flood_xgb.json"))),
        ENABLE_EXPERIMENTAL_LIVE_PIPELINE=os.getenv("ENABLE_EXPERIMENTAL_LIVE_PIPELINE", "false").lower() in ("true", "1", "yes"),
        TELEGRAM_ENABLED=os.getenv("TELEGRAM_ENABLED", "false").lower() in ("true", "1", "yes"),
        TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID", ""),
    )

settings = get_settings()
