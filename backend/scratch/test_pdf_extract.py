import pypdf
import os
import traceback

def extract_text_from_pdf(pdf_path: str) -> str:
    text = ""
    try:
        reader = pypdf.PdfReader(pdf_path)
        print(f"Number of pages: {len(reader.pages)}")
        for i, page in enumerate(reader.pages):
            extracted = page.extract_text()
            print(f"Page {i+1} extracted {len(extracted)} characters.")
            text += extracted + "\n"
    except Exception as e:
        print("Error extracting PDF:")
        print(traceback.format_exc())
    return text

pdf_path = r"c:\Users\jcabrera\TalentoWEB\Antonio Fernandez cv.pdf"
if os.path.exists(pdf_path):
    print(f"File exists: {pdf_path}")
    text = extract_text_from_pdf(pdf_path)
    print("--- Text Sample ---")
    print(text[:500])
    print("--- End Sample ---")
else:
    print(f"File not found: {pdf_path}")
