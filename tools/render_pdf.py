"""Render the exported PDF for visual inspection of every document page."""
from pathlib import Path
import pymupdf as fitz

ROOT = Path(__file__).resolve().parents[1]
out = ROOT / "docs/render"
out.mkdir(exist_ok=True)
with fitz.open(ROOT / "docs/Evidencias_Bookshelf.pdf") as pdf:
    for index, page in enumerate(pdf, 1):
        page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5), alpha=False).save(out / f"page-{index}.png")
        print(f"Page {index}: {len(page.get_text())} text characters")
    print(f"Rendered {len(pdf)} pages")
