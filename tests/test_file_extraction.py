import io

import docx

from utils.files import extract_text_from_bytes


def test_extract_txt_text():
    text = extract_text_from_bytes("doc.txt", b"hello semantic search")
    assert "semantic search" in text


def test_extract_docx_text():
    stream = io.BytesIO()
    document = docx.Document()
    document.add_paragraph("Document extraction works.")
    document.save(stream)

    text = extract_text_from_bytes("doc.docx", stream.getvalue())
    assert "Document extraction works." in text
