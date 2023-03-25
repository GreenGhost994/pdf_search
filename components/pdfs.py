from os import path
import PyPDF2
import fitz
import tempfile
import pytesseract
from PIL import Image
Image.MAX_IMAGE_PIXELS = None


def get_data_from_pdfs(folder_path: str, filename:str, mode: str) -> dict:
    drawings_data={}

    with open(path.join(folder_path, filename), 'rb') as file:
        pdf_reader=PyPDF2.PdfFileReader(file, strict=False)
        text=''
        for page in pdf_reader.pages:
            text+=page.extract_text()
        drawings_data[filename]=text.split()
        drawings_data[filename]+=filename
        if mode == 'elements':
            drawings_data[filename]=[x for x in drawings_data[filename] if validate_name(x)]

    return drawings_data


def validate_name(element_name: str) -> bool:
    if '_' in element_name:
        return True
    elif element_name.startswith(('F', '2F')) and len(element_name) > 1:
        return True
    elif 'det' in element_name.lower():
        return True
    # elif ' ' in element_name:
    #     return False
    else:
        return False


def analyze_pdf_with_tesseract(folder_path: str, filename:str, mode: str, tesseract_path:str, lang:str) -> dict:
    pdf_file_path = path.join(folder_path, filename)
    dpi = 300
    zoom = dpi / 72
    magnify = fitz.Matrix(zoom, zoom)
    doc = fitz.open(pdf_file_path)
    pytesseract.pytesseract.tesseract_cmd=tesseract_path
    result = []
    with tempfile.TemporaryDirectory() as temp:
        for page in doc:
            pix = page.get_pixmap(matrix=magnify)
            png_file_path = path.join(temp, f"{path.splitext(path.basename(pdf_file_path))[0]}-page-{page.number}.png")
            pix.save(png_file_path)

            image = Image.open(png_file_path)
            image = image.convert('L')
            text = pytesseract.image_to_string(image, lang=lang)
            lines = text.split('\n')
            lines = [line for line in lines if line.strip()]

            result.extend(lines)

    drawings_data = {filename: result}
    if mode == 'elements':
        drawings_data[filename]=[x for x in drawings_data[filename] if validate_name(x)]
    return drawings_data
