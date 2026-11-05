"""
Fonctions de génération des exports téléchargeables :

  - build_alert_pdf(alert)        → BytesIO  (PDF fiche d'alerte)
  - build_daily_report_pdf(report)→ BytesIO  (PDF rapport journalier)
  - build_alerts_excel(queryset)  → BytesIO  (Excel liste d'alertes)
"""

from io import BytesIO
from django.utils import timezone
from django.utils.timezone import localtime

# ── ReportLab ────────────────────────────────────────────────────────────────
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    HRFlowable, Paragraph, SimpleDocTemplate, Spacer, Table, TableStyle,
)

# ── OpenPyXL ─────────────────────────────────────────────────────────────────
import openpyxl
from openpyxl.styles import Alignment, Font, PatternFill

# ── Constantes visuelles ──────────────────────────────────────────────────────
NAVY = colors.HexColor("#003366")
LIGHT_BLUE = colors.HexColor("#E8F4FD")
ACCENT = colors.HexColor("#0E9FDA")
WHITE = colors.white

HEADER_FONT = Font(bold=True, color="FFFFFF", size=11)
HEADER_FILL = PatternFill("solid", fgColor="003366")
ALT_FILL = PatternFill("solid", fgColor="EBF5FB")
CENTER_ALIGN = Alignment(horizontal="center", vertical="center", wrap_text=True)
LEFT_ALIGN = Alignment(horizontal="left", vertical="center", wrap_text=True)

W, H = A4  # 595 x 842 points


# ─────────────────────────────────────────────────────────────────────────────
# Helpers communs
# ─────────────────────────────────────────────────────────────────────────────

def _fmt_dt(dt):
    """Formate un datetime en heure locale lisible, ou '--' si None."""
    if dt is None:
        return "--"
    return localtime(dt).strftime("%d/%m/%Y %H:%M")


def _fmt_date(d):
    if d is None:
        return "--"
    return d.strftime("%d/%m/%Y")


def _styles():
    base = getSampleStyleSheet()
    title = ParagraphStyle(
        "sgim_title", parent=base["Title"],
        textColor=WHITE, fontSize=16, spaceAfter=2,
    )
    subtitle = ParagraphStyle(
        "sgim_subtitle", parent=base["Normal"],
        textColor=LIGHT_BLUE, fontSize=10, spaceAfter=0,
    )
    section = ParagraphStyle(
        "sgim_section", parent=base["Heading2"],
        textColor=NAVY, fontSize=11, spaceBefore=10, spaceAfter=4,
        borderPad=2,
    )
    body = ParagraphStyle(
        "sgim_body", parent=base["Normal"],
        fontSize=9, leading=14,
    )
    return title, subtitle, section, body


def _header_table(title_text, subtitle_text, number_text):
    """Bandeau d'en-tête bleu marine commun aux deux PDF."""
    title_s, subtitle_s, *_ = _styles()
    data = [[
        Paragraph(title_text, title_s),
        Paragraph(f"<b>{number_text}</b>", ParagraphStyle(
            "num", textColor=WHITE, fontSize=14, alignment=2)),
    ]]
    t = Table(data, colWidths=[12 * cm, 5.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), NAVY),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (0, 0), 12),
        ("RIGHTPADDING", (-1, 0), (-1, 0), 12),
        ("TOPPADDING", (0, 0), (-1, -1), 10),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
    ]))
    return t


def _section_title(text, section_style):
    return [
        Paragraph(text.upper(), section_style),
        HRFlowable(width="100%", thickness=1, color=ACCENT, spaceAfter=4),
    ]


