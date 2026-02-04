import fitz
import sys
import os

if len(sys.argv) < 2:
    print("Usage: python3 extract_text.py <pdf_path> [output_path]")
    sys.exit(1)

pdf_path = sys.argv[1]
output_path = sys.argv[2] if len(sys.argv) > 2 else "extracted_text.txt"

if not os.path.exists(pdf_path):
    print(f"Error: File not found: {pdf_path}")
    sys.exit(1)

try:
    doc = fitz.open(pdf_path)
    text = ""
    for page in doc:
        text += page.get_text()
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(text)
    
    print(f"Successfully extracted {len(text)} characters to {output_path}")
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)
