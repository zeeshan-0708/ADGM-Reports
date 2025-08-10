# checklist.py
from typing import List, Dict

PROCESS_CHECKLISTS = {
    "Company Incorporation": [
        "Articles of Association",
        "Memorandum of Association",
        "Incorporation Application Form",
        "UBO Declaration Form",
        "Register of Members and Directors"
    ],
    "Licensing": [
        "License Application",
        "Business Plan",
        "Proof of Address",
    ],
    "Employment Contracts": [
        "Employment Contract",
        "Offer Letter",
        "Employee Handbook"
    ]
}

def get_required_docs_for_process(process_name: str):
    return PROCESS_CHECKLISTS.get(process_name, [])

def infer_process_from_doc_types(doc_types: List[str]) -> str:
    # Simple heuristic: if key incorporation docs present, pick incorporation
    inc_set = set(PROCESS_CHECKLISTS["Company Incorporation"])
    if any(d in inc_set for d in doc_types):
        return "Company Incorporation"
    lic_set = set(PROCESS_CHECKLISTS["Licensing"])
    if any(d in lic_set for d in doc_types):
        return "Licensing"
    emp_set = set(PROCESS_CHECKLISTS["Employment Contracts"])
    if any(d in emp_set for d in doc_types):
        return "Employment Contracts"
    # fallback
    return "Company Incorporation"
