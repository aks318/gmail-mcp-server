
import fitz
from pathlib import Path


def extract_pdf_text(file_path: str) -> dict:
    """Extract text and metadata from a PDF."""

    path = Path(file_path)

    if not path.exists():
        raise FileNotFoundError(f"PDF not found: {path}")

    if path.suffix.lower() != ".pdf":
        raise ValueError("Only PDF files are supported")

    pages = []

    with fitz.open(path) as pdf:

        for page_number, page in enumerate(pdf, start=1):
            text = page.get_text("text")

            pages.append({
                "page_number": page_number,
                "text": text.strip()
            })

        return {
            "filename": path.name,
            "total_pages": len(pdf),
            "pages": pages,
            "full_text": "\n".join(
                page["text"] for page in pages
            )
        }
