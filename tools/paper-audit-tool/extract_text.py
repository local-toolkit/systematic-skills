import fitz
import sys
import os

pdf_path = "/Users/xujintao/Documents/workspace/systematic-skills/tools/paper_audit/inbox/IncogniText: Privacy-enhancing Conditional Text Anonymization via LLM-based Private Attribute Randomization.pdf"
output_path = "extracted_text.txt"

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
