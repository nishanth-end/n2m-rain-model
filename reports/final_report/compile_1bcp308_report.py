"""
Compiles the 1BCP308 - 3rd Sem Community Project Report (2026-2027)
for N²M Flood Prediction Model into:
  - reports/final_report/1BCP308_Community_Project_Report.md
  - reports/final_report/N2M_1BCP308_Community_Project_Report.docx
"""

import os
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

OUT_DIR = "reports/final_report"
MD_PATH = os.path.join(OUT_DIR, "1BCP308_Community_Project_Report.md")
DOCX_PATH = os.path.join(OUT_DIR, "N2M_1BCP308_Community_Project_Report.docx")

# Palette
NAVY = RGBColor(15, 23, 42)         # #0f172a
BLUE = RGBColor(30, 58, 138)        # #1e3a8a
SLATE = RGBColor(30, 41, 59)        # #1e293b
MUTED = RGBColor(100, 116, 139)     # #64748b
LABEL_BG = "f1f5f9"                 # Light slate fill for left label column
HDR_BG = "0f172a"                   # Deep navy header
BORDER_HEX = "94a3b8"               # Clean table border

ASSETS = {
    "arch": "reports/final_report/figures/fig1_overall_system_architecture.png",
    "pipeline": "reports/final_report/figures/fig2_data_processing_pipeline.png",
    "ranking": "reports/final_report/figures/fig4_inference_ranking_workflow.png",
    "rain_chart": "reports/final_report/figures/fig2_sept2022_rainfall.png",
    "landing": "presentation/screenshots/01_landing_page.png",
    "map_insp": "presentation/screenshots/02_flood_map_inspector.png",
    "live_sim": "presentation/screenshots/03_live_simulation.png",
    "telegram": "presentation/screenshots/04_telegram_sandbox.png",
}

def set_cell_bg(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=130, right=130):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'''
        <w:tcMar {nsdecls("w")}>
            <w:top w:w="{top}" w:type="dxa"/>
            <w:bottom w:w="{bottom}" w:type="dxa"/>
            <w:left w:w="{left}" w:type="dxa"/>
            <w:right w:w="{right}" w:type="dxa"/>
        </w:tcMar>
    ''')
    tcPr.append(tcMar)

