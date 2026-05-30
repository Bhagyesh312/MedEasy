from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_LEFT, TA_CENTER
import io
from datetime import datetime

STATUS_COLORS = {
    "Normal":   colors.HexColor("#16a34a"),
    "High":     colors.HexColor("#ea580c"),
    "Low":      colors.HexColor("#2563eb"),
    "Critical": colors.HexColor("#dc2626"),
    "Unknown":  colors.HexColor("#64748b"),
}

STATUS_BG = {
    "Normal":   colors.HexColor("#f0fdf4"),
    "High":     colors.HexColor("#fff7ed"),
    "Low":      colors.HexColor("#eff6ff"),
    "Critical": colors.HexColor("#fef2f2"),
    "Unknown":  colors.HexColor("#f8fafc"),
}


def generate_report_pdf(report_data: dict) -> bytes:
    """Generate a PDF from report analysis data. Returns bytes."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles = getSampleStyleSheet()
    story  = []

    # ── Custom styles ──
    title_style = ParagraphStyle(
        "Title", parent=styles["Normal"],
        fontSize=22, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#0f172a"),
        spaceAfter=4
    )
    subtitle_style = ParagraphStyle(
        "Subtitle", parent=styles["Normal"],
        fontSize=11, fontName="Helvetica",
        textColor=colors.HexColor("#64748b"),
        spaceAfter=2
    )
    section_style = ParagraphStyle(
        "Section", parent=styles["Normal"],
        fontSize=13, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#1e40af"),
        spaceBefore=14, spaceAfter=6
    )
    body_style = ParagraphStyle(
        "Body", parent=styles["Normal"],
        fontSize=9.5, fontName="Helvetica",
        textColor=colors.HexColor("#334155"),
        leading=14
    )
    small_style = ParagraphStyle(
        "Small", parent=styles["Normal"],
        fontSize=8.5, fontName="Helvetica",
        textColor=colors.HexColor("#64748b"),
        leading=12
    )
    action_style = ParagraphStyle(
        "Action", parent=styles["Normal"],
        fontSize=9, fontName="Helvetica-Oblique",
        textColor=colors.HexColor("#475569"),
        leading=12
    )

    report   = report_data.get("report", {})
    findings = report_data.get("findings", [])
    questions = report_data.get("questions", [])

    patient  = report.get("patient_name") or "Patient"
    filename = report.get("filename", "Report")
    summary  = report.get("summary", "")
    uploaded = report.get("uploaded_at", "")
    if uploaded:
        try:
            dt = datetime.fromisoformat(uploaded)
            uploaded = dt.strftime("%d %b %Y, %I:%M %p")
        except Exception:
            pass

    # ── Header ──
    story.append(Paragraph("MedEasy", ParagraphStyle(
        "Brand", parent=styles["Normal"],
        fontSize=10, fontName="Helvetica-Bold",
        textColor=colors.HexColor("#2563eb"), spaceAfter=2
    )))
    story.append(Paragraph(f"Medical Report Analysis — {patient}", title_style))
    story.append(Paragraph(f"File: {filename}  |  Generated: {uploaded}", subtitle_style))
    story.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563eb"), spaceAfter=12))

    # ── Stats row ──
    flagged  = [f for f in findings if f.get("is_flagged")]
    normal   = [f for f in findings if not f.get("is_flagged")]
    critical = [f for f in findings if f.get("status") == "Critical"]

    stats_data = [
        ["Total Tests", "Normal", "Need Attention", "Critical"],
        [str(len(findings)), str(len(normal)), str(len(flagged)), str(len(critical))]
    ]
    stats_table = Table(stats_data, colWidths=[4*cm]*4)
    stats_table.setStyle(TableStyle([
        ("BACKGROUND",  (0,0), (-1,0), colors.HexColor("#eff6ff")),
        ("BACKGROUND",  (0,1), (-1,1), colors.white),
        ("TEXTCOLOR",   (0,0), (-1,0), colors.HexColor("#2563eb")),
        ("TEXTCOLOR",   (0,1), (-1,1), colors.HexColor("#0f172a")),
        ("FONTNAME",    (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTNAME",    (0,1), (-1,1), "Helvetica-Bold"),
        ("FONTSIZE",    (0,0), (-1,0), 8),
        ("FONTSIZE",    (0,1), (-1,1), 18),
        ("ALIGN",       (0,0), (-1,-1), "CENTER"),
        ("VALIGN",      (0,0), (-1,-1), "MIDDLE"),
        ("ROWBACKGROUNDS", (0,0), (-1,-1), [colors.HexColor("#eff6ff"), colors.white]),
        ("BOX",         (0,0), (-1,-1), 0.5, colors.HexColor("#bfdbfe")),
        ("INNERGRID",   (0,0), (-1,-1), 0.5, colors.HexColor("#bfdbfe")),
        ("TOPPADDING",  (0,0), (-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
    ]))
    story.append(stats_table)
    story.append(Spacer(1, 14))

    # ── Summary ──
    if summary:
        story.append(Paragraph("Overall Summary", section_style))
        story.append(Paragraph(summary, body_style))
        story.append(Spacer(1, 10))

    # ── Findings ──
    story.append(Paragraph("Detailed Results", section_style))

    for f in findings:
        status = f.get("status", "Unknown")
        sc     = STATUS_COLORS.get(status, colors.gray)
        sbg    = STATUS_BG.get(status, colors.white)
        test   = f.get("test_name") or f.get("test", "Unknown")
        value  = f.get("value", "N/A")
        ref    = f.get("reference_range", "")
        expl   = f.get("explanation", "")
        action = f.get("action", "")

        ref_text = f"  |  Ref: {ref}" if ref and ref != "Not specified" else ""

        row_data = [
            [Paragraph(f"<b>{test}</b>", ParagraphStyle("th", parent=styles["Normal"], fontSize=10, fontName="Helvetica-Bold", textColor=colors.HexColor("#0f172a"))),
             Paragraph(f"<b>{value}</b>{ref_text}", ParagraphStyle("tv", parent=styles["Normal"], fontSize=9.5, textColor=colors.HexColor("#334155"))),
             Paragraph(f"<b>{status}</b>", ParagraphStyle("ts", parent=styles["Normal"], fontSize=9, fontName="Helvetica-Bold", textColor=sc, alignment=TA_CENTER))],
            [Paragraph(expl, small_style), "", ""],
        ]
        if action:
            row_data.append([Paragraph(f"→ {action}", action_style), "", ""])

        t = Table(row_data, colWidths=[5.5*cm, 7.5*cm, 3*cm])
        t.setStyle(TableStyle([
            ("BACKGROUND",  (0,0), (-1,0), sbg),
            ("BACKGROUND",  (0,1), (-1,-1), colors.white),
            ("SPAN",        (0,1), (-1,1)),
            ("SPAN",        (0,2), (-1,2)),
            ("VALIGN",      (0,0), (-1,-1), "TOP"),
            ("TOPPADDING",  (0,0), (-1,-1), 6),
            ("BOTTOMPADDING",(0,0),(-1,-1), 6),
            ("LEFTPADDING", (0,0), (-1,-1), 8),
            ("RIGHTPADDING",(0,0), (-1,-1), 8),
            ("BOX",         (0,0), (-1,-1), 0.5, colors.HexColor("#e2e8f0")),
            ("LINEBELOW",   (0,0), (-1,0), 0.5, colors.HexColor("#e2e8f0")),
            ("LEFTLINE",    (0,0), (0,-1), 3, sc),
        ]))
        story.append(t)
        story.append(Spacer(1, 5))

    # ── Doctor questions ──
    if questions:
        story.append(Spacer(1, 8))
        story.append(Paragraph("Questions to Ask Your Doctor", section_style))
        for i, q in enumerate(questions, 1):
            story.append(Paragraph(f"{i}. {q}", body_style))
            story.append(Spacer(1, 4))

    # ── Footer ──
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#e2e8f0")))
    story.append(Spacer(1, 6))
    story.append(Paragraph(
        "Generated by MedEasy. This report is for informational purposes only and does not constitute medical advice. Always consult a qualified healthcare professional.",
        ParagraphStyle("Footer", parent=styles["Normal"], fontSize=7.5, textColor=colors.HexColor("#94a3b8"), alignment=TA_CENTER)
    ))

    doc.build(story)
    return buffer.getvalue()
