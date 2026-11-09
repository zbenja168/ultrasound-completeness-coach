"""Render one of our plain Markdown docs to a simple letter-size PDF (headings, paragraphs, bullets, check boxes,
numbered items, pipe tables, inline bold and code). Enough for hand-outs like docs/FIRST_PRINT_CHECKLIST.md.

Usage: python scripts/md_to_pdf.py docs/FIRST_PRINT_CHECKLIST.md docs/FIRST_PRINT_CHECKLIST.pdf
"""
import re
import sys
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.platypus import ListFlowable, ListItem, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle

INK = colors.HexColor("#1b2a3a")


def inline(s):
    s = s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    s = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", s)
    s = re.sub(r"`(.+?)`", r"<font face='Courier'>\1</font>", s)
    s = re.sub(r"\[(.+?)\]\((.+?)\)", r"<link href='\2' color='#2c6fb0'>\1</link>", s)
    return s


def build(md_path, pdf_path):
    ss = getSampleStyleSheet()
    body = ParagraphStyle("body", parent=ss["BodyText"], fontName="Helvetica", fontSize=10, leading=13.5, textColor=INK, alignment=TA_LEFT, spaceAfter=4)
    h1 = ParagraphStyle("h1", parent=body, fontName="Helvetica-Bold", fontSize=16, leading=20, spaceAfter=6)
    h2 = ParagraphStyle("h2", parent=body, fontName="Helvetica-Bold", fontSize=12, leading=15, spaceBefore=8, spaceAfter=4)
    cell = ParagraphStyle("cell", parent=body, fontSize=8.5, leading=11, spaceAfter=0)
    lines = Path(md_path).read_text(encoding="utf-8").splitlines()
    story, i = [], 0

    def flush_para(buf):
        if buf:
            story.append(Paragraph(inline(" ".join(buf)), body))
            buf.clear()

    buf = []
    while i < len(lines):
        ln = lines[i]
        if ln.startswith("# "):
            flush_para(buf); story.append(Paragraph(inline(ln[2:]), h1))
        elif ln.startswith("## "):
            flush_para(buf); story.append(Paragraph(inline(ln[3:]), h2))
        elif ln.startswith("|"):
            flush_para(buf)
            rows = []
            while i < len(lines) and lines[i].startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(set(c) <= set("-: ") for c in cells):
                    rows.append([Paragraph(inline(c), cell) for c in cells])
                i += 1
            n = len(rows[0])
            width = (letter[0] - 40 * mm) / n
            t = Table(rows, colWidths=[width] * n, repeatRows=1)
            t.setStyle(TableStyle([("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#e6ebf0")), ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#8a94a0")),
                                   ("VALIGN", (0, 0), (-1, -1), "TOP"), ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4)]))
            story.append(t); story.append(Spacer(1, 6))
            continue
        elif re.match(r"^\s*- ", ln) or re.match(r"^\s*\d+\. ", ln):
            flush_para(buf)
            items, numbered = [], bool(re.match(r"^\s*\d+\. ", ln))
            while i < len(lines) and (re.match(r"^\s*- ", lines[i]) or re.match(r"^\s*\d+\. ", lines[i]) or (lines[i].startswith("   ") and lines[i].strip())):
                if re.match(r"^\s*- ", lines[i]) or re.match(r"^\s*\d+\. ", lines[i]):
                    items.append(re.sub(r"^\s*(- |\d+\. )", "", lines[i]).strip())
                else:
                    items[-1] += " " + lines[i].strip()
                i += 1
            flow = []
            for it in items:
                box = ""
                if it.startswith("[ ] "):
                    box, it = "[&nbsp;&nbsp;&nbsp;]&nbsp; ", it[4:]   # Helvetica has no box glyph
                flow.append(ListItem(Paragraph(box + inline(it), body), leftIndent=12))
            story.append(ListFlowable(flow, bulletType="1" if numbered else "bullet", start=None if numbered else "•", leftIndent=14, bulletFontSize=9))
            continue
        elif ln.strip() == "":
            flush_para(buf)
        else:
            buf.append(ln.strip())
        i += 1
    flush_para(buf)
    doc = SimpleDocTemplate(str(pdf_path), pagesize=letter, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=18 * mm,
                            title=Path(md_path).stem.replace("_", " ").title())
    doc.build(story)
    print("wrote", pdf_path)


if __name__ == "__main__":
    build(sys.argv[1], sys.argv[2])
