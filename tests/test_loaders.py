from docchat.loaders import load_file
import pytest
from docx import Document

def test_txt_loads_as_one_page(tmp_path):
    f = tmp_path / "a.txt"
    f.write_text("hello world")
    pages = load_file(f)
    assert len(pages) == 1
    assert pages[0].text == 'hello world'
    assert pages[0].page == 1

def test_unsupported_extension_raises(tmp_path):
    f = tmp_path / "b.xyz"
    f.write_text("dfd")
    with pytest.raises(ValueError):
        load_file(f)

def test_pdf_one_page_per_pdf_page():
    pages = load_file("tests/fixtures/spiderman.pdf")
    assert len(pages) == 2        
    assert pages[0].page == 1     
    assert pages[0].text.strip() != ""
    assert pages[0].source == "spiderman.pdf"

def test_docx_loads_as_one_page(tmp_path):
    f = tmp_path / "a.docx"
    doc = Document()
    doc.add_paragraph("first paragraph")
    doc.add_paragraph("second paragraph")
    doc.save(f)

    pages = load_file(f)

    assert len(pages) == 1
    assert pages[0].page == 1
    assert pages[0].source == "a.docx"
    assert "first paragraph" in pages[0].text
    assert "second paragraph" in pages[0].text