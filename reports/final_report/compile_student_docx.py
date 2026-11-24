"""
Compiles the revised undergraduate engineering mini-project report
into a clean, professional Word document (`reports/final_report/N2M_Project_Report.docx`).
Target page count: ~25-35 pages.
"""

import os
import re
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT, WD_ALIGN_VERTICAL
from docx.oxml import parse_xml, OxmlElement
from docx.oxml.ns import nsdecls, qn

REPORT_DIR = "reports/final_report"
MD_PATH = os.path.join(REPORT_DIR, "report.md")
DOCX_PATH = os.path.join(REPORT_DIR, "N2M_Project_Report.docx")
PDF_PATH = os.path.join(REPORT_DIR, "N2M_Project_Report.pdf")
FIG_DIR = os.path.join(REPORT_DIR, "figures")
SCREEN_DIR = os.path.join(REPORT_DIR, "screenshots")

# Palette constants
NAVY_PRIMARY = RGBColor(15, 23, 42)      # #0f172a
BLUE_ACCENT = RGBColor(30, 58, 138)      # #1e3a8a
SLATE_BODY = RGBColor(30, 41, 59)        # #1e293b
GRAY_MUTED = RGBColor(100, 116, 139)     # #64748b
BORDER_COLOR = "cbd5e1"
HEADER_FILL = "0f172a"
ALT_ROW_FILL = "f8fafc"
CODE_FILL = "f8fafc"

FIGURE_MAP = {
    1: os.path.join(FIG_DIR, "fig1_overall_system_architecture.png"),
    2: os.path.join(FIG_DIR, "fig2_data_processing_pipeline.png"),
    3: os.path.join(FIG_DIR, "fig4_inference_ranking_workflow.png"),
    4: os.path.join(SCREEN_DIR, "flood_map_interface_overview.png"),
    5: os.path.join(FIG_DIR, "fig2_sept2022_rainfall.png"),
}

FIGURE_TITLES = {
    1: "Figure 1: Overall System Architecture of the N²M Flood Prediction Model",
    2: "Figure 2: Geospatial Data Ingestion and Feature Processing Pipeline",
    3: "Figure 3: XGBoost Inference and Daily Spatial Ranking Flowchart",
    4: "Figure 4: Interactive Cartographic Web Interface Showing Bengaluru Flood Grid",
    5: "Figure 5: Historical Daily Rainfall Trend Across Bengaluru During September 2022",
}

def sanitize_xml(s):
    if not isinstance(s, str):
        return s
    return re.sub(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]', '', s)

def set_cell_background(cell, fill_hex):
    tcPr = cell._tc.get_or_add_tcPr()
    shd = parse_xml(f'<w:shd {nsdecls("w")} w:fill="{fill_hex}"/>')
    tcPr.append(shd)

