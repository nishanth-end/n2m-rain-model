import os
import sys
from pathlib import Path
from pydantic import BaseModel
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
HANDOVER_DIR = BASE_DIR / "handover_member3"

# Automatically load .env if present in project root (skip in unit test runner to preserve baseline defaults)
if "PYTEST_CURRENT_TEST" not in os.environ and not any("pytest" in arg for arg in sys.argv):
    load_dotenv(BASE_DIR / ".env")

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
    
    # Rainfall Provider Configuration (Open-Meteo REST API)
    RAINFALL_PROVIDER_NAME: str = "Open-Meteo Weather API"
    RAINFALL_API_URL: str = "https://api.open-meteo.com/v1/forecast"
    RAINFALL_CITY_LAT: float = 12.9716
    RAINFALL_CITY_LON: float = 77.5946
    RAINFALL_TIMEZONE: str = "Asia/Kolkata"
    RAINFALL_CACHE_TTL_SECONDS: int = 3600
    RAINFALL_TIMEOUT_SECONDS: int = 5

    # Optional Telegram Integration (Demo/Sandbox only, disabled by default)
    TELEGRAM_ENABLED: bool = False
    TELEGRAM_BOT_TOKEN: str = ""
    TELEGRAM_CHAT_ID: str = ""
    TELEGRAM_AUTHORIZED_CHAT_IDS: str = ""
    TELEGRAM_BOT_USERNAME: str = "N2M_Flood_Demo_Bot"

    # CORS Configuration for Deployed Frontends (e.g. Vercel)
    CORS_ORIGINS: str = ""

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
        RAINFALL_PROVIDER_NAME=os.getenv("RAINFALL_PROVIDER_NAME", "Open-Meteo Weather API"),
        RAINFALL_API_URL=os.getenv("RAINFALL_API_URL", "https://api.open-meteo.com/v1/forecast"),
        RAINFALL_CITY_LAT=float(os.getenv("RAINFALL_CITY_LAT", "12.9716")),
        RAINFALL_CITY_LON=float(os.getenv("RAINFALL_CITY_LON", "77.5946")),
        RAINFALL_TIMEZONE=os.getenv("RAINFALL_TIMEZONE", "Asia/Kolkata"),
        RAINFALL_CACHE_TTL_SECONDS=int(os.getenv("RAINFALL_CACHE_TTL_SECONDS", "3600")),
        RAINFALL_TIMEOUT_SECONDS=int(os.getenv("RAINFALL_TIMEOUT_SECONDS", "5")),
        TELEGRAM_ENABLED=os.getenv("TELEGRAM_ENABLED", "false").lower() in ("true", "1", "yes"),
        TELEGRAM_BOT_TOKEN=os.getenv("TELEGRAM_BOT_TOKEN", ""),
        TELEGRAM_CHAT_ID=os.getenv("TELEGRAM_CHAT_ID", ""),
        TELEGRAM_AUTHORIZED_CHAT_IDS=os.getenv("TELEGRAM_AUTHORIZED_CHAT_IDS", ""),
        TELEGRAM_BOT_USERNAME=os.getenv("TELEGRAM_BOT_USERNAME", "N2M_Flood_Demo_Bot"),
        CORS_ORIGINS=os.getenv("CORS_ORIGINS", ""),
    )

settings = get_settings()
