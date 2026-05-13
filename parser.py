from typing import List, Dict, Optional
from pathlib import Path
import datetime

try:
    from pypdf import PdfReader
except Exception:
    # pypdf required; raise meaningful error at runtime
    PdfReader = None


def extract_pages_from_pdf(path: str) -> List[str]:
    """Extract text per page from a PDF file.

    Returns a list where each entry is the text of a page (in order).
    """
    if PdfReader is None:
        raise ImportError("pypdf is required to read PDFs. Install pypdf or pypdf2.")

    reader = PdfReader(path)
    pages = []
    for p in reader.pages:
        try:
            pages.append(p.extract_text() or "")
        except Exception:
            pages.append("")
    return pages


def parse_pdf_to_doc(path: str, doc_id: Optional[str] = None) -> Dict:
    """Parse a PDF and return a document metadata + pages.

    Returned dict includes: _id, source_path, title (filename), pages (list), imported_at
    """
    p = Path(path)
    pages = extract_pages_from_pdf(path)
    doc = {
        "_id": doc_id or p.stem,
        "source_path": str(path),
        "title": p.name,
        "pages": len(pages),
        "imported_at": datetime.datetime.utcnow().isoformat(),
        "page_texts": pages,
    }
    return doc
