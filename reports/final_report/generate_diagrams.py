"""
N²M Flood Prediction Model — Report Diagrams Generator
======================================================
Generates high-resolution publication-grade technical architecture diagrams,
flowcharts, and sequence workflows for the final academic project report.
"""

import os
os.environ['MPLCONFIGDIR'] = '/tmp'
import matplotlib.pyplot as plt
import matplotlib.patches as patches

# Set global styles
plt.rcParams['font.family'] = 'sans-serif'
plt.rcParams['font.size'] = 9.5
plt.rcParams['axes.edgecolor'] = '#cbd5e1'
plt.rcParams['axes.linewidth'] = 0.8

OUT_DIR = "reports/final_report/figures"
os.makedirs(OUT_DIR, exist_ok=True)

def draw_box(ax, x, y, w, h, title, subtitle=None, bg="#f8fafc", edge="#0f172a", title_color="#0f172a", fontsize=9):
    rect = patches.FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.03",
        linewidth=1.2, edgecolor=edge, facecolor=bg, zorder=2
    )
    ax.add_patch(rect)
    if subtitle:
        ax.text(x + w/2, y + h*0.62, title, ha="center", va="center", weight="bold", color=title_color, fontsize=fontsize, zorder=3)
        ax.text(x + w/2, y + h*0.32, subtitle, ha="center", va="center", color="#475569", fontsize=fontsize*0.82, zorder=3)
    else:
        ax.text(x + w/2, y + h/2, title, ha="center", va="center", weight="bold", color=title_color, fontsize=fontsize, zorder=3)

def draw_arrow(ax, x1, y1, x2, y2, label=None, color="#0284c7", lw=1.5):
    ax.annotate(
        "", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="->", color=color, lw=lw, shrinkA=3, shrinkB=3),
        zorder=4
    )
    if label:
        ax.text((x1+x2)/2, (y1+y2)/2 + 0.025, label, ha="center", va="bottom", fontsize=7.5, color="#0369a1", weight="bold", zorder=5)

