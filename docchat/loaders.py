from dataclasses import dataclass
from pathlib import Path
from pypdf import PdfReader
from docx import Document

@dataclass
class Page:
    text: str
    source: str
    page: int

def load_file(path):
    p = Path(path)
    extension = p.suffix
    extension = extension.lower()
    if extension in ['.md', '.txt']:
        text = p.read_text(encoding='utf-8')
        return([
            Page(
                text=text,
                source=p.name,
                page=1
            )]
        )
    elif extension == '.pdf':
        reader = PdfReader(p)
        pages = []

        for page_number, pdf_page in enumerate(reader.pages, start=1):
            text = pdf_page.extract_text()
            page = Page(
            text=text,
            page=page_number,
            source=p.name
            )
            pages.append(page)
        return pages

    elif extension == '.docx':
        doc = Document(p)
        text = "\n".join(paragraph.text for paragraph in doc.paragraphs)
        return [Page(text=text, source=p.name, page=1)]




    raise ValueError(f"Invalid extension provided: {extension}")

