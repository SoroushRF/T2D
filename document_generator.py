import pandas as pd
from docx import Document
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor
from fpdf import FPDF, FontFace


def set_cell_background(cell, color_hex):
    """Sets the background color of a table cell in python-docx."""
    tc_pr = cell._element.get_or_add_tcPr()
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), color_hex)
    tc_pr.append(shd)


def set_cell_margins(cell, top=100, bottom=100, left=150, right=150):
    """Sets cell padding (in dxa/twips) for a DOCX cell."""
    tc_pr = cell._element.get_or_add_tcPr()
    tc_mar = OxmlElement("w:tcMar")
    for m, val in [("top", top), ("bottom", bottom), ("left", left), ("right", right)]:
        node = OxmlElement(f"w:{m}")
        node.set(qn("w:w"), str(val))
        node.set(qn("w:type"), "dxa")
        tc_mar.append(node)
    tc_pr.append(tc_mar)


def export_to_docx(df, output_path, title="Spreadsheet Export"):
    """Exports a pandas DataFrame to a styled Microsoft Word DOCX document."""
    doc = Document()

    # Configure document title
    h1 = doc.add_heading(title, level=1)
    h1.alignment = WD_ALIGN_PARAGRAPH.CENTER
    for run in h1.runs:
        run.font.name = "Arial"
        run.font.color.rgb = RGBColor(45, 55, 72)  # Charcoal Slate

    doc.add_paragraph(f"Exported from Spreadsheet Editor. Shape: {df.shape[0]} rows x {df.shape[1]} columns.\n")

    # Add a table
    num_rows = len(df) + 1  # include header
    num_cols = len(df.columns)

    table = doc.add_table(rows=num_rows, cols=num_cols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.style = "Table Grid"

    # Write and style headers
    hdr_cells = table.rows[0].cells
    for col_idx, col_name in enumerate(df.columns):
        cell = hdr_cells[col_idx]
        cell.text = str(col_name)
        set_cell_background(cell, "2D3748")  # Dark Slate Blue
        set_cell_margins(cell, top=120, bottom=120, left=150, right=150)

        # Center header text and change font
        p = cell.paragraphs[0]
        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
        for run in p.runs:
            run.font.bold = True
            run.font.name = "Arial"
            run.font.size = Pt(10)
            run.font.color.rgb = RGBColor(255, 255, 255)

    # Write and style data rows
    for row_idx, row in df.iterrows():
        row_cells = table.rows[row_idx + 1].cells
        # Zebra striping color
        row_bg = "F7FAFC" if row_idx % 2 == 1 else "FFFFFF"

        for col_idx, val in enumerate(row):
            cell = row_cells[col_idx]

            # Format value
            cell_val = ""
            if not pd.isna(val):
                if isinstance(val, float):
                    cell_val = str(int(val)) if val.is_integer() else f"{val:.4g}"
                else:
                    cell_val = str(val)

            cell.text = cell_val
            set_cell_background(cell, row_bg)
            set_cell_margins(cell, top=80, bottom=80, left=120, right=120)

            p = cell.paragraphs[0]
            # Left align text, right align numbers
            try:
                # Test if numeric
                float(cell_val)
                p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
            except ValueError:
                p.alignment = WD_ALIGN_PARAGRAPH.LEFT

            for run in p.runs:
                run.font.name = "Arial"
                run.font.size = Pt(9.5)
                run.font.color.rgb = RGBColor(45, 55, 72)

    # Save the file
    doc.save(output_path)


class StyledPDF(FPDF):
    def __init__(self, title_text, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.title_text = title_text

    def header(self):
        self.set_font("helvetica", "B", 14)
        self.set_text_color(45, 55, 72)
        self.cell(0, 10, self.title_text, align="C", new_x="LMARGIN", new_y="NEXT")
        self.set_draw_color(226, 232, 240)
        self.line(10, self.get_y(), self.w - 10, self.get_y())
        self.ln(5)

    def footer(self):
        self.set_y(-15)
        self.set_font("helvetica", "I", 8)
        self.set_text_color(160, 174, 192)
        self.cell(0, 10, f"Page {self.page_no()}/{{nb}}", align="C")


def export_to_pdf(df, output_path, title="Spreadsheet Export"):
    """Exports a pandas DataFrame to a styled PDF document."""
    # Determine page orientation based on column count to prevent overflow
    num_cols = len(df.columns)
    orientation = "L" if num_cols > 6 else "P"

    pdf = StyledPDF(title_text=title, orientation=orientation, unit="mm", format="A4")
    pdf.alias_nb_pages()
    pdf.add_page()

    # Subtitle with data metadata
    pdf.set_font("helvetica", "I", 9)
    pdf.set_text_color(113, 128, 150)
    pdf.cell(
        0,
        6,
        f"Shape: {df.shape[0]} rows x {df.shape[1]} columns. Generated via Spreadsheet Editor.",
        new_x="LMARGIN",
        new_y="NEXT",
    )
    pdf.ln(4)

    # Style configuration
    pdf.set_font("helvetica", size=9)

    # Format all cells to strings
    headers = [str(col) for col in df.columns]
    rows = []
    for _, row in df.iterrows():
        row_str = []
        for val in row:
            if pd.isna(val):
                row_str.append("")
            else:
                if isinstance(val, float):
                    row_str.append(str(int(val)) if val.is_integer() else f"{val:.4g}")
                else:
                    row_str.append(str(val))
        rows.append(row_str)

    # Draw table using fpdf2 table feature
    with pdf.table(
        col_widths=None,
        text_align="LEFT",
        line_height=6,
        cell_fill_color=(247, 250, 252),
        cell_fill_mode="ROWS",
        headings_style=FontFace(color=(255, 255, 255), fill_color=(45, 55, 72)),
    ) as table:
        # Style headings
        pdf.set_text_color(255, 255, 255)

        # Write headings
        header_row = table.row()
        for h in headers:
            header_row.cell(h)

        # Style body
        pdf.set_text_color(45, 55, 72)

        # Write data rows
        for idx, r in enumerate(rows):
            data_row = table.row()
            for val in r:
                # Right align numbers
                align = "RIGHT"
                try:
                    float(val)
                except ValueError:
                    align = "LEFT"
                data_row.cell(val, align=align)

    pdf.output(output_path)