# -----------------------------------------------------------------------------
# Figure 1: Overall System Architecture
# -----------------------------------------------------------------------------
def make_fig1():
    fig, ax = plt.subplots(figsize=(11, 6.5), dpi=300)
    ax.set_xlim(0, 1.1)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.55, 0.96, "Figure 1: Overall System Architecture of N²M Flood Prediction Model", 
            ha="center", va="center", weight="bold", fontsize=12, color="#0f172a")

    # Column 1: Data Sources & Pipeline
    draw_box(ax, 0.03, 0.72, 0.20, 0.18, "Data Ingestion Pipeline", "CHIRPS Rain, SRTM DEM,\nESA WorldCover, OSM Vectors", bg="#e0f2fe", edge="#0284c7")
    draw_box(ax, 0.03, 0.44, 0.20, 0.22, "Spatial Discretization", "3,026 Grid Cells (500m×500m)\n10 Static Terrain Indices\n8 Dynamic Rain Matrices", bg="#f0fdf4", edge="#16a34a")
    draw_box(ax, 0.03, 0.16, 0.20, 0.22, "Master Parquet Storage", "1.76M Rows × 42 Cols\n583 Candidate Storm Days\nHistorical Flood Labels", bg="#f8fafc", edge="#64748b")
    draw_arrow(ax, 0.13, 0.72, 0.13, 0.66)
    draw_arrow(ax, 0.13, 0.44, 0.13, 0.38)

    # Column 2: ML Engine & Holdout Scoring
    draw_box(ax, 0.30, 0.52, 0.22, 0.35, "Machine Learning Engine\n(XGBoost Classifier)", 
             "Holdout Model: E2022_09 Sequestered\nscale_pos_weight = 89.16\nInputs: 18 Engineered Features\nOutput: Raw Susceptibility Scores", 
             bg="#fef3c7", edge="#d97706")
    draw_box(ax, 0.30, 0.16, 0.22, 0.28, "Daily Rank-Based Thresholding", 
             "Daily Dense Ranking (1 to 3026)\n• High: Top 150 (Top 5%)\n• Moderate: Ranks 151-300 (5%)\n• Baseline: Ranks 301-3026 (90%)", 
             bg="#ffedd5", edge="#ea580c")
    draw_arrow(ax, 0.23, 0.27, 0.30, 0.27, label="Features")
    draw_arrow(ax, 0.41, 0.52, 0.41, 0.44, label="Raw Probabilities")

    # Column 3: Asynchronous Backend API
    draw_box(ax, 0.58, 0.20, 0.22, 0.68, "FastAPI Application Server\n(Hosted on Render)", 
             "Uvicorn ASGI Gateway (Port 8000)\n\nCore Service Modules:\n• Replay Service (Parquet Slices)\n• Rainfall Service (Open-Meteo Cache)\n• Telegram Service (Bot Controller)\n• Data Loader (Holdout Cache)\n\nREST API Routes:\nGET /api/dates, /api/risk, /api/summary\nPOST /api/telegram/send-demo, /webhook", 
             bg="#f1f5f9", edge="#334155")
    draw_arrow(ax, 0.52, 0.30, 0.58, 0.30, label="Ranked Tiers")

    # Column 4: Client & Integration
    draw_box(ax, 0.86, 0.54, 0.21, 0.34, "React + Vite Frontend\n(Hosted on Vercel)", 
             "Cartographic Interface\n• Leaflet 60 FPS Canvas Grid\n• Interactive Replay (24 Days)\n• Cell Telemetry Inspector\n• Spatial & Tier Filters\n• Live Scaffolding & Demo", 
             bg="#e0e7ff", edge="#4f46e5")
    draw_box(ax, 0.86, 0.16, 0.21, 0.28, "Telegram Demonstration Bot\n(@N2M_Flood_Bot)", 
             "Authorized Evaluator Gateway\n• /start, /help, /status\n• /demo [YYYY-MM-DD]\n• Token-Safe Server Dispatch\n• Scientific Disclaimers", 
             bg="#fce7f3", edge="#db2777")
    
    draw_arrow(ax, 0.80, 0.70, 0.86, 0.70, label="JSON REST")
    draw_arrow(ax, 0.86, 0.62, 0.80, 0.62)
    draw_arrow(ax, 0.80, 0.30, 0.86, 0.30, label="Bot API")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig1_overall_system_architecture.png"), dpi=300)
    plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 2: Data Processing Pipeline
# -----------------------------------------------------------------------------
def make_fig2():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.5, 0.95, "Figure 2: Data Ingestion and Feature Processing Pipeline", 
            ha="center", va="center", weight="bold", fontsize=11.5, color="#0f172a")

    steps = [
        ("1. Raw Geospatial Ingestion", "CHIRPS (0.05°)\nSRTM 30m DEM\nESA WorldCover\nOSM Hydrography", 0.05, 0.40, 0.16, 0.42, "#e0f2fe", "#0284c7"),
        ("2. Spatial Discretization", "Bengaluru 198 Wards\n3,026 Cartesian Cells\n(500m × 500m)\nCell-to-Pixel Indexing", 0.28, 0.40, 0.16, 0.42, "#f0fdf4", "#16a34a"),
        ("3. Hydrological Extraction", "Topographic Wetness (TWI)\nHAND to Nearest Drainage\nElevation, Slope, Catchment\nLake & Drain Proximities", 0.51, 0.40, 0.18, 0.42, "#fef3c7", "#d97706"),
        ("4. Feature Assembly & ML Matrix", "10 Static Terrain Indices\n8 Dynamic Precipitation Lags\n72,624 Replay Matrix Rows\nStrict Holdout Splitting", 0.76, 0.40, 0.19, 0.42, "#f1f5f9", "#334155"),
    ]

    for title, sub, x, y, w, h, bg, edge in steps:
        draw_box(ax, x, y, w, h, title, sub, bg=bg, edge=edge, fontsize=8.5)

    draw_arrow(ax, 0.21, 0.61, 0.28, 0.61)
    draw_arrow(ax, 0.44, 0.61, 0.51, 0.61)
    draw_arrow(ax, 0.69, 0.61, 0.76, 0.61)

    # Sub-note
    ax.text(0.5, 0.15, "Result: Immutable static cell registry (cells_static.csv), spatial mapping table (cell_pixel_map.csv),\nand historical replay matrix (flood_replay_E2022_09.parquet).",
            ha="center", va="center", style="italic", fontsize=8.5, color="#475569")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig2_data_processing_pipeline.png"), dpi=300)
    plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 3: Model Training Workflow
