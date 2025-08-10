# redflags.py
import re
from docx import Document
from typing import List, Dict

AMBIGUOUS_PHRASES = [
    "reasonable endeavours",
    "as may be agreed",
    "at the discretion of",
    "subject to applicable laws",
    "time is of the essence"
]

WRONG_JURISDICTIONS = [
    "uae federal courts", "dubai courts", "sharjah courts", "u.a.e federal", "u.a.e. federal"
]

def detect_issues_for_doc(doc: Document, doc_type: str) -> List[Dict]:
    text = "\n".join([p.text for p in doc.paragraphs])
    issues = []

    # 1) Jurisdiction mismatch
    for wj in WRONG_JURISDICTIONS:
        if re.search(wj, text, flags=re.I):
            issues.append({
                "document": doc_type,
                "section": "Jurisdiction clause",
                "issue": f"Jurisdiction clause refers to '{wj}'. Expected ADGM jurisdiction.",
                "severity": "High",
                "suggestion": "Replace jurisdiction clause with explicit reference to ADGM Courts."
            })
            break

    # 2) Missing signature block
    if not re.search(r"(signature|signed by|for and on behalf|authorized signatory|signature:)", text, flags=re.I):
        issues.append({
            "document": doc_type,
            "section": "Signature block",
            "issue": "No clear signature block found.",
            "severity": "High",
            "suggestion": "Add a signatory section with name, title, signature line and date."
        })

    # 3) Ambiguous phrases
    for phrase in AMBIGUOUS_PHRASES:
        if re.search(re.escape(phrase), text, flags=re.I):
            issues.append({
                "document": doc_type,
                "section": "Contract language",
                "issue": f"Ambiguous phrase detected: '{phrase}'",
                "severity": "Medium",
                "suggestion": f"Replace '{phrase}' with specific obligations, timelines or measurable standards."
            })

    # 4) UBO missing in incorporation docs
    if doc_type.lower().startswith("articles") or doc_type.lower().startswith("memorandum") or "incorporation" in doc_type.lower():
        if not re.search(r"ubo|ultimate beneficial owner|ultimate owner", text, flags=re.I):
            issues.append({
                "document": doc_type,
                "section": "UBO / Ownership",
                "issue": "No UBO/ownership declaration found in document.",
                "severity": "Medium",
                "suggestion": "Include an explicit UBO declaration clause or attach UBO form."
            })

    # 5) Date format flags
    if re.search(r"\d{4}-\d{2}-\d{2}", text):
        issues.append({
            "document": doc_type,
            "section": "Dates",
            "issue": "Date(s) found in YYYY-MM-DD format. Confirm ADGM preferred format.",
            "severity": "Low",
            "suggestion": "Use consistent date formatting as required by filings."
        })

    return issues
