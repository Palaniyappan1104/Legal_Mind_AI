import pdfplumber
import re
from typing import List, Dict

def extract_clauses_from_pdf(pdf_buffer) -> List[Dict[str, str]]:
    """
    Extracts clauses from a PDF using a layout-aware and pattern-based approach.

    It identifies clause headers based on common legal document formats (e.g., "Section X.", "X.1")
    and groups all subsequent text under that header until a new one is found.

    Args:
        pdf_buffer: A file-like object for the PDF document.

    Returns:
        A list of dictionaries, where each dictionary represents a clause
        with 'title' and 'text' keys.
    """
    clauses = []
    
    with pdfplumber.open(pdf_buffer) as pdf:
        full_text = ""
        for page in pdf.pages:
            full_text += page.extract_text() + "\n"

    # Regex to find potential clause headers.
    # Matches patterns like: "Section 5.", "5.", "5.1.", "ARTICLE V."
    clause_pattern = re.compile(
        r'^\s*((?:ARTICLE|Section)\s+[IVXLC\d]+[\.\s]?|[ \t]*\d{1,2}(?:\.\d{1,2})*[\.\s])\s*(.*)',
        re.IGNORECASE | re.MULTILINE
    )
    
    matches = list(clause_pattern.finditer(full_text))
    
    if not matches:
        # If no specific headers are found, fall back to splitting by double newline.
        # This handles simpler, unstructured documents.
        raw_clauses = full_text.split('\n\n')
        return [{"title": f"Clause {i+1}", "text": clause.strip()} for i, clause in enumerate(raw_clauses) if clause.strip()]

    for i, match in enumerate(matches):
        start_pos = match.end()
        # The clause text is everything from the end of the current header
        # to the start of the next header.
        end_pos = matches[i + 1].start() if i + 1 < len(matches) else len(full_text)
        
        clause_text = full_text[start_pos:end_pos].strip()
        
        # Combine the matched number/ID and the rest of the line to form the title.
        clause_title = (match.group(1).strip() + " " + match.group(2).strip()).strip()
        
        # Clean up title by removing trailing dots and extra whitespace
        clause_title = re.sub(r'\s+', ' ', clause_title.replace('\n', ' ')).strip()
        if clause_title.endswith('.'):
            clause_title = clause_title[:-1]

        if clause_text:
            clauses.append({"title": clause_title, "text": clause_text})
            
    return clauses 