# -----------------------------------------------------------------------------
def make_fig3():
    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=300)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.5, 0.95, "Figure 3: XGBoost Training and Out-of-Sample Holdout Workflow", 
            ha="center", va="center", weight="bold", fontsize=11.5, color="#0f172a")

    draw_box(ax, 0.04, 0.48, 0.18, 0.36, "Historical Flood Events", "6 Documented Events\n(2017, 2021, 2022, 2023)\n10 Distinct Seed Cells\n3x3 Grid Label Expansion", bg="#f1f5f9", edge="#475569")
    draw_box(ax, 0.28, 0.58, 0.20, 0.26, "Training Partition\n(5 Historical Events)", "52 Positive Cell-Days\nscale_pos_weight = 89.16\nClass Imbalance Handling", bg="#f0fdf4", edge="#16a34a")
    draw_box(ax, 0.28, 0.22, 0.20, 0.26, "Sequestered Holdout\n(September 2022 Event)", "E2022_09 (24 Days)\n188 Positive Cell-Days\nStrictly Never Seen in Train", bg="#fee2e2", edge="#dc2626")

    draw_arrow(ax, 0.22, 0.68, 0.28, 0.70, label="Train Split")
    draw_arrow(ax, 0.22, 0.55, 0.28, 0.35, label="Holdout Split")

    draw_box(ax, 0.54, 0.58, 0.20, 0.26, "XGBoost Estimator\n(binary:logistic)", "Trees: 100, Depth: 6\nLearning Rate: 0.1\nFeatures: 18 Topo+Rain", bg="#fef3c7", edge="#d97706")
    draw_arrow(ax, 0.48, 0.71, 0.54, 0.71)

    draw_box(ax, 0.79, 0.40, 0.18, 0.44, "Empirical Holdout Evaluation", "PR-AUC: 0.0026 vs 0.0013 (2.0x)\nHigh Tier Hit Rate: 8.3% (1.66x)\nTop 10% Hit Rate: 25.0% (2.53x)\nValidated Spatial Lift", bg="#e0f2fe", edge="#0284c7")
    draw_arrow(ax, 0.74, 0.71, 0.79, 0.65)
    draw_arrow(ax, 0.48, 0.35, 0.79, 0.50, label="Test Evaluation")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig3_model_training_workflow.png"), dpi=300)
    plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 4: Inference and Susceptibility Ranking Workflow
# -----------------------------------------------------------------------------
def make_fig4():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.5, 0.95, "Figure 4: Daily Inference and Susceptibility Ranking Logic", 
            ha="center", va="center", weight="bold", fontsize=11.5, color="#0f172a")

    draw_box(ax, 0.04, 0.45, 0.18, 0.36, "Active Date Input\n(3,026 Cell Rows)", "10 Static Cell Features\n8 Antecedent Rain Lags\n(Same-Day Concurrent)", bg="#f8fafc", edge="#0f172a")
    draw_box(ax, 0.27, 0.45, 0.18, 0.36, "XGBoost Model\npredict_proba()", "Computes Raw Daily\nSusceptibility Probabilities\nScores Range: 0.001 to 0.35", bg="#fef3c7", edge="#d97706")
    draw_box(ax, 0.50, 0.45, 0.18, 0.36, "Dense Spatial Ranking", "Rank = DenseRank(Score)\nAscending=False\nRank 1 = Highest Daily Risk", bg="#ffedd5", edge="#ea580c")
    draw_box(ax, 0.73, 0.36, 0.23, 0.48, "Priority Alert Tiers", "• High (Tier 1):\nRanks 1-150 (Top 5%)\n• Moderate (Tier 2):\nRanks 151-300 (Next 5%)\n• Baseline Risk (Tier 3):\nRanks 301-3026 (Remaining 90%)", bg="#f0fdf4", edge="#16a34a")

    draw_arrow(ax, 0.22, 0.63, 0.27, 0.63)
    draw_arrow(ax, 0.45, 0.63, 0.50, 0.63)
    draw_arrow(ax, 0.68, 0.63, 0.73, 0.63)

    ax.text(0.5, 0.16, "Core Rule: Replaces arbitrary uncalibrated probability cutoffs with robust daily relative rank prioritization.",
            ha="center", va="center", style="italic", fontsize=8.5, color="#475569")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig4_inference_ranking_workflow.png"), dpi=300)
    plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 5: Backend / API Architecture
