def test_extract_names():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_v_Gary_Dobson_and_David_Norris.pdf'
    text = pdf_to_plaintext(pdf_path, pages=[0], raw=True)
    names = extract_names(text)
    assert names == ['Dobson', 'Norris']


def test_extract_names_2():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_-v-_Bradbury.pdf'
    text = pdf_to_plaintext(pdf_path, pages=[0], raw=True)
    names = extract_names(text)
    assert names == ["Myles James Edward Bradbury"]


def test_extract_names_3():
    pdf_path = Path(__file__).parent.parent / 'pdfs' / "crown court" / \
        'R_-v-_Amanda_Hutton_and_Tariq_Khan.pdf'
    text = pdf_to_plaintext(pdf_path, pages=[0], raw=True)
    names = extract_names(text)
    assert names == ["Amanda Hutton", "Tariq Khan"]
