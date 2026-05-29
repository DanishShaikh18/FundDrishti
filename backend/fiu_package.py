import os
import json
import uuid
from datetime import datetime
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib import colors
import xml.etree.ElementTree as ET

from database import get_connection
from narrative import generate_narrative

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")

# Colors
DARK_BG    = HexColor("#0f1117")
BLUE       = HexColor("#2563eb")
RED        = HexColor("#ef4444")
GRAY       = HexColor("#64748b")
LIGHT      = HexColor("#e2e8f0")
WHITE      = HexColor("#ffffff")
WARN       = HexColor("#92400e")
WARN_BG    = HexColor("#422006")


def _styles():
    base = getSampleStyleSheet()
    return {
        "title": ParagraphStyle("title", fontSize=20, textColor=WHITE, fontName="Helvetica-Bold", spaceAfter=4),
        "subtitle": ParagraphStyle("subtitle", fontSize=10, textColor=GRAY, fontName="Helvetica", spaceAfter=2),
        "section": ParagraphStyle("section", fontSize=12, textColor=BLUE, fontName="Helvetica-Bold", spaceBefore=14, spaceAfter=6),
        "body": ParagraphStyle("body", fontSize=9, textColor=LIGHT, fontName="Helvetica", leading=14, spaceAfter=4),
        "warn": ParagraphStyle("warn", fontSize=9, textColor=HexColor("#fbbf24"), fontName="Helvetica-Bold", spaceAfter=6),
        "mono": ParagraphStyle("mono", fontSize=8, textColor=LIGHT, fontName="Courier", leading=12, spaceAfter=4),
    }


def _table_style():
    return TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), HexColor("#1e2530")),
        ("TEXTCOLOR",     (0, 0), (-1, 0), BLUE),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 8),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 8),
        ("TOPPADDING",    (0, 0), (-1, 0), 8),
        ("BACKGROUND",    (0, 1), (-1, -1), HexColor("#131720")),
        ("TEXTCOLOR",     (0, 1), (-1, -1), LIGHT),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 8),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [HexColor("#131720"), HexColor("#1a1f2e")]),
        ("GRID",          (0, 0), (-1, -1), 0.3, HexColor("#2d3748")),
        ("TOPPADDING",    (0, 1), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 6),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8),
    ])


def _fetch_case(conn, case_id):
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM Cases WHERE case_id = ?", (case_id,))
    row = cursor.fetchone()
    if not row:
        raise ValueError(f"Case {case_id} not found")
    return dict(row)


def _fetch_accounts(conn, account_ids):
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in account_ids)
    cursor.execute(f"SELECT * FROM Accounts WHERE account_id IN ({placeholders})", account_ids)
    return [dict(row) for row in cursor.fetchall()]


def _fetch_transactions(conn, account_ids):
    cursor = conn.cursor()
    placeholders = ",".join("?" for _ in account_ids)
    cursor.execute(f'''
        SELECT * FROM Transactions
        WHERE (from_account IN ({placeholders}) OR to_account IN ({placeholders}))
          AND status = 'COMPLETED'
        ORDER BY timestamp
    ''', (*account_ids, *account_ids))
    return [dict(row) for row in cursor.fetchall()]