# -----------------------------------------------------------------------------
def make_fig5():
    fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.5, 0.95, "Figure 5: FastAPI Backend Architecture and Core Subsystems", 
            ha="center", va="center", weight="bold", fontsize=11.5, color="#0f172a")

    # Left: Web Gateway & Middleware
    draw_box(ax, 0.04, 0.25, 0.20, 0.58, "ASGI Entry & Middleware\n(FastAPI / Uvicorn)", 
             "• Dynamic CORS Middleware\n  (Whitelists Vercel & Dev)\n• Health Check Route (/health)\n• Root Diagnostic Route (/)\n• Pydantic Schema Validation\n• Lifespan Asset Loader\n  (Preloads Parquet & Model)", 
             bg="#f1f5f9", edge="#334155")

    # Center: Service Layer
    draw_box(ax, 0.30, 0.65, 0.36, 0.20, "Replay Service (replay_service.py)", "Queries pre-scored 72k-row Parquet slice\nCalculates rank percentiles, filters & summaries", bg="#e0f2fe", edge="#0284c7")
    draw_box(ax, 0.30, 0.42, 0.36, 0.20, "Rainfall Service (rainfall_service.py)", "Fetches Open-Meteo REST API data\nComputes rolling features (3d, 7d, 14d) & caches", bg="#fef3c7", edge="#d97706")
    draw_box(ax, 0.30, 0.18, 0.36, 0.20, "Telegram Service (telegram_service.py)", "Whitelist authorization gate, command parser\nOutbound HTTP message dispatcher to Telegram API", bg="#fce7f3", edge="#db2777")

    draw_arrow(ax, 0.24, 0.75, 0.30, 0.75)
    draw_arrow(ax, 0.24, 0.52, 0.30, 0.52)
    draw_arrow(ax, 0.24, 0.28, 0.30, 0.28)

    # Right: Data Assets
    draw_box(ax, 0.73, 0.22, 0.23, 0.62, "ML & Data Assets\n(handover_member3/)", 
             "• flood_xgb_holdout_E2022_09.json\n  (214 KB Holdout Model)\n• flood_replay_E2022_09.parquet\n  (921 KB 24-Day Replay)\n• cells_static.csv\n  (268 KB Terrain Mesh)\n• cell_pixel_map.csv\n  (193 KB Rain Index)\n• features.json / thresholds.json", 
             bg="#f0fdf4", edge="#16a34a")

    draw_arrow(ax, 0.66, 0.75, 0.73, 0.75)
    draw_arrow(ax, 0.66, 0.52, 0.73, 0.52)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig5_backend_api_architecture.png"), dpi=300)
    plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 6: Frontend Architecture
