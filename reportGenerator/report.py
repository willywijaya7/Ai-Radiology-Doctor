# Tambahan untuk parsing HTML dan mendukung format
from reportlab.platypus import Paragraph, Table, TableStyle, SimpleDocTemplate, Spacer, PageBreak
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm, mm
from reportlab.lib import colors
from reportlab.platypus.flowables import Flowable
from io import BytesIO
from datetime import datetime
import re
from bs4 import BeautifulSoup, Tag

class HeaderFooter(Flowable):
    def __init__(self, width, height, is_header=True, doc=None):
        Flowable.__init__(self)
        self.width = width
        self.height = height
        self.is_header = is_header
        self.doc = doc

    def draw(self):
        c = self.canv
        if self.is_header:
            try:
                c.drawImage("D:\\kuliah\\KP\\app\\reportGenerator\\logo.jpg", 
                            2 * cm, A4[1] - 4 * cm, 
                            width=3 * cm, height=3 * cm, 
                            mask='auto')
            except:
                print("Gagal memuat logo.jpg, pastikan file tersedia!")
            c.setFont("Helvetica-Bold", 16)
            c.drawCentredString(A4[0] / 2, A4[1] - 2.5 * cm, "RS SIMRS KHANZA")
            c.setFont("Helvetica", 10)
            c.drawCentredString(A4[0] / 2, A4[1] - 3.2 * cm, "GUWOSARI, Pajangan, Bantul")
            c.drawCentredString(A4[0] / 2, A4[1] - 3.7 * cm, "Hp: 08562675039, 085296559963")
            c.drawCentredString(A4[0] / 2, A4[1] - 4.2 * cm, "Email: khanzasoftmedia@gmail.com")
            c.line(2 * cm, A4[1] - 4.5 * cm, A4[0] - 2 * cm, A4[1] - 4.5 * cm)
            c.setFont("Helvetica-Bold", 14)
            c.drawCentredString(A4[0] / 2, A4[1] - 5.3 * cm, "HASIL PEMERIKSAAN AI RADIOLOGI")
        else:
            c.setFont("Helvetica", 8)
            tgl_cetak = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
            page_num = c.getPageNumber()
            c.drawString(2 * cm, 2 * cm, f"Tgl. Cetak : {tgl_cetak}")
            c.drawCentredString(A4[0] / 2, 2 * cm, f"Halaman {page_num}")

def extract_table_from_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    tables = []
    for table_tag in soup.find_all('table'):
        table_data = []
        for tr in table_tag.find_all('tr'):
            row = []
            for td in tr.find_all(['td', 'th']):
                cell_text = ' '.join(td.stripped_strings)
                row.append(cell_text)
            if row:
                table_data.append(row)
        if table_data:
            tables.append(table_data)
    return tables

