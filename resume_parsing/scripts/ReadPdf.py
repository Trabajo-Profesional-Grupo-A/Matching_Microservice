import os
import PyPDF2


def read_single_pdf(file_path: str) -> str:
    """
    Read a single PDF file and extract the text from each page.

    Args:
        file_path (str): The path of the PDF file.

    Returns:
        list: A list containing the extracted text from each page of the PDF file.
    """
    output = []
    try:
        with open(file_path, "rb") as f:
            pdf_reader = PyPDF2.PdfReader(f)
            text = ""
            for page in pdf_reader.pages:
                text += page.extract_text()
            output.append(text)
    except Exception as e:
        print(f"Error reading file '{file_path}': {str(e)}")
    return str(" ".join(output))