# -----------------------------------------------------------------------------
def make_fig6():
    fig, ax = plt.subplots(figsize=(10.5, 5.5), dpi=300)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.5, 0.95, "Figure 6: Frontend Component Architecture and Visualization Engine", 
            ha="center", va="center", weight="bold", fontsize=11.5, color="#0f172a")

    draw_box(ax, 0.04, 0.25, 0.20, 0.58, "Top-Level Application\n(App.jsx / Router)", 
             "• Navigation Header\n• Global State Manager\n  (activeDate, selectedCell,\n   apiOnline status)\n• Shared Editorial Footer\n• Content Configurator\n  (content.js)\n• Central API Client (client.js)", 
             bg="#f1f5f9", edge="#334155")

    # Center Pages
    draw_box(ax, 0.30, 0.68, 0.32, 0.17, "FloodMapPage.jsx", "Leaflet Canvas 60 FPS Engine\nInteractive Replay & Scrubbing\nTarget Cell Attribute Inspector", bg="#e0e7ff", edge="#4f46e5")
    draw_box(ax, 0.30, 0.48, 0.32, 0.17, "LiveSimulationPage.jsx", "Meteorological Context Panel\nRolling Precipitation Explorer\nResearch Sandbox Indicator", bg="#e0f2fe", edge="#0284c7")
    draw_box(ax, 0.30, 0.28, 0.32, 0.17, "TelegramPage.jsx", "Demonstration Bot Control\nLive Dispatch Trigger Button\nCommand Reference & Notice", bg="#fce7f3", edge="#db2777")
    draw_box(ax, 0.30, 0.08, 0.32, 0.17, "HomePage.jsx & CreditsPage.jsx", "Project Overview & Methodology\nAcademic Credits & References", bg="#f0fdf4", edge="#16a34a")

    draw_arrow(ax, 0.24, 0.76, 0.30, 0.76)
    draw_arrow(ax, 0.24, 0.56, 0.30, 0.56)
    draw_arrow(ax, 0.24, 0.36, 0.30, 0.36)
    draw_arrow(ax, 0.24, 0.16, 0.30, 0.16)

    # Right: Leaflet Canvas Engine
    draw_box(ax, 0.69, 0.28, 0.27, 0.55, "Custom Leaflet Canvas Engine", 
             "• Standard OpenStreetMap Tiles\n• Canvas Marker Mesh (3,026 dots)\n• Priority Tier Styling:\n  - Red: High (#dc2626)\n  - Amber: Moderate (#ea580c)\n  - Gray: Baseline (#94a3b8)\n• Fast Viewport Caching\n• Coordinate Recenter & Search", 
             bg="#fef3c7", edge="#d97706")

    draw_arrow(ax, 0.62, 0.76, 0.69, 0.65)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig6_frontend_architecture.png"), dpi=300)
    plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 7: Historical Replay Workflow
# -----------------------------------------------------------------------------
def make_fig7():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.5, 0.95, "Figure 7: Historical Replay Sequence and Daily Spatial Updating", 
            ha="center", va="center", weight="bold", fontsize=11.5, color="#0f172a")

    draw_box(ax, 0.04, 0.45, 0.18, 0.36, "User Replay Action", "• Step Next/Prev Date\n• Dropdown Select\n• Play Replay (1.8s loop)\n(24 Available Dates)", bg="#e0e7ff", edge="#4f46e5")
    draw_box(ax, 0.27, 0.45, 0.19, 0.36, "API Client Fetch", "GET /api/risk?date=...\nGET /api/summary?date=...\nCached in Memory", bg="#f1f5f9", edge="#334155")
    draw_box(ax, 0.51, 0.45, 0.20, 0.36, "Backend Slice Lookup", "Extracts 3,026 cell rows\nfrom Parquet holdout matrix\nCalculates citywide metrics", bg="#e0f2fe", edge="#0284c7")
    draw_box(ax, 0.76, 0.45, 0.20, 0.36, "Canvas Mesh Redraw", "Colors 3,026 circles:\n• 150 High (Red)\n• 150 Moderate (Amber)\n• 2,726 None (Gray)", bg="#f0fdf4", edge="#16a34a")

    draw_arrow(ax, 0.22, 0.63, 0.27, 0.63)
    draw_arrow(ax, 0.46, 0.63, 0.51, 0.63)
    draw_arrow(ax, 0.71, 0.63, 0.76, 0.63)

    ax.text(0.5, 0.18, "Replay benchmark spans September 2022 monsoon event (2022-08-22 to 2022-09-14) during historic citywide inundation.",
            ha="center", va="center", style="italic", fontsize=8.5, color="#475569")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig7_historical_replay_workflow.png"), dpi=300)
    plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 8: Telegram Integration Sequence Diagram
