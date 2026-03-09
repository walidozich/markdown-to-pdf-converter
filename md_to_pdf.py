#!/usr/bin/env python3
"""
Markdown to PDF Converter
Usage: python md_to_pdf.py input.md [output.pdf]
"""

import sys
import re
import argparse
from pathlib import Path

# Install dependencies if needed:
# pip install markdown reportlab --break-system-packages

import markdown
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Preformatted,
    HRFlowable, ListFlowable, ListItem
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER


def build_styles():
    styles = getSampleStyleSheet()

    custom = {
        "h1": ParagraphStyle("h1", parent=styles["Heading1"], fontSize=24, spaceAfter=12, textColor=colors.HexColor("#1a1a2e")),
        "h2": ParagraphStyle("h2", parent=styles["Heading2"], fontSize=18, spaceAfter=10, textColor=colors.HexColor("#16213e")),
        "h3": ParagraphStyle("h3", parent=styles["Heading3"], fontSize=14, spaceAfter=8, textColor=colors.HexColor("#0f3460")),
        "body": ParagraphStyle("body", parent=styles["Normal"], fontSize=11, leading=16, spaceAfter=8),
        "code": ParagraphStyle("code", parent=styles["Code"], fontSize=9, leading=14,
                               backColor=colors.HexColor("#f4f4f4"), leftIndent=12,
                               rightIndent=12, spaceBefore=6, spaceAfter=6,
                               fontName="Courier"),
        "blockquote": ParagraphStyle("blockquote", parent=styles["Normal"], fontSize=11, leading=16,
                                     leftIndent=20, textColor=colors.HexColor("#555555"),
                                     borderPadding=(4, 0, 4, 8)),
        "li": ParagraphStyle("li", parent=styles["Normal"], fontSize=11, leading=16),
    }
    return custom


def md_inline_to_rl(text):
    """Convert inline markdown (bold, italic, inline code) to ReportLab XML."""
    # Inline code
    text = re.sub(r'`([^`]+)`', r'<font name="Courier" size="9" backColor="#f4f4f4">\1</font>', text)
    # Bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'_(.+?)_', r'<i>\1</i>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" color="blue">\1</a>', text)
    return text


def parse_md_to_flowables(md_text, styles):
    flowables = []
    lines = md_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fenced code block
        if line.startswith("```"):
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code = "\n".join(code_lines)
            flowables.append(Preformatted(code, styles["code"]))
            i += 1
            continue

        # Headings
        m = re.match(r'^(#{1,6})\s+(.*)', line)
        if m:
            level = len(m.group(1))
            text = md_inline_to_rl(m.group(2).strip())
            style_key = f"h{min(level, 3)}"
            flowables.append(Paragraph(text, styles[style_key]))
            i += 1
            continue

        # Horizontal rule
        if re.match(r'^[-*_]{3,}$', line.strip()):
            flowables.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor("#cccccc")))
            flowables.append(Spacer(1, 6))
            i += 1
            continue

        # Unordered list
        if re.match(r'^[\*\-\+]\s+', line):
            items = []
            while i < len(lines) and re.match(r'^[\*\-\+]\s+', lines[i]):
                item_text = md_inline_to_rl(re.sub(r'^[\*\-\+]\s+', '', lines[i]))
                items.append(ListItem(Paragraph(item_text, styles["li"]), bulletColor=colors.HexColor("#333333")))
                i += 1
            flowables.append(ListFlowable(items, bulletType='bullet', leftIndent=20))
            continue

        # Ordered list
        if re.match(r'^\d+\.\s+', line):
            items = []
            while i < len(lines) and re.match(r'^\d+\.\s+', lines[i]):
                item_text = md_inline_to_rl(re.sub(r'^\d+\.\s+', '', lines[i]))
                items.append(ListItem(Paragraph(item_text, styles["li"])))
                i += 1
            flowables.append(ListFlowable(items, bulletType='1', leftIndent=20))
            continue

        # Blockquote
        if line.startswith("> "):
            quote_text = md_inline_to_rl(line[2:])
            flowables.append(Paragraph(f'<i>{quote_text}</i>', styles["blockquote"]))
            i += 1
            continue

        # Blank line
        if line.strip() == "":
            flowables.append(Spacer(1, 6))
            i += 1
            continue

        # Regular paragraph
        para_lines = []
        while i < len(lines) and lines[i].strip() != "" and not lines[i].startswith("#") \
              and not lines[i].startswith("```") and not re.match(r'^[\*\-\+]\s+', lines[i]) \
              and not re.match(r'^\d+\.\s+', lines[i]):
            para_lines.append(lines[i])
            i += 1
        text = md_inline_to_rl(" ".join(para_lines))
        flowables.append(Paragraph(text, styles["body"]))

    return flowables


def convert(input_path: str, output_path: str):
    md_text = Path(input_path).read_text(encoding="utf-8")
    styles = build_styles()

    doc = SimpleDocTemplate(
        output_path,
        pagesize=letter,
        leftMargin=inch,
        rightMargin=inch,
        topMargin=inch,
        bottomMargin=inch,
    )

    flowables = parse_md_to_flowables(md_text, styles)
    doc.build(flowables)
    print(f"✅ PDF saved to: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="Convert Markdown to PDF")
    parser.add_argument("input", help="Input Markdown file (.md)")
    parser.add_argument("output", nargs="?", help="Output PDF file (default: same name as input)")
    args = parser.parse_args()

    input_path = args.input
    output_path = args.output or str(Path(input_path).with_suffix(".pdf"))

    if not Path(input_path).exists():
        print(f"❌ File not found: {input_path}")
        sys.exit(1)

    convert(input_path, output_path)


if __name__ == "__main__":
    main()
