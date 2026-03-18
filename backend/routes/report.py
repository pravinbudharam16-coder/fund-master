from flask import Blueprint, session, redirect, make_response, request, render_template
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.enums import TA_CENTER
from io import BytesIO
from datetime import datetime
from backend.database import db
from backend.models import Income, Expense, Asset
from sqlalchemy import func

report_bp = Blueprint("report", __name__)


def get_report_data(user_id, from_date, to_date):
    income_records = Income.query.filter(
        Income.user_id == user_id,
        Income.date >= from_date,
        Income.date <= to_date
    ).order_by(Income.date.desc()).all()

    expense_records = Expense.query.filter(
        Expense.user_id == user_id,
        Expense.date >= from_date,
        Expense.date <= to_date
    ).order_by(Expense.date.desc()).all()

    asset_records = Asset.query.filter_by(user_id=user_id).all()

    total_income  = sum(i.amount for i in income_records)
    total_expense = sum(e.amount for e in expense_records)
    total_balance = total_income - total_expense
    total_assets  = sum(a.value for a in asset_records)
    savings_rate  = round((total_balance / total_income * 100), 1) if total_income > 0 else 0

    category_totals = {}
    for e in expense_records:
        cat = e.category or "Other"
        category_totals[cat] = category_totals.get(cat, 0) + e.amount

    return {
        "total_income": total_income,
        "total_expense": total_expense,
        "total_balance": total_balance,
        "total_assets": total_assets,
        "savings_rate": savings_rate,
        "income_records": income_records,
        "expense_records": expense_records,
        "asset_records": asset_records,
        "category_totals": category_totals
    }


