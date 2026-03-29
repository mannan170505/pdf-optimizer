import os
import sys
from pathlib import Path

import fitz  # PyMuPDF
from PIL import Image
import io


def compress_pdf_for_remarkable(
    input_pdf: str,
    output_pdf: str,
    dpi: int = 120,
    jpeg_quality: int = 50,
):
    """
    Compress a PDF by rendering each page to a JPEG image and rebuilding a new PDF.

    Best for:
    - scanned PDFs
    - image-heavy books
    - PDFs that feel slow on e-ink devices

    Trade-offs:
    - text may no longer be selectable/searchable
    - too low DPI or quality may reduce readability

    Recommended starting values:
    - dpi=120
    - jpeg_quality=50

    If text becomes too blurry, try:
    - dpi=140
    - jpeg_quality=60
    """

    input_path = Path(input_pdf)
    output_path = Path(output_pdf)

    if not input_path.exists():
        raise FileNotFoundError(f"Input PDF not found: {input_path}")

    if input_path.suffix.lower() != ".pdf":
        raise ValueError("Input file must be a PDF.")

    src_doc = fitz.open(str(input_path))
    out_doc = fitz.open()

    zoom = dpi / 72.0
    matrix = fitz.Matrix(zoom, zoom)

    try:
        total_pages = len(src_doc)
        print(f"Opened: {input_path}")
        print(f"Total pages: {total_pages}")
        print(f"Using DPI={dpi}, JPEG quality={jpeg_quality}")

        for page_index in range(total_pages):
            page_number = page_index + 1
            print(f"Processing page {page_number}/{total_pages}...")

            page = src_doc.load_page(page_index)
            pix = page.get_pixmap(matrix=matrix, alpha=False)

            # Convert rendered page to PIL image
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

            # Save as compressed JPEG in memory
            img_bytes = io.BytesIO()
            img.save(img_bytes, format="JPEG", quality=jpeg_quality, optimize=True)
            img_bytes.seek(0)

            # Create a new PDF page with same physical dimensions
            rect = page.rect
            new_page = out_doc.new_page(width=rect.width, height=rect.height)
            new_page.insert_image(new_page.rect, stream=img_bytes.getvalue())

        # Save with extra cleanup/compression
        out_doc.save(
            str(output_path),
            garbage=4,
            deflate=True,
            clean=True,
        )

        print("\nDone.")
        print(f"Compressed PDF saved to: {output_path}")

        original_size = input_path.stat().st_size / (1024 * 1024)
        new_size = output_path.stat().st_size / (1024 * 1024)

        print(f"Original size:  {original_size:.2f} MB")
        print(f"New size:       {new_size:.2f} MB")

        if original_size > 0:
            reduction = ((original_size - new_size) / original_size) * 100
            print(f"Reduction:      {reduction:.1f}%")

    finally:
        src_doc.close()
        out_doc.close()


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python compress_pdf.py input.pdf output.pdf")
        print("\nOptional: edit dpi and jpeg_quality directly in the script if needed.")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_pdf = sys.argv[2]

    try:
        compress_pdf_for_remarkable(
            input_pdf=input_pdf,
            output_pdf=output_pdf,
            dpi=120,
            jpeg_quality=50,
        )
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)