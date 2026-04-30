"""
invoice_utils.py  —  NextZen IT Solutions
Place this file inside your `website/` app folder.

Requires:  pip install reportlab
"""

import os
from io import BytesIO
from decimal import Decimal

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.mail import EmailMessage
from django.utils import timezone

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
)
from reportlab.lib.enums import TA_LEFT, TA_RIGHT, TA_CENTER


# ── Colours ────────────────────────────────────────────────────────────
BRAND_COLOR   = colors.HexColor('#1e40af')   # Deep blue
ACCENT_COLOR  = colors.HexColor('#3b82f6')   # Lighter blue
TEXT_DARK     = colors.HexColor('#1f2937')
TEXT_GRAY     = colors.HexColor('#6b7280')
BG_LIGHT      = colors.HexColor('#f8fafc')
SUCCESS_GREEN = colors.HexColor('#10b981')
RED_COLOR     = colors.HexColor('#ef4444')
BORDER_COLOR  = colors.HexColor('#e5e7eb')


def _build_styles():
    """Return a dict of named ParagraphStyles."""
    base = getSampleStyleSheet()
    return {
        'company_name': ParagraphStyle(
            'company_name', fontSize=22, fontName='Helvetica-Bold',
            textColor=BRAND_COLOR, spaceAfter=2,
        ),
        'company_sub': ParagraphStyle(
            'company_sub', fontSize=8, fontName='Helvetica',
            textColor=TEXT_GRAY, spaceAfter=2, leading=12,
        ),
        'invoice_title': ParagraphStyle(
            'invoice_title', fontSize=28, fontName='Helvetica-Bold',
            textColor=TEXT_DARK, alignment=TA_RIGHT,
        ),
        'invoice_meta': ParagraphStyle(
            'invoice_meta', fontSize=9, fontName='Helvetica',
            textColor=TEXT_GRAY, alignment=TA_RIGHT, leading=14,
        ),
        'invoice_meta_val': ParagraphStyle(
            'invoice_meta_val', fontSize=9, fontName='Helvetica-Bold',
            textColor=TEXT_DARK, alignment=TA_RIGHT, leading=14,
        ),
        'section_label': ParagraphStyle(
            'section_label', fontSize=8, fontName='Helvetica-Bold',
            textColor=ACCENT_COLOR, spaceBefore=4, spaceAfter=2,
            textTransform='uppercase',
        ),
        'address_name': ParagraphStyle(
            'address_name', fontSize=10, fontName='Helvetica-Bold',
            textColor=TEXT_DARK, spaceAfter=2,
        ),
        'address_detail': ParagraphStyle(
            'address_detail', fontSize=8.5, fontName='Helvetica',
            textColor=TEXT_GRAY, leading=13,
        ),
        'table_header': ParagraphStyle(
            'table_header', fontSize=9, fontName='Helvetica-Bold',
            textColor=colors.white,
        ),
        'table_cell': ParagraphStyle(
            'table_cell', fontSize=9, fontName='Helvetica',
            textColor=TEXT_DARK,
        ),
        'table_cell_right': ParagraphStyle(
            'table_cell_right', fontSize=9, fontName='Helvetica',
            textColor=TEXT_DARK, alignment=TA_RIGHT,
        ),
        'totals_label': ParagraphStyle(
            'totals_label', fontSize=9, fontName='Helvetica',
            textColor=TEXT_GRAY, alignment=TA_RIGHT,
        ),
        'totals_value': ParagraphStyle(
            'totals_value', fontSize=9, fontName='Helvetica',
            textColor=TEXT_DARK, alignment=TA_RIGHT,
        ),
        'grand_total_label': ParagraphStyle(
            'grand_total_label', fontSize=12, fontName='Helvetica-Bold',
            textColor=colors.white, alignment=TA_RIGHT,
        ),
        'grand_total_value': ParagraphStyle(
            'grand_total_value', fontSize=12, fontName='Helvetica-Bold',
            textColor=colors.white, alignment=TA_RIGHT,
        ),
        'notes_label': ParagraphStyle(
            'notes_label', fontSize=8, fontName='Helvetica-Bold',
            textColor=ACCENT_COLOR, spaceAfter=3, textTransform='uppercase',
        ),
        'notes_text': ParagraphStyle(
            'notes_text', fontSize=8.5, fontName='Helvetica',
            textColor=TEXT_GRAY, leading=13,
        ),
        'footer': ParagraphStyle(
            'footer', fontSize=8, fontName='Helvetica',
            textColor=TEXT_GRAY, alignment=TA_CENTER,
        ),
        'status_paid': ParagraphStyle(
            'status_paid', fontSize=30, fontName='Helvetica-Bold',
            textColor=colors.HexColor('#10b981'), alignment=TA_CENTER,
        ),
    }


