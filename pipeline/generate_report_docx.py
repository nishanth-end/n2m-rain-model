"""
Build delivery/Flood_Data_Pipeline_Report.docx
Master report for Community Project Review (1BCP308, Team N2M, DSCE)
Member 1: Geospatial Data Pipeline
"""

import os, sys
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

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
        hr = hp.add_run("Bengaluru Predictive Flood Data Pipeline Report | Team N2M (1BCP308)")
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

def build_report():
    doc = docx.Document()
    add_header_footer(doc)
    
    # Base styling
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Calibri'
    normal_style.font.size = Pt(11)
    normal_style.font.color.rgb = RGBColor(51, 51, 51)
    
    # -------------------------------------------------------------
    # 1. Title Page
    # -------------------------------------------------------------
    p_title_pre = doc.add_paragraph()
    p_title_pre.paragraph_format.space_before = Pt(72)
    
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("BENGALURU FLOOD PREDICTIVE MODEL")
    r_title.font.size = Pt(26)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(31, 73, 125)
    
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Geospatial Data Engineering & Pipeline Delivery Report")
    r_sub.font.size = Pt(16)
    r_sub.font.color.rgb = RGBColor(89, 89, 89)
    p_sub.paragraph_format.space_after = Pt(40)
    
    p_meta = doc.add_paragraph()
    p_meta.add_run("Course / Project: ").bold = True
    p_meta.add_run("Community Project (1BCP308)\n")
    p_meta.add_run("Institution: ").bold = True
    p_meta.add_run("Dayananda Sagar College of Engineering (DSCE), Bengaluru\n")
    p_meta.add_run("Project Team: ").bold = True
    p_meta.add_run("Team N2M\n")
    p_meta.add_run("Project Member: ").bold = True
    p_meta.add_run("Member 1 — Geospatial Data Pipeline Engineer\n")
    p_meta.add_run("Faculty Guide / Reviewer: ").bold = True
    p_meta.add_run("Prof. Punith Kumar\n")
    p_meta.add_run("Date of Delivery: ").bold = True
    p_meta.add_run("October 9, 2026\n")
    p_meta.add_run("Specification Document: ").bold = True
    p_meta.add_run("Flood Model Dataset Specification v1.0 (Authored by Member 2)\n")
    p_meta.add_run("Dataset Version: ").bold = True
    p_meta.add_run("v1.0-prod\n")
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # Table of Contents placeholder
    # -------------------------------------------------------------
    h_toc = doc.add_heading("Table of Contents", level=1)
    p_toc = doc.add_paragraph()
    p_toc.add_run("1. Executive Summary\n"
                  "2. Project Background, Objectives & Team Scope\n"
                  "3. Master Data Sources Reference\n"
                  "4. Pipeline Architecture & Methodology\n"
                  "5. Ground-Truth Event Catalogue\n"
                  "6. Spatial Labelling Methodology\n"
                  "7. Delivered Data Artifacts\n"
                  "8. Quality Assurance & Section 9 Acceptance Checks\n"
                  "9. Dataset Statistics & Exploratory Analysis\n"
                  "10. Known Technical Limitations & Operational Risks\n"
                  "11. Engineering Recommendations & Roadmap\n"
                  "12. Reproducibility & Software Environment\n"
                  "13. Handoff Briefing for Member 2 (Model Training)\n"
                  "Appendix A: Full Event Ground-Truth Directory\n"
                  "Appendix B: Primary Dataset Schema & Data Dictionary\n"
                  "Appendix C: Acceptance Validator Output (Verbatim)\n"
                  "Appendix D: Discrepancy Log & Open Issues")
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 2. Executive Summary
    # -------------------------------------------------------------
    doc.add_heading("1. Executive Summary", level=1)
    doc.add_paragraph(
        "This engineering report documents the completed geospatial data pipeline and delivery package for the "
        "Bengaluru Predictive Flood Alert System (Community Project 1BCP308, Team N2M). Acting as Member 1 "
        "(Geospatial Data Pipeline), all data assets, terrain transformations, rainfall series, and binary labels "
        "have been engineered strictly adhering to Member 2's Flood Model Dataset Specification v1.0."
    )
    doc.add_paragraph(
        "Key Engineering Milestones Delivered:\n"
        "• Master Spatial Skeleton: Constructed a full-city 500-metre regular lattice across Greater Bengaluru "
        "(EPSG:32643 native projection), partitioning the 711.59 km² Bruhat Bengaluru Mahanagara Palike (BBMP) "
        "administrative extent into exactly 3,026 discrete grid cells spanning 198 municipal wards.\n"
        "• High-Resolution Terrain & Urban Modeling: Extracted and conditioned 10 static hydrological, topographical, "
        "and land-cover features per cell with 0 missing values from Copernicus GLO-30 DSM, ESA WorldCover 2021 v200, "
        "and OpenStreetMap vector networks (Hand Above Nearest Drainage, Topographic Wetness Index, flow accumulation, "
        "built-up fraction, and nearest distances to lakes, rajakaluves, and arterial highways).\n"
        "• Continuous Rainfall Series: Processed 976 daily GeoTIFF rasters from the Climate Hazards Group InfraRed "
        "Precipitation with Stations (CHIRPS v2.0 p05) product over four historical wet seasons (April–November of 2017, "
        "2021, 2022, and 2023). Mapped every cell to its nearest 0.05° pixel and computed rolling sums (1, 3, 7, 14, 30 days) "
        "and antecedent daily lags (lags 1 to 14) from continuous calendars before row selection.\n"
        "• Multi-Year Training Dataset: Assembled the master machine learning table (delivery/flood_dataset.parquet), "
        "capturing all 3,026 cells over 583 May–November candidate stormy days (1,764,158 rows × 42 columns). "
        "All 17 automated acceptance criteria from Appendix B of the specification passed with zero failures.\n"
        "• Verified Ground Truth: Established an audit catalogue of 5 confirmed flood events spanning 2017 to 2023, "
        "yielding 175 positive cell-days (22 report-mapped centre cells and 153 topological 3×3 buffer neighbours)."
    )
    doc.add_paragraph(
        "Primary Operational Limitation: Satellite infrared precipitation (CHIRPS ~5 km) attenuates high-intensity localized "
        "cloudburst peaks (such as the 131.6 mm 12-hour gauge record observed on the night of 4–5 September 2022) to areal averages "
        "of 23–31 mm. Machine learning models trained on this dataset must prioritize cumulative antecedent metrics (rain_3d_mm, "
        "rain_7d_mm) rather than raw single-day peak thresholds."
    )
    
    # -------------------------------------------------------------
    # 3. Project Background & Goal
    # -------------------------------------------------------------
    doc.add_heading("2. Project Background, Objectives & Team Scope", level=1)
    doc.add_paragraph(
        "Bengaluru experiences severe recurring urban waterlogging driven by rapid impermeabilization, loss of historic interconnecting "
        "lake cascades (keres), valley encroachments, and inadequate stormwater drains (rajakaluves). The primary objective of the "
        "N2M project is to develop an automated predictive alerting framework that forecasts the probability of flooding for every 500 m "
        "cell across the metropolitan area 24 to 48 hours in advance."
    )
    doc.add_paragraph(
        "Team Role Division:\n"
        "• Member 1 (Author — Data Pipeline): Responsible for acquiring raw remote sensing and GIS datasets, constructing the 500 m "
        "spatial grid, deriving static physical terrain metrics, processing multi-year daily precipitation rasters, establishing "
        "ground-truth event catalogs, assembling training/replay tables, and executing acceptance quality checks.\n"
        "• Member 2 (Model Development): Responsible for model architecture design, feature selection, training extreme gradient boosting "
        "(XGBoost) classifiers and Long Short-Term Memory (LSTM) recurrent networks, class imbalance compensation, spatial cross-validation, "
        "and evaluating performance metrics (Probability of Detection [POD], False Alarm Ratio [FAR], Critical Success Index [CSI]).\n"
        "• Member 3 (Deployment & Real-time Serving): Responsible for building the production FastAPI backend, caching inference pipelines, "
        "integrating live numerical weather prediction (NWP) rainfall forecasts, and rendering interactive risk heatmaps on the web dashboard."
    )
    
    # -------------------------------------------------------------
    # 4. Data Sources
    # -------------------------------------------------------------
    doc.add_heading("3. Master Data Sources Reference", level=1)
    doc.add_paragraph(
        "Every feature and label in the pipeline originates from open scientific, satellite, or administrative data assets. "
        "No synthetic, fabricated, or ungrounded values exist in any delivered dataset."
    )
    
    table_src = doc.add_table(rows=6, cols=6)
    headers = ["Source / Product", "Publisher", "Native Resolution", "Project Role", "Licence", "Access Date"]
    for j, h in enumerate(headers):
        table_src.rows[0].cells[j].text = h
    
    src_data = [
        ["CHIRPS Daily v2.0 p05", "UCSB Climate Hazards Center", "0.05° (~5.3 km), Daily", "Continuous rainfall & antecedent lags", "Public Domain / CC BY 4.0", "2026-10-08"],
        ["Copernicus GLO-30 DSM", "European Space Agency / Airbus", "30 m (1.0 arcsec)", "Raw elevation, slope, TWI, HAND, flow accumulation", "Open Access (Copernicus)", "2026-10-07"],
        ["WorldCover 2021 v200", "ESA / VITO Remote Sensing", "10 m global raster", "Impervious built-up fraction (Class 50)", "CC BY 4.0", "2026-10-07"],
        ["OpenStreetMap (Overpass)", "OpenStreetMap Contributors", "Vector lines / polygons", "Waterways, rajakaluves, lakes, major highway networks", "ODbL 1.0", "2026-10-08"],
        ["BBMP 198 Ward Boundary", "BBMP / OpenCity Bengaluru", "Administrative vector", "500 m grid boundary clipping & spatial CV folds", "Open Data Commons", "2026-10-05"]
    ]
    for i, row in enumerate(src_data):
        for j, val in enumerate(row):
            table_src.rows[i+1].cells[j].text = val
    style_table(table_src)
    doc.add_paragraph("Table 1: Master repository of external geospatial and meteorological data sources.")
    
    # -------------------------------------------------------------
    # 5. Methodology
    # -------------------------------------------------------------
    doc.add_heading("4. Pipeline Architecture & Methodology", level=1)
    doc.add_paragraph(
        "The data pipeline is designed as an idempotent, linear execution DAG (Directed Acyclic Graph) executed strictly from the "
        "repository root via Python scripts. Below is the technical breakdown of each component."
    )
    
    doc.add_heading("4.1 Spatial Grid Construction (pipeline/01_grid.py)", level=2)
    doc.add_paragraph(
        "• Purpose: Establishes the authoritative 500 m planar grid and administrative ward spatial join.\n"
        "• Projection Framework: All planar spatial distance calculations are executed in EPSG:32643 (WGS 84 / UTM Zone 43N). "
        "Cell centroids are exported as geographic coordinates in EPSG:4326 (WGS 84).\n"
        "• Boundary & Clipping: The official BBMP 2011 boundary (198 wards) covers 711.59 km². A 500 m lattice generates 3,026 cells "
        "(2,674 interior cells of exactly 0.250 km² and 352 boundary-intersected polygons with true clipped area_km2 preserved).\n"
        "• Cell Renumbering Ban: Cell IDs are fixed as integers from 0 to 3,025 and are invariant across all deliverables."
    )
    
    doc.add_heading("4.2 Static Feature Extraction (pipeline/02_static_features.py)", level=2)
    doc.add_paragraph(
        "• Elevation & Slope: Extracted from raw Copernicus GLO-30 DSM (elev_m, slope_deg). Aggregated via zonal mean.\n"
        "• Hydrological Conditioning & HAND: The raw DSM was conditioned using D8 flow routing algorithms. Stream networks were "
        "derived at an optimal contributing threshold matching the vector drainage density of Bengaluru. Height Above Nearest "
        "Drainage (hand_m) measures the vertical elevation difference from each cell to its nearest drainage channel.\n"
        "• Flow Accumulation & TWI: Maximum upstream contributing area (flow_acc) is computed in km². Topographic Wetness Index (twi) "
        "is derived using the standard formula:\n"
        "    TWI = ln( a / tan(β) )\n"
        "where a represents specific contributing catchment area (m²/m) and β represents local terrain slope in radians.\n"
        "• Urban Imperviousness: Built-up fraction (imperv_frac) is extracted as the spatial mean of ESA WorldCover Class 50 (built-up).\n"
        "• Vector Distances & Lake Density: OSM Overpass vectors were projected to UTM 43N. Distances from cell centroids to the nearest "
        "drainage channel (dist_drain_m), lake boundary (dist_lake_m), and major road (dist_road_m) were computed via KDTree Euclidean lookup. "
        "Waterbodies within 1 km (lakes_within_1km) counts dissolved OSM water polygons intersecting a 1,000-metre radius buffer."
    )
    
    doc.add_heading("4.3 Rainfall Processing & Temporal Conventions (pipeline/03_download_chirps.py)", level=2)
    doc.add_paragraph(
        "• Precipitation Rasters: Ingests 976 GeoTIFF rasters from the CHIRPS Daily v2.0 p05 archive, covering the four study seasons "
        "(April 1 to November 30 for 2017, 2021, 2022, 2023). April acts as the 30-day antecedent buffer.\n"
        "• Spatial Allocation: Greater Bengaluru is covered by 37 distinct CHIRPS 0.05° pixels. Each cell is mapped to its nearest pixel "
        "center in cell_pixel_map.csv (mean distance 2.12 km; maximum distance 3.84 km ≤ 4.0 km).\n"
        "• Continuous Rolling Aggregation: Rolling sums (rain_1d_mm, rain_3d_mm, rain_7d_mm, rain_14d_mm, rain_30d_mm) and daily lags "
        "(rain_lag1_mm through rain_lag14_mm) are computed per pixel from the continuous unbroken daily time series BEFORE row selection.\n"
        "• Day 'd' Definition & Alignment: CHIRPS measures rainfall over the UTC calendar day (00:00 to 23:59 UTC, which corresponds to "
        "05:30 IST on day d to 05:30 IST on day d+1). The extreme convective cloudburst that struck on the night of 4 September 2022 "
        "(peaking between 21:00 and 02:00 IST) fell inside UTC calendar day 4 September. The widespread catastrophic flooding observed "
        "on the morning of 5 September aligns with day 5 features via rain_lag1_mm (the day 4 storm total) and rain_3d_mm."
    )
    
    doc.add_heading("4.4 Row Selection, Candidate Days & Sampling Weights", level=2)
    doc.add_paragraph(
        "• Candidate Days Rule: Captures days where the maximum rain_3d_mm across the city reaches at least 10 mm, PLUS all calendar days "
        "from 14 days before to 7 days after each confirmed flood event. Trivial dry days outside flood windows are omitted.\n"
        "• Spatial Completeness: On every candidate day included, ALL 3,026 grid cells are retained. Spatial subsampling is strictly prohibited.\n"
        "• Day Sampling Weights: All 583 candidate days in May–November were fully retained without downsampling. Consequently, "
        "day_sampling_weight is set uniformly to 1.0."
    )
    
    # -------------------------------------------------------------
    # 6. Event Catalogue
    # -------------------------------------------------------------
    doc.add_heading("5. Ground-Truth Event Catalogue", level=1)
    doc.add_paragraph(
        "A rigorous audit was conducted across all potential historical events. Unverifiable sources were expunged. "
        "The final delivery includes 10 documented ground-truth rows across 5 distinct historical flood events spanning 4 years."
    )
    
    table_ev = doc.add_table(rows=11, cols=6)
    ev_headers = ["Event ID", "Date Range", "Documented Location", "Cell ID", "Precision & Source", "Confidence"]
    for j, h in enumerate(ev_headers):
        table_ev.rows[0].cells[j].text = h
        
    ev_data = [
        ["E2022_09", "2022-09-05 to 09-07", "RBD Layout (Sarjapur Road)", "555", "OSM Footprint (Sajjan 2022 Ch.6)", "High"],
        ["E2022_09", "2022-09-05 to 09-07", "Wipro Campus (Sarjapur Road)", "666", "OSM Footprint (Sajjan 2022 Ch.7)", "High"],
        ["E2022_09", "2022-09-05 to 09-07", "Outer Ring Road (RMZ Ecospace)", "847", "Neighbourhood (Sajjan 2022 Ch.8)", "High"],
        ["E2022_09", "2022-09-05 to 09-07", "Epsilon Layout / Yemalur Road", "910", "Neighbourhood (Sajjan 2022 Ch.9)", "High"],
        ["E2022_09", "2022-09-05 to 09-07", "Borewell Road (Whitefield)", "1444", "Neighbourhood (Sajjan 2022 Ch.10)", "High"],
        ["E2022_09", "2022-09-05 to 09-07", "Panathur-Balagere Road (Varthur)", "977", "Neighbourhood (Sajjan 2022 Ch.11)", "High"],
        ["E2022_05", "2022-05-05", "RBD Layout (Sarjapur Road)", "555", "OSM Footprint (Indian Express 2022)", "Low"],
        ["E2021_11", "2021-11-21", "Yelahanka Kendriya Vihar", "2882", "Neighbourhood (The News Minute 2021)", "Low"],
        ["E2017_08", "2017-08-15", "Koramangala 4th Block", "897", "Polygon Centroid (The News Minute 2017)", "Medium"],
        ["E2023_05", "2023-05-21", "KR Circle Underpass", "1478", "Proxy Centroid (Scroll.in 2023)", "Medium"]
    ]
    for i, row in enumerate(ev_data):
        for j, val in enumerate(row):
            table_ev.rows[i+1].cells[j].text = val
    style_table(table_ev)
    doc.add_paragraph("Table 2: Confirmed historical flood event catalogue with precision and source mapping.")
    
    doc.add_paragraph(
        "Events Audited and Removed:\n"
        "• E2017_09 (Hosur-Sarjapur / Anugraha Layout, 27–28 Sep 2017): Cited GardaWorld Crisis24 product 222601. Verification revealed "
        "the URL redirects to a generic login portal, with no public corroboration of flooding in Anugraha Layout on those dates. Expunged.\n"
        "• Deccan Herald Moon Rocket Article (Aug 2022): Discarded due to URL collision/misattribution.\n"
        "• Historical candidate events outside 2017, 2021–2023 (e.g. 2016, 2020) were excluded from active training to maintain unbroken "
        "CHIRPS temporal continuity."
    )
    
    # -------------------------------------------------------------
    # 7. Labelling Approach
    # -------------------------------------------------------------
    doc.add_heading("6. Spatial Labelling Methodology", level=1)
    doc.add_paragraph(
        "Urban flood documentation is inherently incomplete. Low-income valley waterlogging is rarely covered by media, whereas "
        "arterial roads and tech parks receive extensive reporting. The labelling framework addresses this asymmetry transparently:\n"
        "• Centre Cells: The specific 500 m grid cell containing the documented centroid or polygon footprint receives flood_label = 1, "
        "audit_is_buffer_cell = 0, and label_confidence = 'high' or 'medium' as justified by ground evidence.\n"
        "• Topological 3×3 Buffer Neighbours: Surrounding cells in the 8-connected Moore neighborhood receive flood_label = 1, "
        "audit_is_buffer_cell = 1, and are strictly graded with label_confidence = 'low'.\n"
        "• Multi-Day Event Duration: Documented multi-day events (e.g. September 5–7, 2022) carry flood_label = 1 across all active event "
        "days for affected cells, reflecting multi-day inundation cited in technical reports.\n"
        "• Assumed Negatives: Every grid cell not covered by a positive report on a candidate stormy day receives flood_label = 0, "
        "label_source = 'none', and label_confidence = 'low'. Unreported areas are treated as 'not observed flooded', not 'proven dry'."
    )
    
    # -------------------------------------------------------------
    # 8. Delivered Data Artifacts
    # -------------------------------------------------------------
    doc.add_heading("7. Delivered Data Artifacts", level=1)
    doc.add_paragraph(
        "All deliverable datasets are located in delivery/. Every file has been verified against the acceptance schema."
    )
    
    table_deliv = doc.add_table(rows=8, cols=6)
    deliv_headers = ["File Name", "Format", "Rows", "Columns", "Unique Days", "Description"]
    for j, h in enumerate(deliv_headers):
        table_deliv.rows[0].cells[j].text = h
        
    deliv_data = [
        ["cells_static.csv", "CSV", "3,026", "16", "—", "Master static lookup table for all 3,026 cells."],
        ["events.csv", "CSV", "10", "19", "9", "Ground-truth flood event audit directory."],
        ["rainfall_daily.csv", "CSV", "36,112", "5", "976", "Continuous daily rainfall across 37 CHIRPS pixels."],
        ["flood_dataset.parquet", "Parquet", "1,764,158", "42", "583", "Master XGBoost ML table across May–Nov candidate days."],
        ["flood_dataset_event_windows.csv", "CSV", "308,652", "42", "102", "Full cell extract for all 102 May–Nov event window days."],
        ["flood_dataset_pilot.parquet", "Parquet", "66,572", "30", "22", "First test sample (22 Aug to 12 Sep 2022)."],
        ["flood_replay_E2022_09.parquet", "Parquet", "72,624", "42", "24", "Held-out validation replay window for E2022_09."]
    ]
    for i, row in enumerate(deliv_data):
        for j, val in enumerate(row):
            table_deliv.rows[i+1].cells[j].text = val
    style_table(table_deliv)
    doc.add_paragraph("Table 3: Inventory of delivered dataset files in delivery/ directory.")
    
    # -------------------------------------------------------------
    # 9. Validation & Section 9 Checks
    # -------------------------------------------------------------
    doc.add_heading("8. Quality Assurance & Section 9 Acceptance Checks", level=1)
    doc.add_paragraph(
        "The automated acceptance script (pipeline/validate_dataset.py) prescribed in Appendix B of the specification was "
        "executed on the final delivered dataset. All 17 automated criteria passed with zero failures."
    )
    
    table_chk = doc.add_table(rows=15, cols=4)
    chk_headers = ["#", "Acceptance Check (Spec Sec 9)", "Status", "Observed Empirical Evidence"]
    for j, h in enumerate(chk_headers):
        table_chk.rows[0].cells[j].text = h
        
    chk_data = [
        ["1", "Required columns & types", "PASS", "All 42 required and static columns present with correct dtypes."],
        ["2", "Unique key (cell_id, date)", "PASS", "Zero duplicate (cell_id, date) index pairs across 1.76M rows."],
        ["3", "Complete days", "PASS", "Every single date contains exactly all 3,026 grid cells."],
        ["4", "Rainfall consistency", "PASS", "rain_3d == rain_1d + lag1 + lag2 (|diff| < 0.02); non-decreasing windows."],
        ["5", "Missing values", "PASS", "Zero null or NaN values in static and rainfall feature columns."],
        ["6", "Ranges sanity", "PASS", "Elevation (767–952 m), slope (0–12.3°), TWI (4.8–13.1), rain (0–61 mm)."],
        ["7", "Static consistency", "PASS", "Static feature values are perfectly identical on every row for each cell."],
        ["8", "Label validity", "PASS", "flood_label strictly in {0, 1}; all positives carry valid source and event ID."],
        ["9", "Events representation", "PASS", "5 distinct historical events present; all 5 contain positive cell-days."],
        ["10", "Class balance", "PASS", "Reported overall (0.010%), on event windows (0.057%), and wet days (0.013%)."],
        ["11", "No leakage columns", "PASS", "Zero forbidden columns (is_hotspot, primary_cause, etc.) outside audit_."],
        ["12", "rainfall_daily completeness", "PASS", "Continuous calendar: exactly 976 days × 37 pixels = 36,112 rows, is_imputed=0."],
        ["13", "Spatial sanity", "PASS", "September 2022 positives cluster accurately at the 6 documented hotspots."],
        ["14", "Rainfall peak sanity", "PASS", "CHIRPS rain for hotspot pixels peaks on 2022-09-04 (aligning with storm)."]
    ]
    for i, row in enumerate(chk_data):
        for j, val in enumerate(row):
            table_chk.rows[i+1].cells[j].text = val
    style_table(table_chk)
    doc.add_paragraph("Table 4: Status of Section 9 acceptance checks on delivery/flood_dataset.parquet.")
    
    # -------------------------------------------------------------
    # 10. Dataset Statistics & Charts
    # -------------------------------------------------------------
    doc.add_heading("9. Dataset Statistics & Exploratory Analysis", level=1)
    doc.add_paragraph(
        "Summary Metrics:\n"
        "• Total Assembled Rows: 1,764,158\n"
        "• Grid Cell Count: 3,026\n"
        "• Candidate Days: 583 (May 1 to November 30 across 2017, 2021, 2022, 2023)\n"
        "• Total Positive Cell-Days: 175 (Flood rate: 0.0099% overall; 0.0132% on wet days where max rain_3d ≥ 10 mm)\n"
        "• Centre-Only Positive Cell-Days: 22\n"
        "• Buffer-Only Positive Cell-Days: 153"
    )
    
    # Embed Figures
    fig1_path = "delivery/figures/fig1_positives_breakdown.png"
    if os.path.exists(fig1_path):
        p_img1 = doc.add_paragraph()
        p_img1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img1.add_run().add_picture(fig1_path, width=Inches(5.5))
        p_cap1 = doc.add_paragraph("Figure 1: Breakdown of positive cell-days across confirmed flood events.")
        p_cap1.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    fig2_path = "delivery/figures/fig2_sept2022_rainfall.png"
    if os.path.exists(fig2_path):
        p_img2 = doc.add_paragraph()
        p_img2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img2.add_run().add_picture(fig2_path, width=Inches(5.8))
        p_cap2 = doc.add_paragraph("Figure 2: Daily CHIRPS rainfall time series for September 2022 hotspot pixels.")
        p_cap2.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    fig3_path = "delivery/figures/fig3_hotspot_spatial_map.png"
    if os.path.exists(fig3_path):
        p_img3 = doc.add_paragraph()
        p_img3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        p_img3.add_run().add_picture(fig3_path, width=Inches(4.5))
        p_cap3 = doc.add_paragraph("Figure 3: Spatial distribution of documented flood hotspots across Greater Bengaluru.")
        p_cap3.alignment = WD_ALIGN_PARAGRAPH.CENTER
        
    # -------------------------------------------------------------
    # 11. Known Limitations & Risks
    # -------------------------------------------------------------
    doc.add_heading("10. Known Technical Limitations & Operational Risks", level=1)
    doc.add_paragraph(
        "1. CHIRPS Coarse Spatial Resolution & Extreme Underestimation:\n"
        "CHIRPS provides precipitation on a nominal 0.05° (~5.3 km) lattice. Convective urban downpours in Bengaluru are highly localized. "
        "A single-night storm that records 131.6 mm at a municipal ground station is smoothed down to 23–31 mm over a 25 km² pixel area. "
        "XGBoost models must not be trained on single-day absolute thresholds; cumulative features (rain_3d_mm, rain_7d_mm) provide far more reliable signals.\n\n"
        "2. UTC vs. Indian Standard Time (IST) Calendar Offset:\n"
        "CHIRPS daily totals represent 00:00 to 23:59 UTC (ending at 05:30 IST the following morning). Rain falling between midnight and 05:30 IST "
        "is recorded under the previous UTC calendar day. Using rain_lag1_mm and rolling sums accounts for this offset.\n\n"
        "3. Severe Reporting Asymmetry (False Negatives):\n"
        "Documented flood locations heavily favor tech parks (ORR, Sarjapur, Whitefield) and prominent underpasses. Poor informal settlements "
        "and valley slum reaches regularly flood without civic media reporting. Cells labeled flood_label = 0 represent 'unreported' locations, "
        "not confirmed dry conditions.\n\n"
        "4. Effective Training Sample Size Thinness:\n"
        "If event E2022_09 (September 2022) is held out for testing, exactly 34 positive cell-days remain across 4 events for model training "
        "(only 4 centre-cells-only positives). Model training requires aggressive scale_pos_weight or focal loss tuning.\n\n"
        "5. Pre-Monsoon Event E2022_05 Window Truncation:\n"
        "E2022_05 occurred on 5 May 2022. Because CHIRPS downloads covered April 1 to November 30 (with April acting as antecedent buffer), "
        "the nominal -14 day window (21–30 April) is excluded from flood_dataset.parquet to prevent missing values in 30-day rolling sums."
    )
    
    # -------------------------------------------------------------
    # 12. Recommendations & Next Steps
    # -------------------------------------------------------------
    doc.add_heading("11. Engineering Recommendations & Roadmap", level=1)
    doc.add_paragraph(
        "The following engineering extensions are recommended for subsequent project phases (currently marked NOT DONE):\n"
        "1. Ingestion of 2024 and 2025 Seasons: Extending the pipeline to include 2024–2025 CHIRPS data would capture recent heavy rainfall "
        "events and expand positive training volume.\n"
        "2. Sentinel-1 SAR Flood Detection: Authenticating Google Earth Engine (GEE) to ingest Sentinel-1 GRD SAR backscatter differences "
        "would provide objective satellite water detection, overcoming urban reporting biases.\n"
        "3. KSNDMC Ground Telemetry Integration: Integrating rain gauge data from Karnataka State Natural Disaster Monitoring Centre "
        "(KSNDMC) would calibrate local cloudburst extremes.\n"
        "4. Numerical Weather Forecast Archive: Ingesting IMD GFS/NCUM numerical forecast archives to train models on predicted rainfall."
    )
    
    # -------------------------------------------------------------
    # 13. Reproducibility
    # -------------------------------------------------------------
    doc.add_heading("12. Reproducibility & Software Environment", level=1)
    doc.add_paragraph(
        "Software Dependencies: Python 3.9.6, pandas 2.3.3, numpy 2.0.2, pyarrow 21.0.0, rasterio 1.4.3, geopandas 1.0.1, scipy 1.13.1, shapely 2.0.7.\n"
        "Determinism: Random seed is fixed at 42 across all scripts.\n"
        "Regeneration Command Sequence:\n"
        "    python pipeline/01_grid.py\n"
        "    python pipeline/02_static_features.py\n"
        "    python pipeline/03_download_chirps.py\n"
        "    python pipeline/validate_dataset.py delivery/flood_dataset.parquet"
    )
    
    # -------------------------------------------------------------
    # 14. Handoff Notes for Member 2
    # -------------------------------------------------------------
    doc.add_heading("13. Handoff Briefing for Member 2 (Model Training)", level=1)
    doc.add_paragraph(
        "Briefing for Member 2 Prior to Training:\n"
        "1. Primary Dataset: Train XGBoost directly on delivery/flood_dataset.parquet (1,764,158 rows). Numeric features are in raw physical units.\n"
        "2. Group Columns: Do NOT use date, cell_id, ward, or event_id as feature inputs. Use event_id for leave-one-event-out CV and ward for spatial CV.\n"
        "3. Feature Leakage Safeguard: All forbidden outcome columns (is_hotspot, primary_cause) have been removed. Any traceability column begins with audit_.\n"
        "4. Handling Class Imbalance: The overall flood rate is ~0.010%. When holding out E2022_09, exactly 34 positives remain. Set XGBoost "
        "scale_pos_weight = (N_neg / N_pos) or use weighted PR-AUC objectives.\n"
        "5. Buffer Cells: Filter or downweight rows where audit_is_buffer_cell == 1 if training on high-confidence reports only."
    )
    
    # -------------------------------------------------------------
    # Appendices
    # -------------------------------------------------------------
    doc.add_page_break()
    doc.add_heading("Appendix A: Full Event Ground-Truth Directory", level=1)
    p_app_a = doc.add_paragraph("Full audit trail from delivery/events.csv:")
    
    table_app_a = doc.add_table(rows=11, cols=5)
    app_a_headers = ["Event ID", "Place Name", "Cell ID", "Source Citation", "URL / Access"]
    for j, h in enumerate(app_a_headers):
        table_app_a.rows[0].cells[j].text = h
    
    events_df = [
        ["E2022_09", "RBD Layout (Sarjapur Road)", "555", "Sajjan, S. 2022. Floods at Bengaluru City. Ch.6", "Local PDF (2026-10-05)"],
        ["E2022_09", "Wipro Campus (Sarjapur Road)", "666", "Sajjan, S. 2022. Floods at Bengaluru City. Ch.7", "Local PDF (2026-10-05)"],
        ["E2022_09", "ORR (RMZ Ecospace)", "847", "Sajjan, S. 2022. Floods at Bengaluru City. Ch.8", "Local PDF (2026-10-05)"],
        ["E2022_09", "Epsilon Layout / Yemalur", "910", "Sajjan, S. 2022. Floods at Bengaluru City. Ch.9", "Local PDF (2026-10-05)"],
        ["E2022_09", "Borewell Road (Whitefield)", "1444", "Sajjan, S. 2022. Floods at Bengaluru City. Ch.10", "Local PDF (2026-10-05)"],
        ["E2022_09", "Panathur-Balagere Road", "977", "Sajjan, S. 2022. Floods at Bengaluru City. Ch.11", "Local PDF (2026-10-05)"],
        ["E2022_05", "RBD Layout (Sarjapur Road)", "555", "The Indian Express, 18 May 2022", "indianexpress.com/article/...-7924521/"],
        ["E2021_11", "Yelahanka Kendriya Vihar", "2882", "The News Minute, 22 Nov 2021", "thenewsminute.com/...-157884"],
        ["E2017_08", "Koramangala 4th Block", "897", "The News Minute, 04 Oct 2017", "thenewsminute.com/...-koramangala"],
        ["E2023_05", "KR Circle Underpass", "1478", "Scroll.in, 22 May 2023", "scroll.in/latest/1049516/..."]
    ]
    for i, row in enumerate(events_df):
        for j, val in enumerate(row):
            table_app_a.rows[i+1].cells[j].text = val
    style_table(table_app_a)
    
    doc.add_page_break()
    doc.add_heading("Appendix B: Primary Dataset Schema & Data Dictionary", level=1)
    doc.add_paragraph("Master schema for delivery/flood_dataset.parquet (42 columns, 0.00% missing):")
    
    table_app_b = doc.add_table(rows=22, cols=4)
    app_b_headers = ["Column Name", "Data Type", "Physical Unit", "Description & Derivation"]
    for j, h in enumerate(app_b_headers):
        table_app_b.rows[0].cells[j].text = h
        
    schema_sample = [
        ["cell_id", "int64", "ID (0-3025)", "Stable grid cell identifier across all files (EPSG:32643 native)."],
        ["date", "string", "ISO Date", "Calendar day d (UTC day for CHIRPS precipitation)."],
        ["lat, lon", "float64", "Degrees", "Cell centroid coordinates in WGS 84 (EPSG:4326)."],
        ["ward", "int64", "ID (1-198)", "BBMP 2011 municipal ward ID containing centroid."],
        ["rain_pixel_id", "int64", "ID (0-36)", "Nearest CHIRPS 0.05° precipitation pixel supplying rainfall."],
        ["rain_1d_mm", "float64", "mm", "Daily precipitation on day d."],
        ["rain_3d_mm", "float64", "mm", "Rolling 3-day precipitation: rain(d-2) + rain(d-1) + rain(d)."],
        ["rain_7d_mm", "float64", "mm", "Rolling 7-day cumulative precipitation ending on day d."],
        ["rain_14d_mm", "float64", "mm", "Rolling 14-day cumulative precipitation ending on day d."],
        ["rain_30d_mm", "float64", "mm", "Rolling 30-day cumulative antecedent precipitation ending on day d."],
        ["rain_lag1_mm..14_mm", "float64", "mm", "Precipitation on day d-k for k in 1..14."],
        ["elev_m", "float64", "metres", "Mean raw elevation from Copernicus GLO-30 DSM."],
        ["slope_deg", "float64", "degrees", "Mean terrain slope in degrees."],
        ["twi", "float64", "index", "Topographic Wetness Index: ln(flow_acc / tan(slope))."],
        ["hand_m", "float64", "metres", "Height Above Nearest Drainage to hydrologic channel."],
        ["flow_acc", "float64", "km²", "Maximum upstream contributing drainage area."],
        ["imperv_frac", "float64", "fraction", "ESA WorldCover 2021 built-up urban fraction."],
        ["dist_lake_m", "float64", "metres", "Euclidean distance to nearest OSM waterbody polygon."],
        ["dist_drain_m", "float64", "metres", "Euclidean distance to nearest OSM waterway / rajakaluve."],
        ["dist_road_m", "float64", "metres", "Euclidean distance to nearest OSM major road network."],
        ["flood_label", "int64", "binary (0/1)", "1 = flood/waterlogging documented; 0 = assumed dry."]
    ]
    for i, row in enumerate(schema_sample):
        for j, val in enumerate(row):
            table_app_b.rows[i+1].cells[j].text = val
    style_table(table_app_b)
    
    doc.add_page_break()
    doc.add_heading("Appendix C: Acceptance Validator Output (Verbatim)", level=1)
    doc.add_paragraph("Direct output from pipeline/validate_dataset.py on delivery/flood_dataset.parquet:")
    
    val_text = (
        "PASS  required columns present \n"
        "PASS  no duplicate (cell_id, date)\n"
        "PASS  every date has all 3026 cells (0 incomplete days)\n"
        "PASS  no missing rain\n"
        "PASS  no missing static features\n"
        "PASS  rain_1d <= rain_3d <= rain_7d\n"
        "PASS  rain_3d == rain_1d + lag1 + lag2\n"
        "PASS  static features constant per cell\n"
        "PASS  flood_label only 0/1\n"
        "PASS  label_source values allowed\n"
        "PASS  label_confidence values allowed\n"
        "PASS  day_sampling_weight >= 1\n"
        "PASS  175 positive rows\n"
        "PASS  every positive has a label_source\n"
        "PASS  every positive has an event_id\n"
        "PASS  at least 3 distinct events (found 5)\n"
        "PASS  no forbidden columns \n\n"
        "rows: 1764158 | cells: 3026 | days: 583 | date range: 2017-05-07 to 2023-11-09\n"
        "flood rate (all rows): 0.0001\n"
        "positives per event:\n"
        "event_id\n"
        "E2017_08      9\n"
        "E2021_11      9\n"
        "E2022_05      7\n"
        "E2022_09    141\n"
        "E2023_05      9\n\n"
        "FAILED CHECKS: 0"
    )
    p_code = doc.add_paragraph()
    r_code = p_code.add_run(val_text)
    r_code.font.name = "Courier New"
    r_code.font.size = Pt(9.5)
    
    doc.add_page_break()
    doc.add_heading("Appendix D: Discrepancy Log & Open Issues", level=1)
    doc.add_paragraph(
        "1. Discrepancy in Spec vs Actual Cell Count: Spec section 4.2 states 'about 2,900 cells (716 km² at 500 m)'. "
        "The authoritative vector intersection with the 198 BBMP wards yields exactly 3,026 cells (711.59 km²). "
        "Cell ID sequence 0..3025 is preserved intact.\n\n"
        "2. Removal of Event E2017_09: The preliminary catalog included E2017_09 (Crisis24 URL). Re-verification identified "
        "that the URL returned HTTP 301 to a generic portal, with zero independent news verification. Per strict audit rules, "
        "the event was purged from all datasets, reducing the confirmed event count from 6 to 5.\n\n"
        "3. Truncation of E2022_05 -14 Day Window: E2022_05 (5 May 2022) nominally begins its -14 day window on 21 April 2022. "
        "Because March 2022 CHIRPS data was not in the original study download (which starts April 1), computing rolling 30-day "
        "precipitation in late April yields missing values. To preserve the strict rule of zero missing values and adherence to "
        "May–November study periods, April days are excluded from flood_dataset.parquet.\n\n"
        "4. Extreme Class Imbalance for Leave-One-Event-Out Validation: Holding out E2022_09 leaves only 34 positive cell-days for "
        "training across the entire city. Member 2 must be alerted to apply heavy positive class weighting during training."
    )
    
    out_path = "delivery/Flood_Data_Pipeline_Report.docx"
    doc.save(out_path)
    print(f"Master report saved successfully to {out_path}")

if __name__ == "__main__":
    build_report()
