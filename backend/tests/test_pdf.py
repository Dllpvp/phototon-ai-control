import io

from pypdf import PdfReader

from app.report.pdf import generate_executive_summary

TARGET = "\u041c\u0430\u0440\u0436\u0438\u043d\u0430\u043b\u044c\u043d\u043e\u0441\u0442\u044c"


def test_pdf_bytes_start_with_header():
    """\u00a711.4: PDF начинается с %PDF и весит больше 1000 байт."""
    pdf = generate_executive_summary("main")
    assert pdf.startswith(b"%PDF")
    assert len(pdf) > 1000


def test_pdf_contains_cyrillic_metric_name():
    """\u00a711.4: extract_text содержит «Маржинальность» — шрифт встроился."""
    pdf = generate_executive_summary("main")
    reader = PdfReader(io.BytesIO(pdf))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    assert TARGET in text
