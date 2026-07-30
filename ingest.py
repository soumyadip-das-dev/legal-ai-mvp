import pdfplumber
import json
import os
import re
from tqdm import tqdm

RAW_DIR = "data/raw_pdfs"
OUT_FILE = "data/processed/judgments.json"

all_records = []

def is_junk_line(line: str, case_title: str) -> bool:
    line_lower = line.strip().lower()
    if not line_lower:
        return True
        
    junk_patterns = [
        "indian kanoon",
        "indiankanoon",
        "http://",
        "https://",
        "www.",
        "equivalent citation",
        "judgment dated",
        "date of judgment",
    ]
    if any(p in line_lower for p in junk_patterns):
        return True
        
    # Check page numbers
    if line_lower.isdigit():
        return True
    if line_lower.startswith("page") and any(c.isdigit() for c in line_lower) and len(line_lower) < 15:
        return True
        
    # Case title header matching
    title_words = [w.strip(",.() ") for w in case_title.split() if len(w.strip(",.() ")) > 2]
    generic_words = {"state", "government", "union", "india", "of", "and", "vs", "versus"}
    specific_title_words = [w for w in title_words if w.lower() not in generic_words]
    
    if len(specific_title_words) >= 1:
        match_count = sum(1 for w in specific_title_words if w.lower() in line_lower)
        if match_count == len(specific_title_words) and ("vs" in line_lower or " v " in line_lower or " v. " in line_lower or " on " in line_lower):
            return True
            
    return False

def is_paragraph_end(line: str, next_line: str = None) -> bool:
    line = line.strip()
    if not line:
        return False
        
    abbrev_endings = ["e.g.", "i.e.", "vs.", "v.", "co.", "corp.", "ltd.", "j.", "p.c.", "cr.p.c.", "sec.", "arts.", "art."]
    for abbrev in abbrev_endings:
        if line.lower().endswith(abbrev):
            return False
            
    if next_line:
        next_line_stripped = next_line.strip()
        if next_line_stripped and next_line_stripped[0].islower():
            # If next line starts with lowercase, it's a continuation of the same sentence
            return False
            
    if line.endswith(('.', '?', '!')):
        return True
        
    if len(line) >= 2:
        if line[-1] in ('"', "'", ')', ']') and line[-2] in ('.', '?', '!'):
            return True
        if len(line) >= 3 and line[-1] in ('"', "'", ')', ']') and line[-2] in ('"', "'", ')', ']') and line[-3] in ('.', '?', '!'):
            return True
            
    return False

def extract_paragraphs(pdf_path, case_title):
    paragraphs = []
    buffer = ""
    
    with pdfplumber.open(pdf_path) as pdf:
        all_lines = []
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue
            all_lines.extend(text.split("\n"))
            
        valid_lines = []
        for line in all_lines:
            stripped = line.strip()
            if not stripped:
                continue
            if is_junk_line(stripped, case_title):
                continue
            valid_lines.append(stripped)
            
        for idx, line in enumerate(valid_lines):
            buffer += " " + line
            
            next_line = valid_lines[idx+1] if idx + 1 < len(valid_lines) else None
            
            if is_paragraph_end(line, next_line):
                cleaned_para = buffer.strip()
                if len(cleaned_para) > 50:
                    paragraphs.append(cleaned_para)
                buffer = ""
                
        if buffer.strip():
            cleaned_para = buffer.strip()
            if len(cleaned_para) > 50:
                paragraphs.append(cleaned_para)
                
    return paragraphs

