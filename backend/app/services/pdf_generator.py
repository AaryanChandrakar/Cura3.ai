"""
Cura3.ai — PDF Report Generator
Create professionally formatted PDF diagnosis reports.
"""
import io
from datetime import datetime, timezone
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm, cm
from reportlab.lib.colors import HexColor
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# ── Color Palette ────────────────────────────────────────
PRIMARY = HexColor("#0A6EBD")
PRIMARY_DARK = HexColor("#064D85")
SECONDARY = HexColor("#12B886")
TEXT_DARK = HexColor("#1A202C")
TEXT_SECONDARY = HexColor("#4A5568")
TEXT_MUTED = HexColor("#A0AEC0")
BG_LIGHT = HexColor("#F4F7FA")
BG_ACCENT = HexColor("#E8F4FD")
BORDER = HexColor("#E2E8F0")
DANGER = HexColor("#E74C3C")
WHITE = HexColor("#FFFFFF")


def _build_styles():
    """Create custom paragraph styles for the PDF."""
    styles = getSampleStyleSheet()

    styles.add(ParagraphStyle(
        name="BrandTitle",
        fontName="Helvetica-Bold",
        fontSize=22,
        textColor=PRIMARY_DARK,
        alignment=TA_CENTER,
        spaceAfter=2 * mm,
    ))

    styles.add(ParagraphStyle(
        name="BrandSubtitle",
        fontName="Helvetica",
        fontSize=10,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        spaceAfter=6 * mm,
    ))

    styles.add(ParagraphStyle(
        name="SectionHeader",
        fontName="Helvetica-Bold",
        fontSize=14,
        textColor=PRIMARY_DARK,
        spaceBefore=8 * mm,
        spaceAfter=4 * mm,
        borderPadding=(0, 0, 2, 0),
    ))

    styles.add(ParagraphStyle(
        name="SpecialistName",
        fontName="Helvetica-Bold",
        fontSize=12,
        textColor=SECONDARY,
        spaceBefore=6 * mm,
        spaceAfter=3 * mm,
    ))

    styles.add(ParagraphStyle(
        name="BodyText2",
        fontName="Helvetica",
        fontSize=10,
        textColor=TEXT_DARK,
        leading=15,
        alignment=TA_JUSTIFY,
        spaceAfter=3 * mm,
    ))

    styles.add(ParagraphStyle(
        name="MetaInfo",
        fontName="Helvetica",
        fontSize=9,
        textColor=TEXT_SECONDARY,
        spaceAfter=1 * mm,
    ))

    styles.add(ParagraphStyle(
        name="Disclaimer",
        fontName="Helvetica-Oblique",
        fontSize=8,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
        spaceBefore=8 * mm,
        spaceAfter=4 * mm,
        leading=12,
    ))

    styles.add(ParagraphStyle(
        name="PageFooter",
        fontName="Helvetica",
        fontSize=7,
        textColor=TEXT_MUTED,
        alignment=TA_CENTER,
    ))

    return styles


def _header_section(styles, patient_name: str, specialists: list[str], created_at: str):
    """Build the header/branding section."""
    elements = []

    # Brand
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph("CURA3.AI", styles["BrandTitle"]))
    elements.append(Paragraph("AI-Powered Medical Diagnostics Platform", styles["BrandSubtitle"]))

    # Divider
    elements.append(HRFlowable(
        width="100%", thickness=1.5, color=PRIMARY,
        spaceAfter=6 * mm, spaceBefore=2 * mm,
    ))

    # Patient Info Table
    date_str = created_at if isinstance(created_at, str) else created_at.strftime("%B %d, %Y at %I:%M %p")
    try:
        dt = datetime.fromisoformat(created_at.replace("Z", "+00:00")) if isinstance(created_at, str) else created_at
        date_str = dt.strftime("%B %d, %Y at %I:%M %p UTC")
    except Exception:
        pass

    specialist_str = ", ".join(specialists) if specialists else "—"

    info_data = [
        [
            Paragraph("<b>Patient:</b>", styles["MetaInfo"]),
            Paragraph(patient_name or "Unknown Patient", styles["MetaInfo"]),
        ],
        [
            Paragraph("<b>Date:</b>", styles["MetaInfo"]),
            Paragraph(date_str, styles["MetaInfo"]),
        ],
        [
            Paragraph("<b>Specialists:</b>", styles["MetaInfo"]),
            Paragraph(specialist_str, styles["MetaInfo"]),
        ],
    ]

    info_table = Table(info_data, colWidths=[3 * cm, 14 * cm])
    info_table.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 2),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 2),
        ("BACKGROUND", (0, 0), (-1, -1), BG_ACCENT),
        ("BOX", (0, 0), (-1, -1), 0.5, BORDER),
        ("INNERGRID", (0, 0), (-1, -1), 0, WHITE),
        ("LEFTPADDING", (0, 0), (-1, -1), 8),
        ("RIGHTPADDING", (0, 0), (-1, -1), 8),
    ]))
    elements.append(info_table)
    elements.append(Spacer(1, 6 * mm))

    return elements