# -----------------------------------------------------------------------------
def make_fig8():
    fig, ax = plt.subplots(figsize=(10.5, 5.8), dpi=300)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.5, 0.96, "Figure 8: Telegram Demonstration Dispatch Sequence Diagram", 
            ha="center", va="center", weight="bold", fontsize=11.5, color="#0f172a")

    # Lifelines
    actors = [
        ("Evaluator\n(Browser)", 0.12),
        ("FastAPI Backend\n(Render)", 0.38),
        ("Telegram Service\n(Internal)", 0.64),
        ("Telegram Bot API\n(api.telegram.org)", 0.88),
    ]

    for title, x in actors:
        draw_box(ax, x - 0.08, 0.82, 0.16, 0.10, title, bg="#f1f5f9", edge="#0f172a", fontsize=8.5)
        ax.plot([x, x], [0.12, 0.82], color="#cbd5e1", linestyle="--", lw=1.2, zorder=1)

    # Messages
    y_levels = [0.72, 0.62, 0.50, 0.38, 0.26, 0.16]
    
    # 1. Click Send Demo
    draw_arrow(ax, 0.12, 0.72, 0.38, 0.72, label="POST /api/telegram/send-demo {date, chat_id}")
    # 2. Check Whitelist
    draw_arrow(ax, 0.38, 0.62, 0.64, 0.62, label="is_authorized(chat_id)")
    # 3. Format Bulletin
    draw_arrow(ax, 0.64, 0.50, 0.64, 0.50)
    ax.text(0.64, 0.52, "format_demo_message()\n(Add safety disclaimers & top 5 cells)", ha="center", va="bottom", fontsize=7.5, color="#475569")
    # 4. Outbound HTTP
    draw_arrow(ax, 0.64, 0.38, 0.88, 0.38, label="POST /sendMessage {chat_id, text}")
    # 5. Telegram Response
    draw_arrow(ax, 0.88, 0.26, 0.38, 0.26, label="200 OK / Error JSON", color="#16a34a")
    # 6. UI Feedback
    draw_arrow(ax, 0.38, 0.16, 0.12, 0.16, label="{sent: true/false, reason}", color="#16a34a")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig8_telegram_sequence_diagram.png"), dpi=300)
    plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 9: Cloud Deployment Architecture
# -----------------------------------------------------------------------------
def make_fig9():
    fig, ax = plt.subplots(figsize=(10.5, 5.2), dpi=300)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.5, 0.95, "Figure 9: Cloud Deployment Architecture on Vercel and Render", 
            ha="center", va="center", weight="bold", fontsize=11.5, color="#0f172a")

    # User Browser
    draw_box(ax, 0.04, 0.40, 0.18, 0.38, "Client Web Browser", "End-User / Researcher\nAccessing System via HTTPS\n(Desktop / Mobile)", bg="#f8fafc", edge="#0f172a")

    # Vercel Frontend
    draw_box(ax, 0.30, 0.40, 0.25, 0.38, "Vercel Cloud Platform\n(Free Tier Edge CDN)", 
             "React 18 + Vite Production Build\n• Output Directory: dist/\n• Rewrites: /(.*) -> /index.html (SPA)\n• Environment: VITE_API_BASE_URL\n• Assets: 57 kB CSS, 377 kB JS (Gzip: 120 kB)", 
             bg="#e0e7ff", edge="#4f46e5")

    # Render Backend
    draw_box(ax, 0.65, 0.40, 0.31, 0.46, "Render Cloud Platform\n(Free Tier Web Service)", 
             "FastAPI / Uvicorn ASGI Server (Port 10000)\n• Health Probe: /health\n• Environment Configuration:\n  - MODE=historical_replay\n  - CORS_ORIGINS=*\n  - TELEGRAM_ENABLED=true/false\n  - TELEGRAM_BOT_TOKEN & CHAT_ID\n• Bundled Assets: handover_member3/ (1.9 MB)\n• Resident RAM: ~15 MB (<4% of 512 MB)", 
             bg="#f1f5f9", edge="#334155")

    draw_arrow(ax, 0.22, 0.65, 0.30, 0.65, label="HTTPS Web Request")
    draw_arrow(ax, 0.55, 0.65, 0.65, 0.65, label="REST API (CORS)")
    draw_arrow(ax, 0.22, 0.48, 0.65, 0.48, label="Direct API Calls")

    ax.text(0.5, 0.14, "Free-Tier Note: Render instance sleeps after 15 min of inactivity; first cold-start request incurs ~30-50s wake-up delay.",
            ha="center", va="center", style="italic", fontsize=8.5, color="#64748b")

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig9_cloud_deployment_architecture.png"), dpi=300)
    plt.close(fig)

