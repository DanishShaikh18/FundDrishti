import os
import xml.etree.ElementTree as ET
from xml.dom import minidom
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors

def generate_fiu_pdf(case_id, case_data, output_path):
    """
    Generates a structured, professional compliance PDF report for FIU submission.
    """
    # Create directory if not exists
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    doc = SimpleDocTemplate(output_path, pagesize=letter,
                            rightMargin=40, leftMargin=40, topMargin=40, bottomMargin=40)
    story = []
    styles = getSampleStyleSheet()
    
    # Custom Styles
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=20,
        leading=24,
        textColor=colors.HexColor('#0f172a'),
        alignment=1, # Centered
        spaceAfter=15
    )
    
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor('#1e3a8a'),
        spaceBefore=10,
        spaceAfter=6,
        keepWithNext=True
    )
    
    body_style = ParagraphStyle(
        'BodyStyle',
        parent=styles['BodyText'],
        fontName='Helvetica',
        fontSize=9,
        leading=12,
        textColor=colors.HexColor('#334155'),
        spaceAfter=8
    )
    
    table_header_style = ParagraphStyle(
        'TableHeader',
        parent=body_style,
        fontName='Helvetica-Bold',
        textColor=colors.white
    )
    
    # 1. Header Title
    story.append(Paragraph("FINANCIAL INTELLIGENCE UNIT (FIU-IND)", title_style))
    story.append(Paragraph("SUSPICIOUS TRANSACTION REPORT (STR)", title_style))
    story.append(Spacer(1, 10))
    
    # 2. Case Summary Table
    meta_data = [
        [Paragraph("<b>Case Reference ID:</b>", body_style), Paragraph(case_id, body_style),
         Paragraph("<b>Pattern Category:</b>", body_style), Paragraph(case_data['pattern_type'], body_style)],
        [Paragraph("<b>Risk Score:</b>", body_style), Paragraph(f"{case_data['score']}/100", body_style),
         Paragraph("<b>Case Status:</b>", body_style), Paragraph("Closed (FIU Generated)", body_style)],
        [Paragraph("<b>Investigator Signature:</b>", body_style), Paragraph(case_data.get('investigator_name', 'N/A'), body_style),
         Paragraph("<b>Signature Timestamp:</b>", body_style), Paragraph(case_data.get('signed_at', 'N/A'), body_style)]
    ]
    t_meta = Table(meta_data, colWidths=[120, 140, 120, 140])
    t_meta.setStyle(TableStyle([
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0,0), (0,-1), colors.HexColor('#f8fafc')),
        ('BACKGROUND', (2,0), (2,-1), colors.HexColor('#f8fafc')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_meta)
    story.append(Spacer(1, 15))
    
    # 3. AI Narratives Draft
    story.append(Paragraph("I. AI Narrative & Investigator Findings Summary", section_heading))
    story.append(Paragraph(case_data.get('summary', ''), body_style))
    story.append(Spacer(1, 10))
    
    # 4. Involved Accounts Table
    story.append(Paragraph("II. Involved Accounts Directory", section_heading))
    acc_headers = ["Account ID", "Customer Name", "Profile Group", "Investigation Role", "Txn Volume"]
    acc_rows = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in acc_headers]]
    for acc in case_data.get('accounts', []):
        acc_rows.append([
            Paragraph(acc['id'], body_style),
            Paragraph(acc['name'], body_style),
            Paragraph(acc['profile_type'], body_style),
            Paragraph(acc['role'], body_style),
            Paragraph(str(acc['transactions_count']), body_style)
        ])
    t_acc = Table(acc_rows, colWidths=[100, 110, 100, 110, 100])
    t_acc.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    story.append(t_acc)
    story.append(Spacer(1, 15))
    
    # 5. Transaction Subgraph Timeline
    story.append(Paragraph("III. Chronological Suspicious Transactions Subgraph Timeline", section_heading))
    tx_headers = ["Timestamp", "From Account", "To Account", "Amount", "Channel"]
    tx_rows = [[Paragraph(f"<b>{h}</b>", table_header_style) for h in tx_headers]]
    
    edges = case_data.get('transaction_subgraph', {}).get('edges', [])
    sorted_edges = sorted(edges, key=lambda x: x.get('timestamp', ''))
    
    for tx in sorted_edges:
        tx_rows.append([
            Paragraph(tx['timestamp'][:19].replace('T', ' '), body_style),
            Paragraph(tx['source'], body_style),
            Paragraph(tx['target'], body_style),
            Paragraph(f"${tx['amount']:,.2f}", body_style),
            Paragraph(tx.get('channel', 'TRANSFER'), body_style)
        ])
    t_tx = Table(tx_rows, colWidths=[110, 100, 100, 110, 100])
    t_tx.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#1e3a8a')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#cbd5e1')),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f8fafc')]),
        ('TOPPADDING', (0,0), (-1,-1), 4),
        ('BOTTOMPADDING', (0,0), (-1,-1), 4),
    ]))
    story.append(t_tx)
    
    # Build PDF doc
    doc.build(story)

def generate_fiu_xml(case_id, case_data, output_path):
    """
    Generates a structured XML file matching the official goAML STR regulatory schema.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    root = ET.Element("report")
    
    # Header Elements
    ET.SubElement(root, "report_type").text = "STR"
    ET.SubElement(root, "reporting_entity").text = "Union Bank of India"
    ET.SubElement(root, "case_id").text = case_id
    ET.SubElement(root, "risk_score").text = str(case_data['score'])
    ET.SubElement(root, "investigator_name").text = case_data.get('investigator_name', '')
    ET.SubElement(root, "signed_at").text = case_data.get('signed_at', '')
    ET.SubElement(root, "reason").text = case_data.get('summary', '')
    
    # Accounts involved list
    accounts_el = ET.SubElement(root, "involved_accounts")
    for acc in case_data.get('accounts', []):
        acc_el = ET.SubElement(accounts_el, "account")
        ET.SubElement(acc_el, "account_id").text = acc['id']
        ET.SubElement(acc_el, "owner_name").text = acc['name']
        ET.SubElement(acc_el, "profile_group").text = acc['profile_type']
        ET.SubElement(acc_el, "role").text = acc['role']
        ET.SubElement(acc_el, "transaction_count").text = str(acc['transactions_count'])
        
    # Transaction timeline list
    txns_el = ET.SubElement(root, "flagged_transactions")
    edges = case_data.get('transaction_subgraph', {}).get('edges', [])
    for tx in edges:
        tx_el = ET.SubElement(txns_el, "transaction")
        ET.SubElement(tx_el, "timestamp").text = tx['timestamp']
        ET.SubElement(tx_el, "from_account").text = tx['source']
        ET.SubElement(tx_el, "to_account").text = tx['target']
        ET.SubElement(tx_el, "amount").text = str(tx['amount'])
        ET.SubElement(tx_el, "channel").text = tx.get('channel', 'TRANSFER')
        ET.SubElement(tx_el, "narration").text = tx.get('narration', '')
        
    # Pretty print XML
    xml_str = ET.tostring(root, encoding='utf-8')
    parsed_xml = minidom.parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(pretty_xml)
