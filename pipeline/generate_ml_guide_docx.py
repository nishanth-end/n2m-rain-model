"""pipeline/generate_ml_guide_docx.py
Builds delivery/ML_Model_Training_Guide_for_Member2.docx
Generates the Member 1 -> Member 2 ML Handoff Guide in identical styling and structure
strictly matching docs/ML_ENGINEER_GUIDE.md and containing the 7 required sections.
"""

import os, sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import parse_xml
from docx.oxml.ns import nsdecls

def set_cell_background(cell, hex_color):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{hex_color}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = parse_xml(f'<w:tcMar {nsdecls("w")}><w:top w:w="{top}" w:type="dxa"/><w:bottom w:w="{bottom}" w:type="dxa"/><w:left w:w="{left}" w:type="dxa"/><w:right w:w="{right}" w:type="dxa"/></w:tcMar>')
    tcPr.append(tcMar)

def style_table(table, header_bg="1F497D", alt_bg="F2F5F8"):
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    for i, row in enumerate(table.rows):
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if i == 0:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            for cell in row.cells:
                set_cell_background(cell, header_bg)
                set_cell_margins(cell, top=140, bottom=140, left=180, right=180)
                for p in cell.paragraphs:
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    for r in p.runs:
                        r.font.bold = True
                        r.font.color.rgb = RGBColor(255, 255, 255)
                        r.font.name = "Calibri"
                        r.font.size = Pt(9.5)
        else:
            bg = alt_bg if i % 2 == 1 else "FFFFFF"
            for cell in row.cells:
                set_cell_background(cell, bg)
                set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
                for p in cell.paragraphs:
                    for r in p.runs:
                        r.font.name = "Calibri"
                        r.font.size = Pt(9)

def add_header_footer(doc):
    for s in doc.sections:
        s.top_margin = Inches(1.0)
        s.bottom_margin = Inches(1.0)
        s.left_margin = Inches(1.0)
        s.right_margin = Inches(1.0)
        s.different_first_page_header_footer = True
        
        # Header (pages 2+)
        header = s.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hr = hp.add_run("ML Handoff Guide | Team N2M (Member 1 -> Member 2)")
        hr.font.name = "Calibri"
        hr.font.size = Pt(8.5)
        hr.font.color.rgb = RGBColor(128, 128, 128)
        
        # Footer
        footer = s.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        fr = fp.add_run("Page ")
        fr.font.name = "Calibri"
        fr.font.size = Pt(9)
        fr.font.color.rgb = RGBColor(128, 128, 128)
        f_fld1 = parse_xml(r'<w:fldSimple %s w:instr="PAGE"/>' % nsdecls('w'))
        fp._p.append(f_fld1)
        fr2 = fp.add_run(" of ")
        fr2.font.name = "Calibri"
        fr2.font.size = Pt(9)
        fr2.font.color.rgb = RGBColor(128, 128, 128)
        f_fld2 = parse_xml(r'<w:fldSimple %s w:instr="NUMPAGES"/>' % nsdecls('w'))
        fp._p.append(f_fld2)