def _sanitize_for_pdf(text: str) -> str:
    """Sanitize text for ReportLab (replace problematic characters)."""
    replacements = {
        "\u2018": "'", "\u2019": "'",
        "\u201C": '"', "\u201D": '"',
        "\u2013": "-", "\u2014": "--",
        "\u2026": "...",
        "\u2022": "-",
        "\u00A0": " ",
        "&": "&amp;",
        "<": "&lt;",
        ">": "&gt;",
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text


async def generate_diagnosis_pdf(
    patient_name: str,
    specialists: list[str],
    specialist_reports: list[dict],
    final_diagnosis: str,
    created_at: str | datetime = None,
) -> bytes:
    """
    Generate a professional PDF diagnosis report.

    Returns:
        PDF file as bytes.
    """
    buffer = io.BytesIO()
    styles = _build_styles()

    if created_at is None:
        created_at = datetime.now(timezone.utc).isoformat()

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
        leftMargin=18 * mm,
        rightMargin=18 * mm,
        title=f"Cura3.ai - Diagnosis Report - {patient_name}",
        author="Cura3.ai",
        subject="AI Medical Diagnosis Report",
    )

    elements = []

    # ── Header ────────────────────────────────────────────
    elements.extend(_header_section(styles, patient_name, specialists, created_at))

    # ── Final Diagnosis ───────────────────────────────────
    elements.append(Paragraph("FINAL DIAGNOSIS REPORT", styles["SectionHeader"]))
    elements.append(HRFlowable(
        width="100%", thickness=0.5, color=BORDER,
        spaceAfter=4 * mm,
    ))

    # Split final diagnosis into paragraphs
    diagnosis_text = _sanitize_for_pdf(final_diagnosis or "No diagnosis available.")
    for para in diagnosis_text.split("\n"):
        stripped = para.strip()
        if not stripped:
            elements.append(Spacer(1, 2 * mm))
            continue

        # Detect section headers (all caps lines or lines with === or ---)
        if stripped.startswith("===") or stripped.startswith("---"):
            elements.append(HRFlowable(
                width="100%", thickness=0.5, color=BORDER,
                spaceAfter=2 * mm, spaceBefore=2 * mm,
            ))
        elif stripped == stripped.upper() and len(stripped) > 3 and not stripped.startswith("-"):
            elements.append(Paragraph(
                f"<b>{stripped}</b>",
                ParagraphStyle(
                    "DiagHeader", parent=styles["BodyText2"],
                    fontName="Helvetica-Bold", fontSize=11,
                    textColor=PRIMARY_DARK, spaceBefore=4 * mm,
                )
            ))
        else:
            elements.append(Paragraph(stripped, styles["BodyText2"]))

    # ── Individual Specialist Reports ─────────────────────
    if specialist_reports:
        elements.append(Spacer(1, 6 * mm))
        elements.append(Paragraph("INDIVIDUAL SPECIALIST REPORTS", styles["SectionHeader"]))
        elements.append(HRFlowable(
            width="100%", thickness=0.5, color=BORDER,
            spaceAfter=4 * mm,
        ))

        for report in specialist_reports:
            name = report.get("specialist_name", "Unknown")
            content = _sanitize_for_pdf(report.get("report_content", "No report available."))

            specialist_block = []
            specialist_block.append(Paragraph(f"{name}", styles["SpecialistName"]))

            for para in content.split("\n"):
                stripped = para.strip()
                if stripped:
                    specialist_block.append(Paragraph(stripped, styles["BodyText2"]))

            specialist_block.append(Spacer(1, 3 * mm))
            specialist_block.append(HRFlowable(
                width="100%", thickness=0.3, color=BORDER,
                spaceAfter=2 * mm,
            ))

            elements.append(KeepTogether(specialist_block[:5]))  # Try to keep header + first paras together
            elements.extend(specialist_block[5:])

    # ── Disclaimer ────────────────────────────────────────
    elements.append(Spacer(1, 8 * mm))
    elements.append(HRFlowable(
        width="100%", thickness=1, color=DANGER,
        spaceAfter=4 * mm,
    ))
    elements.append(Paragraph(
        "IMPORTANT DISCLAIMER: This report is generated by AI for research and educational "
        "purposes only. It is NOT a substitute for professional medical advice, diagnosis, "
        "or treatment. Always consult a qualified healthcare provider for medical decisions. "
        "Cura3.ai and its creators bear no responsibility for any actions taken based on this report.",
        styles["Disclaimer"],
    ))

    # ── Footer ────────────────────────────────────────────
    elements.append(Spacer(1, 4 * mm))
    elements.append(Paragraph(
        f"Generated by Cura3.ai v2.0 | {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M UTC')}",
        styles["PageFooter"],
    ))

    # Build PDF
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    return pdf_bytes