def _info_table(rows, col_widths=(5.5 * cm, 12 * cm)):
    """
    Tableau deux colonnes : label (gris) | valeur (blanc).
    rows = list of (label, value).
    """
    data = [[Paragraph(f"<b>{label}</b>", ParagraphStyle(
        "lbl", fontSize=9, textColor=NAVY)),
             Paragraph(str(value) if value is not None else "--",
                       ParagraphStyle("val", fontSize=9))]
            for label, value in rows]

    t = Table(data, colWidths=list(col_widths))
    style = [
        ("BACKGROUND", (0, 0), (0, -1), LIGHT_BLUE),
        ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("TOPPADDING", (0, 0), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
    ]
    # Alternance légère sur les valeurs
    for i in range(1, len(data), 2):
        style.append(("BACKGROUND", (1, i), (1, i), colors.HexColor("#F8FBFF")))
    t.setStyle(TableStyle(style))
    return t


# ─────────────────────────────────────────────────────────────────────────────
# 1. PDF — Fiche d'alerte
# ─────────────────────────────────────────────────────────────────────────────

def build_alert_pdf(alert) -> BytesIO:
    """
    Génère la fiche complète d'une alerte au format PDF (A4).
    Inclut : infos générales, localisation, moyens engagés, historique des statuts.
    """
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )
    _, _, section_s, body_s = _styles()
    story = []

    # ── En-tête ───────────────────────────────────────────────────────────────
    story.append(_header_table(
        "FICHE D'ALERTE — SGIM",
        f"Générée le {_fmt_dt(timezone.now())}",
        alert.number,
    ))
    story.append(Spacer(1, 0.5 * cm))

    # ── Informations générales ────────────────────────────────────────────────
    story.extend(_section_title("Informations générales", section_s))
    story.append(_info_table([
        ("Numéro", alert.number),
        ("Statut", alert.get_status_display()),
        ("Centre", str(alert.center)),
        ("Date / heure appel", _fmt_dt(alert.call_time)),
        ("Canal (source)", str(alert.channel)),
        ("Type d'alerte", str(alert.alert_type)),
        ("Priorité", str(alert.priority) if alert.priority else "--"),
        ("Opérateur", alert.operator_signature),
        ("Créé par", str(alert.created_by)),
        ("Créé le", _fmt_dt(alert.created_at)),
    ]))
    story.append(Spacer(1, 0.3 * cm))

    # ── Description ───────────────────────────────────────────────────────────
    story.extend(_section_title("Description", section_s))
    story.append(Paragraph(alert.description or "--", body_s))
    story.append(Spacer(1, 0.3 * cm))

    # ── Localisation ──────────────────────────────────────────────────────────
    story.extend(_section_title("Localisation", section_s))
    story.append(_info_table([
        ("Latitude", str(alert.latitude) if alert.latitude else "--"),
        ("Longitude", str(alert.longitude) if alert.longitude else "--"),
    ]))
    story.append(Spacer(1, 0.3 * cm))

    # ── Partenaire notifié ─────────────────────────────────────────────────────
    if alert.notified_partner:
        story.extend(_section_title("Transmission partenaire", section_s))
        story.append(_info_table([
            ("Partenaire", str(alert.notified_partner)),
            ("Notifié le", _fmt_dt(alert.notified_at)),
        ]))
        story.append(Spacer(1, 0.3 * cm))

    # ── Moyens engagés ────────────────────────────────────────────────────────
    engagements = list(alert.engagements.select_related("means", "engaged_by").all())
    if engagements:
        story.extend(_section_title(f"Moyens engagés ({len(engagements)})", section_s))
        headers = [["Moyen", "Rôle", "Engagé le", "Libéré le", "Rapport"]]
        rows = [[
            str(e.means),
            e.mission_role or "--",
            _fmt_dt(e.engaged_at),
            _fmt_dt(e.released_at),
            e.report or "--",
        ] for e in engagements]
        et = Table(headers + rows, colWidths=[3.5 * cm, 3 * cm, 3 * cm, 3 * cm, 5 * cm])
        et.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BLUE]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(et)
        story.append(Spacer(1, 0.3 * cm))

    # ── Historique des statuts ────────────────────────────────────────────────
    history = list(alert.history.select_related("user").all())
    if history:
        story.extend(_section_title(f"Historique des statuts ({len(history)})", section_s))
        headers = [["Date", "Ancien statut", "Nouveau statut", "Utilisateur", "Commentaire"]]
        rows = [[
            _fmt_dt(h.created_at),
            h.old_status or "--",
            h.new_status,
            str(h.user) if h.user else "--",
            h.comment or "--",
        ] for h in history]
        ht = Table(headers + rows, colWidths=[3.5 * cm, 3 * cm, 3 * cm, 3.5 * cm, 4.5 * cm])
        ht.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), NAVY),
            ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
            ("FONTSIZE", (0, 0), (-1, -1), 8),
            ("GRID", (0, 0), (-1, -1), 0.4, colors.HexColor("#BDC3C7")),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [WHITE, LIGHT_BLUE]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ]))
        story.append(ht)

    # ── Pied de page ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDC3C7")))
    story.append(Paragraph(
        f"<font size='8' color='grey'>Document généré automatiquement par le SGIM · "
        f"{_fmt_dt(timezone.now())}</font>",
        ParagraphStyle("footer", alignment=1),
    ))

    doc.build(story)
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# 2. PDF — Rapport journalier
# ─────────────────────────────────────────────────────────────────────────────

