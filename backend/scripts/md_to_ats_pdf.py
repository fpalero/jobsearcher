import argparse
import tempfile
from pathlib import Path

import typst


CMARKER_WRAPPER = """\
#import "@preview/cmarker:0.1.8"
#set page(paper: "us-letter", margin: (x: 1.5cm, y: 1.5cm))
#set text(size: 11pt)
#cmarker.render(read("cv.md"))
"""


def markdown_to_pdf(md_content: str, pdf_path: Path) -> None:
    pdf_path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory() as tmp_dir:
        md_file = Path(tmp_dir) / "cv.md"
        md_file.write_text(md_content, encoding="utf-8")
        typ_file = Path(tmp_dir) / "cv.typ"
        typ_file.write_text(CMARKER_WRAPPER, encoding="utf-8")
        typst.compile(str(typ_file), output=str(pdf_path))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Render a markdown CV to PDF via cmarker")
    parser.add_argument("input", type=Path, help="Path to input markdown file")
    parser.add_argument("output", type=Path, help="Path to output PDF file")
    args = parser.parse_args()
    content = args.input.read_text(encoding="utf-8")
    markdown_to_pdf(content, args.output)
