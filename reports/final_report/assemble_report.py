"""
Assembles and validates `reports/final_report/report.md`
"""

import sys
import re

sys.path.append("reports/final_report")
import write_report_markdown
import student_ch1_3
import student_ch4_7

full_md = "\n\n".join([
    write_report_markdown.FRONT_MATTER.strip(),
    student_ch1_3.CHAPTERS_1_TO_3.strip(),
    student_ch4_7.CHAPTERS_4_TO_7.strip()
])

# Validate XML character compatibility
xml_invalid_re = re.compile(r'[^\x09\x0A\x0D\x20-\uD7FF\uE000-\uFFFD]')
matches = list(xml_invalid_re.finditer(full_md))
if matches:
    print(f"Warning: Found {len(matches)} invalid XML characters! Cleaning...")
    full_md = xml_invalid_re.sub('', full_md)

with open("reports/final_report/report.md", "w", encoding="utf-8") as f:
    f.write(full_md)

words = len(full_md.split())
lines = len(full_md.splitlines())
chars = len(full_md)
print(f"Compiled reports/final_report/report.md successfully:")
print(f"  Words: {words}")
print(f"  Lines: {lines}")
print(f"  Characters: {chars}")
