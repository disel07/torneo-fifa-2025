
import zipfile
import re
import sys
import os

def get_docx_text(path):
    if not os.path.exists(path):
        return "File not found"
    try:
        with zipfile.ZipFile(path) as document:
            xml_content = document.read('word/document.xml').decode('utf-8')
            # Very basic XML tag stripping for readability
            text = re.sub('<[^>]+>', ' ', xml_content)
            # Cleanup whitespace
            text = re.sub('\s+', ' ', text).strip()
            return text
    except Exception as e:
        return f"Error reading docx: {e}"

if __name__ == "__main__":
    print(get_docx_text("/home/disel/Desktop/progetto fifa/TORNEO AUTOGESTIONE FIFA.docx"))
