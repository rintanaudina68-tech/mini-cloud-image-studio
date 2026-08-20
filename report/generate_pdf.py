import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class LaporanPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(100, 100, 100)
            self.cell(0, 8, "Laporan Remidi Cloud Computing - Mini Cloud Image Studio", border=0, align="L")
            self.cell(0, 8, f"Halaman {self.page_no()}", border=0, align="R")
            self.ln(10)
            self.set_draw_color(200, 200, 200)
            self.line(15, 18, 195, 18)
            self.ln(2)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Helvetica", "I", 8)
            self.set_text_color(150, 150, 150)
            self.cell(0, 10, "Dokumen Resmi Hasil Praktikum Cloud Computing & Boto3 Integration", align="C")

def sanitize(text: str) -> str:
    """Sanitize string for standard Helvetica PDF encoding."""
    if not text:
        return ""
    replacements = {
        "—": " - ",
        "–": "-",
        "➔": "->",
        "✅": "[BERHASIL]",
        "❌": "[GAGAL]",
        "•": "*",
        "“": '"',
        "”": '"',
        "‘": "'",
        "’": "'"
    }
    for old, new in replacements.items():
        text = text.replace(old, new)
    return text.encode("latin-1", "replace").decode("latin-1")

def build_pdf():
    pdf = LaporanPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)

    # Read markdown source
    md_path = os.path.join(os.path.dirname(__file__), "laporan_remidi.md")
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pdf.add_page()
    epw = pdf.epw  # Effective page width

    # Cover Page Styling
    pdf.ln(10)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(30, 41, 59)
    pdf.multi_cell(epw, 10, sanitize("LAPORAN REMIDI CLOUD COMPUTING"), align="C")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 16)
    pdf.set_text_color(67, 56, 202)
    pdf.multi_cell(epw, 8, sanitize("MINI CLOUD IMAGE STUDIO"), align="C")
    
    pdf.set_font("Helvetica", "I", 11)
    pdf.set_text_color(100, 116, 139)
    pdf.multi_cell(epw, 6, sanitize("Sistem Pemrosesan Gambar dan Manajemen Metadata Berbasis Cloud Native"), align="C")
    
    pdf.ln(15)

    # Decorative Line
    pdf.set_draw_color(67, 56, 202)
    pdf.set_line_width(1)
    pdf.line(40, pdf.get_y(), 170, pdf.get_y())
    pdf.ln(15)

    # Student Identity Box
    pdf.set_fill_color(248, 250, 252)
    pdf.set_draw_color(226, 232, 240)
    pdf.rect(25, pdf.get_y(), 160, 70, style="FD")
    
    start_y = pdf.get_y() + 6
    pdf.set_y(start_y)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(15, 23, 42)
    pdf.cell(epw, 7, sanitize("IDENTITAS MAHASISWA"), align="C", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
    pdf.ln(4)

    identity_info = [
        ("Nama Mahasiswa", ": Rintan Audina"),
        ("NIM", ": 32602400035"),
        ("Kelas", ": TIF 24"),
        ("Mata Kuliah", ": Cloud Computing (Remidi)"),
        ("Dosen Pengampu", ": Dosen Cloud Computing"),
        ("Tahun Akademik", ": 2026")
    ]

    for label, val in identity_info:
        pdf.set_x(35)
        pdf.set_font("Helvetica", "B", 10)
        pdf.set_text_color(51, 65, 85)
        pdf.cell(45, 6, sanitize(label), align="L")
        pdf.set_font("Helvetica", "", 10)
        pdf.set_text_color(30, 41, 59)
        pdf.cell(90, 6, sanitize(val), align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(start_y + 75)
    pdf.ln(10)

    # Parse and add Markdown content lines
    in_code_block = False
    in_table = False
    table_rows = []

    def flush_table(rows):
        if not rows: return
        pdf.ln(3)
        pdf.set_font("Helvetica", "B", 8.5)
        pdf.set_fill_color(238, 242, 255)
        pdf.set_draw_color(199, 210, 254)
        
        # Calculate col widths (Total ~180mm)
        col_w = [10, 38, 70, 44, 18]
        
        # Render Table Header
        headers = rows[0]
        for i, cell in enumerate(headers):
            w = col_w[i] if i < len(col_w) else 30
            pdf.cell(w, 7, sanitize(cell.strip()), border=1, fill=True, align="C")
        pdf.ln()

        # Render Data Rows
        pdf.set_font("Helvetica", "", 8)
        pdf.set_fill_color(255, 255, 255)
        for row in rows:
            if len(row) < len(headers) or row[0].startswith(":-") or row[0].startswith("--"):
                continue
            if row == headers:
                continue
            for i, cell in enumerate(row):
                w = col_w[i] if i < len(col_w) else 30
                align_choice = "C" if i in (0, 4) else "L"
                clean_cell = cell.replace("**", "").replace("*", "").strip()
                pdf.cell(w, 6, sanitize(clean_cell), border=1, fill=False, align=align_choice)
            pdf.ln()
        pdf.ln(4)

    for line in lines:
        raw_line = line.strip()

        # Page Break on BAB Headers
        if raw_line.startswith("## BAB "):
            if in_table:
                flush_table(table_rows)
                table_rows = []
                in_table = False
            pdf.add_page()
            pdf.set_font("Helvetica", "B", 14)
            pdf.set_text_color(30, 27, 75)
            pdf.multi_cell(epw, 8, sanitize(raw_line.replace("## ", "")), align="L")
            pdf.set_draw_color(99, 102, 241)
            pdf.line(15, pdf.get_y(), 195, pdf.get_y())
            pdf.ln(4)
            continue

        # Subheadings
        if raw_line.startswith("### "):
            if in_table:
                flush_table(table_rows)
                table_rows = []
                in_table = False
            pdf.ln(3)
            pdf.set_font("Helvetica", "B", 11)
            pdf.set_text_color(49, 46, 129)
            pdf.multi_cell(epw, 7, sanitize(raw_line.replace("### ", "")), align="L")
            pdf.ln(2)
            continue

        # Code block handling
        if raw_line.startswith("```"):
            if in_code_block:
                in_code_block = False
                pdf.ln(2)
            else:
                in_code_block = True
                pdf.ln(2)
            continue

        if in_code_block:
            pdf.set_font("Courier", "", 8)
            pdf.set_text_color(30, 41, 59)
            pdf.set_fill_color(241, 245, 249)
            pdf.multi_cell(epw, 5, sanitize(f"  {raw_line}"), fill=True)
            continue

        # Table handling
        if raw_line.startswith("|"):
            in_table = True
            cols = [c.strip() for c in raw_line.split("|")[1:-1]]
            table_rows.append(cols)
            continue
        elif in_table:
            flush_table(table_rows)
            table_rows = []
            in_table = False

        # Ignore cover titles from MD line stream as cover is already built
        if raw_line.startswith("# LAPORAN") or raw_line.startswith("## MINI CLOUD") or raw_line.startswith("**Sistem Pemrosesan") or raw_line.startswith("### IDENTITAS"):
            continue

        # Regular Text Paragraphs
        if raw_line:
            pdf.set_font("Helvetica", "", 9.5)
            pdf.set_text_color(51, 65, 85)
            clean_text = raw_line.replace("**", "").replace("*", "").replace("`", "")
            pdf.multi_cell(epw, 5, sanitize(clean_text))
            pdf.ln(2)

    if in_table:
        flush_table(table_rows)

    output_pdf_path = os.path.join(os.path.dirname(__file__), "Laporan_Remidi_Cloud_Computing.pdf")
    pdf.output(output_pdf_path)
    print(f"Generated official PDF report: {output_pdf_path}")

if __name__ == "__main__":
    build_pdf()