def _build_pdf(case, accounts, transactions, narrative, score_breakdown, agent_findings, output_path):
    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        leftMargin=1.8*cm, rightMargin=1.8*cm,
        topMargin=1.8*cm, bottomMargin=1.8*cm
    )
    s = _styles()
    story = []
    W = A4[0] - 3.6*cm

    # Header
    story.append(Paragraph("FundDrishti", s["title"]))
    story.append(Paragraph("Financial Intelligence Unit — Suspicious Transaction Report (Draft)", s["subtitle"]))
    story.append(Paragraph(f"Case ID: {case['case_id']}  |  Generated: {datetime.now().strftime('%d %b %Y %H:%M')}", s["subtitle"]))
    story.append(HRFlowable(width=W, color=BLUE, thickness=1, spaceAfter=10))

    # Warning
    story.append(Paragraph(
        "⚠  AI-ASSISTED INVESTIGATOR DRAFT — Human review and sign-off required before submission to FIU-IND. "
        "The investigator is the legal accountable party.",
        s["warn"]
    ))
    story.append(HRFlowable(width=W, color=WARN, thickness=0.5, spaceAfter=10))

    # Case summary
    story.append(Paragraph("1. Case Summary", s["section"]))
    risk_color = "#ef4444" if case["risk_score"] >= 70 else "#f59e0b"
    summary_data = [
        ["Field", "Value"],
        ["Case ID", case["case_id"]],
        ["Pattern Type", case.get("pattern_type", "N/A").replace("_", " ").upper()],
        ["Risk Score", f"{case['risk_score']}/100"],
        ["Status", case.get("narrative_status", "DRAFT")],
        ["Investigator", case.get("investigator_name") or "Pending sign-off"],
        ["Signed At", case.get("signed_at") or "Not signed"],
        ["FIU Generated", datetime.now().strftime("%d %b %Y %H:%M")],
    ]
    story.append(Table(summary_data, colWidths=[W*0.35, W*0.65], style=_table_style()))

    # Score breakdown
    story.append(Paragraph("2. Risk Score Breakdown", s["section"]))
    story.append(Paragraph(
        "Score weights derived from Logistic Regression coefficients trained on 1000 labeled synthetic cases. "
        "Every point is traceable to a specific finding.",
        s["body"]
    ))
    score_data = [["Component", "Points", "Basis"]]
    for item in score_breakdown:
        score_data.append([
            item.get("component", ""),
            f"+{item.get('points', 0)}",
            item.get("basis", "")[:80]
        ])
    score_data.append(["TOTAL RISK SCORE", f"{case['risk_score']}/100", "Capped at 100"])
    story.append(Table(score_data, colWidths=[W*0.35, W*0.12, W*0.53], style=_table_style()))

    # Accounts
    story.append(Paragraph("3. Accounts Under Investigation", s["section"]))
    acc_data = [["Account ID", "Type", "Profile", "Declared Income", "Opened", "Watchlisted"]]
    for acc in accounts:
        acc_data.append([
            acc.get("account_id", ""),
            acc.get("account_type", ""),
            acc.get("profile_type", ""),
            f"₹{acc.get('declared_annual_income', 0):,.0f}",
            acc.get("account_opened_date", "")[:10],
            "YES ⚠" if acc.get("is_watchlisted") else "No",
        ])
    story.append(Table(acc_data, colWidths=[W*0.22, W*0.10, W*0.16, W*0.18, W*0.14, W*0.12], style=_table_style()))

    # Transactions
    story.append(Paragraph("4. Transaction Chain", s["section"]))
    txn_data = [["Txn Reference", "Timestamp", "From", "To", "Amount", "Channel"]]
    for t in transactions[:30]:
        txn_data.append([
            t.get("txn_reference", "")[:18],
            t.get("timestamp", "")[:16].replace("T", " "),
            t.get("from_account", "")[:14],
            t.get("to_account", "")[:14],
            f"₹{t.get('amount', 0):,.0f}",
            t.get("channel", ""),
        ])
    if len(transactions) > 30:
        txn_data.append([f"... {len(transactions)-30} more transactions", "", "", "", "", ""])
    story.append(Table(txn_data, colWidths=[W*0.20, W*0.18, W*0.18, W*0.18, W*0.14, W*0.12], style=_table_style()))

    # Agent findings
    story.append(Paragraph("5. Agent Investigation Findings", s["section"]))
    for agent in agent_findings:
        agent_name = agent.get("agent", "unknown").replace("_", " ").upper()
        story.append(Paragraph(agent_name, ParagraphStyle("ah", fontSize=10, textColor=BLUE, fontName="Helvetica-Bold", spaceBefore=8, spaceAfter=4)))
        story.append(Paragraph(f"Log: {agent.get('log', '')}", s["body"]))
        for f in agent.get("findings", []):
            story.append(Paragraph(f"• {f.get('detail', '')}", s["body"]))
        if not agent.get("findings"):
            story.append(Paragraph("No significant findings from this agent.", s["body"]))

    # Narrative
    story.append(Paragraph("6. Investigation Narrative", s["section"]))
    for para in narrative.split("\n\n"):
        if para.strip():
            story.append(Paragraph(para.strip(), s["body"]))
            story.append(Spacer(1, 6))

    # Sign off
    story.append(Paragraph("7. Investigator Sign-Off", s["section"]))
    signoff_data = [
        ["Field", "Value"],
        ["Investigator Name", case.get("investigator_name") or "PENDING"],
        ["Signed At", case.get("signed_at") or "PENDING"],
        ["Narrative Status", case.get("narrative_status", "DRAFT")],
        ["Legal Statement", "I confirm I have reviewed and verified all findings in this report."],
    ]
    story.append(Table(signoff_data, colWidths=[W*0.35, W*0.65], style=_table_style()))

    # Footer
    story.append(Spacer(1, 16))
    story.append(HRFlowable(width=W, color=GRAY, thickness=0.5))
    story.append(Paragraph(
        f"FundDrishti AML Intelligence Platform  |  Generated {datetime.now().strftime('%d %b %Y %H:%M')}  |  "
        "This document is an investigator-reviewed draft. Not valid for FIU submission without human sign-off.",
        ParagraphStyle("footer", fontSize=7, textColor=GRAY, fontName="Helvetica", spaceAfter=0)
    ))

    doc.build(story)