def build_ml_guide():
    doc = docx.Document()
    add_header_footer(doc)
    
    # Base styling
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(51, 51, 51)
    
    # Title Page
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(40)
    
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("ML ENGINEER HANDOFF GUIDE")
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(31, 73, 125)
    
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("N²M Predictive Flood Alert System — Final Data Handoff Package")
    r_sub.font.size = Pt(14)
    r_sub.font.color.rgb = RGBColor(89, 89, 89)
    p_sub.paragraph_format.space_after = Pt(28)
    
    p_meta = doc.add_paragraph()
    p_meta.add_run("Author: ").bold = True
    p_meta.add_run("Member 1 (Data Engineer)\n")
    p_meta.add_run("Recipient: ").bold = True
    p_meta.add_run("Member 2 (ML Engineer)\n")
    p_meta.add_run("Project: ").bold = True
    p_meta.add_run("N²M Predictive Flood Alert System (Bengaluru, 24–48h Ahead Flood Risk)\n")
    p_meta.add_run("Date of Delivery: ").bold = True
    p_meta.add_run("2026-11-16\n")
    p_meta.add_run("Git Commit: ").bold = True
    p_meta.add_run("e615b72\n")
    p_meta.add_run("Dataset Acceptance: ").bold = True
    p_meta.add_run("17 / 17 checks passed (pipeline/validate_dataset.py, 0 failures)\n")
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 1. What you are receiving
    # -------------------------------------------------------------
    doc.add_heading("1. What You Are Receiving", level=1)
    doc.add_paragraph(
        "This handoff package delivers the complete, audited, and verified datasets for machine learning training, "
        "cross-validation, and operational replay under delivery/. All numeric features are provided in raw physical units."
    )
    
    table_files = doc.add_table(rows=9, cols=6)
    f_headers = ["File Path", "Format", "Size", "Rows", "Cols", "Purpose"]
    for j, h in enumerate(f_headers):
        table_files.rows[0].cells[j].text = h
        
    f_data = [
        ["delivery/flood_dataset.parquet", "Parquet", "18.01 MB", "1,764,158", "42", "Master ML dataset: all 3,026 cells across 583 candidate stormy days in May–Nov (2017, 2021, 2022, 2023). 240 positive cell-days across 6 events."],
        ["delivery/cells_static.csv", "CSV", "0.26 MB", "3,026", "16", "Master spatial lookup table: 10 static terrain, hydrology, and urban features per cell, plus ward IDs and nearest CHIRPS pixel ID."],
        ["delivery/rainfall_daily.csv", "CSV", "1.13 MB", "36,112", "5", "Continuous daily rainfall calendar across 37 CHIRPS pixels for April 1 – November 30 of 2017, 2021, 2022, 2023 (976 days x 37 pixels). Zero nulls, is_imputed=0."],
        ["delivery/events.csv", "CSV", "0.01 MB", "11", "19", "Ground-truth flood event audit directory: 11 site records across 6 confirmed events with coordinates, cell IDs, citations, live URLs, and confidence grades."],
        ["delivery/flood_replay_E2022_09.parquet", "Parquet", "0.90 MB", "72,624", "42", "Held-out validation replay sequence for E2022_09: 24 consecutive days (22 Aug – 14 Sep 2022 x 3,026 cells) with 188 positive labels across 4–7 Sep 2022."],
        ["delivery/flood_dataset_event_windows.csv", "CSV", "131.29 MB", "366,146", "42", "CSV extract of all 3,026 cells for the 121 May–Nov candidate days within [-14, +7] days of all 6 confirmed events (240 positives)."],
        ["delivery/flood_dataset_pilot.parquet", "Parquet", "0.30 MB", "66,572", "31", "Lightweight subset for quick code sanity checks: 22 consecutive days (22 Aug – 12 Sep 2022 x 3,026 cells)."],
        ["data/evidence/manifest.csv", "CSV", "0.02 MB", "73", "8", "Cryptographic SHA-256 provenance manifest recording requested URLs, final redirected URLs, HTTP status codes, publish timestamps, and local text hashes."]
    ]
    for i, row in enumerate(f_data):
        for j, val in enumerate(row):
            table_files.rows[i+1].cells[j].text = val
    style_table(table_files)
    doc.add_paragraph("Table 1: Inventory of delivered dataset files in delivery/ directory.")
    
    # -------------------------------------------------------------
    # 2. How the data was built (one subsection per pipeline component)
    # -------------------------------------------------------------
    doc.add_heading("2. How the Data Was Built", level=1)
    
    doc.add_heading("a. Spatial Grid Skeleton", level=2)
    doc.add_paragraph(
        "• Source: BBMP 2011 administrative ward boundary GeoJSON (198 wards, DataMeet).\n"
        "• Coverage / Scale: Greater Bengaluru metropolitan area (711.59 km², 198 wards).\n"
        "• Method: Reprojected ward boundaries to EPSG:32643 (UTM Zone 43N) and overlaid a regular 500 m × 500 m lattice (0.25 km² per cell). Intersected with ward polygons; cells with centroid inside municipal boundaries were retained, yielding 2,674 full cells and 352 boundary-clipped cells.\n"
        "• Output File: delivery/cells_static.csv (identifiers) and data/interim/cells_grid.csv.\n"
        "• Integrity Checks Passed: Total cells = 3,026; ward coverage = 198/198; area = 711.59 km²; zero duplicate cell_ids; 14 tests passing in tests/test_grid.py."
    )
    
    doc.add_heading("b. Static Terrain and Hydrology Features", level=2)
    doc.add_paragraph(
        "• Sources: Copernicus GLO-30 DEM (30 m DSM), ESA WorldCover 2021 v200 (10 m land cover), and OpenStreetMap vector networks (highways, waterways, lakes).\n"
        "• Coverage / Scale: Full city across all 3,026 cells.\n"
        "• Method: Conditioned elevation rasters using pysheds and Horn's slope algorithm. Computed 10 static physical features per cell: elev_m (767.1–951.7 m), slope_deg (0.0–12.3°), twi (4.8–13.1), hand_m (0.0–58.5 m), flow_acc (0.0–76.5 km²), imperv_frac (0.00–0.99), dist_lake_m, dist_drain_m, dist_road_m, and lakes_within_1km (0–11).\n"
        "• Output File: delivery/cells_static.csv.\n"
        "• Integrity Checks Passed: Zero nulls across all 10 features; features constant per cell across all dates; 5 tests passing in tests/test_static.py."
    )
    
    doc.add_heading("c. Continuous Rainfall Series", level=2)
    doc.add_paragraph(
        "• Source: UCSB CHIRPS Daily v2.0 p05 GeoTIFFs (0.05° resolution, ~5.3 km).\n"
        "• Coverage / Scale: 37 grid pixels covering Greater Bengaluru across wet seasons (April 1 to November 30) of 2017, 2021, 2022, 2023.\n"
        "• Method: Downloaded 976 daily GeoTIFF rasters. Mapped each 500 m grid cell to its nearest Euclidean CHIRPS pixel center (mean distance 2.12 km, max 3.84 km). Ingested continuous calendars starting April 1 (30-day buffer) and computed rolling sums (rain_1d_mm, rain_3d_mm, rain_7d_mm, rain_14d_mm, rain_30d_mm) and daily lags (rain_lag1_mm..14_mm) strictly within each year prior to row filtering.\n"
        "• Output File: delivery/rainfall_daily.csv (36,112 rows) and data/interim/rain_timeseries.csv.\n"
        "• Integrity Checks Passed: Continuous unbroken dates (976 days x 37 pixels); zero nulls; is_imputed = 0; rolling monotonicity holds (rain_1d <= rain_3d <= rain_7d); lag identity holds (rain_3d == rain_1d + lag1 + lag2 with error < 0.02 mm); 5 tests passing in tests/test_rainfall.py."
    )
    
    doc.add_heading("d. Ground-Truth Flood Catalog", level=2)
    doc.add_paragraph(
        "• Sources: Technical Study by Dr. Sudhir Sajjan (Floods at Bengaluru City: A Technical Study, 2022) for September 2022 hotspots; contemporaneous verified media reports from The Indian Express, The News Minute, Gulf Times, and Scroll.in.\n"
        "• Coverage / Scale: 6 confirmed flood events spanning 2017 to 2023 across 11 site records and 10 distinct seed cells.\n"
        "• Method: Coordinates were resolved against OpenStreetMap feature polygons / centroids (e.g. Rainbow Drive OSM way 101573097, Wipro Campus way 370327479, Koramangala 4th Block way 1066116298) and mapped to grid cells via strict point-in-polygon matching. Where historical sources reported layout boundaries extending beyond the 2011 BBMP boundary, inside polygon centroids were assigned (Cell 555 for RBD Layout, Cell 666 for Wipro Campus).\n"
        "• Output File: delivery/events.csv.\n"
        "• Integrity Checks Passed: All 11 records lie strictly within the 3,026 production cells; every cited quote matches saved source text with <= 25 words; live URLs verified; pipeline/verify_quotes.py passing with 0 errors."
    )
    
    doc.add_heading("e. Master ML Dataset Assembly", level=2)
    doc.add_paragraph(
        "• Source: Inner join of grid skeleton, static features, CHIRPS rainfall time series, and flood event labels.\n"
        "• Coverage / Scale: 1,764,158 rows x 42 columns (3,026 cells x 583 candidate stormy days).\n"
        "• Method: Assembled all cells on days meeting the candidate stormy days rule. Assigned flood_label = 1 to report-mapped seed cells on active event days (audit_is_buffer_cell = 0, high/medium confidence). Applied an 8-connected Moore neighborhood (3x3 lattice buffer) around seed cells, setting buffer cells to flood_label = 1 (audit_is_buffer_cell = 1, label_confidence = 'low'). All remaining cells on candidate days received flood_label = 0, label_source = 'none', and label_confidence = 'low'.\n"
        "• Output File: delivery/flood_dataset.parquet.\n"
        "• Integrity Checks Passed: Passed all 17 automated acceptance criteria of pipeline/validate_dataset.py with zero failures (unique compound key (cell_id, date), zero missing values, zero forbidden columns)."
    )
    
    doc.add_heading("f. Validation and Replay Subsets", level=2)
    doc.add_paragraph(
        "• Source: Sliced directly from delivery/flood_dataset.parquet.\n"
        "• Coverage / Scale: Replay: held-out E2022_09 (72,624 rows, 188 positives across 4–7 Sep 2022); Event Windows: 121 days within [-14, +7] days of events (366,146 rows, 240 positives); Pilot: 66,572 rows.\n"
        "• Method: Filtered master table by date ranges. Audit columns and targets were cross-verified against the master parquet table.\n"
        "• Output Files: delivery/flood_replay_E2022_09.parquet, delivery/flood_dataset_event_windows.csv, delivery/flood_dataset_pilot.parquet.\n"
        "• Integrity Checks Passed: Replay parity achieved: labels equal: True between replay and master parquet across the 24-day evaluation window."
    )
    
    doc.add_heading("g. Evidence Store and Quote Verification", level=2)
    doc.add_paragraph(
        "• Source: 15 saved full-page texts (data/evidence/*.txt), Overpass / Nominatim raw JSON query responses (data/evidence/geocode/*.json), and publication metadata.\n"
        "• Coverage / Scale: 73 manifest entries across all citations, geocode queries, and calibration sources.\n"
        "• Method: Every cited quotation in documentation and interim tables is checked by pipeline/verify_quotes.py to ensure: (1) it exists verbatim in the saved page text, (2) length is <= 25 words, and (3) cited publication dates match the source page header.\n"
        "• Output Files: data/evidence/manifest.csv and data/evidence/.\n"
        "• Integrity Checks Passed: python pipeline/verify_quotes.py exits with code 0 (all quotes verified verbatim)."
    )
    
    # -------------------------------------------------------------
    # 3. Column Reference
    # -------------------------------------------------------------
    doc.add_heading("3. Column Reference", level=1)
    doc.add_paragraph(
        "The master table delivery/flood_dataset.parquet contains 42 columns grouped into 6 logical types. "
        "All numeric features are in raw physical units (no scaling, standardisation, or log-transforms). "
        "For complete schema ranges and units, see delivery/data_dictionary.md."
    )
    doc.add_paragraph(
        "• Identifiers & Coordinates (6 columns): cell_id (int64, 0..3025), date (object, YYYY-MM-DD), lat (float64), lon (float64), ward (int64, 1..198), rain_pixel_id (int64, 0..36).\n"
        "• Static Terrain & Hydrology (10 columns): elev_m, slope_deg, twi, hand_m, flow_acc, imperv_frac, dist_lake_m, dist_drain_m, dist_road_m, lakes_within_1km.\n"
        "• Dynamic Cumulative Rainfall (5 columns): rain_1d_mm, rain_3d_mm, rain_7d_mm, rain_14d_mm, rain_30d_mm.\n"
        "• Antecedent Daily Lags (14 columns): rain_lag1_mm through rain_lag14_mm (daily precipitation on day d-k for k in 1..14).\n"
        "• Target & Sampling Weight (4 columns): flood_label (int64 binary target: 1 = flooded, 0 = dry), label_source (category: 'reported', 'buffered', 'restored', 'none'), label_confidence (grade: 'high', 'medium', 'low'), day_sampling_weight (float64: uniformly 1.0).\n"
        "• Audit & Provenance Columns (3 columns): event_id (string, e.g. 'E2022_09'), audit_is_buffer_cell (int64: 0 = seed, 1 = 3x3 buffer), audit_geocode_precision (string)."
    )
    
    # -------------------------------------------------------------
    # 4. KNOWN LIMITATIONS
    # -------------------------------------------------------------
    doc.add_heading("4. KNOWN LIMITATIONS (Mandatory Blunt Section)", level=1)
    doc.add_paragraph(
        "The following limitations are computed directly from the repository data and reflect physical, statistical, "
        "and operational constraints:"
    )
    doc.add_paragraph(
        "1. Tiny Effective Sample Size:\n"
        "While delivery/flood_dataset.parquet contains 1,764,158 rows, the headline count of 240 positive cell-days is deceptive. "
        "Exactly 30 positives are report-mapped centre seed-days (10 distinct seed cells across active event days). The remaining "
        "210 positives (87.5%) are topological 3x3 buffer cells surrounding those seeds. The true number of independent flood events "
        "is 6, and the number of independent storm episodes is 5 (since May 2022 and September 2022 occurred in the same season). "
        "Treating 240 positive rows as independent observations will cause severe overfitting. Effective degrees of freedom are governed "
        "by the 30 seed-days, not the 240 expanded rows.\n\n"
        "2. Positive Scarcity in Leave-One-Event-Out Validation:\n"
        "Holding out the September 2022 catastrophic flood (E2022_09) removes 188 positive cell-days. Exactly 52 positive cell-days "
        "remain for training across the entire city: 6 centre seed-days (E2017_08: 1, E2017_09: 2, E2021_11: 1, E2022_05: 1, E2023_05: 1) "
        "and 46 buffer cell-days. We strongly recommend Leave-One-Event-Out cross-validation across all 6 events; keep the replay file as a "
        "demonstration replay, not the sole validation benchmark.\n\n"
        "3. Coarse Spatial Rainfall Resolution:\n"
        "Greater Bengaluru's 3,026 grid cells map to only 37 CHIRPS pixels (mean 81.8 cells per pixel). All positive cells map to only 8 distinct "
        "CHIRPS pixels (Pixel 11: 121 city cells, 16 positive; Pixel 12: 118 city cells, 35 positive; Pixel 17: 121 city cells, 9 positive; "
        "Pixel 20: 121 city cells, 6 positive). Because all cells under the same pixel receive identical rainfall on any given day, rainfall "
        "cannot separate neighbouring flooded cells from dry cells within the same pixel. Static terrain features (hand_m, twi, elev_m, dist_drain_m) "
        "will dominate spatial discrimination.\n\n"
        "4. Severe Label Noise in Negatives (False Negative Ambiguity):\n"
        "A label of flood_label == 0 does NOT denote verified dry ground; it means no verified media or civic report was indexed. In flood_dataset.parquet, "
        "there are 1,019 pixel-days where 3-day rainfall reaches >= 60 mm. Of those 1,019 heavy rain pixel-days, ONLY 7 coincide with a positive label (flood_label == 1). "
        "The remaining 1,012 pixel-days with 3-day rain >= 60 mm carry flood_label == 0. Status of label-gap enrichment tasks:\n"
        "  (i) Rainiest unlabelled dates (11 Oct 2017, 7–8 Sep 2017, 26–27 Aug 2022): STILL OPEN. No independent media or civic reports were verified in delivery/events.csv; these dates remain unlabelled.\n"
        "  (ii) 2024–2025 flood events: STILL OPEN. News articles for October 2024 floods exist in data/evidence/, but lie outside the 2017/2021–2023 study period and have not been ingested into the master dataset.\n"
        "  (iii) KSNDMC / IMD ground rain-gauge data: STILL OPEN. A formal request draft was prepared in docs/request_formal_ksndmc_telemetry.md, but no official gauge telemetry has been acquired or merged.\n\n"
        "5. Label Timing vs. 24–48h Forecast Horizon (Temporal Leakage Risk):\n"
        "At row (cell_id, date=d), flood_label represents flooding observed on day d. The feature rain_1d_mm is the realized 24-hour precipitation on day d inclusive (00:00 to 24:00 UTC). "
        "The label is same-day concurrent (diagnostic / nowcast) with the rainfall features, NOT shifted ahead. In an operational 24–48h early warning setting, day d's realized rainfall "
        "is unknown at the morning of day d. Training a model that relies on rain_1d_mm to predict flooding on day d constitutes temporal leakage relative to the 24–48h alert goal. "
        "For a true 24h ahead alert system, you must either drop rain_1d_mm and predict day d flooding strictly from antecedent lags (rain_lag1_mm..14_mm), or substitute rain_1d_mm with an NWP rainfall forecast.\n\n"
        "6. Rain-Gated Sampling:\n"
        "The dataset contains only 583 candidate stormy days selected by the rule: 'Captures days where the maximum rain_3d_mm across the city reaches at least 10 mm, PLUS all calendar days "
        "from 14 days before to 7 days after each confirmed flood event.' Trivial dry days outside flood windows were omitted during construction. The deployed model serving pipeline "
        "must implement the identical candidate pre-filter (max(rain_3d) >= 10 mm) before invoking model inference.\n\n"
        "7. Catalog Source Limits:\n"
        "The 6 confirmed events originate from a single civil engineering technical study (Sajjan 2022) supplemented by mainstream English media articles. "
        "High-income commercial tech corridors receive extensive reporting; low-income valley informal settlements flood regularly but lack media coverage. The catalog has high precision but low recall.\n\n"
        "8. Satellite-Derived vs. Gauge Rainfall:\n"
        "CHIRPS is a satellite infrared product blended with sparse stations. Convective cloudburst cells in Bengaluru are hyper-local (< 2 km across). On 4 September 2022, local rain gauges recorded "
        "131.6 mm to 148.0 mm, but CHIRPS Pixel 12 smoothed this down to 30.85 mm (a 4.3x areal attenuation). Never apply absolute rain thresholds (e.g. > 70 mm) to CHIRPS features."
    )
    
    # -------------------------------------------------------------
    # 5. Recommended Modelling Protocol
    # -------------------------------------------------------------
    doc.add_heading("5. Recommended Modelling Protocol", level=1)
    doc.add_paragraph(
        "These modeling guidelines are recommendations based on empirical dataset properties, not rigid requirements:\n"
        "• Baseline Model: Fit a simple Logistic Regression with L2 regularization first to establish linear benchmarks.\n"
        "• Tree-Based Model: Train XGBoost with shallow trees (max_depth = 3 to 5), high shrinkage (learning_rate = 0.03), and strong column subsampling (colsample_bytree = 0.7) to prevent tree splits from memorizing specific pixel-cell combinations.\n"
        "• Cross-Validation Strategy: Use 6-fold Leave-One-Event-Out cross-validation (LOEO-CV). Purge candidate days within +/- 7 days of the test event from the training fold to eliminate antecedent moisture leakage.\n"
        "• Class Imbalance Weighting: Set XGBoost scale_pos_weight = (len(neg) / len(pos)) ≈ 7,350, or train with sample weights (high confidence = 1.0, medium = 0.7, low buffer = 0.4).\n"
        "• Evaluation Metrics: Do NOT evaluate using raw accuracy or ROC-AUC (which are inflated by 99.98% true negatives). Report Precision-Recall AUC (PR-AUC) against the base rate (0.0136%), Recall at fixed alert rates (e.g. recall in top 1% or top 2% highest-risk cells in the city), and Critical Success Index (CSI / Threat Score).\n"
        "• Report Confidence Honestly: Given the sample size of 6 events, always report per-event results and cross-validation standard deviations."
    )
    
    # -------------------------------------------------------------
    # 6. Reproducibility
    # -------------------------------------------------------------
    doc.add_heading("6. Reproducibility", level=1)
    doc.add_paragraph(
        "Exact commands to rebuild, validate, and test from repository root:\n"
        "  1. python pipeline/validate_dataset.py delivery/flood_dataset.parquet\n"
        "  2. pytest tests/test_rainfall.py tests/test_geocode.py tests/test_static.py tests/test_grid.py\n"
        "  3. python pipeline/verify_quotes.py\n"
        "  4. python pipeline/handoff_stats.py\n\n"
        "Dataset Version: v1.0-prod | Git Commit: e615b72 | Manifest Location: data/evidence/manifest.csv\n\n"
        "Execution Results Recorded on 2026-11-16:\n"
        "• pipeline/validate_dataset.py: PASS across all 17 Section 9 checks; FAILED CHECKS: 0 (rows: 1,764,158 | cells: 3,026 | days: 583 | positives: 240).\n"
        "• pytest (4 test suites): 28 passed in 2.58s (test_rainfall: 5 passed, test_geocode: 4 passed, test_static: 5 passed, test_grid: 14 passed).\n"
        "• pipeline/verify_quotes.py: All cited quotes verified verbatim against data/evidence/ files (0 errors)."
    )
    
    # -------------------------------------------------------------
    # 7. Open Items for the Team
    # -------------------------------------------------------------
    doc.add_heading("7. Open Items for the Team", level=1)
    doc.add_paragraph("The following tasks remain open from the data pipeline audit, with designated owner placeholders:")
    
    table_open = doc.add_table(rows=6, cols=4)
    o_headers = ["Item #", "Open Task Description", "Current State", "Assigned Owner Placeholder"]
    for j, h in enumerate(o_headers):
        table_open.rows[0].cells[j].text = h
        
    o_data = [
        ["1", "Unlabelled Heavy Rain Dates: Corroborate media/civic reports for 11 Oct 2017, 7–8 Sep 2017, 26–27 Aug 2022 (>60 mm rain).", "STILL OPEN", "[Owner: Data Engineering / Member 1]"],
        ["2", "2024–2025 Event Ingestion: Acquire 2024 CHIRPS rasters and ingest October 2024 flood events into catalog.", "STILL OPEN", "[Owner: Data Engineering / Member 1]"],
        ["3", "KSNDMC Telemetry Access: Follow up on formal RTI/telemetry request for ground weather station records.", "STILL OPEN", "[Owner: Project Lead]"],
        ["4", "24h Ahead Feature Split: Construct lag-only feature set (rain_lag1_mm..14_mm) to prevent nowcast temporal leakage.", "READY FOR ML", "[Owner: ML Engineering / Member 2]"],
        ["5", "Pre-Inference Rain Gate: Implement candidate day gate (max(rain_3d) >= 10 mm) in FastAPI serving backend.", "READY FOR BACKEND", "[Owner: Backend / Member 3]"]
    ]
    for i, row in enumerate(o_data):
        for j, val in enumerate(row):
            table_open.rows[i+1].cells[j].text = val
    style_table(table_open)
    doc.add_paragraph("Table 3: Tracked open items and designated team owner placeholders.")
    
    out_file = "delivery/ML_Model_Training_Guide_for_Member2.docx"
    doc.save(out_file)
    print(f"Guide successfully written to {out_file}")

if __name__ == "__main__":
    build_ml_guide()
