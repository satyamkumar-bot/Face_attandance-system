import pandas as pd
import io
from fpdf import FPDF
from datetime import date

def df_to_excel_bytes(df: pd.DataFrame, sheet_name: str = "Report") -> bytes:
    buf = io.BytesIO()
    with pd.ExcelWriter(buf, engine="openpyxl") as writer:
        df.to_excel(writer, sheet_name=sheet_name, index=False)
    return buf.getvalue()

def df_to_csv_bytes(df: pd.DataFrame) -> bytes:
    return df.to_csv(index=False).encode("utf-8")

def generate_attendance_pdf(df: pd.DataFrame, title: str, school_name: str = "") -> bytes:
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Helvetica", "B", 16)
    if school_name:
        pdf.cell(0, 10, school_name, ln=True, align="C")
    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(0, 9, title, ln=True, align="C")
    pdf.set_font("Helvetica", "", 9)
    pdf.cell(0, 7, f"Generated: {date.today().strftime('%d %B %Y')}", ln=True, align="C")
    pdf.ln(4)
    # Table header
    col_widths = []
    cols = list(df.columns)
    page_w = pdf.w - 2 * pdf.l_margin
    col_w = page_w / max(len(cols), 1)
    col_w = min(col_w, 45)
    col_widths = [col_w] * len(cols)
    pdf.set_font("Helvetica", "B", 8)
    pdf.set_fill_color(30, 110, 120)
    pdf.set_text_color(255, 255, 255)
    for col, w in zip(cols, col_widths):
        pdf.cell(w, 8, str(col)[:18], border=1, fill=True, align="C")
    pdf.ln()
    pdf.set_font("Helvetica", "", 7)
    pdf.set_text_color(30, 30, 30)
    for i, row in df.iterrows():
        fill = i % 2 == 0
        pdf.set_fill_color(240, 248, 248) if fill else pdf.set_fill_color(255, 255, 255)
        for val, w in zip(row.values, col_widths):
            pdf.cell(w, 7, str(val)[:20], border=1, fill=fill, align="C")
        pdf.ln()
    return bytes(pdf.output())