def generate_pdf(data, from_date, to_date):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=2*cm, leftMargin=2*cm,
        topMargin=2*cm, bottomMargin=2*cm
    )

    styles    = getSampleStyleSheet()
    DARK_BG   = colors.HexColor("#0b1f24")
    CYAN      = colors.HexColor("#00f2ff")
    GREEN     = colors.HexColor("#00ffa6")
    RED       = colors.HexColor("#ff5252")
    LIGHT_GRY = colors.HexColor("#f5f5f5")
    MID_GRY   = colors.HexColor("#dddddd")
    WHITE     = colors.white

    def style(name, **kw):
        return ParagraphStyle(name, parent=styles["Normal"], **kw)

    title_s    = style("T", fontSize=24, textColor=CYAN, alignment=TA_CENTER, spaceAfter=16)
    sub_s      = style("S", fontSize=11, textColor=colors.HexColor("#b0bec5"), alignment=TA_CENTER, spaceAfter=8)
    section_s  = style("H",  fontSize=13, textColor=CYAN, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6)
    footer_s   = style("F",  fontSize=8,  textColor=colors.HexColor("#999999"),   alignment=TA_CENTER)

    def tbl_style(header_color):
        return TableStyle([
            ("BACKGROUND",    (0,0),  (-1,0),  DARK_BG),
            ("TEXTCOLOR",     (0,0),  (-1,0),  header_color),
            ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),  (-1,-1), 10),
            ("ALIGN",         (0,0),  (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS",(0,1),  (-1,-1), [WHITE, LIGHT_GRY]),
            ("GRID",          (0,0),  (-1,-1), 0.5, MID_GRY),
            ("BOTTOMPADDING", (0,0),  (-1,-1), 7),
            ("TOPPADDING",    (0,0),  (-1,-1), 7),
        ])

    story = []

    # Header
    story.append(Paragraph("Fund Master", title_s))
    story.append(Paragraph("Financial Statement", sub_s))
    story.append(Paragraph(f"Period: {from_date} to {to_date}", sub_s))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%d %B %Y, %I:%M %p')}", sub_s))
    story.append(Spacer(1, 0.3*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=CYAN))
    story.append(Spacer(1, 0.4*cm))

    # Summary
    story.append(Paragraph("Summary", section_s))
    sum_data = [
        ["Total Income", "Total Expense", "Net Balance", "Savings Rate"],
        [
            f"Rs. {data['total_income']:,.2f}",
            f"Rs. {data['total_expense']:,.2f}",
            f"Rs. {data['total_balance']:,.2f}",
            f"{data['savings_rate']}%"
        ]
    ]
    sum_tbl = Table(sum_data, colWidths=[4.2*cm]*4)
    sum_tbl.setStyle(TableStyle([
        ("BACKGROUND",    (0,0), (-1,0), DARK_BG),
        ("TEXTCOLOR",     (0,0), (-1,0), CYAN),
        ("FONTNAME",      (0,0), (-1,0), "Helvetica-Bold"),
        ("FONTSIZE",      (0,0), (-1,-1), 11),
        ("ALIGN",         (0,0), (-1,-1), "CENTER"),
        ("BACKGROUND",    (0,1), (-1,1), LIGHT_GRY),
        ("FONTNAME",      (0,1), (-1,1), "Helvetica-Bold"),
        ("TEXTCOLOR",     (0,1), (0,1),  colors.HexColor("#00aa77")),
        ("TEXTCOLOR",     (1,1), (1,1),  RED),
        ("TEXTCOLOR",     (2,1), (2,1),  colors.HexColor("#0077cc")),
        ("GRID",          (0,0), (-1,-1), 0.5, MID_GRY),
        ("BOTTOMPADDING", (0,0), (-1,-1), 10),
        ("TOPPADDING",    (0,0), (-1,-1), 10),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 0.5*cm))

    # Expense by Category
    if data["category_totals"]:
        story.append(Paragraph("Expense by Category", section_s))
        rows = [["Category", "Amount (Rs.)", "% of Total"]]
        for cat, amt in sorted(data["category_totals"].items(), key=lambda x: -x[1]):
            pct = round(amt / data["total_expense"] * 100, 1) if data["total_expense"] > 0 else 0
            rows.append([cat, f"Rs. {amt:,.2f}", f"{pct}%"])
        tbl = Table(rows, colWidths=[6*cm, 6*cm, 5.6*cm])
        tbl.setStyle(tbl_style(CYAN))
        story.append(tbl)
        story.append(Spacer(1, 0.5*cm))

    # Income Records
    if data["income_records"]:
        story.append(Paragraph("Income Records", section_s))
        rows = [["Source", "Amount (Rs.)", "Date"]]
        for i in data["income_records"]:
            rows.append([i.source, f"Rs. {i.amount:,.2f}", i.date])
        tbl = Table(rows, colWidths=[6*cm, 6*cm, 5.6*cm])
        tbl.setStyle(tbl_style(GREEN))
        story.append(tbl)
        story.append(Spacer(1, 0.5*cm))

    # Expense Records
    if data["expense_records"]:
        story.append(Paragraph("Expense Records", section_s))
        rows = [["Title", "Category", "Amount (Rs.)", "Date"]]
        for e in data["expense_records"]:
            rows.append([e.title, e.category or "Other", f"Rs. {e.amount:,.2f}", e.date])
        tbl = Table(rows, colWidths=[4.5*cm, 4.5*cm, 4.5*cm, 4.1*cm])
        tbl.setStyle(tbl_style(RED))
        story.append(tbl)
        story.append(Spacer(1, 0.5*cm))

    # Assets
    if data["asset_records"]:
        story.append(Paragraph("Assets", section_s))
        rows = [["Asset Name", "Value (Rs.)"]]
        for a in data["asset_records"]:
            rows.append([a.name, f"Rs. {a.value:,.2f}"])
        rows.append(["Total", f"Rs. {data['total_assets']:,.2f}"])
        tbl = Table(rows, colWidths=[8.7*cm, 8.9*cm])
        tbl.setStyle(TableStyle([
            ("BACKGROUND",    (0,0),  (-1,0),  DARK_BG),
            ("TEXTCOLOR",     (0,0),  (-1,0),  CYAN),
            ("FONTNAME",      (0,0),  (-1,0),  "Helvetica-Bold"),
            ("FONTSIZE",      (0,0),  (-1,-1), 10),
            ("ALIGN",         (0,0),  (-1,-1), "CENTER"),
            ("ROWBACKGROUNDS",(0,1),  (-1,-2), [WHITE, LIGHT_GRY]),
            ("BACKGROUND",    (0,-1), (-1,-1), DARK_BG),
            ("TEXTCOLOR",     (0,-1), (-1,-1), GREEN),
            ("FONTNAME",      (0,-1), (-1,-1), "Helvetica-Bold"),
            ("GRID",          (0,0),  (-1,-1), 0.5, MID_GRY),
            ("BOTTOMPADDING", (0,0),  (-1,-1), 7),
            ("TOPPADDING",    (0,0),  (-1,-1), 7),
        ]))
        story.append(tbl)

    # Footer
    story.append(Spacer(1, 0.5*cm))
    story.append(HRFlowable(width="100%", thickness=1, color=MID_GRY))
    story.append(Spacer(1, 0.2*cm))
    story.append(Paragraph("Generated by Fund Master | Confidential Financial Statement", footer_s))

    doc.build(story)
    buffer.seek(0)
    return buffer


@report_bp.route("/export/pdf", methods=["GET", "POST"])
def export_pdf():
    if "user_id" not in session:
        return redirect("/login")

    if request.method == "POST":
        from_date = request.form.get("from_date")
        to_date   = request.form.get("to_date")

        if not from_date or not to_date:
            return render_template("export.html", error="Please select both dates.")

        if from_date > to_date:
            return render_template("export.html", error="From date cannot be after To date.")

        data   = get_report_data(session["user_id"], from_date, to_date)
        buffer = generate_pdf(data, from_date, to_date)

        filename = f"FundMaster_{from_date}_to_{to_date}.pdf"
        response = make_response(buffer.read())
        response.headers["Content-Type"]        = "application/pdf"
        response.headers["Content-Disposition"] = f"attachment; filename={filename}"
        return response

    return render_template("export.html", error=None)
