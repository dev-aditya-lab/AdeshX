"""OCR Service — PDF text extraction using PyMuPDF and Tesseract."""

import fitz  # PyMuPDF
import os
import logging
from pathlib import Path
from typing import Optional

logger = logging.getLogger(__name__)


# Check if Tesseract is available
TESSERACT_AVAILABLE = False
try:
    import pytesseract
    from PIL import Image
    import io
    # Try to find tesseract executable
    tesseract_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
        "/usr/bin/tesseract",
        "/usr/local/bin/tesseract",
    ]
    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            TESSERACT_AVAILABLE = True
            break
    if not TESSERACT_AVAILABLE:
        # Try system PATH
        try:
            pytesseract.get_tesseract_version()
            TESSERACT_AVAILABLE = True
        except Exception:
            pass
except ImportError:
    pass

logger.info(f"Tesseract OCR available: {TESSERACT_AVAILABLE}")


def extract_text_from_pdf(file_path: str) -> dict:
    """
    Extract text from a PDF file.

    Strategy:
    1. Try PyMuPDF for digital text extraction
    2. If text is sparse/empty, fall back to Tesseract OCR

    Returns:
        {
            "full_text": str,
            "pages": [{"page_num": int, "text": str}],
            "page_count": int,
            "is_scanned": bool,
            "method": "pymupdf" | "tesseract" | "hybrid"
        }
    """
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"PDF file not found: {file_path}")

    doc = fitz.open(file_path)
    pages = []
    full_text_parts = []
    is_scanned = False
    method = "pymupdf"

    for page_num in range(len(doc)):
        page = doc[page_num]
        text = page.get_text("text").strip()

        # If digital text is very sparse, try OCR
        if len(text) < 50 and TESSERACT_AVAILABLE:
            ocr_text = _ocr_page(page)
            if len(ocr_text) > len(text):
                text = ocr_text
                is_scanned = True
                method = "tesseract" if method == "pymupdf" else "hybrid"

        pages.append({
            "page_num": page_num + 1,
            "text": text
        })
        full_text_parts.append(text)

    doc.close()

    full_text = "\n\n".join(full_text_parts)

    # Clean up the text
    full_text = _clean_text(full_text)

    return {
        "full_text": full_text,
        "pages": pages,
        "page_count": len(pages),
        "is_scanned": is_scanned,
        "method": method,
    }


def _ocr_page(page) -> str:
    """OCR a single PDF page using Tesseract."""
    try:
        # Render page to image at 300 DPI
        mat = fitz.Matrix(300 / 72, 300 / 72)
        pix = page.get_pixmap(matrix=mat)
        img_data = pix.tobytes("png")

        # OCR with Tesseract
        from PIL import Image
        import io
        image = Image.open(io.BytesIO(img_data))
        text = pytesseract.image_to_string(image, lang="eng")
        return text.strip()
    except Exception as e:
        logger.warning(f"OCR failed for page: {e}")
        return ""


def _clean_text(text: str) -> str:
    """Clean extracted text — remove noise, fix spacing."""
    import re

    # Remove excessive whitespace
    text = re.sub(r'\n{3,}', '\n\n', text)

    # Remove page headers/footers (common patterns)
    # e.g., "Page 1 of 10", running headers
    text = re.sub(r'Page\s+\d+\s+of\s+\d+', '', text, flags=re.IGNORECASE)

    # Remove excessive spaces
    text = re.sub(r' {3,}', '  ', text)

    # Fix common OCR artifacts
    text = re.sub(r'[^\S\n]+', ' ', text)

    return text.strip()


def get_page_count(file_path: str) -> int:
    """Get the number of pages in a PDF."""
    doc = fitz.open(file_path)
    count = len(doc)
    doc.close()
    return count