def set_table_borders(table):
    tblPr = table._tbl.tblPr
    borders = parse_xml(f'''
        <w:tblBorders {nsdecls("w")}>
            <w:top w:val="single" w:sz="8" w:space="0" w:color="{BORDER_HEX}"/>
            <w:bottom w:val="single" w:sz="8" w:space="0" w:color="{BORDER_HEX}"/>
            <w:left w:val="single" w:sz="8" w:space="0" w:color="{BORDER_HEX}"/>
            <w:right w:val="single" w:sz="8" w:space="0" w:color="{BORDER_HEX}"/>
            <w:insideH w:val="single" w:sz="6" w:space="0" w:color="{BORDER_HEX}"/>
            <w:insideV w:val="single" w:sz="6" w:space="0" w:color="{BORDER_HEX}"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def add_label_cell(cell, text):
    set_cell_bg(cell, LABEL_BG)
    set_cell_margins(cell, top=100, bottom=100, left=120, right=120)
    cell.vertical_alignment = WD_ALIGN_VERTICAL.TOP
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.1
    r = p.add_run(text)
    r.font.name = "Calibri"
    r.font.size = Pt(10)
    r.font.bold = True
    r.font.color.rgb = NAVY

def add_para(cell, text="", bold_prefix=None, size=10, color=SLATE, space_after=4, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.LEFT, use_existing_first=False):
    if use_existing_first:
        p = cell.paragraphs[0]
    else:
        p = cell.add_paragraph()
    p.alignment = align
    p.paragraph_format.space_before = Pt(1)
    p.paragraph_format.space_after = Pt(space_after)
    p.paragraph_format.line_spacing = 1.15
    if bold_prefix:
        rb = p.add_run(bold_prefix)
        rb.font.name = "Calibri"
        rb.font.size = Pt(size)
        rb.font.bold = True
        rb.font.color.rgb = NAVY
    if text:
        r = p.add_run(text)
        r.font.name = "Calibri"
        r.font.size = Pt(size)
        r.font.bold = bold
        r.font.italic = italic
        r.font.color.rgb = color
    return p

def add_image_with_caption(cell, img_path, caption, width_in=4.8):
    if not os.path.exists(img_path):
        add_para(cell, f"[Missing image: {img_path}]", italic=True, color=MUTED)
        return
    p_img = cell.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    run = p_img.add_run()
    run.add_picture(img_path, width=Inches(width_in))

    p_cap = cell.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(0)
    p_cap.paragraph_format.space_after = Pt(8)
    rc = p_cap.add_run(caption)
    rc.font.name = "Calibri"
    rc.font.size = Pt(8.5)
    rc.font.bold = True
    rc.font.italic = True
    rc.font.color.rgb = BLUE

def write_markdown():
    md = """# 1BCP308 – 3rd Sem Community Project Report (2026–2027)

**Institution:** Dayananda Sagar College of Engineering, Bengaluru (Department of Computer Science & Engineering)  
**Guide name:** Dr. Punith Kumar (Associate Professor, Dept. of CSE)  

| Field | Details |
| :--- | :--- |
| **TITLE OF THE PROJECT** | **N²M Flood Prediction Model** — An ML-Based Urban Flood Susceptibility Mapping and Visualization System for Bengaluru |
| **PROJECT OVERVIEW** | Urban flooding in Bengaluru's BBMP area (711.59 km², 198 wards) disrupts daily life during monsoons due to >93% impervious surface cover, encroached lake cascades (*keres*), narrowed stormwater drains (*rajakaluves*), and localized convective storms. This community engineering project implements an experimental geospatial ML and web visualization platform that partitions Bengaluru into **3,026 spatial cells** (~500 m × 500 m) and ranks neighborhoods daily by relative flood susceptibility. |
| **STUDENT NAME** | **1.** Nishanth G M \| **2.** Mohith M \| **3.** Nihal Rao \| **4.** — |
| **USN** | **1.** `1DS25CS161` \| **2.** `1DS25CS147` \| **3.** `1DS25CS160` \| **4.** — |
| **INDIVIDUAL CONTRIBUTION** | **Nishanth G M:** Spatial grid discretization (3,026 cells), SRTM DEM / ESA WorldCover / OSM terrain feature extraction (`elev_m`, `slope_deg`, `twi`, `hand_m`, distances), CHIRPS precipitation pixel linkage, and Parquet matrix assembly.<br>**Mohith M:** XGBoost classifier training and imbalance tuning (`scale_pos_weight = 89.16`), September 2022 temporal holdout validation protocol, PR-AUC and Top-K enrichment evaluation.<br>**Nihal Rao:** FastAPI backend API (`ReplayService`, `RainfallService`, `TelegramService`), React + Vite frontend with 60 FPS Leaflet Canvas map visualization, 24-day historical replay controls, and private Telegram demonstration bot. |
| **DESIGN / Methodology** | **1. Spatial Grid:** Greater Bengaluru discretized into 3,026 uniform 500 m × 500 m cells (0.25 km² each).<br>**2. Feature Engineering (18 Features):** 10 static terrain indices (elevation, slope, TWI, HAND, imperviousness, lake/drain/road distances, waterbody density, catchment area) + 8 dynamic CHIRPS rainfall features (daily, 1d/2d lags, 3d/5d/7d/10d/14d sums).<br>**3. Imbalance-Aware XGBoost & Daily Ranking:** Trained on 5 historical monsoon storms (`scale_pos_weight = 89.16` for 0.0136% positive prevalence); ranks all 3,026 cells daily into **High Priority** (Top 150 / 5%), **Moderate Priority** (151–300 / 5%), and **Baseline** (301–3,026 / 90%).<br>**4. Architecture & Diagrams:** Offline Parquet Pipeline → FastAPI Backend → React + Leaflet Canvas Web App + Private Telegram Sandbox.<br>*(Diagrams included in DOCX/PDF: Fig 1 System Architecture, Fig 2 Data Pipeline, Fig 3 Inference & Ranking Workflow)* |
| **PLATFORM USED** | **Languages & ML:** Python 3.10+, JavaScript (ES6+), XGBoost 2.1.4, Scikit-Learn 1.6.1, Pandas 2.3.3, PyArrow 21.0, GeoPandas 1.0.1, Shapely 2.0.7, Rasterio 1.4.3<br>**Backend & APIs:** FastAPI 0.128, Uvicorn 0.39, Pytest 8.4.2, Open-Meteo REST API, Telegram Bot API<br>**Frontend & GIS:** React 18, Vite 5.4, Leaflet 1.9.4 (HTML5 Canvas Renderer), Lucide Icons<br>**Datasets & Cloud:** SRTM DEM (30 m), ESA WorldCover (10 m), OpenStreetMap, CHIRPS (0.05°), Render, Vercel, GitHub |
| **PROJECT CODE LINK (GITHUB/ GOOGLE DRIVE)** | `https://github.com/nishanth-end/n2m-rain-model` |
| **SCREENSHOTS / results** | **Empirical Holdout Results (September 2022 Event `E2022_09`, 24 days, 72,624 cell-days, 188 positives):**<br>• **PR-AUC:** `0.0026` vs. `0.0013` random chance (**2.00× Lift**)<br>• **Top 10% Hit Rate (Top 300 cells):** `25.0%` vs. `9.9%` baseline (**2.53× Enrichment**)<br>• **High Priority Tier Hit Rate (Top 150 / 5%):** `8.3%` vs. `5.0%` baseline (**1.66× Lift**)<br>• **Peak Cell Identified:** Cell #722 (Bellandur Ward 150) reached score `0.2191` on Sep 8, 2022.<br>• **Automated Backend Tests:** **82 / 82 passing** across API routes, Parquet schemas, rainfall cache, and Telegram security.<br>*(Screenshots included in DOCX/PDF: Landing Page, Flood Map & Cell Inspector, Live Simulation Lab, Telegram Sandbox, Sep 2022 Rainfall Chart)* |
| **CONCLUSION** | Successfully delivered an end-to-end experimental urban flood susceptibility mapping and visualization prototype for Bengaluru. Topography establishes the spatial baseline while multi-day antecedent rainfall triggers elevated ranks, and daily spatial ranking overcomes extreme 0.0136% label sparsity. **Limitations:** Outputs represent relative susceptibility tiers rather than physical inundation depths or civic flood alerts; CHIRPS (5.3 km) is coarser than 500 m cells and lacks subterranean sewer telemetry. **Future Scope:** Integrating KSNDMC telemetric rain gauges, IMD NWP forecasts, and coupled 1D/2D SWMM modeling. |
| **References** | [1] T. Islam et al., *Remote Sensing*, vol. 17, no. 3, p. 524, 2025. DOI: `10.3390/rs17030524`<br>[2] A. Pourzangbar et al., *J. Flood Risk Management*, vol. 18, e70042, 2025. DOI: `10.1111/jfr3.70042`<br>[3] R. Joseph, P. P. Mujumdar, and R. Das Bhowmik, *Water*, vol. 14, no. 23, p. 3900, 2022. DOI: `10.3390/w14233900`<br>[4] G. Al-Rawas et al., *Water*, vol. 16, no. 14, p. 2069, 2024. DOI: `10.3390/w16142069`<br>[5] A. A. Pathak, A. R. Mathad, and A. S. Gagnon, *Natural Hazards*, vol. 121, pp. 1007–1032, 2025.<br>[6] P. Mukhopadhyay and B. K. Das, *ETASR*, vol. 16, no. 4, pp. 37667–37672, 2026.<br>[7] T. Chen and C. Guestrin, *Proc. 22nd ACM SIGKDD*, pp. 785–794, 2016.<br>[8] C. Funk et al., *Scientific Data*, vol. 2, p. 150066, 2015. |

Signature of Guide: ___________________________
"""
    with open(MD_PATH, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"Wrote {MD_PATH}")

def build_docx():
    doc = docx.Document()

    # A4 Page Setup with 0.7-inch margins for clean form layout
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(0.65)
        section.bottom_margin = Inches(0.65)
        section.left_margin = Inches(0.65)
        section.right_margin = Inches(0.65)

        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hr = hp.add_run("1BCP308 — 3rd Sem Community Project Report (2026–2027) | DSCE CSE")
        hr.font.name = "Calibri"
        hr.font.size = Pt(8.5)
        hr.font.color.rgb = MUTED

        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fr = fp.add_run("N²M Flood Prediction Model — Dayananda Sagar College of Engineering, Bengaluru")
        fr.font.name = "Calibri"
        fr.font.size = Pt(8.5)
        fr.font.color.rgb = MUTED

    # ================= HEADER BLOCK =================
    p_inst = doc.add_paragraph()
    p_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_inst.paragraph_format.space_before = Pt(0)
    p_inst.paragraph_format.space_after = Pt(2)
    r = p_inst.add_run("DAYANANDA SAGAR COLLEGE OF ENGINEERING, BENGALURU\n")
    r.font.name = "Calibri"
    r.font.size = Pt(12)
    r.font.bold = True
    r.font.color.rgb = NAVY
    r2 = p_inst.add_run("DEPARTMENT OF COMPUTER SCIENCE & ENGINEERING")
    r2.font.name = "Calibri"
    r2.font.size = Pt(10)
    r2.font.bold = True
    r2.font.color.rgb = BLUE

    p_course = doc.add_paragraph()
    p_course.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_course.paragraph_format.space_before = Pt(4)
    p_course.paragraph_format.space_after = Pt(2)
    rc = p_course.add_run("1BCP308 – 3rd Sem Community Project Report\n2026–2027")
    rc.font.name = "Calibri"
    rc.font.size = Pt(13)
    rc.font.bold = True
    rc.font.color.rgb = NAVY

    p_guide = doc.add_paragraph()
    p_guide.alignment = WD_ALIGN_PARAGRAPH.LEFT
    p_guide.paragraph_format.space_before = Pt(6)
    p_guide.paragraph_format.space_after = Pt(6)
    rg1 = p_guide.add_run("Guide name: ")
    rg1.font.name = "Calibri"
    rg1.font.size = Pt(10.5)
    rg1.font.bold = True
    rg1.font.color.rgb = NAVY
    rg2 = p_guide.add_run("Dr. Punith Kumar, Associate Professor, Department of Computer Science & Engineering")
    rg2.font.name = "Calibri"
    rg2.font.size = Pt(10.5)
    rg2.font.color.rgb = SLATE

    # ================= MAIN 5-COLUMN FORM TABLE =================
    # Rows:
    # 0: TITLE OF THE PROJECT (merged 1..4)
    # 1: Abstract / Overview (merged 1..4)
    # 2: STUDENT NAME (4 cols)
    # 3: USN (4 cols)
    # 4: INDIVIDUAL CONTRIBUTION (4 cols)
    # 5: DESIGN / Methodology (merged 1..4)
    # 6: PLATFORM USED (merged 1..4)
    # 7: PROJECT CODE LINK (GITHUB/ GOOGLE DRIVE) (merged 1..4)
    # 8: SCREENSHOTS / results (merged 1..4)
    # 9: CONCLUSION (merged 1..4)
    # 10: References (merged 1..4)
    table = doc.add_table(rows=11, cols=5)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    set_table_borders(table)

    col_widths = [Inches(1.45), Inches(1.38), Inches(1.38), Inches(1.38), Inches(1.38)]
    for row in table.rows:
        for idx, w in enumerate(col_widths):
            row.cells[idx].width = w

    def merge_right(row_idx):
        row = table.rows[row_idx]
        c1 = row.cells[1]
        c4 = row.cells[4]
        c1.merge(c4)
        c1.width = Inches(5.52)
        set_cell_margins(c1, top=90, bottom=90, left=120, right=120)
        return c1

    # Row 0: TITLE OF THE PROJECT
    add_label_cell(table.rows[0].cells[0], "TITLE OF THE PROJECT")
    c = merge_right(0)
    add_para(
        c,
        "N²M Flood Prediction Model — An ML-Based Urban Flood Susceptibility Mapping and Visualization System for Bengaluru",
        size=11,
        bold=True,
        color=NAVY,
        space_after=2,
        use_existing_first=True,
    )

    # Row 1: Community Context & Project Scope (from blank row in template)
    add_label_cell(table.rows[1].cells[0], "COMMUNITY CONTEXT & ABSTRACT")
    c = merge_right(1)
    add_para(
        c,
        "Rapid urbanization in Bengaluru (711.59 km², 198 BBMP wards) has expanded impervious concrete cover to over 93%, encroached on interconnected lake cascades (keres), and narrowed primary stormwater channels (rajakaluves). Combined with localized convective storms, low-lying valleys frequently flood while city-wide municipal alerts provide no neighborhood-level differentiation.",
        size=9.5,
        space_after=4,
        use_existing_first=True,
    )
    add_para(
        c,
        "The N²M Flood Prediction Model is an experimental data science and web visualization system that partitions Bengaluru into 3,026 spatial cells (~500 m × 500 m) and trains an imbalance-aware XGBoost classifier on 18 terrain and rainfall features to rank neighborhoods daily into High Priority, Moderate Priority, and Baseline susceptibility tiers. Note: It is an academic research prototype for relative spatial prioritization, not a physical inundation-depth forecast or operational emergency alert system.",
        size=9.5,
        space_after=2,
    )

    # Row 2: STUDENT NAME
    add_label_cell(table.rows[2].cells[0], "STUDENT NAME")
    names = ["Nishanth G M", "Mohith M", "Nihal Rao", "—"]
    for idx, nm in enumerate(names):
        cell = table.rows[2].cells[idx + 1]
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        add_para(cell, nm, size=10, bold=True, color=NAVY, space_after=0, use_existing_first=True)

    # Row 3: USN
    add_label_cell(table.rows[3].cells[0], "USN")
    usns = ["1DS25CS161", "1DS25CS147", "1DS25CS160", "—"]
    for idx, usn in enumerate(usns):
        cell = table.rows[3].cells[idx + 1]
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        add_para(cell, usn, size=9.5, bold=True, color=BLUE, space_after=0, use_existing_first=True)

    # Row 4: INDIVIDUAL CONTRIBUTION
    add_label_cell(table.rows[4].cells[0], "INDIVIDUAL CONTRIBUTION")
    contribs = [
        "Constructed the 3,026-cell spatial grid (01_grid.py), extracted 10 static DEM/WorldCover/OSM terrain & drainage features (02_features.py: elevation, slope, TWI, HAND, lake/drain/road distances), linked 0.05° CHIRPS precipitation grids (03_chirps.py), and built the Parquet feature matrix (04_build_matrix.py).",
        "Developed and tuned the XGBoost classifier (scale_pos_weight = 89.16) for extreme class imbalance (0.0136% positive flood prevalence), designed the September 2022 temporal holdout validation protocol, and evaluated PR-AUC and Top-K enrichment metrics.",
        "Built the asynchronous FastAPI backend (main.py, ReplayService, RainfallService), the React + Vite frontend with 60 FPS Leaflet Canvas vector rendering, 24-day historical replay controls, sensitivity simulation lab, and the private Telegram demonstration bot.",
        "—",
    ]
    for idx, ct in enumerate(contribs):
        cell = table.rows[4].cells[idx + 1]
        set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
        add_para(cell, ct, size=8.8, space_after=0, use_existing_first=True)

    # Row 5: DESIGN / Methodology
    add_label_cell(table.rows[5].cells[0], "DESIGN /\nMethodology")
    c = merge_right(5)
    add_para(
        c,
        "Greater Bengaluru is discretized into a uniform Cartesian grid of 3,026 cells (500 m × 500 m, 0.25 km² each). Each cell combines 10 static terrain/built-environment features (SRTM 30 m DEM elevation, slope, Topographic Wetness Index [TWI], Height Above Nearest Drainage [HAND], ESA WorldCover 10 m impervious fraction, OpenStreetMap distances to lakes, rajakaluves, and roads, waterbody density, catchment area) with 8 dynamic CHIRPS 0.05° rainfall features (daily rain, 1d/2d lags, 3d/5d/7d/10d/14d cumulative sums).",
        bold_prefix="1. Geospatial Grid & 18-Feature Matrix: ",
        size=9.5,
        space_after=4,
        use_existing_first=True,
    )
    add_para(
        c,
        "Confirmed historical flood events are extremely sparse: 240 positive cell-days across 1,764,158 cell-days (0.0136% prevalence across 6 monsoonal events). An XGBoost classifier (100 trees, max_depth=6, learning_rate=0.1) is trained on 5 historical events with scale_pos_weight = 89.16 to heavily penalize missed floods. Rather than using a rigid 0.5 probability cutoff, daily scores are sorted into dense ranks (1 to 3,026): High Priority (Top 150 / ~5%), Moderate Priority (Ranks 151–300 / ~5%), and Baseline (Ranks 301–3,026 / ~90%).",
        bold_prefix="2. Imbalance-Aware XGBoost & Dense Ranking: ",
        size=9.5,
        space_after=4,
    )
    add_para(
        c,
        "Precomputed Parquet datasets are cached in memory at startup by FastAPI (~18 MB resident RAM) and served via REST endpoints (/api/risk, /api/dates, /api/summary, /api/rainfall/latest, /api/telegram/*) to a React + Leaflet HTML5 Canvas dashboard rendering 3,026 cells at 60 FPS.",
        bold_prefix="3. Decoupled System Architecture: ",
        size=9.5,
        space_after=4,
    )
    add_image_with_caption(c, ASSETS["arch"], "Figure 1: Overall System Architecture of the N²M Flood Prediction Model", width_in=5.0)
    add_image_with_caption(c, ASSETS["pipeline"], "Figure 2: Geospatial Data Ingestion and Feature Processing Pipeline", width_in=5.0)
    add_image_with_caption(c, ASSETS["ranking"], "Figure 3: XGBoost Inference and Daily Spatial Ranking Workflow", width_in=4.8)

    # Row 6: PLATFORM USED
    add_label_cell(table.rows[6].cells[0], "PLATFORM USED")
    c = merge_right(6)
    add_para(c, "Python 3.10+, JavaScript (ES6+), XGBoost 2.1.4, Scikit-Learn 1.6.1, Pandas 2.3.3, PyArrow 21.0, GeoPandas 1.0.1, Shapely 2.0.7, Rasterio 1.4.3", bold_prefix="Languages & ML Stack: ", size=9.5, space_after=3, use_existing_first=True)
    add_para(c, "FastAPI 0.128, Uvicorn 0.39 (ASGI), Pytest 8.4.2, Open-Meteo REST API, Telegram Bot API", bold_prefix="Backend & Testing: ", size=9.5, space_after=3)
    add_para(c, "React 18, Vite 5.4, Leaflet 1.9.4 (HTML5 Canvas Vector Renderer), Lucide React Icons", bold_prefix="Frontend & Mapping: ", size=9.5, space_after=3)
    add_para(c, "NASA/USGS SRTM DEM (30 m), ESA WorldCover (10 m), OpenStreetMap Vectors, CHIRPS Gridded Rainfall (0.05°)", bold_prefix="Geospatial Datasets: ", size=9.5, space_after=3)
    add_para(c, "Vercel (Frontend SPA), Render (Backend Python Web Service), Git & GitHub", bold_prefix="Cloud & Version Control: ", size=9.5, space_after=2)

    # Row 7: PROJECT CODE LINK
    add_label_cell(table.rows[7].cells[0], "PROJECT CODE LINK\n(GITHUB / GOOGLE DRIVE)")
    c = merge_right(7)
    add_para(c, "https://github.com/nishanth-end/n2m-rain-model", bold_prefix="GitHub Repository: ", size=10, color=BLUE, space_after=2, use_existing_first=True)

    # Row 8: SCREENSHOTS / results
    add_label_cell(table.rows[8].cells[0], "SCREENSHOTS /\nresults")
    c = merge_right(8)
    add_para(
        c,
        "Evaluated strictly out-of-sample on the sequestered 24-day September 2022 monsoon sequence (Event E2022_09: 72,624 cell-days, 188 confirmed flood points):\n"
        "• Precision-Recall AUC (PR-AUC): 0.0026 vs. 0.0013 random chance baseline (2.00× Lift)\n"
        "• Top 10% Ranked Cell Hit Rate (Top 300 cells): 25.0% vs. 9.9% random baseline (2.53× Enrichment)\n"
        "• High Priority Tier Hit Rate (Top 150 / Top 5%): 8.3% vs. 5.0% random baseline (1.66× Lift)\n"
        "• Peak Susceptibility Case Study: Cell #722 (Bellandur Ward 150) reached peak score 0.2191 on September 8, 2022.\n"
        "• Automated Backend Test Suite: 82 / 82 tests passed (100%) across API routes, Parquet schemas, rainfall cache, and Telegram security.",
        bold_prefix="Verified Empirical & Testing Results:\n",
        size=9.5,
        space_after=4,
        use_existing_first=True,
    )
    add_image_with_caption(c, ASSETS["landing"], "Figure 4: N²M Research Landing Page & Multi-Source Coupling Overview", width_in=4.9)
    add_image_with_caption(c, ASSETS["map_insp"], "Figure 5: Interactive Leaflet Canvas Map (Sep 8, 2022) & Cell Inspector Drawer (Bellandur Ward 150)", width_in=4.9)
    add_image_with_caption(c, ASSETS["live_sim"], "Figure 6: Live Ingestion & Rainfall Sensitivity Simulation Lab (Cell #722)", width_in=4.9)
    add_image_with_caption(c, ASSETS["telegram"], "Figure 7: Private Telegram Demonstration Bot Sandbox (@N2M_Flood_Bot) & Payload Preview", width_in=4.9)
    add_image_with_caption(c, ASSETS["rain_chart"], "Figure 8: Daily CHIRPS Precipitation Profile During September 2022 Replay Window", width_in=4.7)

    # Row 9: CONCLUSION
    add_label_cell(table.rows[9].cells[0], "CONCLUSION")
    c = merge_right(9)
    add_para(
        c,
        "Our student team successfully designed, validated, and deployed the N²M Flood Prediction Model, demonstrating how open geospatial terrain datasets, satellite precipitation records, and imbalance-aware machine learning can map neighborhood-scale urban flood susceptibility across Bengaluru. Key findings show that terrain morphology defines baseline spatial risk while 3-day and 7-day antecedent rainfall acts as the primary temporal trigger, and daily dense ranking provides actionable prioritization (2.53× top-10% enrichment) despite extreme label sparsity (0.0136%).",
        size=9.5,
        space_after=4,
        use_existing_first=True,
    )
    add_para(
        c,
        "Limitations & Future Scope: The system outputs relative susceptibility tiers rather than physical inundation depths or civic flood warnings; CHIRPS grids (~5.3 km) are coarser than 500 m cells and surface features do not capture underground sewer blockages. Future iterations can integrate hyper-local KSNDMC telemetric rain gauges, IMD numerical weather forecasts, and coupled 1D/2D hydrodynamic simulation (SWMM).",
        size=9.5,
        space_after=2,
    )

    # Row 10: References
    add_label_cell(table.rows[10].cells[0], "References")
    c = merge_right(10)
    refs = [
        "[1] T. Islam, E. B. Zeleke, M. Afroz, and A. M. Melesse, \"A Systematic Review of Urban Flood Susceptibility Mapping: Remote Sensing, Machine Learning, and Other Modeling Approaches,\" Remote Sensing, vol. 17, no. 3, p. 524, Feb. 2025. DOI: 10.3390/rs17030524",
        "[2] A. Pourzangbar, P. Oberle, A. Kron, and M. J. Franca, \"Analysis of the Utilization of Machine Learning to Map Flood Susceptibility,\" J. Flood Risk Management, vol. 18, p. e70042, 2025. DOI: 10.1111/jfr3.70042",
        "[3] R. Joseph, P. P. Mujumdar, and R. Das Bhowmik, \"Reconstruction of Urban Rainfall Measurements to Estimate the Spatiotemporal Variability of Extreme Rainfall,\" Water, vol. 14, no. 23, p. 3900, Nov. 2022. DOI: 10.3390/w14233900",
        "[4] G. Al-Rawas, M. R. Nikoo, M. Al-Wardy, and T. Etri, \"A Critical Review of Emerging Technologies for Flash Flood Prediction,\" Water, vol. 16, no. 14, p. 2069, Jul. 2024. DOI: 10.3390/w16142069",
        "[5] A. A. Pathak, A. R. Mathad, and A. S. Gagnon, \"Integrating Socio-Economic Variables in Urban Flood Damage Assessments: A Case Study of Bengaluru, India,\" Natural Hazards, vol. 121, pp. 1007–1032, Jan. 2025.",
        "[6] P. Mukhopadhyay and B. K. Das, \"Composite Flood Risk Index Assessment and Operationalization for Bellandur Ward, Bengaluru,\" ETASR, vol. 16, no. 4, pp. 37667–37672, Aug. 2026.",
        "[7] T. Chen and C. Guestrin, \"XGBoost: A Scalable Tree Boosting System,\" in Proc. 22nd ACM SIGKDD, Aug. 2016, pp. 785–794.",
        "[8] C. Funk et al., \"The Climate Hazards Group InfraRed Precipitation with Stations—A New Environmental Record for Monitoring Extremes,\" Scientific Data, vol. 2, p. 150066, Dec. 2015.",
    ]
    for idx, rf in enumerate(refs):
        add_para(c, rf, size=8.5, space_after=2, use_existing_first=(idx == 0))

    # ================= SIGNATURE OF GUIDE =================
    p_sig = doc.add_paragraph()
    p_sig.alignment = WD_ALIGN_PARAGRAPH.RIGHT
    p_sig.paragraph_format.space_before = Pt(28)
    p_sig.paragraph_format.space_after = Pt(4)
    rs1 = p_sig.add_run("___________________________\n")
    rs1.font.name = "Calibri"
    rs1.font.size = Pt(10.5)
    rs1.font.color.rgb = SLATE
    rs2 = p_sig.add_run("Signature of Guide\n")
    rs2.font.name = "Calibri"
    rs2.font.size = Pt(10.5)
    rs2.font.bold = True
    rs2.font.color.rgb = NAVY
    rs3 = p_sig.add_run("(Dr. Punith Kumar, Associate Professor, Dept. of CSE)")
    rs3.font.name = "Calibri"
    rs3.font.size = Pt(9)
    rs3.font.color.rgb = MUTED

    doc.save(DOCX_PATH)
    print(f"Wrote {DOCX_PATH}")

if __name__ == "__main__":
    write_markdown()
    build_docx()
