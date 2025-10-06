import argparse
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import textwrap
import os
import sys

def txt_to_pdf(input_file, output_file, font_size=10, max_chars=90):
    try:
        # Register monospaced font (Courier or fallback)
        font_name = "Courier"
        pdfmetrics.registerFont(TTFont('Courier', 'Courier.ttf'))

        # Create PDF canvas
        c = canvas.Canvas(output_file, pagesize=A4)
        width, height = A4

        # Margins
        margin_left = 15 * mm
        margin_top = 15 * mm
        y = height - margin_top

        line_height = font_size + 2
        c.setFont(font_name, font_size)

        with open(input_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.rstrip('\n')
                wrapped = textwrap.wrap(line, width=max_chars) or ['']
                for wrap_line in wrapped:
                    if y < margin_top:
                        c.showPage()
                        c.setFont(font_name, font_size)
                        y = height - margin_top
                    c.drawString(margin_left, y, wrap_line)
                    y -= line_height

        c.save()
        print(f"[✓] PDF berhasil dibuat: {output_file}")

    except Exception as e:
        print(f"[✗] Gagal membuat PDF: {e}")
        sys.exit(1)

def main():
    parser = argparse.ArgumentParser(description="Convert TXT file to PDF")
    parser.add_argument("--filename", required=True, help="Path to input .txt file")
    parser.add_argument("--output", required=True, help="Path to output .pdf file")
    args = parser.parse_args()

    if not os.path.isfile(args.filename):
        print(f"[✗] File tidak ditemukan: {args.filename}")
        sys.exit(1)

    txt_to_pdf(args.filename, args.output)

if __name__ == "__main__":
    main()
