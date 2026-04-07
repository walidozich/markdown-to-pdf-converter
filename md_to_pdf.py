#!/usr/bin/env python3
"""
Markdown to PDF Converter
Usage: python md_to_pdf.py input.md [output.pdf]
"""

import sys
import re
import argparse
import math
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
    HRFlowable, ListFlowable, ListItem, Table, TableStyle
)
from reportlab.lib.enums import TA_LEFT, TA_CENTER
from reportlab.platypus.flowables import Flowable


MERMAID_STARTERS = (
    "graph ",
    "flowchart ",
    "sequenceDiagram",
    "classDiagram",
    "stateDiagram",
    "stateDiagram-v2",
    "erDiagram",
    "journey",
    "gantt",
    "pie",
    "mindmap",
    "timeline",
    "gitGraph",
    "xychart-beta",
)


def is_mermaid_start(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return False
    return any(stripped.startswith(prefix) for prefix in MERMAID_STARTERS)


def _parse_number_list(payload: str):
    values = []
    for part in payload.split(","):
        token = part.strip()
        if not token:
            continue
        values.append(float(token))
    return values


def parse_mermaid_xychart(code: str):
    """
    Parse a Mermaid xychart-beta block.
    Returns a dict with parsed spec or None if not a valid xychart-beta.
    """
    lines = [ln.strip() for ln in code.splitlines() if ln.strip()]
    if not lines or lines[0] != "xychart-beta":
        return None

    title = ""
    x_values = []
    y_label = ""
    y_min = None
    y_max = None
    series = []

    for ln in lines[1:]:
        m = re.match(r'^title\s+"(.*)"$', ln)
        if m:
            title = m.group(1)
            continue

        m = re.match(r"^x-axis\s+\[(.*)\]$", ln)
        if m:
            x_values = _parse_number_list(m.group(1))
            continue

        m = re.match(r'^y-axis\s+"(.*)"\s+([\-0-9.]+)\s*-->\s*([\-0-9.]+)$', ln)
        if m:
            y_label = m.group(1)
            y_min = float(m.group(2))
            y_max = float(m.group(3))
            continue

        m = re.match(r'^(line|bar)\s+"(.*)"\s+\[(.*)\]$', ln)
        if m:
            kind = m.group(1)
            name = m.group(2)
            values = _parse_number_list(m.group(3))
            series.append({"kind": kind, "name": name, "values": values})
            continue

    if not x_values or not series:
        return None

    if y_min is None or y_max is None:
        y_min = min(min(s["values"]) for s in series if s["values"])
        y_max = max(max(s["values"]) for s in series if s["values"])
        if y_min == y_max:
            y_max = y_min + 1.0

    return {
        "title": title,
        "x_values": x_values,
        "y_label": y_label,
        "y_min": y_min,
        "y_max": y_max,
        "series": series,
    }


class MermaidXYChart(Flowable):
    """Render Mermaid xychart-beta as a vector chart in the PDF."""

    COLORS = [
        colors.HexColor("#2563eb"),
        colors.HexColor("#ef4444"),
        colors.HexColor("#10b981"),
        colors.HexColor("#f59e0b"),
        colors.HexColor("#8b5cf6"),
    ]

    def __init__(self, chart_spec: dict, available_width: float | None = None):
        super().__init__()
        self.spec = chart_spec
        self.available_width = available_width
        self.chart_height = 260

    def wrap(self, availWidth, availHeight):
        if self.available_width is None:
            self.width = availWidth
        else:
            self.width = min(self.available_width, availWidth)
        self.height = self.chart_height
        return self.width, self.height

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        # Container
        c.setFillColor(colors.HexColor("#f8fafc"))
        c.setStrokeColor(colors.HexColor("#cbd5e1"))
        c.setLineWidth(0.7)
        c.roundRect(0, 0, w, h, 6, stroke=1, fill=1)

        left = 62
        right = 24
        top = 38
        bottom = 46
        plot_x0 = left
        plot_y0 = bottom
        plot_w = max(80, w - left - right)
        plot_h = max(80, h - top - bottom)

        title = self.spec.get("title", "")
        if title:
            c.setFillColor(colors.HexColor("#0f172a"))
            c.setFont("Helvetica-Bold", 12)
            c.drawString(14, h - 22, title)

        # Axes
        c.setStrokeColor(colors.HexColor("#334155"))
        c.setLineWidth(1)
        c.line(plot_x0, plot_y0, plot_x0, plot_y0 + plot_h)
        c.line(plot_x0, plot_y0, plot_x0 + plot_w, plot_y0)

        y_min = float(self.spec["y_min"])
        y_max = float(self.spec["y_max"])
        if y_max <= y_min:
            y_max = y_min + 1.0

        x_values = self.spec["x_values"]
        y_label = self.spec.get("y_label", "")
        n = len(x_values)
        x_step = 0 if n <= 1 else plot_w / (n - 1)

        # Grid + y ticks
        ticks = 5
        c.setFont("Helvetica", 8)
        for t in range(ticks + 1):
            ratio = t / ticks
            y = plot_y0 + ratio * plot_h
            v = y_min + ratio * (y_max - y_min)
            c.setStrokeColor(colors.HexColor("#e2e8f0"))
            c.setLineWidth(0.6)
            c.line(plot_x0, y, plot_x0 + plot_w, y)
            c.setFillColor(colors.HexColor("#475569"))
            c.drawRightString(plot_x0 - 6, y - 3, f"{v:.1f}")

        # X ticks
        c.setFillColor(colors.HexColor("#475569"))
        for idx, xv in enumerate(x_values):
            x = plot_x0 + (idx * x_step if n > 1 else plot_w / 2)
            c.drawCentredString(x, plot_y0 - 14, f"{int(xv) if xv.is_integer() else xv:g}")

        # Y-axis label
        if y_label:
            c.saveState()
            c.setFillColor(colors.HexColor("#334155"))
            c.setFont("Helvetica", 8)
            c.translate(16, plot_y0 + (plot_h / 2))
            c.rotate(90)
            c.drawCentredString(0, 0, y_label)
            c.restoreState()

        # Series rendering
        legend_x = plot_x0 + 8
        legend_y = h - 18
        legend_offset = 0

        for idx, s in enumerate(self.spec["series"]):
            color = self.COLORS[idx % len(self.COLORS)]
            values = s["values"]
            points = []
            for j, value in enumerate(values[:n]):
                px = plot_x0 + (j * x_step if n > 1 else plot_w / 2)
                ratio = (value - y_min) / (y_max - y_min)
                py = plot_y0 + max(0.0, min(1.0, ratio)) * plot_h
                points.append((px, py))

            if s["kind"] == "bar":
                if n > 1:
                    bar_w = max(6, min(20, x_step * 0.55))
                else:
                    bar_w = min(30, plot_w * 0.5)
                for px, py in points:
                    c.setFillColor(color)
                    c.setStrokeColor(color)
                    c.rect(px - (bar_w / 2), plot_y0, bar_w, max(1, py - plot_y0), stroke=0, fill=1)
            else:
                c.setStrokeColor(color)
                c.setLineWidth(1.8)
                for p0, p1 in zip(points, points[1:]):
                    c.line(p0[0], p0[1], p1[0], p1[1])
                c.setFillColor(color)
                for px, py in points:
                    c.circle(px, py, 2.4, stroke=0, fill=1)

            # Legend
            c.setFillColor(color)
            c.rect(legend_x + legend_offset, legend_y - 6, 8, 8, stroke=0, fill=1)
            c.setFillColor(colors.HexColor("#1e293b"))
            c.setFont("Helvetica", 8)
            c.drawString(legend_x + legend_offset + 11, legend_y - 5, s["name"])
            legend_offset += 95


def mermaid_block_to_flowables(code: str):
    chart = parse_mermaid_xychart(code)
    if chart:
        return [
            Spacer(1, 6),
            MermaidXYChart(chart, available_width=None),
            Spacer(1, 10),
        ]

    return [
        Spacer(1, 6),
        DarkCodeBlock(code, available_width=None),
        Spacer(1, 10),
    ]


class DarkCodeBlock(Flowable):
    """A flowable that renders a code block with a dark background and bright text."""

    BG      = colors.HexColor("#1e1e2e")
    FG      = colors.HexColor("#f8f8f2")
    BORDER  = colors.HexColor("#44475a")
    FONT    = "Courier"
    FONT_SIZE = 9
    LEADING   = 14
    PAD_H     = 14   # horizontal padding
    PAD_V     = 12   # vertical padding
    RADIUS    = 5

    def __init__(self, code: str, available_width: float | None = None):
        super().__init__()
        self.code = code
        self.available_width = available_width
        self.lines = code.splitlines()

    def wrap(self, availWidth, availHeight):
        if self.available_width is None:
            self.width = availWidth
        else:
            self.width = min(self.available_width, availWidth)
        self.height = (len(self.lines) * self.LEADING) + (self.PAD_V * 2)
        return self.width, self.height

    def split(self, availWidth, availHeight):
        """Allow long code blocks to split across pages instead of raising LayoutError."""
        usable_height = availHeight - (self.PAD_V * 2)
        max_lines = int(usable_height // self.LEADING)

        if max_lines <= 0:
            return []
        if len(self.lines) <= max_lines:
            return [self]

        first = "\n".join(self.lines[:max_lines])
        rest = "\n".join(self.lines[max_lines:])
        return [
            DarkCodeBlock(first, self.available_width),
            DarkCodeBlock(rest, self.available_width),
        ]

    def draw(self):
        c = self.canv
        w, h = self.width, self.height

        # Draw rounded dark background
        c.setFillColor(self.BG)
        c.setStrokeColor(self.BORDER)
        c.setLineWidth(0.5)
        c.roundRect(0, 0, w, h, self.RADIUS, stroke=1, fill=1)

        # Draw each line of code in bright colour
        c.setFillColor(self.FG)
        c.setFont(self.FONT, self.FONT_SIZE)
        y = h - self.PAD_V - self.FONT_SIZE   # start from top
        for line in self.lines:
            c.drawString(self.PAD_H, y, line)
            y -= self.LEADING


def build_styles():
    styles = getSampleStyleSheet()

    custom = {
        "h1": ParagraphStyle("h1", parent=styles["Heading1"], fontSize=24, spaceAfter=12, textColor=colors.HexColor("#1a1a2e")),
        "h2": ParagraphStyle("h2", parent=styles["Heading2"], fontSize=18, spaceAfter=10, textColor=colors.HexColor("#16213e")),
        "h3": ParagraphStyle("h3", parent=styles["Heading3"], fontSize=14, spaceAfter=8, textColor=colors.HexColor("#0f3460")),
        "body": ParagraphStyle("body", parent=styles["Normal"], fontSize=11, leading=16, spaceAfter=8),
        "code": ParagraphStyle("code", parent=styles["Code"], fontSize=9, leading=14,
                               backColor=colors.HexColor("#1e1e2e"), textColor=colors.HexColor("#f8f8f2"),
                               leftIndent=16, rightIndent=16, spaceBefore=10, spaceAfter=10,
                               borderPadding=(10, 10, 10, 10),
                               fontName="Courier"),
        "blockquote": ParagraphStyle("blockquote", parent=styles["Normal"], fontSize=11, leading=16,
                                     leftIndent=20, textColor=colors.HexColor("#555555"),
                                     borderPadding=(4, 0, 4, 8)),
        "li": ParagraphStyle("li", parent=styles["Normal"], fontSize=11, leading=16),
    }
    return custom


def md_inline_to_rl(text):
    """Convert inline markdown (bold, italic, inline code) to ReportLab XML."""
    code_spans = []

    def stash_code(match):
        code_spans.append(match.group(1))
        return f"@@CODE{len(code_spans) - 1}@@"

    # Inline code (stash first to avoid markdown formatting inside code spans)
    text = re.sub(r'`([^`]+)`', stash_code, text)
    # Bold + italic
    text = re.sub(r'\*\*\*(.+?)\*\*\*', r'<b><i>\1</i></b>', text)
    # Bold
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<b>\1</b>', text)
    # Italic
    text = re.sub(r'\*(.+?)\*', r'<i>\1</i>', text)
    text = re.sub(r'(?<!\w)_(.+?)_(?!\w)', r'<i>\1</i>', text)
    # Links
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<a href="\2" color="blue">\1</a>', text)

    # Restore inline code spans
    for idx, code in enumerate(code_spans):
        escaped_code = (
            code.replace("&", "&amp;")
            .replace("<", "&lt;")
            .replace(">", "&gt;")
        )
        text = text.replace(
            f"@@CODE{idx}@@",
            f'<font name="Courier" size="9" color="#f8f8f2" backColor="#1e1e2e"> {escaped_code} </font>'
        )

    return text


def parse_md_to_flowables(md_text, styles):
    flowables = []
    lines = md_text.splitlines()
    i = 0

    while i < len(lines):
        line = lines[i]

        # Fenced code block (supports ``` and ```mermaid)
        if line.startswith("```"):
            fence_lang = line.strip()[3:].strip().lower()
            code_lines = []
            i += 1
            while i < len(lines) and not lines[i].startswith("```"):
                code_lines.append(lines[i])
                i += 1
            code = "\n".join(code_lines)
            if fence_lang == "mermaid":
                flowables.extend(mermaid_block_to_flowables(code))
            else:
                flowables.append(Spacer(1, 6))
                flowables.append(DarkCodeBlock(code, available_width=None))
                flowables.append(Spacer(1, 10))
            i += 1
            continue

        # Mermaid block written without fenced code markers.
        # We keep reading until a blank line so the source appears verbatim in the PDF.
        if is_mermaid_start(line):
            mermaid_lines = [line]
            i += 1
            while i < len(lines) and lines[i].strip() != "":
                mermaid_lines.append(lines[i])
                i += 1
            flowables.extend(mermaid_block_to_flowables("\n".join(mermaid_lines)))
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