def create_table_with_wrapping(table_data, available_width):
    max_cols = max(len(row) for row in table_data)
    table_text_style = ParagraphStyle(
        name='TableText',
        fontName='Helvetica',
        fontSize=9,
        leading=11,
        spaceBefore=1,
        spaceAfter=1
    )
    wrapped_table_data = []
    for row in table_data:
        wrapped_row = []
        for cell in row:
            wrapped_cell = Paragraph(cell.replace('\n', '<br/>'), table_text_style)
            wrapped_row.append(wrapped_cell)
        wrapped_table_data.append(wrapped_row)
    if max_cols == 1:
        col_widths = [available_width]
    elif max_cols == 2:
        col_widths = [available_width * 0.3, available_width * 0.7]
    else:
        col_widths = [available_width / max_cols] * max_cols
    table = Table(wrapped_table_data, 
                 colWidths=col_widths, 
                 repeatRows=1,
                 hAlign='LEFT')
    table_style = TableStyle([
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTNAME', (0, 1), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.grey),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('LEFTPADDING', (0, 0), (-1, -1), 3),
        ('RIGHTPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('TOPPADDING', (0, 0), (-1, -1), 3)
    ])
    if max_cols >= 2:
        table_style.add('ALIGN', (0, 0), (0, -1), 'CENTER')
    table.setStyle(table_style)
    return table

def create_justified_paragraph(text, font_name="Helvetica", font_size=10):
    style = ParagraphStyle(
        name='Justified',
        fontName=font_name,
        fontSize=font_size,
        alignment=4,
        spaceAfter=0.2*cm,
        leading=14
    )
    return Paragraph(text, style)

def create_bold_paragraph(text, font_name="Helvetica-Bold", font_size=10):
    style = ParagraphStyle(
        name='Bold',
        fontName=font_name,
        fontSize=font_size,
        spaceAfter=0.2*cm
    )
    return Paragraph(text, style)

def create_html_paragraph(html_text, font_name="Helvetica", font_size=10):
    style = ParagraphStyle(
        name='HTML',
        fontName=font_name,
        fontSize=font_size,
        leading=font_size + 4,
        alignment=4,  # rata kanan kiri
        allowOrphans=0,
        allowWidows=1,
        spaceAfter=6
    )
    return Paragraph(html_text, style)


def create_bullet_paragraph(text, font_name="Helvetica", font_size=10, bullet_char="•"):
    style = ParagraphStyle(
        name='Bullet',
        fontName=font_name,
        fontSize=font_size,
        alignment=0,
        leftIndent=10,
        bulletIndent=0,
        spaceAfter=0.2*cm,
        leading=14,
        bulletFontName=font_name,
        bulletFontSize=font_size,
        bulletOffsetY=2
    )
    bullet_text = f"<bullet>{bullet_char}</bullet> {text}"
    return Paragraph(bullet_text, style)

def buat_pdf(session_data):
    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, 
        pagesize=A4,
        leftMargin=2*cm,
        rightMargin=2*cm,
        topMargin=6*cm,
        bottomMargin=2.5*cm
    )
    elements = []

    # Data Pasien
    match = re.match(r'^(\d+)\s+([A-Z\s]+)\s+\((.*?)\)$', session_data['nama'])
    if not match:
        parts = session_data['nama'].split()
        if len(parts) >= 2:
            no_rm = parts[0]
            nama = ' '.join(parts[1:-1]) if len(parts) > 2 else parts[1]
            poli = parts[-1].strip('()')
        else:
            no_rm = "N/A"
            nama = session_data['nama']
            poli = "N/A"
    else:
        no_rm = match.group(1)
        nama = match.group(2).strip()
        poli = match.group(3).strip()

    data_pasien = [
        f"<b>No.RM</b> : {no_rm}",
        f"<b>Nama Pasien</b> : {nama}",
        f"<b>No. Pemeriksaan</b> : {session_data.get('no_rawat', 'N/A')}",
        f"<b>Tgl. Pemeriksaan</b> : {session_data.get('tanggal pemeriksaan', 'N/A')}",
        f"<b>Jam Pemeriksaan</b> : {session_data.get('jam', 'N/A')}",
        f"<b>Poli</b> : {poli}"
    ]
    pasien_style = ParagraphStyle(
        name='Pasien',
        fontName='Helvetica',
        fontSize=10,
        leading=14
    )
    for data in data_pasien:
        elements.append(Paragraph(data, pasien_style))
        elements.append(Spacer(1, 2*mm))

    elements.append(Spacer(1, 5*mm))
    elements.append(create_bold_paragraph("Hasil Pemeriksaan:"))
    elements.append(Spacer(1, 5*mm))

    for key, value in session_data.get("results", {}).items():
        elements.append(create_bold_paragraph(f"{key}:"))
        html_content = str(value)
        tables = extract_table_from_html(html_content)
        if tables:
            for table_data in tables:
                available_width = A4[0] - 4*cm
                table = create_table_with_wrapping(table_data, available_width)
                elements.append(table)
                elements.append(Spacer(1, 5*mm))
        else:
            soup = BeautifulSoup(html_content, 'html.parser')
            for child in soup.children:
                if isinstance(child, Tag):
                    elements.append(create_html_paragraph(str(child), font_size=10))
        elements.append(Spacer(1, 5*mm))


    disclaimer_text = "Disclaimer: Sebagai asisten AI, interpretasi ini bersifat sementara dan harus dikonfirmasi oleh dokter radiologi atau ahli medis yang berwenang."
    elements.append(Spacer(1, 5*mm))
    elements.append(create_justified_paragraph(disclaimer_text))

    elements.append(PageBreak())
    elements.append(Spacer(1, 3*cm))
    elements.append(create_bold_paragraph("Dokter Radiologi:"))
    elements.append(Spacer(1, 2*cm))
    elements.append(create_bold_paragraph("(__________________________)"))
    elements.append(Spacer(1, 0.5*cm))
    elements.append(create_justified_paragraph("Nama Lengkap & SIP"))

    def header_footer(canvas, doc):
        canvas.saveState()
        header = HeaderFooter(doc.width, doc.height, is_header=True, doc=doc)
        header.canv = canvas
        header.draw()
        footer = HeaderFooter(doc.width, doc.height, is_header=False, doc=doc)
        footer.canv = canvas
        footer.draw()
        canvas.restoreState()

    doc.build(elements, onFirstPage=header_footer, onLaterPages=header_footer)
    buffer.seek(0)
    return buffer.getvalue()
