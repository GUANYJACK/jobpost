import os
from docx import Document
from fpdf import FPDF

def docx_to_pdf(docx_path, pdf_path):
    doc = Document(docx_path)
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    for para in doc.paragraphs:
        text = para.text.strip()
        if text:
            pdf.multi_cell(0, 10, text)
    pdf.output(pdf_path)
    return pdf_path
