"""
Build delivery/ML_Model_Training_Guide_for_Member2.docx
Master handoff and AI context specification for Member 2 (Model Developer)
Community Project (1BCP308, Team N2M, DSCE)
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
        hr = hp.add_run("ML Training Guide & Dataset Specification | Team N2M (Member 2 Handoff)")
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
    
    # -------------------------------------------------------------
    # Title Page
    # -------------------------------------------------------------
    p_pre = doc.add_paragraph()
    p_pre.paragraph_format.space_before = Pt(60)
    
    p_title = doc.add_paragraph()
    r_title = p_title.add_run("ML MODEL TRAINING GUIDE & DATASET SPECIFICATION")
    r_title.font.size = Pt(24)
    r_title.font.bold = True
    r_title.font.color.rgb = RGBColor(31, 73, 125)
    
    p_sub = doc.add_paragraph()
    r_sub = p_sub.add_run("Comprehensive Hand-off Briefing & AI-Assisted Modeling Context for Member 2")
    r_sub.font.size = Pt(15)
    r_sub.font.color.rgb = RGBColor(89, 89, 89)
    p_sub.paragraph_format.space_after = Pt(36)
    
    p_meta = doc.add_paragraph()
    p_meta.add_run("Project Title: ").bold = True
    p_meta.add_run("Predictive Flood Alert System for Bengaluru (500 m Grid, 24–48h Forecast)\n")
    p_meta.add_run("Course / Institutional Context: ").bold = True
    p_meta.add_run("Community Project (1BCP308), DSCE Bengaluru\n")
    p_meta.add_run("Prepared by: ").bold = True
    p_meta.add_run("Member 1 (Geospatial Data Pipeline)\n")
    p_meta.add_run("Target Audience / Recipient: ").bold = True
    p_meta.add_run("Member 2 (ML Model Developer & AI Pairing Assistant)\n")
    p_meta.add_run("Dataset Version: ").bold = True
    p_meta.add_run("v1.0-prod (Conforms to Flood Model Dataset Specification v1.0)\n")
    p_meta.add_run("Date of Delivery: ").bold = True
    p_meta.add_run("October 9, 2026\n")
    
    doc.add_page_break()
    
    # -------------------------------------------------------------
    # 1. Executive Summary & Fast-Start Guide
    # -------------------------------------------------------------
    doc.add_heading("1. Executive Summary & Fast-Start Guide", level=1)
    doc.add_paragraph(
        "Welcome Member 2! This document is your comprehensive operational guide and LLM prompt context for training "
        "the machine learning models (XGBoost and sequential LSTM) for the Bengaluru Flood Prediction System. "
        "The data engineering phase is 100% complete. You do not need to download, clean, interpolate, or re-grid any raw files."
    )
    doc.add_paragraph(
        "Key Quick-Start Facts:\n"
        "• Primary ML Table: delivery/flood_dataset.parquet (18 MB, 1,764,158 rows × 42 columns).\n"
        "• Observations: Each row represents one 500 m grid cell on one calendar day across Greater Bengaluru (3,026 cells over 583 candidate stormy days).\n"
        "• Target Variable: flood_label (Binary: 1 = flooded/waterlogged, 0 = assumed dry).\n"
        "• Overall Class Imbalance: Flood rate is 0.0099% (~1 in 10,000 rows). Exactly 175 positive cell-days exist in the full dataset.\n"
        "• Validation File: delivery/flood_replay_E2022_09.parquet (72,624 rows covering 24 contiguous days around the catastrophic September 2022 floods).\n"
        "• All 17 automated acceptance criteria from your spec (Appendix B) have passed with zero failures."
    )
    
    # -------------------------------------------------------------
    # 2. Dataset Files in delivery/
    # -------------------------------------------------------------
    doc.add_heading("2. Inventory of Delivered Data Files", level=1)
    doc.add_paragraph("You have been delivered a clean, ready-to-use directory structure in delivery/:")
    
    table_files = doc.add_table(rows=6, cols=5)
    f_headers = ["File Name", "Format", "Size", "Rows", "Primary ML Purpose"]
    for j, h in enumerate(f_headers):
        table_files.rows[0].cells[j].text = h
        
    f_data = [
        ["flood_dataset.parquet", "Parquet", "18 MB", "1,764,158", "Primary training & evaluation table for XGBoost."],
        ["flood_dataset_event_windows.csv", "CSV", "111 MB", "308,652", "All cells on the 102 event window days (-14 to +7 days around events)."],
        ["flood_replay_E2022_09.parquet", "Parquet", "921 KB", "72,624", "Held-out test replay file for September 2022 (24 contiguous days)."],
        ["cells_static.csv", "CSV", "268 KB", "3,026", "Static terrain features and ward lookups for all cells."],
        ["rainfall_daily.csv", "CSV", "1.1 MB", "36,112", "Continuous daily rainfall (976 days × 37 pixels) for LSTM recurrent training."]
    ]
    for i, row in enumerate(f_data):
        for j, val in enumerate(row):
            table_files.rows[i+1].cells[j].text = val
    style_table(table_files)
    doc.add_paragraph("Table 1: Description of files provided in the delivery/ directory.")
    
    # -------------------------------------------------------------
    # 3. Master Schema & Column Rules
    # -------------------------------------------------------------
    doc.add_heading("3. Master Feature Schema & Usage Rules", level=1)
    doc.add_paragraph(
        "The primary dataset (flood_dataset.parquet) contains 42 columns. For your convenience, the columns are categorized "
        "into Features (to feed into the model), Group/Split Keys (for CV only), Labels, and Traceability Audit columns."
    )
    
    doc.add_heading("3.1 Dynamic Rainfall Features (Feed into Model)", level=2)
    doc.add_paragraph(
        "• rain_1d_mm: Rainfall on day d (mm).\n"
        "• rain_3d_mm: Rolling 3-day sum (rain(d-2) + rain(d-1) + rain(d)).\n"
        "• rain_7d_mm, rain_14d_mm, rain_30d_mm: Rolling cumulative precipitation (mm).\n"
        "• rain_lag1_mm ... rain_lag14_mm: Daily rainfall on day d-k for k in 1..14 (mm).\n"
        "Rule: All rolling sums and lags were precomputed from continuous daily time series before row selection. "
        "Every row satisfies the invariant: rain_3d_mm == rain_1d_mm + rain_lag1_mm + rain_lag2_mm (|diff| < 0.02)."
    )
    
    doc.add_heading("3.2 Static Terrain, Hydrologic & Urban Features (Feed into Model)", level=2)
    doc.add_paragraph(
        "• elev_m: Mean elevation from raw Copernicus GLO-30 DSM (range: 767.1 to 951.7 metres).\n"
        "• slope_deg: Mean terrain slope derived from DEM via Horn's method (range: 0.0 to 12.3 degrees).\n"
        "• twi: Topographic Wetness Index = ln(flow_acc_m2 / tan(slope_rad)) (range: 4.8 to 13.1).\n"
        "• hand_m: Height Above Nearest Drainage to hydrologically conditioned stream channels (range: 0.0 to 58.5 metres).\n"
        "• flow_acc: Maximum upstream contributing catchment area in km² (range: 0.0 to 76.5 km²).\n"
        "• imperv_frac: Built-up urban fraction from ESA WorldCover 2021 Class 50 (range: 0.00 to 0.99).\n"
        "• dist_lake_m: Euclidean distance to nearest OpenStreetMap waterbody polygon (metres).\n"
        "• dist_drain_m: Euclidean distance to nearest OSM waterway / rajakaluve (metres).\n"
        "• dist_road_m: Euclidean distance to nearest OSM major road network (motorway/trunk/primary/secondary).\n"
        "• lakes_within_1km: Count of dissolved OSM water polygons intersecting a 1,000 m centroid radius (integer: 0 to 11).\n"
        "Rule: Zero missing values exist in static features. Static values are strictly invariant across time for each cell."
    )
    
    doc.add_heading("3.3 Splitting & Grouping Keys (NEVER Feed as Features)", level=2)
    doc.add_paragraph(
        "• cell_id: Integer (0 to 3,025). Do NOT use as a feature (leads to spatial memorization).\n"
        "• date: ISO string (YYYY-MM-DD). Do NOT use as a feature (temporal memorization).\n"
        "• lat, lon: WGS84 geographic coordinates. Optional for spatial coordinates, but prefer physical terrain features.\n"
        "• ward: Municipal ward ID (1 to 198). Use STRICTLY for GroupKFold spatial cross-validation.\n"
        "• event_id: Code e.g. 'E2022_09'. Use STRICTLY for Leave-One-Event-Out cross-validation."
    )
    
    doc.add_heading("3.4 Labels & Audit Columns", level=2)
    doc.add_paragraph(
        "• flood_label: Binary target (1 = documented flood/waterlogging, 0 = assumed dry).\n"
        "• label_source: Category ('hotspot_pdf', 'news', or 'none').\n"
        "• label_confidence: Grade ('high', 'medium', or 'low').\n"
        "• day_sampling_weight: Float (uniformly 1.0; no downsampling of candidate days was performed).\n"
        "• audit_is_buffer_cell: Binary flag (0 = report-mapped centre cell, 1 = topological 3×3 neighbour).\n"
        "• audit_geocode_precision: String ('landuse_footprint', 'polygon_centroid', 'neighbourhood_centroid')."
    )
    
    # -------------------------------------------------------------
    # 4. Critical Physics & Alignment Nuances
    # -------------------------------------------------------------
    doc.add_heading("4. Critical Physical Nuances: What Your Model Needs to Know", level=1)
    doc.add_paragraph(
        "Your model will fail or learn distorted correlations if you do not account for these three physical realities:"
    )
    doc.add_paragraph(
        "1. CHIRPS Peak Attenuation vs. Ground Cloudbursts:\n"
        "CHIRPS provides satellite infrared precipitation at ~5.3 km resolution (0.05°). In Bengaluru, urban cloudbursts are "
        "hyper-localized convective storms. On the night of 4–5 September 2022, an official IMD city gauge recorded 131.6 mm in 12 hours. "
        "In CHIRPS, this appears as 23.1 mm (Pixel 12) and 30.8 mm (Pixel 20) because the rainfall is spatially averaged across 25 km². "
        "CRITICAL MODELING RULE: Do NOT set hard classification rules expecting >100 mm rainfall. Your model must rely on "
        "cumulative 3-day (rain_3d_mm) and 7-day (rain_7d_mm) features combined with low HAND (hand_m < 5 m) and high TWI.\n\n"
        "2. The UTC Day Definition & Lag 1 Alignment:\n"
        "CHIRPS daily precipitation is measured on the UTC calendar day (00:00 to 23:59 UTC), which corresponds to 05:30 IST on day d to "
        "05:30 IST on day d+1. The catastrophic storm on 4 September 2022 peaked around 21:00–02:00 IST (15:30–20:30 UTC), registering "
        "inside UTC day 4 September. The catastrophic flooding was documented on the morning of 5 September. "
        "CRITICAL MODELING RULE: On day 5, the primary flood signal is captured by rain_lag1_mm (the day 4 storm) and rain_3d_mm. "
        "Always ensure your feature set includes rain_lag1_mm and rain_3d_mm.\n\n"
        "3. Severe Ground-Truth Reporting Asymmetry (False Negatives):\n"
        "Positive labels exist only where citizens or technical agencies documented flooding (tech corridors like ORR, Sarjapur, "
        "Whitefield, Yelahanka, and major arterial underpasses). Unreported valley slums that flooded are labeled 0 ('assumed dry'). "
        "CRITICAL MODELING RULE: Treat flood_label = 0 as 'unobserved/unreported', not guaranteed dry ground. Evaluate models using "
        "Precision-Recall AUC (PR-AUC) and Critical Success Index (CSI), NOT raw accuracy."
    )
    
    # -------------------------------------------------------------
    # 5. Effective Sample Size & Splitting Strategy
    # -------------------------------------------------------------
    doc.add_heading("5. Effective Sample Size & Recommended Splitting", level=1)
    doc.add_paragraph(
        "The ground-truth catalog contains 5 confirmed flood events across 4 years. Here is the exact positive label breakdown:"
    )
    
    table_split = doc.add_table(rows=7, cols=5)
    s_headers = ["Event ID", "Date Range", "Total Positives", "Centre-Only (Seed)", "Buffer Neighbours (3×3)"]
    for j, h in enumerate(s_headers):
        table_split.rows[0].cells[j].text = h
        
    s_data = [
        ["E2017_08", "2017-08-15 (1 day)", "9", "1 (Cell 897, Koramangala)", "8"],
        ["E2021_11", "2021-11-21 (1 day)", "9", "1 (Cell 2882, Yelahanka)", "8"],
        ["E2022_05", "2022-05-05 (1 day)", "7", "1 (Cell 555, Rainbow Drive)", "6 (Boundary lattice)"],
        ["E2022_09", "2022-09-05 to 09-07 (3 days)", "141", "18 (6 hotspots × 3 days)", "123"],
        ["E2023_05", "2023-05-21 (1 day)", "9", "1 (Cell 1478, KR Circle)", "8"],
        ["TOTAL", "5 Historical Events", "175", "22 Centre Positives", "153 Buffer Positives"]
    ]
    for i, row in enumerate(s_data):
        for j, val in enumerate(row):
            table_split.rows[i+1].cells[j].text = val
    style_table(table_split)
    doc.add_paragraph("Table 2: Breakdown of positive training labels by event and spatial precision.")
    
    doc.add_paragraph(
        "THE LEAVE-ONE-EVENT-OUT (LOEO) WARNING:\n"
        "If you hold out event E2022_09 (September 2022) as your validation/test set:\n"
        "• Test Set: 141 positive cell-days across 3 days.\n"
        "• Training Set: ONLY 34 positive cell-days remaining across 4 events (only 4 centre-cells-only positives)!\n"
        "RECOMMENDED MODELING STRATEGY:\n"
        "1. For XGBoost, set scale_pos_weight = (len(train_neg) / len(train_pos)) ≈ 10,000, or train with sample weights:\n"
        "       sample_weight = np.where(df.flood_label == 1, 100.0, 1.0)\n"
        "2. If you want high-precision models, you can optionally filter training to centre cells only (audit_is_buffer_cell == 0), "
        "   or downweight buffer cells (sample weight: centre = 1.0, buffer = 0.4, negative = 1.0).\n"
        "3. Evaluate spatial generalization using GroupKFold(n_splits=5) on ward to ensure the model does not overfit to specific locations."
    )
    
    # -------------------------------------------------------------
    # 6. Complete Python Baseline Script for Member 2
    # -------------------------------------------------------------
    doc.add_heading("6. Ready-to-Run Python Training Script (Copy-Pasteable)", level=1)
    doc.add_paragraph(
        "Here is a complete, leakage-free training baseline you can immediately execute in Python with XGBoost:"
    )
    
    code_text = (
        "import pandas as pd, numpy as np, xgboost as xgb\n"
        "from sklearn.metrics import precision_recall_curve, auc, classification_report\n\n"
        "# 1. Load the dataset\n"
        "df = pd.read_parquet('delivery/flood_dataset.parquet')\n\n"
        "# 2. Define explicit feature list (Zero leakage!)\n"
        "FEATURES = [\n"
        "    'rain_1d_mm', 'rain_3d_mm', 'rain_7d_mm', 'rain_14d_mm', 'rain_30d_mm',\n"
        "    'rain_lag1_mm', 'rain_lag2_mm', 'rain_lag3_mm',\n"
        "    'elev_m', 'slope_deg', 'twi', 'hand_m', 'flow_acc', 'imperv_frac',\n"
        "    'dist_lake_m', 'dist_drain_m', 'dist_road_m', 'lakes_within_1km'\n"
        "]\n\n"
        "# 3. Split by Event: Hold out E2022_09 (September 2022 catastrophic floods)\n"
        "train_df = df[df['event_id'] != 'E2022_09'].copy()\n"
        "test_df  = df[df['event_id'] == 'E2022_09'].copy()\n\n"
        "# 4. Calculate class weighting for extreme imbalance\n"
        "n_pos = (train_df['flood_label'] == 1).sum()\n"
        "n_neg = (train_df['flood_label'] == 0).sum()\n"
        "scale_weight = n_neg / max(n_pos, 1)\n\n"
        "# Sample weights: trust centre cells fully, discount buffer cells\n"
        "train_weights = np.where(\n"
        "    train_df['flood_label'] == 1,\n"
        "    np.where(train_df['audit_is_buffer_cell'] == 0, 1.0, 0.5),\n"
        "    1.0\n"
        ")\n\n"
        "# 5. Train XGBoost Classifier\n"
        "model = xgb.XGBClassifier(\n"
        "    n_estimators=300,\n"
        "    max_depth=4,\n"
        "    learning_rate=0.03,\n"
        "    subsample=0.8,\n"
        "    colsample_bytree=0.8,\n"
        "    scale_pos_weight=scale_weight,\n"
        "    eval_metric='aucpr',\n"
        "    random_state=42\n"
        ")\n"
        "model.fit(train_df[FEATURES], train_df['flood_label'], sample_weight=train_weights)\n\n"
        "# 6. Evaluate on Held-out Event\n"
        "test_preds = model.predict_proba(test_df[FEATURES])[:, 1]\n"
        "p, r, _ = precision_recall_curve(test_df['flood_label'], test_preds)\n"
        "pr_auc = auc(r, p)\n"
        "print(f'Test Event PR-AUC: {pr_auc:.4f}')\n"
    )
    p_code = doc.add_paragraph()
    r_code = p_code.add_run(code_text)
    r_code.font.name = "Courier New"
    r_code.font.size = Pt(9)
    
    # -------------------------------------------------------------
    # 7. AI Prompt Context for Member 2
    # -------------------------------------------------------------
    doc.add_heading("7. Master System Prompt to Feed into Your Coding AI", level=1)
    doc.add_paragraph(
        "If you are using Claude, Cursor, Copilot, or ChatGPT to build your models, copy and paste the box below as your "
        "System Prompt. It provides complete context so your AI will not make beginner errors:"
    )
    
    ai_prompt_text = (
        "=== SYSTEM PROMPT FOR MODELING AI ===\n"
        "You are an expert machine learning engineer assisting Member 2 in building an XGBoost and LSTM predictive flood model "
        "for Bengaluru, India (Community Project 1BCP308, Team N2M). Member 1 has delivered the verified training dataset.\n\n"
        "DATASET SPECIFICATIONS:\n"
        "1. Master file: 'delivery/flood_dataset.parquet' (1,764,158 rows, 42 columns, 3,026 spatial cells, 583 candidate stormy days).\n"
        "2. Ground truth target: 'flood_label' (0 or 1). Extreme class imbalance: 175 positives out of 1.76M rows (~0.0099%).\n"
        "3. Physical features to use: rain_1d_mm, rain_3d_mm, rain_7d_mm, rain_14d_mm, rain_30d_mm, rain_lag1_mm..14_mm, "
        "   elev_m, slope_deg, twi, hand_m, flow_acc, imperv_frac, dist_lake_m, dist_drain_m, dist_road_m, lakes_within_1km.\n"
        "4. DO NOT use date, cell_id, ward, or event_id as features (use ward for spatial GroupKFold, event_id for event cross-validation).\n"
        "5. Physical Nuance: CHIRPS daily rain (~5.3 km) attenuates extreme single-day cloudbursts (a 131 mm storm registers as ~25-30 mm). "
        "   Rely heavily on cumulative sums (rain_3d_mm, rain_7d_mm) and lag 1.\n"
        "6. Validation: Hold out event 'E2022_09' for test replay using 'delivery/flood_replay_E2022_09.parquet' (72,624 rows).\n"
        "7. Class weighting: Use scale_pos_weight or weighted cross-entropy. Do not evaluate with raw accuracy; use PR-AUC and Critical Success Index (CSI).\n"
        "=== END SYSTEM PROMPT ===\n"
    )
    p_ai = doc.add_paragraph()
    r_ai = p_ai.add_run(ai_prompt_text)
    r_ai.font.name = "Courier New"
    r_ai.font.size = Pt(8.5)
    
    out_file = "delivery/ML_Model_Training_Guide_for_Member2.docx"
    doc.save(out_file)
    print(f"Guide successfully written to {out_file}")

if __name__ == "__main__":
    build_ml_guide()