def set_cell_margins(cell, top=100, bottom=100, left=140, right=140):
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
            <w:top w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
            <w:insideH w:val="single" w:sz="4" w:space="0" w:color="{BORDER_COLOR}"/>
            <w:insideV w:val="none"/>
            <w:left w:val="none"/>
            <w:right w:val="none"/>
        </w:tblBorders>
    ''')
    tblPr.append(borders)

def format_inlines(paragraph, text, base_font="Calibri", base_size=11, base_color=SLATE_BODY, is_italic=False):
    """Parses markdown bold (**), italic (*), and code (`) inlines into docx runs."""
    text = sanitize_xml(text)
    tokens = re.split(r'(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`)', text)
    for token in tokens:
        if not token:
            continue
        token = sanitize_xml(token)
        if token.startswith('**') and token.endswith('**'):
            inner = token[2:-2]
            run = paragraph.add_run(inner)
            run.font.name = base_font
            run.font.size = Pt(base_size)
            run.font.bold = True
            run.font.color.rgb = base_color
        elif token.startswith('*') and token.endswith('*'):
            inner = token[1:-1]
            run = paragraph.add_run(inner)
            run.font.name = base_font
            run.font.size = Pt(base_size)
            run.font.italic = True
            run.font.color.rgb = base_color
        elif token.startswith('`') and token.endswith('`'):
            inner = token[1:-1]
            run = paragraph.add_run(inner)
            run.font.name = "Consolas"
            run.font.size = Pt(base_size - 1)
            run.font.color.rgb = RGBColor(15, 23, 42)
        else:
            run = paragraph.add_run(token)
            run.font.name = base_font
            run.font.size = Pt(base_size)
            run.font.color.rgb = base_color
            if is_italic:
                run.font.italic = True

def add_code_block(doc, code_text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.columns[0].width = Inches(6.5)
    
    cell = table.cell(0, 0)
    set_cell_background(cell, CODE_FILL)
    set_cell_margins(cell, top=100, bottom=100, left=150, right=150)
    
    tcPr = cell._tc.get_or_add_tcPr()
    borders = parse_xml(f'''
        <w:tcBorders {nsdecls("w")}>
            <w:left w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
            <w:top w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
            <w:right w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
            <w:bottom w:val="single" w:sz="6" w:space="0" w:color="{BORDER_COLOR}"/>
        </w:tcBorders>
    ''')
    tcPr.append(borders)
    
    p = cell.paragraphs[0]
    p.paragraph_format.space_before = Pt(0)
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.05
    run = p.add_run(sanitize_xml(code_text))
    run.font.name = "Consolas"
    run.font.size = Pt(9.0)
    run.font.color.rgb = RGBColor(15, 23, 42)

def build_docx():
    print("Building N²M Project Report DOCX (Student Edition)...")
    doc = docx.Document()
    
    # Page setup: A4, 1-inch margins
    for section in doc.sections:
        section.page_width = Inches(8.27)
        section.page_height = Inches(11.69)
        section.top_margin = Inches(1.0)
        section.bottom_margin = Inches(1.0)
        section.left_margin = Inches(1.0)
        section.right_margin = Inches(1.0)
        
        # Header / Footer setup
        header = section.header
        hp = header.paragraphs[0]
        hp.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        hrun = hp.add_run("N²M Flood Prediction Model — Engineering Mini-Project Report | DSCE CSE")
        hrun.font.name = "Calibri"
        hrun.font.size = Pt(8.5)
        hrun.font.color.rgb = GRAY_MUTED
        
        footer = section.footer
        fp = footer.paragraphs[0]
        fp.alignment = WD_ALIGN_PARAGRAPH.CENTER
        frun = fp.add_run("Department of Computer Science & Engineering, Dayananda Sagar College of Engineering")
        frun.font.name = "Calibri"
        frun.font.size = Pt(8.5)
        frun.font.color.rgb = GRAY_MUTED

    # ================= COVER PAGE =================
    cover_inst = doc.add_paragraph()
    cover_inst.alignment = WD_ALIGN_PARAGRAPH.CENTER
    cover_inst.paragraph_format.space_before = Pt(28)
    cover_inst.paragraph_format.space_after = Pt(4)
    run = cover_inst.add_run("DAYANANDA SAGAR COLLEGE OF ENGINEERING\n")
    run.font.name = "Calibri"
    run.font.size = Pt(13.5)
    run.font.bold = True
    run.font.color.rgb = NAVY_PRIMARY
    
    run2 = cover_inst.add_run("(An Autonomous Institute Affiliated to VTU, Belagavi, Approved by AICTE & UGC, Accredited by NAAC with 'A+' Grade)\nShavige Malleshwara Hills, Kumaraswamy Layout, Bengaluru – 560078\n\nDEPARTMENT OF COMPUTER SCIENCE & ENGINEERING")
    run2.font.name = "Calibri"
    run2.font.size = Pt(9.5)
    run2.font.color.rgb = GRAY_MUTED

    # Divider bar
    p_div = doc.add_paragraph()
    p_div.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_div.paragraph_format.space_before = Pt(12)
    p_div.paragraph_format.space_after = Pt(20)
    r_div = p_div.add_run("━" * 45)
    r_div.font.color.rgb = BLUE_ACCENT
    r_div.font.size = Pt(13)

    # Title
    p_title = doc.add_paragraph()
    p_title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_title.paragraph_format.space_before = Pt(10)
    p_title.paragraph_format.space_after = Pt(10)
    r_title = p_title.add_run("N²M FLOOD PREDICTION MODEL\n")
    r_title.font.name = "Calibri"
    r_title.font.size = Pt(22)
    r_title.font.bold = True
    r_title.font.color.rgb = NAVY_PRIMARY
    
    r_sub = p_title.add_run("An ML-Based Urban Flood Susceptibility Mapping and Visualization System for Bengaluru")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(12.5)
    r_sub.font.italic = True
    r_sub.font.color.rgb = BLUE_ACCENT

    # Submission statement
    p_sub = doc.add_paragraph()
    p_sub.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_sub.paragraph_format.space_before = Pt(24)
    p_sub.paragraph_format.space_after = Pt(20)
    r_sub = p_sub.add_run("A TECHNICAL MINI-PROJECT REPORT\nSUBMITTED IN PARTIAL FULFILLMENT OF THE REQUIREMENTS FOR THE DEGREE OF\nBACHELOR OF ENGINEERING IN COMPUTER SCIENCE AND ENGINEERING")
    r_sub.font.name = "Calibri"
    r_sub.font.size = Pt(10)
    r_sub.font.bold = True
    r_sub.font.color.rgb = SLATE_BODY

    # Contributors & Advisor Table
    table_team = doc.add_table(rows=2, cols=2)
    table_team.alignment = WD_TABLE_ALIGNMENT.CENTER
    table_team.autofit = False
    table_team.columns[0].width = Inches(3.2)
    table_team.columns[1].width = Inches(3.2)
    
    c_left_hdr = table_team.cell(0, 0).paragraphs[0]
    c_left_hdr.paragraph_format.space_after = Pt(3)
    r = c_left_hdr.add_run("Submitted by:")
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = BLUE_ACCENT
    
    c_left_body = table_team.cell(1, 0).paragraphs[0]
    c_left_body.paragraph_format.line_spacing = 1.15
    c_left_body.paragraph_format.space_after = Pt(0)
    r_team = c_left_body.add_run("NISHANTH G M (Data & Hydrology)\nMOHITH M (ML & Validation)\nNIHAL RAO (Full-Stack & Cartography)")
    r_team.font.bold = True
    r_team.font.size = Pt(9.5)
    r_team.font.color.rgb = SLATE_BODY
    
    c_right_hdr = table_team.cell(0, 1).paragraphs[0]
    c_right_hdr.paragraph_format.space_after = Pt(3)
    r = c_right_hdr.add_run("Under the Guidance of:")
    r.font.bold = True
    r.font.size = Pt(10)
    r.font.color.rgb = BLUE_ACCENT
    
    c_right_body = table_team.cell(1, 1).paragraphs[0]
    c_right_body.paragraph_format.line_spacing = 1.15
    c_right_body.paragraph_format.space_after = Pt(0)
    r_adv = c_right_body.add_run("Dr. PUNITH KUMAR\nAssociate Professor\nDept. of Computer Science & Engineering\nDSCE, Bengaluru")
    r_adv.font.bold = True
    r_adv.font.size = Pt(9.5)
    r_adv.font.color.rgb = SLATE_BODY

    # Year
    p_year = doc.add_paragraph()
    p_year.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_year.paragraph_format.space_before = Pt(40)
    p_year.paragraph_format.space_after = Pt(0)
    r_year = p_year.add_run("ACADEMIC YEAR: 2026 – 2027")
    r_year.font.name = "Calibri"
    r_year.font.size = Pt(10.5)
    r_year.font.bold = True
    r_year.font.color.rgb = NAVY_PRIMARY

    doc.add_page_break()

    # ================= READ MARKDOWN CONTENT =================
    with open(MD_PATH, "r", encoding="utf-8") as f:
        md_text = f.read()

    # Skip title metadata block that is already on the cover page
    abstract_pos = md_text.find("## ABSTRACT")
    if abstract_pos != -1:
        md_text = md_text[abstract_pos:]

    lines = md_text.splitlines()
    in_code_block = False
    code_lines = []
    table_lines = []
    
    i = 0
    while i < len(lines):
        line = lines[i]
        
        # Check code fence
        if line.strip().startswith("```"):
            if in_code_block:
                in_code_block = False
                add_code_block(doc, "\n".join(code_lines))
                code_lines = []
            else:
                in_code_block = True
                code_lines = []
            i += 1
            continue
            
        if in_code_block:
            code_lines.append(line)
            i += 1
            continue

        # Check table
        if line.strip().startswith("|") and line.strip().endswith("|"):
            table_lines.append(line)
            i += 1
            while i < len(lines) and lines[i].strip().startswith("|") and lines[i].strip().endswith("|"):
                table_lines.append(lines[i])
                i += 1
            render_markdown_table(doc, table_lines)
            table_lines = []
            continue

        # Check Figure placeholder
        fig_match = re.search(r'\*\(Refer to Figure (\d+):[^\)]+\)\*', line)
        if fig_match:
            fig_num = int(fig_match.group(1))
            embed_figure(doc, fig_num)
            i += 1
            continue

        # Check horizontal rule
        if line.strip() == "---":
            i += 1
            continue

        # Check Headings
        if line.startswith("# "):
            heading_text = line[2:].strip()
            if "CHAPTER" in heading_text.upper():
                doc.add_page_break()
                h = doc.add_paragraph()
                h.paragraph_format.space_before = Pt(14)
                h.paragraph_format.space_after = Pt(8)
                h.paragraph_format.keep_with_next = True
                run = h.add_run(heading_text)
                run.font.name = "Calibri"
                run.font.size = Pt(15)
                run.font.bold = True
                run.font.color.rgb = NAVY_PRIMARY
            elif heading_text.startswith("N²M FLOOD"):
                # Title already on cover page
                pass
            elif "REFERENCES" in heading_text.upper():
                doc.add_page_break()
                h = doc.add_paragraph()
                h.paragraph_format.space_before = Pt(14)
                h.paragraph_format.space_after = Pt(8)
                h.paragraph_format.keep_with_next = True
                run = h.add_run(heading_text)
                run.font.name = "Calibri"
                run.font.size = Pt(15)
                run.font.bold = True
                run.font.color.rgb = NAVY_PRIMARY
            else:
                h = doc.add_paragraph()
                h.paragraph_format.space_before = Pt(12)
                h.paragraph_format.space_after = Pt(6)
                h.paragraph_format.keep_with_next = True
                run = h.add_run(heading_text)
                run.font.name = "Calibri"
                run.font.size = Pt(13.5)
                run.font.bold = True
                run.font.color.rgb = NAVY_PRIMARY
            i += 1
            continue

        if line.startswith("## "):
            heading_text = line[3:].strip()
            # Only page break for Abstract and Table of Contents and List of Figures
            if heading_text.upper().startswith("TABLE OF CONTENTS") or heading_text.upper().startswith("LIST OF FIGURES"):
                doc.add_page_break()
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(11)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(heading_text)
            run.font.name = "Calibri"
            run.font.size = Pt(12.5)
            run.font.bold = True
            run.font.color.rgb = BLUE_ACCENT
            i += 1
            continue

        if line.startswith("### "):
            heading_text = line[4:].strip()
            h = doc.add_paragraph()
            h.paragraph_format.space_before = Pt(11)
            h.paragraph_format.space_after = Pt(4)
            h.paragraph_format.keep_with_next = True
            run = h.add_run(heading_text)
            run.font.name = "Calibri"
            run.font.size = Pt(11.5)
            run.font.bold = True
            run.font.color.rgb = NAVY_PRIMARY
            i += 1
            continue

        if line.startswith("#### "):
            heading_text = line[5:].strip()
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            run = p.add_run(heading_text)
            run.font.name = "Calibri"
            run.font.size = Pt(10.5)
            run.font.bold = True
            run.font.color.rgb = NAVY_PRIMARY if "Table " in heading_text else SLATE_BODY
            i += 1
            continue

        # Check bullet points
        if line.strip().startswith("- ") or line.strip().startswith("* "):
            bullet_text = line.strip()[2:].strip()
            p = doc.add_paragraph(style='List Bullet')
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.left_indent = Inches(0.25)
            format_inlines(p, bullet_text, base_font="Calibri", base_size=10.5)
            i += 1
            continue

        # Check numbered lists
        num_match = re.match(r'^\s*(\d+)\.\s+(.*)$', line)
        if num_match:
            num_val = num_match.group(1)
            num_text = num_match.group(2)
            p = doc.add_paragraph()
            p.paragraph_format.space_before = Pt(1)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.left_indent = Inches(0.25)
            
            r_num = p.add_run(f"{num_val}. ")
            r_num.font.name = "Calibri"
            r_num.font.size = Pt(10.5)
            r_num.font.bold = True
            r_num.font.color.rgb = NAVY_PRIMARY
            
            format_inlines(p, num_text, base_font="Calibri", base_size=10.5)
            i += 1
            continue

        # Regular paragraph or reference entry
        if line.strip():
            if re.match(r'^\[\d+\]\s+', line.strip()):
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(3)
                p.paragraph_format.space_after = Pt(4)
                p.paragraph_format.line_spacing = 1.15
                p.paragraph_format.left_indent = Inches(0.35)
                format_inlines(p, line.strip(), base_font="Calibri", base_size=10)
            else:
                p = doc.add_paragraph()
                p.paragraph_format.space_before = Pt(1.5)
                p.paragraph_format.space_after = Pt(3.5)
                p.paragraph_format.line_spacing = 1.12
                format_inlines(p, line.strip(), base_font="Calibri", base_size=10.0)
        
        i += 1

    print(f"Saving compiled DOCX to {DOCX_PATH}...")
    doc.save(DOCX_PATH)
    print("DOCX generated successfully!")

def render_markdown_table(doc, table_lines):
    if len(table_lines) < 2:
        return
        
    raw_rows = []
    for line in table_lines:
        parts = [c.strip() for c in line.split("|")[1:-1]]
        if all(re.match(r'^:?-+:?$', p) for p in parts if p):
            continue
        raw_rows.append(parts)
        
    if not raw_rows:
        return
        
    num_cols = max(len(r) for r in raw_rows)
    num_rows = len(raw_rows)
    
    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = True
    set_table_borders(table)
    
    for r_idx, row_data in enumerate(raw_rows):
        is_header = (r_idx == 0)
        row = table.rows[r_idx]
        
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(f'<w:cantSplit {nsdecls("w")}/>'))
        if is_header:
            trPr.append(parse_xml(f'<w:tblHeader {nsdecls("w")}/>'))
            
        for c_idx in range(num_cols):
            cell = row.cells[c_idx]
            text = row_data[c_idx] if c_idx < len(row_data) else ""
            
            if is_header:
                set_cell_background(cell, HEADER_FILL)
                set_cell_margins(cell, top=80, bottom=80, left=100, right=100)
            else:
                bg = ALT_ROW_FILL if (r_idx % 2 == 1) else "ffffff"
                set_cell_background(cell, bg)
                set_cell_margins(cell, top=60, bottom=60, left=100, right=100)
                
            p = cell.paragraphs[0]
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(1)
            p.paragraph_format.line_spacing = 1.02
            
            if is_header:
                clean_text = text.replace("**", "").replace("*", "")
                run = p.add_run(sanitize_xml(clean_text))
                run.font.name = "Calibri"
                run.font.size = Pt(8.5)
                run.font.bold = True
                run.font.color.rgb = RGBColor(255, 255, 255)
            else:
                format_inlines(p, text, base_font="Calibri", base_size=8.0)

    p_after = doc.add_paragraph()
    p_after.paragraph_format.space_before = Pt(0)
    p_after.paragraph_format.space_after = Pt(4)

def embed_figure(doc, fig_num):
    img_path = FIGURE_MAP.get(fig_num)
    if not img_path or not os.path.exists(img_path):
        print(f"Warning: Figure {fig_num} not found at {img_path}")
        return
        
    p_img = doc.add_paragraph()
    p_img.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_img.paragraph_format.space_before = Pt(6)
    p_img.paragraph_format.space_after = Pt(2)
    p_img.paragraph_format.keep_with_next = True
    
    width = Inches(5.0)
    run = p_img.add_run()
    run.add_picture(img_path, width=width)
    
    caption_text = FIGURE_TITLES.get(fig_num, f"Figure {fig_num}")
    p_cap = doc.add_paragraph()
    p_cap.alignment = WD_ALIGN_PARAGRAPH.CENTER
    p_cap.paragraph_format.space_before = Pt(2)
    p_cap.paragraph_format.space_after = Pt(8)
    
    r_cap = p_cap.add_run(caption_text)
    r_cap.font.name = "Calibri"
    r_cap.font.size = Pt(8.5)
    r_cap.font.bold = True
    r_cap.font.color.rgb = NAVY_PRIMARY

if __name__ == "__main__":
    build_docx()