def _inr(amount):
    """Format a Decimal as  ₹ 1,23,456.00"""
    try:
        val = float(amount)
        # Indian number format
        s   = f'{val:,.2f}'
        return f'₹ {s}'
    except Exception:
        return f'₹ {amount}'


def generate_invoice_pdf(invoice) -> None:
    """
    Generate a professional PDF invoice using ReportLab.
    Saves the file to invoice.pdf_file and marks invoice.sent_at if needed.
    """
    from .models import Invoice   # local import to avoid circular

    styles = _build_styles()
    buffer = BytesIO()
    W, H   = A4
    margin = 18 * mm

    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=margin, leftMargin=margin,
        topMargin=margin,   bottomMargin=margin,
        title=f'Invoice {invoice.invoice_number}',
        author=invoice.from_name,
    )

    story = []

    # ── HEADER ────────────────────────────────────────────────────
    header_left = [
        [Paragraph(invoice.from_name, styles['company_name'])],
        [Paragraph(invoice.from_address.replace('\n', '<br/>') if invoice.from_address else '', styles['company_sub'])],
        [Paragraph(invoice.from_email, styles['company_sub'])],
        [Paragraph(f'GSTIN: {invoice.from_gstin}' if invoice.from_gstin else '', styles['company_sub'])],
    ]
    header_right = [
        [Paragraph('INVOICE', styles['invoice_title'])],
        [Paragraph(f'# {invoice.invoice_number}', styles['invoice_meta_val'])],
        [Paragraph(f'Issue Date: {invoice.issue_date.strftime("%d %b %Y")}', styles['invoice_meta'])],
        [Paragraph(f'Due Date: {invoice.due_date.strftime("%d %b %Y") if invoice.due_date else "On Receipt"}', styles['invoice_meta'])],
    ]

    header_table = Table(
        [[
            Table(header_left, colWidths=[85 * mm]),
            Table(header_right, colWidths=[85 * mm]),
        ]],
        colWidths=[90 * mm, 85 * mm],
    )
    header_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(header_table)
    story.append(HRFlowable(width='100%', thickness=0.5, color=BORDER_COLOR, spaceAfter=6))
    story.append(Spacer(1, 4 * mm))

    # ── BILL TO / FROM ────────────────────────────────────────────
    bill_to = [
        [Paragraph('BILL TO', styles['section_label'])],
        [Paragraph(invoice.client_name, styles['address_name'])],
    ]
    if invoice.client_company:
        bill_to.append([Paragraph(invoice.client_company, styles['address_detail'])])
    if invoice.client_address:
        for line in invoice.client_address.splitlines():
            bill_to.append([Paragraph(line, styles['address_detail'])])
    if invoice.client_email:
        bill_to.append([Paragraph(invoice.client_email, styles['address_detail'])])
    if invoice.client_phone:
        bill_to.append([Paragraph(invoice.client_phone, styles['address_detail'])])
    if invoice.client_gstin:
        bill_to.append([Paragraph(f'GSTIN: {invoice.client_gstin}', styles['address_detail'])])

    # Status stamp
    status_display = invoice.get_status_display().replace('✅ ', '').replace('⚠️ ', '').upper()
    status_color   = SUCCESS_GREEN if invoice.status == 'paid' else (RED_COLOR if invoice.status == 'overdue' else ACCENT_COLOR)

    bill_right = [
        [Paragraph('PAYMENT STATUS', styles['section_label'])],
        [Paragraph(status_display, ParagraphStyle(
            'st', fontSize=22, fontName='Helvetica-Bold',
            textColor=status_color, alignment=TA_RIGHT,
        ))],
    ]

    billing_table = Table(
        [[
            Table(bill_to, colWidths=[90 * mm]),
            Table(bill_right, colWidths=[85 * mm]),
        ]],
        colWidths=[90 * mm, 85 * mm],
    )
    billing_table.setStyle(TableStyle([
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(billing_table)
    story.append(Spacer(1, 6 * mm))

    # ── LINE ITEMS TABLE ──────────────────────────────────────────
    item_data = [[
        Paragraph('#',           styles['table_header']),
        Paragraph('Description', styles['table_header']),
        Paragraph('Qty',         styles['table_header']),
        Paragraph('Unit Price',  styles['table_header']),
        Paragraph('Total',       styles['table_header']),
    ]]

    items = list(invoice.items.all())
    for idx, item in enumerate(items, 1):
        item_data.append([
            Paragraph(str(idx),                       styles['table_cell']),
            Paragraph(item.description,               styles['table_cell']),
            Paragraph(str(item.quantity),             styles['table_cell_right']),
            Paragraph(_inr(item.unit_price),          styles['table_cell_right']),
            Paragraph(_inr(item.total),               styles['table_cell_right']),
        ])

    col_widths = [10 * mm, 85 * mm, 20 * mm, 30 * mm, 30 * mm]
    items_table = Table(item_data, colWidths=col_widths, repeatRows=1)
    items_table.setStyle(TableStyle([
        # Header row
        ('BACKGROUND',    (0, 0), (-1, 0), BRAND_COLOR),
        ('TEXTCOLOR',     (0, 0), (-1, 0), colors.white),
        ('FONTNAME',      (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE',      (0, 0), (-1, 0), 9),
        ('ROWBACKGROUNDS',(0, 1), (-1, -1), [colors.white, BG_LIGHT]),
        ('ALIGN',         (2, 0), (-1, -1), 'RIGHT'),
        ('VALIGN',        (0, 0), (-1, -1), 'MIDDLE'),
        ('TOPPADDING',    (0, 0), (-1, -1), 6),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LEFTPADDING',   (0, 0), (-1, -1), 6),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 6),
        ('GRID',          (0, 0), (-1, -1), 0.4, BORDER_COLOR),
        ('ROUNDEDCORNERS', [4]),
    ]))
    story.append(items_table)
    story.append(Spacer(1, 4 * mm))

    # ── TOTALS BLOCK ──────────────────────────────────────────────
    totals_data = [
        ['', Paragraph('Subtotal',   styles['totals_label']), Paragraph(_inr(invoice.subtotal),    styles['totals_value'])],
        ['', Paragraph(f'GST ({invoice.tax_percent}%)', styles['totals_label']), Paragraph(_inr(invoice.tax_amount), styles['totals_value'])],
    ]
    if invoice.discount and invoice.discount > 0:
        totals_data.append([
            '', Paragraph('Discount', styles['totals_label']),
            Paragraph(f'- {_inr(invoice.discount)}', ParagraphStyle('disc', fontSize=9, textColor=RED_COLOR, alignment=TA_RIGHT)),
        ])

    totals_table = Table(totals_data, colWidths=[85 * mm, 60 * mm, 30 * mm])
    totals_table.setStyle(TableStyle([
        ('ALIGN',        (1, 0), (-1, -1), 'RIGHT'),
        ('TOPPADDING',   (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING',(0, 0), (-1, -1), 3),
        ('LEFTPADDING',  (0, 0), (-1, -1), 0),
        ('RIGHTPADDING', (0, 0), (-1, -1), 0),
    ]))
    story.append(totals_table)

    # Grand total row
    grand_total_table = Table(
        [[
            Paragraph('', styles['totals_label']),
            Paragraph('TOTAL AMOUNT DUE', styles['grand_total_label']),
            Paragraph(_inr(invoice.total_amount), styles['grand_total_value']),
        ]],
        colWidths=[85 * mm, 60 * mm, 30 * mm],
    )
    grand_total_table.setStyle(TableStyle([
        ('BACKGROUND',    (1, 0), (-1, 0), BRAND_COLOR),
        ('ROUNDEDCORNERS', [4]),
        ('TOPPADDING',    (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING',   (0, 0), (-1, -1), 8),
        ('RIGHTPADDING',  (0, 0), (-1, -1), 8),
    ]))
    story.append(grand_total_table)
    story.append(Spacer(1, 6 * mm))

    # ── NOTES & TERMS ─────────────────────────────────────────────
    if invoice.notes or invoice.terms:
        notes_rows = []
        if invoice.notes:
            notes_rows.append([Paragraph('Notes', styles['notes_label'])])
            for line in invoice.notes.splitlines():
                notes_rows.append([Paragraph(line, styles['notes_text'])])
        if invoice.terms:
            notes_rows.append([Paragraph('Terms & Conditions', styles['notes_label'])])
            for line in invoice.terms.splitlines():
                notes_rows.append([Paragraph(line, styles['notes_text'])])
        notes_table = Table(notes_rows, colWidths=[175 * mm])
        notes_table.setStyle(TableStyle([
            ('BACKGROUND',   (0, 0), (-1, -1), BG_LIGHT),
            ('TOPPADDING',   (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING',(0, 0), (-1, -1), 4),
            ('LEFTPADDING',  (0, 0), (-1, -1), 8),
            ('RIGHTPADDING', (0, 0), (-1, -1), 8),
            ('GRID',         (0, 0), (-1, -1), 0.3, BORDER_COLOR),
        ]))
        story.append(notes_table)
        story.append(Spacer(1, 4 * mm))

    # ── FOOTER ────────────────────────────────────────────────────
    story.append(HRFlowable(width='100%', thickness=0.5, color=BORDER_COLOR, spaceBefore=4))
    story.append(Spacer(1, 2 * mm))
    story.append(Paragraph(
        f'Thank you for your business! | {invoice.from_name} | {invoice.from_email}',
        styles['footer']
    ))

    # ── BUILD PDF ─────────────────────────────────────────────────
    doc.build(story)
    pdf_bytes = buffer.getvalue()
    buffer.close()

    # Save to model
    filename = f'{invoice.invoice_number}.pdf'
    invoice.pdf_file.save(filename, ContentFile(pdf_bytes), save=True)
    invoice.save(update_fields=['pdf_file'])


def send_invoice_by_email(invoice) -> None:
    """
    Email the invoice PDF to the client.
    Generates PDF first if not already generated.
    """
    if not invoice.pdf_file:
        generate_invoice_pdf(invoice)

    subject = f'Invoice {invoice.invoice_number} from {invoice.from_name}'
    body    = (
        f'Dear {invoice.client_name},\n\n'
        f'Please find your invoice {invoice.invoice_number} attached.\n\n'
        f'Amount Due : {float(invoice.total_amount):,.2f}\n'
        f'Due Date   : {invoice.due_date.strftime("%d %b %Y") if invoice.due_date else "On Receipt"}\n\n'
        f'Thank you for your business!\n\n'
        f'Regards,\n{invoice.from_name}\n{invoice.from_email}'
    )

    email = EmailMessage(
        subject     = subject,
        body        = body,
        from_email  = settings.DEFAULT_FROM_EMAIL,
        to          = [invoice.client_email],
    )

    # Attach PDF
    with invoice.pdf_file.open('rb') as f:
        email.attach(f'{invoice.invoice_number}.pdf', f.read(), 'application/pdf')

    email.send(fail_silently=False)

    # Mark sent
    invoice.sent_at = timezone.now()
    if invoice.status == 'draft':
        invoice.status = 'sent'
    invoice.save(update_fields=['sent_at', 'status'])