def classify_paragraph(text: str) -> str:
    text_lower = text.lower()

    # STRONG ratio signals
    ratio_keywords = [
        "we hold",
        "we therefore hold",
        "it was held",
        "this court held",
        "we are of the considered view",
        "we are of the opinion",
        "in our view",
        "in our opinion",
        "it is settled law",
        "the law on the point",
        "it cannot be disputed",
        "no arrest can be made",
        "arrest should not be automatic",
        "custodial torture",
        "violates article 21",
        "fundamental right",
        "safeguards against arbitrary arrest",
        "registration of fir is mandatory",
        "the requirements shall be followed",
        "the above requirements shall be followed",
        "the guidelines are as follows",
        "the following requirements"
    ]

    # WEAK procedural / explanatory signals (not ratio)
    procedural_keywords = [
        "for example",
        "under section",
        "procedure",
        "has to be in writing",
        "shall be in writing",
        "is mandatory that",
        "a written notice",
        "a written order",
        "seizure memo",
        "panchnama"
    ]

    facts_keywords = [
        "facts of the case",
        "brief facts",
        "the appellant submitted",
        "learned counsel",
        "it was contended",
        "the prosecution case",
        "according to the petitioner",
        "it was argued",
        "the respondent submitted"
    ]

    # Penalize procedural explanation first
    for kw in procedural_keywords:
        if kw in text_lower:
            return "OTHER"

    # Strong ratio next
    for kw in ratio_keywords:
        if kw in text_lower:
            return "RATIO"

    # Facts last
    for kw in facts_keywords:
        if kw in text_lower:
            return "FACTS"

    return "OTHER"

def detect_cross_citation(text: str, current_case: str) -> bool:
    text_lower = text.lower()
    
    # Capitalized word, followed by spaces, then v/vs/versus (case insensitive), then capitalized word
    pattern = r'\b[A-Z][a-zA-Z\s\.\,]*?\s+(?:[vV]s\.?|[vV]\.?|[vV]ersus)\s+[A-Z][a-zA-Z\s\.\,]*?\b'
    matches = re.findall(pattern, text)
    
    title_words = [w.strip(",.() ").lower() for w in current_case.split() if len(w.strip(",.() ")) > 2]
    generic_words = {"state", "government", "union", "india", "of", "and", "vs", "versus"}
    specific_title_words = [w for w in title_words if w not in generic_words]
    
    actual_cross_citations = []
    for match in matches:
        match_lower = match.lower()
        is_self = False
        if specific_title_words:
            # If any keyword of the current case is in the match, treat as self-citation
            is_self = any(w in match_lower for w in specific_title_words)
        if not is_self:
            actual_cross_citations.append(match)
            
    if actual_cross_citations:
        return True
        
    other_signals = [
        "held in",
        "as held in",
        "in the case of",
        "referred to",
        "relied upon",
        "as observed in",
        "this court in",
    ]
    for signal in other_signals:
        if signal in text_lower:
            is_self_ref = False
            if specific_title_words:
                is_self_ref = any(w in text_lower for w in specific_title_words)
            if not is_self_ref:
                return True
                
    return False

def is_header_paragraph(text: str) -> bool:
    text_lower = text.lower()

    if any(x in text_lower for x in ["indiankanoon", "http", "new delhi"]):
        return True

    if text.strip().startswith("(") and "j." in text_lower:
        return True

    return False

# Ingest all files from RAW_DIR
for file in tqdm(os.listdir(RAW_DIR)):
    if not file.lower().endswith(".pdf"):
        continue

    # Extract year and case title robustly
    raw_name, ext = os.path.splitext(file)
    if raw_name.lower().endswith(".pdf"):
        raw_name = raw_name[:-4]
        
    parts = raw_name.split("_")
    year = None
    if parts[-1].isdigit():
        year = int(parts[-1])
        parts = parts[:-1]

    case_title = " ".join(parts).replace("vs", "v.").strip()

    path = os.path.join(RAW_DIR, file)
    paragraphs = extract_paragraphs(path, case_title)

    valid_idx = 1
    for para in paragraphs:
        if is_header_paragraph(para):
            continue

        para_type = classify_paragraph(para)
        is_cross = detect_cross_citation(para, case_title)

        record = {
            "case_title": case_title,
            "court": "Supreme Court of India",
            "year": year,
            "paragraph": valid_idx,
            "para_type": para_type,
            "is_cross_citation": is_cross,
            "text": para
        }

        all_records.append(record)
        valid_idx += 1

# Save processed records
os.makedirs(os.path.dirname(OUT_FILE), exist_ok=True)
with open(OUT_FILE, "w", encoding="utf-8") as f:
    json.dump(all_records, f, ensure_ascii=False, indent=2)

print(f"Extracted {len(all_records)} paragraphs successfully.")
