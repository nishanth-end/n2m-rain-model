from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field

class RootResponse(BaseModel):
    project: str = Field(..., description="Project name")
    status: str = Field(..., description="API operational status")
    available_routes: List[str] = Field(..., description="List of available API endpoints")
    mode: str = Field(..., description="Current operational mode (e.g. historical_replay)")
    model: str = Field(..., description="Active ML model description")
    version: str = Field(..., description="API version")

class ValidationStats(BaseModel):
    labelled_places_count: int = Field(10, description="Approximate number of labelled places")
    historical_events_count: int = Field(6, description="Number of historical events covered")
    spatial_resolution_km: float = Field(5.0, description="CHIRPS daily rainfall grid spatial resolution")
    holdout_event: str = Field("September 2022 (E2022_09)", description="Holdout evaluation event")
    pr_auc: float = Field(0.0026, description="Precision-Recall AUC on Sept 2022 holdout")
    random_chance_auc: float = Field(0.0013, description="Random chance baseline PR-AUC")
    high_hit_rate_pct: float = Field(8.3, description="Hit rate for High rank (top 150) on flood days")
    high_random_baseline_pct: float = Field(5.0, description="Random baseline for top 150 cells (5%)")
    moderate_high_hit_rate_pct: float = Field(25.0, description="Hit rate for Moderate + High (top 300) on flood days")
    moderate_high_random_baseline_pct: float = Field(9.9, description="Random baseline for top 300 cells (~10%)")

class AboutResponse(BaseModel):
    project_title: str
    description: str
    nature_of_output: str
    operational_warnings: List[str]
    model_details: Dict[str, Any]
    validation_limitations: ValidationStats
    guidance_notes: List[str]

class DatesResponse(BaseModel):
    dates: List[str] = Field(..., description="Chronologically sorted historical replay dates")
    total_dates: int = Field(..., description="Total count of available dates")
    min_date: str = Field(..., description="Earliest available date")
    max_date: str = Field(..., description="Latest available date")
    mode: str = Field("historical_replay", description="Data source mode")

class RiskCell(BaseModel):
    cell_id: int
    date: str
    lat: float
    lon: float
    ward: int
    score: float
    rank: int
    level: str  # High, Moderate, None

class RiskResponse(BaseModel):
    date: str
    total_cells: int
    high_count: int
    moderate_count: int
    none_count: int
    mode: str
    is_latest_replay: bool = False
    is_live: bool = False
    disclaimer: str
    cells: List[RiskCell]

class TopRankedCellSummary(BaseModel):
    cell_id: int
    ward: int
    score: float
    rank: int
    level: str
    lat: float
    lon: float

class SummaryResponse(BaseModel):
    date: str
    total_cells_scored: int
    high_count: int
    moderate_count: int
    none_count: int
    top_ranked_cell: Optional[TopRankedCellSummary]
    average_score: float
    min_score: float
    max_score: float
    data_mode: str
    disclaimer: str

class TelegramPreviewResponse(BaseModel):
    date: str
    status: str
    enabled: bool
    formatted_message: str
    note: str