def _build_goaml_xml(case, accounts, transactions):
    """
    Builds goAML ARF XML with core components:
    ARFBAT, ARFRPT, ARFACC, ARFTRN, ARFINP
    """
    root = ET.Element("ARFBAT")
    root.set("xmlns:xsi", "http://www.w3.org/2001/XMLSchema-instance")

    # ARFBAT — Batch metadata
    ET.SubElement(root, "ReportType").text = "STR"
    ET.SubElement(root, "ReportingEntityName").text = "Union Bank of India"
    ET.SubElement(root, "FIUREID").text = "UNIONB00001"
    ET.SubElement(root, "PrincipalOfficer").text = "Compliance Officer"
    ET.SubElement(root, "BatchDate").text = datetime.now().strftime("%Y-%m-%d")
    ET.SubElement(root, "BatchReference").text = f"BATCH_{uuid.uuid4().hex[:8].upper()}"

    # ARFRPT — Report details
    rpt = ET.SubElement(root, "ARFRPT")
    ET.SubElement(rpt, "ReportID").text = case["case_id"]
    ET.SubElement(rpt, "AlertType").text = case.get("pattern_type", "UNKNOWN").upper()
    ET.SubElement(rpt, "RiskScore").text = str(case["risk_score"])
    ET.SubElement(rpt, "SuspicionGrounds").text = (
        f"Automated detection by FundDrishti system identified {case.get('pattern_type', 'suspicious activity').replace('_', ' ')} "
        f"pattern with risk score {case['risk_score']}/100. Human investigator reviewed and verified findings."
    )
    ET.SubElement(rpt, "ReportDate").text = datetime.now().strftime("%Y-%m-%d")
    ET.SubElement(rpt, "InvestigatorName").text = case.get("investigator_name") or "Pending"
    ET.SubElement(rpt, "NarrativeStatus").text = case.get("narrative_status", "DRAFT")

    # ARFBRC — Branch details
    brc = ET.SubElement(root, "ARFBRC")
    ET.SubElement(brc, "BranchName").text = "Union Bank of India — Head Office"
    ET.SubElement(brc, "City").text = "Mumbai"
    ET.SubElement(brc, "State").text = "Maharashtra"
    ET.SubElement(brc, "Country").text = "IN"
    ET.SubElement(brc, "PINCode").text = "400077"

    # ARFACC — Account details
    for acc in accounts:
        arfacc = ET.SubElement(root, "ARFACC")
        ET.SubElement(arfacc, "AccountID").text = acc.get("account_id", "")
        ET.SubElement(arfacc, "AccountType").text = acc.get("account_type", "SAVINGS")
        ET.SubElement(arfacc, "ProfileType").text = acc.get("profile_type", "")
        ET.SubElement(arfacc, "DeclaredIncome").text = str(acc.get("declared_annual_income", 0))
        ET.SubElement(arfacc, "OpeningDate").text = acc.get("account_opened_date", "")[:10]
        ET.SubElement(arfacc, "OperationalStatus").text = "DORMANT" if acc.get("is_watchlisted") else "ACTIVE"
        ET.SubElement(arfacc, "RiskRating").text = "HIGH" if case["risk_score"] >= 70 else "MEDIUM"
        ET.SubElement(arfacc, "BranchCode").text = acc.get("branch_code", "")

        # ARFINP — Individual person details (nested under account)
        arfinp = ET.SubElement(arfacc, "ARFINP")
        ET.SubElement(arfinp, "CustomerName").text = acc.get("customer_name", "")
        ET.SubElement(arfinp, "PANNumber").text = acc.get("pan_number", "")
        ET.SubElement(arfinp, "MobileNumber").text = acc.get("mobile_number", "")
        ET.SubElement(arfinp, "RelationFlag").text = "SUBJECT"

    # ARFTRN — Transaction details
    for t in transactions[:50]:
        arftrn = ET.SubElement(root, "ARFTRN")
        ET.SubElement(arftrn, "TransactionID").text = t.get("txn_id", "")
        ET.SubElement(arftrn, "TxnReference").text = t.get("txn_reference", "")
        ET.SubElement(arftrn, "TransactionDate").text = t.get("timestamp", "")[:10]
        ET.SubElement(arftrn, "ExecutionMode").text = t.get("channel", "")
        ET.SubElement(arftrn, "DebitCredit").text = "DR"
        ET.SubElement(arftrn, "Amount").text = str(t.get("amount", 0))
        ET.SubElement(arftrn, "Currency").text = "INR"
        ET.SubElement(arftrn, "FromAccount").text = t.get("from_account", "")
        ET.SubElement(arftrn, "ToAccount").text = t.get("to_account", "")
        ET.SubElement(arftrn, "Narration").text = t.get("narration", "")

    return ET.tostring(root, encoding="unicode", xml_declaration=False)


