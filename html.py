import os
from pdfminer.high_level import extract_text_to_fp
from io import StringIO

def extract_text_from_pdf(pdf_path):
    output = StringIO()
    try:
        with open(pdf_path, 'rb') as pdf_file:
            extract_text_to_fp(pdf_file, output)
        text = output.getvalue()
        return text
    except Exception as e:
        print(f"Error extracting text from {pdf_path}: {str(e)}")
        return None

def save_text_as_txt(text, txt_path):
    try:
        with open(txt_path, 'w', encoding='utf-8') as txt_file:
            txt_file.write(text)
        print(f"Text saved as {txt_path}")
    except Exception as e:
        print(f"Error saving text as {txt_path}: {str(e)}")

def batch_extract_text_from_pdfs(folder_path, output_folder):
    for filename in os.listdir(folder_path):
        if filename.endswith(".pdf"):
            pdf_path = os.path.join(folder_path, filename)
            text = extract_text_from_pdf(pdf_path)
            if text:
                pdf_filename = os.path.splitext(filename)[0]
                txt_filename = f"{pdf_filename}.txt"
                txt_path = os.path.join(output_folder, txt_filename)
                save_text_as_txt(text, txt_path)

if __name__ == '__main__':
    folder_path = "./test_pdf"  # 包含PDF文件的文件夹路径
    output_folder = "./test_pdf"  # 保存文本文件的文件夹路径
    batch_extract_text_from_pdfs(folder_path, output_folder)