# -----------------------------------------------------------------------------
# Figure 10: User Interaction Flowchart
# -----------------------------------------------------------------------------
def make_fig10():
    fig, ax = plt.subplots(figsize=(10, 5), dpi=300)
    ax.set_xlim(0, 1.0)
    ax.set_ylim(0, 1.0)
    ax.axis('off')

    ax.text(0.5, 0.95, "Figure 10: User Interaction and Research Navigation Flowchart", 
            ha="center", va="center", weight="bold", fontsize=11.5, color="#0f172a")

    draw_box(ax, 0.04, 0.42, 0.16, 0.35, "1. Visit Homepage", "• Read Project Overview\n• Review Objectives\n• Inspect Disclaimers\n• Access Navigation Tabs", bg="#f8fafc", edge="#0f172a")
    draw_box(ax, 0.24, 0.42, 0.18, 0.35, "2. Explore Flood Map", "• View 3,026 Grid Cells\n• Step / Play 24-Day Replay\n• Apply Tier Filters (High/Mod)\n• Find Specific Cell ID", bg="#e0e7ff", edge="#4f46e5")
    draw_box(ax, 0.46, 0.42, 0.18, 0.35, "3. Cell Inspector", "• Click Cell on Canvas\n• Inspect Elevation & HAND\n• Review TWI & Rainfall\n• Analyze Spatial Rank", bg="#fef3c7", edge="#d97706")
    draw_box(ax, 0.68, 0.42, 0.16, 0.35, "4. Live Simulation", "• View Open-Meteo Context\n• Examine Rolling Rain\n• Inspect Pipeline Scaffold\n• Compare Weather Shifts", bg="#e0f2fe", edge="#0284c7")
    draw_box(ax, 0.86, 0.42, 0.12, 0.35, "5. Telegram", "• Review Bot\n• Test Dispatch\n• Verify Notice", bg="#fce7f3", edge="#db2777")

    draw_arrow(ax, 0.20, 0.60, 0.24, 0.60)
    draw_arrow(ax, 0.42, 0.60, 0.46, 0.60)
    draw_arrow(ax, 0.64, 0.60, 0.68, 0.60)
    draw_arrow(ax, 0.84, 0.60, 0.86, 0.60)

    fig.tight_layout()
    fig.savefig(os.path.join(OUT_DIR, "fig10_user_interaction_flowchart.png"), dpi=300)
    plt.close(fig)

if __name__ == "__main__":
    print("Generating Figure 1...")
    make_fig1()
    print("Generating Figure 2...")
    make_fig2()
    print("Generating Figure 3...")
    make_fig3()
    print("Generating Figure 4...")
    make_fig4()
    print("Generating Figure 5...")
    make_fig5()
    print("Generating Figure 6...")
    make_fig6()
    print("Generating Figure 7...")
    make_fig7()
    print("Generating Figure 8...")
    make_fig8()
    print("Generating Figure 9...")
    make_fig9()
    print("Generating Figure 10...")
    make_fig10()
    print("All 10 report diagrams successfully generated in", OUT_DIR)