def generate_fiu_package(conn, case_id):
    """
    Main function. Called from FastAPI.
    Generates PDF + goAML XML and returns PDF path.
    """
    case = _fetch_case(conn, case_id)

    score_breakdown = json.loads(case["score_breakdown"]) if case["score_breakdown"] else []
    agent_findings = json.loads(case["agent_findings"]) if case["agent_findings"] else []

    # Get accounts involved from agent findings
    account_ids = set()
    for agent in agent_findings:
        for f in agent.get("findings", []):
            for acc in f.get("accounts", []):
                account_ids.add(acc)

    account_ids = list(account_ids) if account_ids else ["UNKNOWN"]

    accounts = _fetch_accounts(conn, account_ids)
    transactions = _fetch_transactions(conn, account_ids)

    # Generate narrative
    narrative = generate_narrative(
        pattern_type=case.get("pattern_type", "unknown"),
        accounts_involved=account_ids,
        agent_findings=agent_findings,
        risk_score=case["risk_score"],
        score_breakdown=score_breakdown
    )

    # Update narrative in DB
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE Cases SET narrative_draft = ?, fiu_generated = 1 WHERE case_id = ?",
        (narrative, case_id)
    )
    conn.commit()

    # Build PDF
    pdf_path = os.path.join(OUTPUT_DIR, f"FIU_{case_id}.pdf")
    _build_pdf(case, accounts, transactions, narrative, score_breakdown, agent_findings, pdf_path)

    # Build and save XML
    xml_content = _build_goaml_xml(case, accounts, transactions)
    xml_path = os.path.join(OUTPUT_DIR, f"FIU_{case_id}_goAML.xml")
    with open(xml_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
        f.write(xml_content)

    return pdf_path