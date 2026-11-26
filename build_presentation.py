"""
N²M Flood Prediction Model — 10-Slide Presentation Generator
============================================================
Creates a publication-grade, professional 10-slide PowerPoint presentation (.pptx)
adhering to the project's exact palette, layout guidelines, and genuine assets.
"""

import os
import pptx
from pptx import Presentation
from pptx.util import Inches, Pt
from pptx.enum.text import PP_ALIGN, MSO_ANCHOR
from pptx.enum.shapes import MSO_SHAPE
from pptx.dml.color import RGBColor

# -----------------------------------------------------------------------------
# PALETTE CONSTANTS
# -----------------------------------------------------------------------------
COLOR_BG = RGBColor(16, 24, 32)          # Midnight Slate: #101820
COLOR_SURFACE = RGBColor(28, 42, 53)     # Slate Surface: #1C2A35
COLOR_SURFACE_ALT = RGBColor(36, 52, 66) # Card Fill: #243442
COLOR_MINT = RGBColor(53, 208, 160)      # Signal Mint: #35D0A0
COLOR_AMBER = RGBColor(242, 184, 75)     # Rain Amber: #F2B84B
COLOR_WHITE = RGBColor(231, 237, 242)    # Cloud White: #E7EDF2
COLOR_MUTED = RGBColor(152, 170, 183)    # Muted Text: #98AAB7
COLOR_BORDER = RGBColor(42, 63, 80)      # Subtle Border: #2A3F50
COLOR_RED = RGBColor(239, 68, 68)        # High Priority Red
COLOR_ORANGE = RGBColor(249, 115, 22)    # Moderate Priority Orange

FONT_HEADING = "Inter"
FONT_BODY = "Inter"
FONT_MONO = "JetBrains Mono"

def set_slide_background(slide):
    background = slide.background
    fill = background.fill
    fill.solid()
    fill.fore_color.rgb = COLOR_BG

def add_header(slide, title_text, category_text=None, slide_num=None):
    # Category / breadcrumb tag
    if category_text:
        cat_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.4), Inches(10), Inches(0.3))
        tf = cat_box.text_frame
        tf.word_wrap = True
        tf.margin_left = tf.margin_top = tf.margin_right = tf.margin_bottom = 0
        p = tf.paragraphs[0]
        p.text = category_text.upper()
        p.font.name = FONT_MONO
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = COLOR_MINT

    # Title
    t_box = slide.shapes.add_textbox(Inches(0.8), Inches(0.68), Inches(10.5), Inches(0.6))
    tf2 = t_box.text_frame
    tf2.word_wrap = True
    tf2.margin_left = tf2.margin_top = tf2.margin_right = tf2.margin_bottom = 0
    p2 = tf2.paragraphs[0]
    p2.text = title_text
    p2.font.name = FONT_HEADING
    p2.font.size = Pt(22)
    p2.font.bold = True
    p2.font.color.rgb = COLOR_WHITE

    # Slide number indicator
    if slide_num:
        num_box = slide.shapes.add_textbox(Inches(11.8), Inches(0.45), Inches(0.8), Inches(0.3))
        tf_num = num_box.text_frame
        p_num = tf_num.paragraphs[0]
        p_num.alignment = PP_ALIGN.RIGHT
        p_num.text = f"{slide_num:02d} / 10"
        p_num.font.name = FONT_MONO
        p_num.font.size = Pt(10)
        p_num.font.color.rgb = COLOR_MUTED

def add_card(slide, left, top, width, height, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER):
    shape = slide.shapes.add_shape(MSO_SHAPE.RECTANGLE, left, top, width, height)
    shape.fill.solid()
    shape.fill.fore_color.rgb = bg_color
    if border_color:
        shape.line.color.rgb = border_color
        shape.line.width = Pt(1)
    else:
        shape.line.fill.background()
    return shape

# -----------------------------------------------------------------------------
# BUILD SLIDES
# -----------------------------------------------------------------------------