def build_daily_report_pdf(report) -> BytesIO:
    """Génère le PDF d'un rapport de fin de journée."""
    buf = BytesIO()
    doc = SimpleDocTemplate(
        buf, pagesize=A4,
        leftMargin=1.5 * cm, rightMargin=1.5 * cm,
        topMargin=1.5 * cm, bottomMargin=1.5 * cm,
    )
    _, _, section_s, body_s = _styles()
    story = []

    title = f"RAPPORT DE FIN DE JOURNÉE — {_fmt_date(report.report_date)}"
    story.append(_header_table(
        title,
        f"Généré le {_fmt_dt(timezone.now())}",
        report.team,
    ))
    story.append(Spacer(1, 0.5 * cm))

    # ── En-tête rapport ───────────────────────────────────────────────────────
    story.extend(_section_title("Informations du quart", section_s))
    story.append(_info_table([
        ("Centre", str(report.center)),
        ("Équipe / quart", report.team),
        ("Date du rapport", _fmt_date(report.report_date)),
        ("Rédigé par", str(report.created_by)),
        ("Créé le", _fmt_dt(report.created_at)),
    ]))
    story.append(Spacer(1, 0.3 * cm))

    # ── Statistiques ──────────────────────────────────────────────────────────
    story.extend(_section_title("Statistiques du quart", section_s))
    stats_data = [
        ["Alertes reçues", "Sauvetages", "Coordinations", "Appels reçus"],
        [
            str(report.alerts_count),
            str(report.rescues_count),
            str(report.coordinations_count),
            str(report.calls_received_count),
        ],
    ]
    st = Table(stats_data, colWidths=[4.375 * cm] * 4)
    st.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("TEXTCOLOR", (0, 0), (-1, 0), WHITE),
        ("FONTSIZE", (0, 0), (-1, -1), 11),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#BDC3C7")),
        ("BACKGROUND", (0, 1), (-1, 1), LIGHT_BLUE),
        ("FONTSIZE", (0, 1), (-1, 1), 16),
        ("FONTNAME", (0, 1), (-1, 1), "Helvetica-Bold"),
        ("TOPPADDING", (0, 0), (-1, -1), 8),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(st)
    story.append(Spacer(1, 0.3 * cm))

    # ── Synthèse ──────────────────────────────────────────────────────────────
    story.extend(_section_title("Synthèse des événements", section_s))
    story.append(Paragraph(report.summary or "--", body_s))
    story.append(Spacer(1, 0.3 * cm))

    # ── Validation ────────────────────────────────────────────────────────────
    story.extend(_section_title("Validation", section_s))
    valid_rows = [
        ("Validé", "Oui" if report.is_validated else "Non"),
    ]
    if report.is_validated:
        valid_rows += [
            ("Validé par", str(report.validated_by) if report.validated_by else "--"),
            ("Validé le", _fmt_dt(report.validated_at)),
            ("Email envoyé", "Oui" if report.email_sent else "Non"),
        ]
    story.append(_info_table(valid_rows))

    # ── Pied de page ──────────────────────────────────────────────────────────
    story.append(Spacer(1, 0.5 * cm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=colors.HexColor("#BDC3C7")))
    story.append(Paragraph(
        f"<font size='8' color='grey'>Document généré automatiquement par le SGIM · "
        f"{_fmt_dt(timezone.now())}</font>",
        ParagraphStyle("footer", alignment=1),
    ))

    doc.build(story)
    buf.seek(0)
    return buf


