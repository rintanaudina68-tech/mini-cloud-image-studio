import os
from fpdf import FPDF
from fpdf.enums import XPos, YPos

class FormalAcademicPDF(FPDF):
    def header(self):
        if self.page_no() > 1:
            self.set_font("Times", "I", 9)
            self.set_text_color(0, 0, 0)
            self.cell(0, 6, "Laporan Remidi Cloud Computing - Mini Cloud Image Studio", border=0, align="L")
            self.cell(0, 6, f"Halaman {self.page_no()}", border=0, align="R", new_x=XPos.LMARGIN, new_y=YPos.NEXT)
            self.set_draw_color(0, 0, 0)
            self.set_line_width(0.4)
            self.line(20, 15, 190, 15)
            self.ln(6)

    def footer(self):
        if self.page_no() > 1:
            self.set_y(-15)
            self.set_font("Times", "I", 8.5)
            self.set_text_color(0, 0, 0)
            self.cell(0, 8, "Program Studi Teknik Informatika - Tugas Remidi Cloud Computing", align="C")

def sanitize(text: str) -> str:
    """Sanitize string for standard FPDF Times/Helvetica PDF encoding."""
    if not text:
        return ""
    replacements = {
        "—": " - ",
        "–": "-",
        "➔": " -> ",
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
    pdf = FormalAcademicPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=20)
    pdf.set_margins(20, 20, 20)

    # Read markdown source
    md_path = os.path.join(os.path.dirname(__file__), "laporan_remidi.md")
    with open(md_path, "r", encoding="utf-8") as f:
        lines = f.readlines()

    pdf.add_page()
    epw = pdf.epw  # Effective page width (210 - 40 = 170mm)

    # =========================================================================
    # COVER PAGE (Formal Academic Style - Black Text)
    # =========================================================================
    pdf.ln(10)
    pdf.set_font("Times", "B", 16)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(epw, 8, sanitize("LAPORAN REMIDI CLOUD COMPUTING"), align="C")
    pdf.ln(2)

    pdf.set_font("Times", "B", 14)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(epw, 7, sanitize("MINI CLOUD IMAGE STUDIO"), align="C")
    
    pdf.set_font("Times", "I", 11)
    pdf.set_text_color(0, 0, 0)
    pdf.multi_cell(epw, 6, sanitize("Sistem Pemrosesan Gambar dan Manajemen Metadata Berbasis Cloud Native"), align="C")
    
    pdf.ln(12)

    # Decorative Line
    pdf.set_draw_color(0, 0, 0)
    pdf.set_line_width(0.6)
    pdf.line(35, pdf.get_y(), 175, pdf.get_y())
    pdf.ln(15)

    # Student Identity Box
    box_start_y = pdf.get_y()
    pdf.set_draw_color(0, 0, 0)
    pdf.set_fill_color(255, 255, 255)
    pdf.rect(30, box_start_y, 150, 72, style="D")
    
    pdf.set_y(box_start_y + 8)
    pdf.set_font("Times", "B", 12)
    pdf.set_text_color(0, 0, 0)
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
        pdf.set_x(40)
        pdf.set_font("Times", "B", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(45, 7, sanitize(label), align="L")
        pdf.set_font("Times", "", 11)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(85, 7, sanitize(val), align="L", new_x=XPos.LMARGIN, new_y=YPos.NEXT)

    pdf.set_y(box_start_y + 80)
    pdf.ln(15)

    # =========================================================================
    # MARKDOWN CONTENT PARSER (Pure Black, Wrapped Cells, No Truncation)
    # =========================================================================
    in_code_block = False
    in_table = False
    table_rows = []

    def render_formal_table(rows):
        if not rows:
            return
        
        pdf.ln(4)
        col_widths = [10, 42, 58, 42, 18]  # Total = 170mm
        
        # Filter valid rows (skip separator lines like |---|)
        valid_rows = []
        for r in rows:
            clean_r = [c.strip() for c in r]
            if any(c.startswith(":-") or c.startswith("--") for c in clean_r):
                continue
            valid_rows.append(clean_r)

        if not valid_rows:
            return

        headers = valid_rows[0]
        data_rows = valid_rows[1:]

        # Render Header Row
        pdf.set_font("Times", "B", 10)
        pdf.set_text_color(0, 0, 0)
        pdf.set_fill_color(240, 240, 240)
        pdf.set_draw_color(0, 0, 0)

        # Calculate line heights for header
        header_heights = []
        for idx, h_text in enumerate(headers):
            w = col_widths[idx] if idx < len(col_widths) else 30
            # Calculate lines needed
            lines_cnt = pdf.multi_cell(w, 5, sanitize(h_text), dry_run=True, output="LINES")
            header_heights.append(len(lines_cnt) * 5)

        max_header_h = max(header_heights) if header_heights else 7

        start_x = pdf.get_x()
        curr_y = pdf.get_y()

        # Check page break before header
        if curr_y + max_header_h > 270:
            pdf.add_page()
            curr_y = pdf.get_y()

        for idx, h_text in enumerate(headers):
            w = col_widths[idx] if idx < len(col_widths) else 30
            pdf.set_xy(start_x + sum(col_widths[:idx]), curr_y)
            pdf.rect(start_x + sum(col_widths[:idx]), curr_y, w, max_header_h, style="DF")
            pdf.multi_cell(w, 5, sanitize(h_text), align="C")

        pdf.set_y(curr_y + max_header_h)

        # Render Data Rows
        pdf.set_font("Times", "", 9.5)
        pdf.set_text_color(0, 0, 0)

        for row in data_rows:
            if len(row) < len(headers):
                continue
            
            # Calculate heights for each cell in this row
            row_heights = []
            for idx, cell_text in enumerate(row):
                w = col_widths[idx] if idx < len(col_widths) else 30
                clean_cell = cell_text.replace("**", "").replace("*", "").replace("`", "").strip()
                lines_cnt = pdf.multi_cell(w, 5, sanitize(clean_cell), dry_run=True, output="LINES")
                row_heights.append(max(1, len(lines_cnt)) * 5)

            max_row_h = max(row_heights) if row_heights else 6
            # Add padding
            max_row_h += 2

            curr_y = pdf.get_y()
            if curr_y + max_row_h > 270:
                pdf.add_page()
                curr_y = pdf.get_y()

            for idx, cell_text in enumerate(row):
                w = col_widths[idx] if idx < len(col_widths) else 30
                align_choice = "C" if idx in (0, 4) else "L"
                clean_cell = cell_text.replace("**", "").replace("*", "").replace("`", "").strip()

                pdf.set_xy(start_x + sum(col_widths[:idx]), curr_y)
                pdf.rect(start_x + sum(col_widths[:idx]), curr_y, w, max_row_h, style="D")
                pdf.set_xy(start_x + sum(col_widths[:idx]), curr_y + 1)
                pdf.multi_cell(w, 5, sanitize(clean_cell), align=align_choice)

            pdf.set_y(curr_y + max_row_h)

        pdf.ln(5)

    for line in lines:
        raw_line = line.strip()

        # Page Break on BAB Headers
        if raw_line.startswith("## BAB "):
            if in_table:
                render_formal_table(table_rows)
                table_rows = []
                in_table = False
            
            pdf.add_page()
            pdf.set_font("Times", "B", 14)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(epw, 8, sanitize(raw_line.replace("## ", "")), align="L")
            pdf.set_draw_color(0, 0, 0)
            pdf.set_line_width(0.5)
            pdf.line(20, pdf.get_y(), 190, pdf.get_y())
            pdf.ln(5)
            continue

        # Subheadings
        if raw_line.startswith("### "):
            if in_table:
                render_formal_table(table_rows)
                table_rows = []
                in_table = False
            pdf.ln(4)
            pdf.set_font("Times", "B", 12)
            pdf.set_text_color(0, 0, 0)
            pdf.multi_cell(epw, 6, sanitize(raw_line.replace("### ", "")), align="L")
            pdf.ln(2)
            continue

        # Code block handling
        if raw_line.startswith("```"):
            if in_code_block:
                in_code_block = False
                pdf.ln(3)
            else:
                in_code_block = True
                pdf.ln(3)
            continue

        if in_code_block:
            pdf.set_font("Courier", "", 8.5)
            pdf.set_text_color(0, 0, 0)
            pdf.set_fill_color(245, 245, 245)
            pdf.multi_cell(epw, 5, sanitize(f"  {raw_line}"), fill=True)
            continue

        # Table handling
        if raw_line.startswith("|"):
            in_table = True
            cols = [c.strip() for c in raw_line.split("|")[1:-1]]
            table_rows.append(cols)
            continue
        elif in_table:
            render_formal_table(table_rows)
            table_rows = []
            in_table = False

        # Ignore cover headers from MD line stream
        if raw_line.startswith("# LAPORAN") or raw_line.startswith("## MINI CLOUD") or raw_line.startswith("**Sistem Pemrosesan") or raw_line.startswith("### IDENTITAS"):
            continue

        # Regular Text Paragraphs
        if raw_line:
            pdf.set_font("Times", "", 11)
            pdf.set_text_color(0, 0, 0)
            clean_text = raw_line.replace("**", "").replace("*", "").replace("`", "")
            pdf.multi_cell(epw, 6, sanitize(clean_text), align="J")
            pdf.ln(3)

    if in_table:
        render_formal_table(table_rows)

    output_pdf_path = os.path.join(os.path.dirname(__file__), "Laporan_Remidi_Cloud_Computing.pdf")
    pdf.output(output_pdf_path)
    print(f"Generated formal black font PDF report: {output_pdf_path}")

if __name__ == "__main__":
    build_pdf()