def build_presentation(output_pptx="N2M_Flood_Prediction_Presentation.pptx"):
    prs = Presentation()
    prs.slide_width = Inches(13.333)
    prs.slide_height = Inches(7.5)
    blank_layout = prs.slide_layouts[6]

    # =========================================================================
    # SLIDE 1: TITLE SLIDE
    # =========================================================================
    s1 = prs.slides.add_slide(blank_layout)
    set_slide_background(s1)

    # Ambient backdrop card
    add_card(s1, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
    
    # Accent badge
    badge = s1.shapes.add_textbox(Inches(1.3), Inches(1.2), Inches(6.0), Inches(0.35))
    tf = badge.text_frame
    p = tf.paragraphs[0]
    p.text = "UNDERGRADUATE ENGINEERING MINI-PROJECT PRESENTATION"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_MINT

    # Big Brand Title
    title_box = s1.shapes.add_textbox(Inches(1.3), Inches(1.65), Inches(10.5), Inches(1.3))
    tf_t = title_box.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = "N²M"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(56)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

    # Subtitle
    sub_box = s1.shapes.add_textbox(Inches(1.3), Inches(2.95), Inches(10.5), Inches(0.6))
    tf_s = sub_box.text_frame
    p_s = tf_s.paragraphs[0]
    p_s.text = "Flood Prediction & Urban Susceptibility Analysis"
    p_s.font.name = FONT_HEADING
    p_s.font.size = Pt(24)
    p_s.font.bold = True
    p_s.font.color.rgb = COLOR_AMBER

    # Lead description
    desc_box = s1.shapes.add_textbox(Inches(1.3), Inches(3.65), Inches(10.5), Inches(0.8))
    tf_d = desc_box.text_frame
    tf_d.word_wrap = True
    p_d = tf_d.paragraphs[0]
    p_d.text = "A data-driven exploration of urban flood susceptibility in Bengaluru combining 30 m terrain indices, multi-pixel satellite precipitation matrices, and gradient-boosted spatial ranking."
    p_d.font.name = FONT_BODY
    p_d.font.size = Pt(14)
    p_d.font.color.rgb = COLOR_MUTED

    # Institutional bottom bar inside card
    div = s1.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.3), Inches(4.7), Inches(10.733), Pt(1))
    div.fill.solid()
    div.fill.fore_color.rgb = COLOR_BORDER
    div.line.fill.background()

    # Meta details
    meta_box = s1.shapes.add_textbox(Inches(1.3), Inches(4.9), Inches(10.733), Inches(1.4))
    tf_m = meta_box.text_frame
    p_m1 = tf_m.paragraphs[0]
    p_m1.text = "Department of Computer Science & Engineering  •  Dayananda Sagar College of Engineering"
    p_m1.font.name = FONT_HEADING
    p_m1.font.size = Pt(13)
    p_m1.font.bold = True
    p_m1.font.color.rgb = COLOR_WHITE

    p_m2 = tf_m.add_paragraph()
    p_m2.text = "Team: Nishanth G M  •  Mohith M  •  Nihal Rao   |   Faculty Guide: Dr. Punith Kumar"
    p_m2.font.name = FONT_BODY
    p_m2.font.size = Pt(12)
    p_m2.font.color.rgb = COLOR_MUTED
    p_m2.space_before = Pt(4)

    p_m3 = tf_m.add_paragraph()
    p_m3.text = "Academic Year 2026–2027  •  Bengaluru, Karnataka, India"
    p_m3.font.name = FONT_MONO
    p_m3.font.size = Pt(11)
    p_m3.font.color.rgb = COLOR_MINT
    p_m3.space_before = Pt(4)

    # =========================================================================
    # SLIDE 2: THE PROBLEM
    # =========================================================================
    s2 = prs.slides.add_slide(blank_layout)
    set_slide_background(s2)
    add_header(s2, "Why urban flooding is difficult to anticipate", "01 / CONTEXT & MOTIVATION", 2)

    # Left Column: Key Problem Drivers (3 Cards)
    cards_data = [
        ("Disrupted Natural Drainage", "Bengaluru's historic interconnected lake cascades (keres) and primary stormwater channels (rajakaluves) have been heavily encroached, turning natural drainage corridors into artificial backflow bottlenecks.", COLOR_AMBER),
        ("Massive Concretization (>93%)", "Impervious surface area expanded from <8% in 1973 to over 93% in 2020. Rainwater cannot infiltrate natural soil, generating instantaneous surface runoff during heavy storms.", COLOR_MINT),
        ("Localized Convective Thunderstorms", "Tropical storms drop 70–120 mm within 90 minutes over isolated sectors (e.g. Bellandur / Mahadevapura) while northern wards remain dry. City-wide rain alerts fail to capture micro-topography.", COLOR_WHITE),
    ]

    card_w = Inches(5.6)
    card_h = Inches(1.55)
    for idx, (head, body, color_accent) in enumerate(cards_data):
        top_pos = Inches(1.4) + idx * Inches(1.75)
        add_card(s2, Inches(0.8), top_pos, card_w, card_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
        
        # Indicator line
        ind = s2.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(0.8), top_pos, Pt(4), card_h)
        ind.fill.solid()
        ind.fill.fore_color.rgb = color_accent
        ind.line.fill.background()

        tb = s2.shapes.add_textbox(Inches(1.05), top_pos + Inches(0.12), card_w - Inches(0.35), card_h - Inches(0.24))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = head
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(13)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        
        p2 = tf.add_paragraph()
        p2.text = body
        p2.font.name = FONT_BODY
        p2.font.size = Pt(10.5)
        p2.font.color.rgb = COLOR_MUTED
        p2.space_before = Pt(3)

    # Right Column: The Core Challenge / Motivation Callout Card
    rc_left = Inches(6.7)
    rc_width = Inches(5.8)
    rc_height = Inches(5.05)
    add_card(s2, rc_left, Inches(1.4), rc_width, rc_height, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)

    tb_r = s2.shapes.add_textbox(rc_left + Inches(0.4), Inches(1.7), rc_width - Inches(0.8), rc_height - Inches(0.6))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    
    p = tf_r.paragraphs[0]
    p.text = "THE CIVIC & SCIENTIFIC DILEMMA"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER

    p = tf_r.add_paragraph()
    p.text = "Generalized municipal alerts do not tell residents or engineers which specific streets or underpasses will flood."
    p.font.name = FONT_HEADING
    p.font.size = Pt(16)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(8)

    p = tf_r.add_paragraph()
    p.text = "• Full 2D hydrodynamic civil simulations (e.g. SWMM) require unavailable underground sewer pipe telemetry and take hours to compute.\n\n• Citizens receive broad city-wide warnings that offer zero spatial differentiation.\n\n• Our Motivation: Build an open-source, data-driven machine learning framework that evaluates physical terrain hollows and dynamic rainfall to provide actionable, neighborhood-scale relative susceptibility rankings."
    p.font.name = FONT_BODY
    p.font.size = Pt(11.5)
    p.font.color.rgb = COLOR_MUTED
    p.space_before = Pt(14)

    # =========================================================================
    # SLIDE 3: FROM CITY TO DATA
    # =========================================================================
    s3 = prs.slides.add_slide(blank_layout)
    set_slide_background(s3)
    add_header(s3, "Turning a city into a dataset", "02 / SPATIAL DISCRETIZATION", 3)

    # 4 Stat Metric Cards across the top
    stats = [
        ("3,026", "Spatial Cells", "Uniform Cartesian grid covering all BBMP wards", COLOR_MINT),
        ("500 × 500 m", "Cell Dimension", "0.25 km² (25 hectares) micro-catchment resolution", COLOR_AMBER),
        ("711.59 km²", "Study Area", "Greater Bengaluru municipal territory (198 wards)", COLOR_WHITE),
        ("18 Features", "Input Vector", "10 static terrain morphology + 8 dynamic rainfall", COLOR_MINT),
    ]

    stat_w = Inches(2.78)
    stat_h = Inches(1.5)
    for idx, (num, label, desc, col) in enumerate(stats):
        x = Inches(0.8) + idx * Inches(2.98)
        add_card(s3, x, Inches(1.4), stat_w, stat_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
        
        tb = s3.shapes.add_textbox(x + Inches(0.15), Inches(1.5), stat_w - Inches(0.3), stat_h - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = num
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(24)
        p1.font.bold = True
        p1.font.color.rgb = col
        
        p2 = tf.add_paragraph()
        p2.text = label
        p2.font.name = FONT_HEADING
        p2.font.size = Pt(11)
        p2.font.bold = True
        p2.font.color.rgb = COLOR_WHITE
        p2.space_before = Pt(2)

        p3 = tf.add_paragraph()
        p3.text = desc
        p3.font.name = FONT_BODY
        p3.font.size = Pt(9)
        p3.font.color.rgb = COLOR_MUTED
        p3.space_before = Pt(2)

    # Bottom Split Layout: Why Grid Discretization Matters
    b_left = Inches(0.8)
    b_w = Inches(5.7)
    b_h = Inches(3.7)
    add_card(s3, b_left, Inches(3.1), b_w, b_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)

    tb = s3.shapes.add_textbox(b_left + Inches(0.3), Inches(3.25), b_w - Inches(0.6), b_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True
    p = tf.paragraphs[0]
    p.text = "THE SPATIAL ABSTRACTION"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_MINT

    p = tf.add_paragraph()
    p.text = "Why 500 m Cartesian Cells?"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(4)

    p = tf.add_paragraph()
    p.text = "• Bridges continuous elevation rasters and discrete machine learning tabular vectors.\n\n• Coarse enough to match regional satellite rainfall products (~5.3 km CHIRPS) without artificial overfitting.\n\n• Fine enough to capture local valley depressions, distinguishing hilltop ridges from low-lying underpasses.\n\n• Fast enough to compute daily ranks across all 3,026 points in under 2 milliseconds on a web server."
    p.font.name = FONT_BODY
    p.font.size = Pt(11)
    p.font.color.rgb = COLOR_MUTED
    p.space_before = Pt(8)

    # Bottom Right: Spatial Map Visual / Hotspot Distribution Chart
    br_left = Inches(6.8)
    br_w = Inches(5.733)
    br_h = Inches(3.7)
    add_card(s3, br_left, Inches(3.1), br_w, br_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
    
    # Embed spatial chart
    img_spatial = "delivery/figures/fig3_hotspot_spatial_map.png"
    if os.path.exists(img_spatial):
        s3.shapes.add_picture(img_spatial, br_left + Inches(0.2), Inches(3.25), width=br_w - Inches(0.4), height=br_h - Inches(0.5))

    # =========================================================================
    # SLIDE 4: DATA & HYDROLOGY
    # =========================================================================
    s4 = prs.slides.add_slide(blank_layout)
    set_slide_background(s4)
    add_header(s4, "The geography behind the model", "03 / GEOSPATIAL DATA SOURCES", 4)

    # 4 Data Source Cards
    sources = [
        ("SRTM DEM (30 m)", "Terrain & Surface Elevation", [
            "Mean elevation above sea level (elev_m: 840–960 m)",
            "Terrain gradient in degrees (slope_deg)",
            "Topographic Wetness Index: TWI = ln(a / tan β)",
            "Height Above Nearest Drainage (HAND in meters)"
        ], COLOR_MINT),
        ("ESA WorldCover (10 m)", "Built Environment & Infiltration", [
            "10 m multispectral land-use classification",
            "Impervious concrete surface fraction (imperv_frac)",
            "Quantifies loss of permeable soil to roads and rooftops",
            "High imperviousness blocks infiltration, multiplying runoff"
        ], COLOR_AMBER),
        ("OpenStreetMap Vectors", "Hydrographic & Road Network", [
            "Vector primary stormwater drains (rajakaluves)",
            "Euclidean distance to nearest lake margin (dist_lake_m)",
            "Euclidean distance to nearest storm channel (dist_drain_m)",
            "Distance to arterial road corridors (dist_road_m)"
        ], COLOR_WHITE),
        ("CHIRPS Gridded Rainfall", "Dynamic Atmospheric Forcing", [
            "0.05° (~5.3 km) satellite-gauge blended precipitation",
            "37 distinct meteorological pixels across Greater Bengaluru",
            "8 rolling parameters: daily rain, lags (lag1, lag2), and cumulative sums (3d, 5d, 7d, 10d, 14d)",
            "*Resolution limitation acknowledged: regional driver, not micro radar"
        ], COLOR_MINT),
    ]

    card_w = Inches(5.7)
    card_h = Inches(2.35)
    for idx, (title, subtitle, bullets, col) in enumerate(sources):
        col_idx = idx % 2
        row_idx = idx // 2
        x = Inches(0.8) + col_idx * Inches(6.033)
        y = Inches(1.4) + row_idx * Inches(2.6)
        
        add_card(s4, x, y, card_w, card_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
        
        # Color bar
        cbar = s4.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, card_w, Pt(3))
        cbar.fill.solid()
        cbar.fill.fore_color.rgb = col
        cbar.line.fill.background()

        tb = s4.shapes.add_textbox(x + Inches(0.25), y + Inches(0.12), card_w - Inches(0.5), card_h - Inches(0.25))
        tf = tb.text_frame
        tf.word_wrap = True
        p1 = tf.paragraphs[0]
        p1.text = title
        p1.font.name = FONT_HEADING
        p1.font.size = Pt(13.5)
        p1.font.bold = True
        p1.font.color.rgb = COLOR_WHITE
        
        p2 = tf.add_paragraph()
        p2.text = subtitle
        p2.font.name = FONT_MONO
        p2.font.size = Pt(9.5)
        p2.font.color.rgb = col
        p2.space_before = Pt(1)

        for b in bullets:
            p_b = tf.add_paragraph()
            p_b.text = f"• {b}"
            p_b.font.name = FONT_BODY
            p_b.font.size = Pt(9.5)
            p_b.font.color.rgb = COLOR_MUTED
            p_b.space_before = Pt(2)

    # Notice banner at bottom
    notif = s4.shapes.add_textbox(Inches(0.8), Inches(6.65), Inches(11.733), Inches(0.35))
    tf_n = notif.text_frame
    p_n = tf_n.paragraphs[0]
    p_n.text = "Grounding Rule: Topography dictates baseline physical susceptibility; multi-day antecedent rainfall provides the temporal trigger."
    p_n.font.name = FONT_BODY
    p_n.font.size = Pt(10)
    p_n.font.italic = True
    p_n.font.color.rgb = COLOR_MUTED

    # =========================================================================
    # SLIDE 5: THE INTELLIGENCE ENGINE
    # =========================================================================
    s5 = prs.slides.add_slide(blank_layout)
    set_slide_background(s5)
    add_header(s5, "From features to susceptibility", "04 / MACHINE LEARNING PIPELINE", 5)

    # 4 Pipeline Step Flow Across the Slide
    pipeline_steps = [
        ("01 / INPUT", "18 Features", "10 static terrain indices (elevation, slope, TWI, HAND, lake/drain distances)\n+ 8 dynamic CHIRPS rainfall sums", COLOR_WHITE),
        ("02 / CHALLENGE", "Extreme Imbalance", "Only 240 positive flood cell-days in 1.76M records (0.0136% prevalence)\nStandard models predict 'no flood' 100% of the time", COLOR_AMBER),
        ("03 / SOLUTION", "XGBoost + Weighting", "scale_pos_weight = 89.16\nPenalizes missed floods ~89× heavier during gradient tree construction\n100 trees, max depth = 6", COLOR_MINT),
        ("04 / OUTPUT", "Dense Spatial Rank", "Raw scores mapped to daily ranks (1 to 3,026)\nAvoids rigid 0.5 probability cutoffs\nTiers: High (Top 150), Moderate (151–300)", COLOR_WHITE),
    ]

    p_w = Inches(2.78)
    p_h = Inches(4.8)
    for idx, (step_tag, step_title, step_desc, col) in enumerate(pipeline_steps):
        x = Inches(0.8) + idx * Inches(2.98)
        y = Inches(1.5)
        add_card(s5, x, y, p_w, p_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
        
        # Header strip
        top_strip = s5.shapes.add_shape(MSO_SHAPE.RECTANGLE, x, y, p_w, Pt(4))
        top_strip.fill.solid()
        top_strip.fill.fore_color.rgb = col
        top_strip.line.fill.background()

        tb = s5.shapes.add_textbox(x + Inches(0.2), y + Inches(0.25), p_w - Inches(0.4), p_h - Inches(0.5))
        tf = tb.text_frame
        tf.word_wrap = True
        
        p = tf.paragraphs[0]
        p.text = step_tag
        p.font.name = FONT_MONO
        p.font.size = Pt(10)
        p.font.bold = True
        p.font.color.rgb = col

        p = tf.add_paragraph()
        p.text = step_title
        p.font.name = FONT_HEADING
        p.font.size = Pt(16)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(4)

        p = tf.add_paragraph()
        p.text = step_desc
        p.font.name = FONT_BODY
        p.font.size = Pt(11)
        p.font.color.rgb = COLOR_MUTED
        p.space_before = Pt(12)

    # Bottom Banner
    banner = s5.shapes.add_textbox(Inches(0.8), Inches(6.5), Inches(11.733), Inches(0.4))
    tf_b = banner.text_frame
    p_b = tf_b.paragraphs[0]
    p_b.text = "Key Insight: On extreme rare-event data, rank-based prioritization delivers an operational triage list rather than misleading probabilities."
    p_b.font.name = FONT_MONO
    p_b.font.size = Pt(10.5)
    p_b.font.color.rgb = COLOR_AMBER

    # =========================================================================
    # SLIDE 6: THE MAP THAT MATTERS
    # =========================================================================
    s6 = prs.slides.add_slide(blank_layout)
    set_slide_background(s6)
    add_header(s6, "Spatial susceptibility visualization", "05 / INTERACTIVE CARTOGRAPHY", 6)

    # Left: Genuine Screenshot of the Deployed Flood Map
    map_screenshot = "presentation/screenshots/02_flood_map_inspector.png"
    if os.path.exists(map_screenshot):
        s6.shapes.add_picture(map_screenshot, Inches(0.8), Inches(1.4), width=Inches(8.2), height=Inches(5.3))
    else:
        # Fallback card
        add_card(s6, Inches(0.8), Inches(1.4), Inches(8.2), Inches(5.3), bg_color=COLOR_SURFACE)

    # Right Column: Tier Explanation & Guardrails
    r_left = Inches(9.2)
    r_w = Inches(3.333)
    r_h = Inches(5.3)
    add_card(s6, r_left, Inches(1.4), r_w, r_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)

    tb = s6.shapes.add_textbox(r_left + Inches(0.2), Inches(1.55), r_w - Inches(0.4), r_h - Inches(0.3))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "PRIORITY TIERS"
    p.font.name = FONT_MONO
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_MINT

    p = tf.add_paragraph()
    p.text = "Daily Spatial Triage"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(2)

    tiers = [
        ("High Priority (Top 5%)", "Ranks 1–150 (Red)\nCritical low-lying valleys, high impervious cover, drainage bottlenecks.", COLOR_RED),
        ("Moderate (Ranks 151–300)", "Top 10% (Orange)\nSecondary vulnerable underpasses and lake buffer zones.", COLOR_ORANGE),
        ("Baseline (Ranks 301–3,026)", "Remaining 90% (Muted Gray)\nNormal monsoonal runoff behavior; typical terrain drainage.", COLOR_MUTED),
    ]

    for t_head, t_desc, col in tiers:
        p_th = tf.add_paragraph()
        p_th.text = f"■ {t_head}"
        p_th.font.name = FONT_HEADING
        p_th.font.size = Pt(11)
        p_th.font.bold = True
        p_th.font.color.rgb = col
        p_th.space_before = Pt(8)

        p_td = tf.add_paragraph()
        p_td.text = t_desc
        p_td.font.name = FONT_BODY
        p_td.font.size = Pt(9.5)
        p_td.font.color.rgb = COLOR_MUTED
        p_td.space_before = Pt(1)

    p_warn = tf.add_paragraph()
    p_warn.text = "Academic Guardrail: Susceptibility scores reflect relative spatial vulnerability, not physical inundation depth or flood velocity."
    p_warn.font.name = FONT_BODY
    p_warn.font.size = Pt(9)
    p_warn.font.italic = True
    p_warn.font.color.rgb = COLOR_AMBER
    p_warn.space_before = Pt(10)

    # =========================================================================
    # SLIDE 7: THE SYSTEM IN ACTION
    # =========================================================================
    s7 = prs.slides.add_slide(blank_layout)
    set_slide_background(s7)
    add_header(s7, "From model to usable interface", "06 / FULL-STACK APPLICATION", 7)

    # Left Card: Live Simulation Lab Screenshot & Description
    left_w = Inches(5.7)
    left_h = Inches(5.2)
    add_card(s7, Inches(0.8), Inches(1.4), left_w, left_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
    
    sim_screenshot = "presentation/screenshots/03_live_simulation.png"
    if os.path.exists(sim_screenshot):
        s7.shapes.add_picture(sim_screenshot, Inches(1.0), Inches(1.55), width=left_w - Inches(0.4), height=Inches(3.0))

    tb_l = s7.shapes.add_textbox(Inches(1.0), Inches(4.7), left_w - Inches(0.4), Inches(1.7))
    tf_l = tb_l.text_frame
    tf_l.word_wrap = True
    p = tf_l.paragraphs[0]
    p.text = "LIVE SIMULATION & SENSITIVITY LAB"
    p.font.name = FONT_MONO
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_MINT

    p = tf_l.add_paragraph()
    p.text = "Interactive sensitivity testing across individual cells (e.g. Cell #722, Bellandur Valley). Users adjust 1-day, 3-day, and 7-day rainfall sliders to observe instantaneous model response."
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_MUTED
    p.space_before = Pt(2)

    # Right Card: Telegram Bot Sandbox Screenshot & Description
    right_left = Inches(6.833)
    right_w = Inches(5.7)
    add_card(s7, right_left, Inches(1.4), right_w, left_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
    
    tg_screenshot = "presentation/screenshots/04_telegram_sandbox.png"
    if os.path.exists(tg_screenshot):
        s7.shapes.add_picture(tg_screenshot, right_left + Inches(0.2), Inches(1.55), width=right_w - Inches(0.4), height=Inches(3.0))

    tb_r = s7.shapes.add_textbox(right_left + Inches(0.2), Inches(4.7), right_w - Inches(0.4), Inches(1.7))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True
    p = tf_r.paragraphs[0]
    p.text = "PRIVATE TELEGRAM DEMONSTRATION BOT"
    p.font.name = FONT_MONO
    p.font.size = Pt(10)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER

    p = tf_r.add_paragraph()
    p.text = "Secure mobile bulletin sandbox (@N2M_Flood_Bot). Enforces token redaction and chat-ID whitelist authorization. Evaluators test /demo dispatch without exposing experimental alerts publicly."
    p.font.name = FONT_BODY
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_MUTED
    p.space_before = Pt(2)

    # =========================================================================
    # SLIDE 8: TESTING & RESULTS
    # =========================================================================
    s8 = prs.slides.add_slide(blank_layout)
    set_slide_background(s8)
    add_header(s8, "What did we evaluate?", "07 / EMPIRICAL EVALUATION", 8)

    # Top Row: 4 Metric Cards
    m_cards = [
        ("0.0026", "PR-AUC (Precision-Recall)", "2.00× Lift over random chance baseline (0.0013)", COLOR_MINT),
        ("25.0%", "Top 10% Hit Rate", "2.53× Enrichment (captures 1 in 4 verified flood points)", COLOR_AMBER),
        ("8.3%", "High Priority Hit Rate", "1.66× Lift in top 150 cells (~5% of Greater Bengaluru)", COLOR_WHITE),
        ("82 / 82", "Automated Tests", "100% Pass Rate across backend routes, schemas & bot", COLOR_MINT),
    ]

    mw = Inches(2.78)
    mh = Inches(1.45)
    for idx, (val, title, sub, col) in enumerate(m_cards):
        x = Inches(0.8) + idx * Inches(2.98)
        y = Inches(1.4)
        add_card(s8, x, y, mw, mh, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)
        
        tb = s8.shapes.add_textbox(x + Inches(0.15), y + Inches(0.1), mw - Inches(0.3), mh - Inches(0.2))
        tf = tb.text_frame
        tf.word_wrap = True
        p = tf.paragraphs[0]
        p.text = val
        p.font.name = FONT_HEADING
        p.font.size = Pt(24)
        p.font.bold = True
        p.font.color.rgb = col
        
        p = tf.add_paragraph()
        p.text = title
        p.font.name = FONT_HEADING
        p.font.size = Pt(10.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE
        p.space_before = Pt(1)

        p = tf.add_paragraph()
        p.text = sub
        p.font.name = FONT_BODY
        p.font.size = Pt(8.5)
        p.font.color.rgb = COLOR_MUTED
        p.space_before = Pt(1)

    # Bottom Left: September 2022 Holdout Benchmark Chart
    b_left = Inches(0.8)
    b_w = Inches(6.0)
    b_h = Inches(3.85)
    add_card(s8, b_left, Inches(3.05), b_w, b_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)

    rain_chart = "delivery/figures/fig2_sept2022_rainfall.png"
    if os.path.exists(rain_chart):
        s8.shapes.add_picture(rain_chart, b_left + Inches(0.15), Inches(3.15), width=b_w - Inches(0.3), height=b_h - Inches(0.4))

    # Bottom Right: Case Study & Empirical Interpretation
    r_left = Inches(7.0)
    r_w = Inches(5.533)
    add_card(s8, r_left, Inches(3.05), r_w, b_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)

    tb = s8.shapes.add_textbox(r_left + Inches(0.3), Inches(3.2), r_w - Inches(0.6), b_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "HOLDOUT CASE STUDY: SEPTEMBER 2022"
    p.font.name = FONT_MONO
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_MINT

    p = tf.add_paragraph()
    p.text = "Unbiased Validation on Unseen Flood Event"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(3)

    p = tf.add_paragraph()
    p.text = "• Event E2022_09 (24 consecutive monsoon days, 72,624 instances, 188 confirmed flood points) was held out completely during model training.\n\n• Peak Susceptibility Observed: Cell #722 (Bellandur basin) reached maximum citywide score 0.2191 on Sep 8, 2022, matching verified historical inundation.\n\n• Information Retrieval: In extreme class imbalance (0.0136%), ranking the top 10% cells captures 25% of all historical flood locations—a 2.53× operational enrichment over random search."
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_MUTED
    p.space_before = Pt(8)

    # =========================================================================
    # SLIDE 9: LIMITATIONS & NEXT STEPS
    # =========================================================================
    s9 = prs.slides.add_slide(blank_layout)
    set_slide_background(s9)
    add_header(s9, "Where we go from here", "08 / LIMITATIONS & ROADMAP", 9)

    # Left Column: Honest Technical Limitations
    l_w = Inches(5.7)
    l_h = Inches(5.1)
    add_card(s9, Inches(0.8), Inches(1.4), l_w, l_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)

    tb = s9.shapes.add_textbox(Inches(1.1), Inches(1.6), l_w - Inches(0.6), l_h - Inches(0.4))
    tf = tb.text_frame
    tf.word_wrap = True

    p = tf.paragraphs[0]
    p.text = "CURRENT TECHNICAL BOUNDARIES"
    p.font.name = FONT_MONO
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_AMBER

    p = tf.add_paragraph()
    p.text = "Honest Engineering Constraints"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(2)

    limits = [
        ("Coarse Satellite Rainfall Resolution", "CHIRPS precipitation is gridded at 0.05° (~5.3 km), unable to resolve hyper-local convective cloudbursts under 1 km."),
        ("Surface Terrain Only", "The model currently has no real-time telemetry regarding underground stormwater pipe siltation, culvert clogs, or pump station failures."),
        ("Historical Label Sparsity", "Only 240 positive flood cell-days documented in municipal logs; minor street ponding in alleys may be underreported."),
        ("Relative Ranking Prototype", "Outputs relative spatial susceptibility tiers to guide inspection; does not calculate physical inundation depths in cm."),
    ]

    for h, b in limits:
        p_h = tf.add_paragraph()
        p_h.text = f"• {h}"
        p_h.font.name = FONT_HEADING
        p_h.font.size = Pt(11)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_WHITE
        p_h.space_before = Pt(6)

        p_b = tf.add_paragraph()
        p_b.text = f"  {b}"
        p_b.font.name = FONT_BODY
        p_b.font.size = Pt(9.5)
        p_b.font.color.rgb = COLOR_MUTED
        p_b.space_before = Pt(1)

    # Right Column: 3 Actionable Next Steps
    r_left = Inches(6.833)
    r_w = Inches(5.7)
    add_card(s9, r_left, Inches(1.4), r_w, l_h, bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)

    tb_r = s9.shapes.add_textbox(r_left + Inches(0.3), Inches(1.6), r_w - Inches(0.6), l_h - Inches(0.4))
    tf_r = tb_r.text_frame
    tf_r.word_wrap = True

    p = tf_r.paragraphs[0]
    p.text = "ENGINEERING ROADMAP"
    p.font.name = FONT_MONO
    p.font.size = Pt(10.5)
    p.font.bold = True
    p.font.color.rgb = COLOR_MINT

    p = tf_r.add_paragraph()
    p.text = "Practical Future Enhancements"
    p.font.name = FONT_HEADING
    p.font.size = Pt(15)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE
    p.space_before = Pt(2)

    roadmap = [
        ("1. Hyper-Local Telemetric Rain Gauges", "Ingest real-time automated weather stations from KSNDMC (100+ stations across Bengaluru), replacing 5.3 km satellite estimates with dense ground rain gauge networks."),
        ("2. Numerical Weather Prediction (NWP)", "Integrate forward-looking IMD/WRF quantitative precipitation forecasts to transition from retrospective nowcasting to 6–24 hour predictive early warnings."),
        ("3. Coupled 1D/2D Hydrodynamic Modeling", "Use the machine learning ranking as an initial filter, coupling the top 150 high-priority cells with EPA SWMM to simulate physical water depth and drain overflow."),
    ]

    for h, b in roadmap:
        p_h = tf_r.add_paragraph()
        p_h.text = h
        p_h.font.name = FONT_HEADING
        p_h.font.size = Pt(11)
        p_h.font.bold = True
        p_h.font.color.rgb = COLOR_MINT
        p_h.space_before = Pt(10)

        p_b = tf_r.add_paragraph()
        p_b.text = b
        p_b.font.name = FONT_BODY
        p_b.font.size = Pt(10)
        p_b.font.color.rgb = COLOR_MUTED
        p_b.space_before = Pt(2)

    # =========================================================================
    # SLIDE 10: CREDITS / CLOSING SLIDE
    # =========================================================================
    s10 = prs.slides.add_slide(blank_layout)
    set_slide_background(s10)

    # Outer border card
    add_card(s10, Inches(0.8), Inches(0.8), Inches(11.733), Inches(5.9), bg_color=COLOR_SURFACE, border_color=COLOR_BORDER)

    # Top Tag
    tb = s10.shapes.add_textbox(Inches(1.3), Inches(1.2), Inches(8.0), Inches(0.35))
    tf = tb.text_frame
    p = tf.paragraphs[0]
    p.text = "PROJECT CREDITS & ACKNOWLEDGMENTS"
    p.font.name = FONT_MONO
    p.font.size = Pt(11)
    p.font.bold = True
    p.font.color.rgb = COLOR_MINT

    # Big Title
    tb_t = s10.shapes.add_textbox(Inches(1.3), Inches(1.6), Inches(10.5), Inches(0.8))
    tf_t = tb_t.text_frame
    p_t = tf_t.paragraphs[0]
    p_t.text = "N²M Flood Prediction Model"
    p_t.font.name = FONT_HEADING
    p_t.font.size = Pt(36)
    p_t.font.bold = True
    p_t.font.color.rgb = COLOR_WHITE

    # 3-Column Student Team Block
    team = [
        ("Nishanth G M", "Data Pipeline & Hydrology", "3,026 spatial grid, DEM terrain feature extraction, HAND index, and CHIRPS rainfall linkage."),
        ("Mohith M", "Machine Learning & Evaluation", "XGBoost classifier, class imbalance tuning (scale_pos_weight = 89.16), and holdout PR-AUC validation."),
        ("Nihal Rao", "Full-Stack & Cartography", "FastAPI backend, Leaflet Canvas 60 FPS vector map, historical replay, and demonstration bot."),
    ]

    col_w = Inches(3.38)
    col_h = Inches(1.8)
    for idx, (name, role, work) in enumerate(team):
        x = Inches(1.3) + idx * Inches(3.67)
        y = Inches(2.55)
        add_card(s10, x, y, col_w, col_h, bg_color=COLOR_SURFACE_ALT, border_color=COLOR_BORDER)

        tb_c = s10.shapes.add_textbox(x + Inches(0.15), y + Inches(0.12), col_w - Inches(0.3), col_h - Inches(0.24))
        tf_c = tb_c.text_frame
        tf_c.word_wrap = True
        
        p = tf_c.paragraphs[0]
        p.text = name
        p.font.name = FONT_HEADING
        p.font.size = Pt(13)
        p.font.bold = True
        p.font.color.rgb = COLOR_WHITE

        p = tf_c.add_paragraph()
        p.text = role
        p.font.name = FONT_MONO
        p.font.size = Pt(9.5)
        p.font.bold = True
        p.font.color.rgb = COLOR_AMBER
        p.space_before = Pt(1)

        p = tf_c.add_paragraph()
        p.text = work
        p.font.name = FONT_BODY
        p.font.size = Pt(8.5)
        p.font.color.rgb = COLOR_MUTED
        p.space_before = Pt(3)

    # Faculty & Institution Block at Bottom
    div = s10.shapes.add_shape(MSO_SHAPE.RECTANGLE, Inches(1.3), Inches(4.55), Inches(10.733), Pt(1))
    div.fill.solid()
    div.fill.fore_color.rgb = COLOR_BORDER
    div.line.fill.background()

    # Left: Faculty Guide & Department
    tb_guide = s10.shapes.add_textbox(Inches(1.3), Inches(4.7), Inches(6.5), Inches(1.8))
    tf_g = tb_guide.text_frame
    p = tf_g.paragraphs[0]
    p.text = "Faculty Project Advisor: Dr. Punith Kumar, Associate Professor"
    p.font.name = FONT_HEADING
    p.font.size = Pt(12)
    p.font.bold = True
    p.font.color.rgb = COLOR_WHITE

    p = tf_g.add_paragraph()
    p.text = "Department of Computer Science & Engineering\nDayananda Sagar College of Engineering, Bengaluru — 560078"
    p.font.name = FONT_BODY
    p.font.size = Pt(10.5)
    p.font.color.rgb = COLOR_MUTED
    p.space_before = Pt(2)

    p = tf_g.add_paragraph()
    p.text = "Repository: https://github.com/nishanth-end/n2m-rain-model"
    p.font.name = FONT_MONO
    p.font.size = Pt(9.5)
    p.font.color.rgb = COLOR_MINT
    p.space_before = Pt(4)

    # Right: Thank You & Questions Callout
    tb_q = s10.shapes.add_textbox(Inches(8.5), Inches(4.7), Inches(3.5), Inches(1.8))
    tf_q = tb_q.text_frame
    p_q1 = tf_q.paragraphs[0]
    p_q1.text = "Thank you."
    p_q1.font.name = FONT_HEADING
    p_q1.font.size = Pt(26)
    p_q1.font.bold = True
    p_q1.font.color.rgb = COLOR_WHITE
    p_q1.alignment = PP_ALIGN.RIGHT

    p_q2 = tf_q.add_paragraph()
    p_q2.text = "Questions & Discussion"
    p_q2.font.name = FONT_HEADING
    p_q2.font.size = Pt(14)
    p_q2.font.color.rgb = COLOR_AMBER
    p_q2.alignment = PP_ALIGN.RIGHT
    p_q2.space_before = Pt(2)

    # Save
    prs.save(output_pptx)
    print(f"Successfully generated PowerPoint presentation: {output_pptx}")

if __name__ == "__main__":
    build_presentation()