# ─────────────────────────────────────────────────────────────────────────────
# 3. Excel — Liste des alertes
# ─────────────────────────────────────────────────────────────────────────────

_ALERT_COLUMNS = [
    ("Numéro",             lambda a: a.number),
    ("Statut",             lambda a: a.get_status_display()),
    ("Centre",             lambda a: str(a.center)),
    ("Date / heure appel", lambda a: localtime(a.call_time).replace(tzinfo=None) if a.call_time else None),
    ("Canal",              lambda a: str(a.channel)),
    ("Type d'alerte",      lambda a: str(a.alert_type)),
    ("Priorité",           lambda a: str(a.priority) if a.priority else ""),
    ("Latitude",           lambda a: float(a.latitude) if a.latitude else None),
    ("Longitude",          lambda a: float(a.longitude) if a.longitude else None),
    ("Description",        lambda a: a.description),
    ("Opérateur",          lambda a: a.operator_signature),
    ("Partenaire notifié", lambda a: str(a.notified_partner) if a.notified_partner else ""),
    ("Notifié le",         lambda a: localtime(a.notified_at).replace(tzinfo=None) if a.notified_at else None),
    ("Créé par",           lambda a: str(a.created_by)),
    ("Créé le",            lambda a: localtime(a.created_at).replace(tzinfo=None) if a.created_at else None),
]


def build_alerts_excel(queryset) -> BytesIO:
    """
    Génère un fichier Excel (.xlsx) à partir d'un queryset d'alertes.
    Une feuille principale avec toutes les colonnes + mise en forme.
    """
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Alertes"

    # ── En-tête ───────────────────────────────────────────────────────────────
    headers = [col[0] for col in _ALERT_COLUMNS]
    ws.append(headers)
    for col_idx, _ in enumerate(headers, start=1):
        cell = ws.cell(row=1, column=col_idx)
        cell.font = HEADER_FONT
        cell.fill = HEADER_FILL
        cell.alignment = CENTER_ALIGN

    # ── Données ───────────────────────────────────────────────────────────────
    for row_idx, alert in enumerate(queryset, start=2):
        fill = ALT_FILL if row_idx % 2 == 0 else None
        for col_idx, (_, extractor) in enumerate(_ALERT_COLUMNS, start=1):
            cell = ws.cell(row=row_idx, column=col_idx, value=extractor(alert))
            cell.alignment = LEFT_ALIGN
            if fill:
                cell.fill = fill

    # ── Largeurs automatiques ─────────────────────────────────────────────────
    col_widths = [20, 14, 18, 20, 16, 22, 12, 12, 12, 40, 20, 22, 20, 22, 20]
    for i, width in enumerate(col_widths, start=1):
        ws.column_dimensions[openpyxl.utils.get_column_letter(i)].width = width

    # ── Figer la ligne d'en-tête ──────────────────────────────────────────────
    ws.freeze_panes = "A2"

    # ── Filtre automatique ────────────────────────────────────────────────────
    ws.auto_filter.ref = ws.dimensions

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)
    return buf
