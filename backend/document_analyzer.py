import re
from typing import List, Dict, Any
from backend.explanation_generator import ExplanationGenerator

# Mock ExplanationGenerator and LEDGAR_MAPPING for demonstration purposes.
# In a real scenario, these would be properly imported or defined elsewhere.
LEDGAR_MAPPING = {
    "Termination for Cause": "Provides conditions under which either party can terminate the contract due to a breach or specific default by the other party.",
    "Termination for Convenience": "Allows one or both parties to terminate the contract without cause, often with a notice period or penalty.",
    "Force Majeure": "Excuses non-performance due to unforeseen circumstances beyond the parties' control, like natural disasters or government actions.",
    "Confidentiality": "Protects sensitive information exchanged between parties, restricting its disclosure and use.",
    "Indemnification": "Obligates one party to compensate the other for losses or damages arising from specific events or breaches.",
    "Limitation of Liability": "Caps or excludes the amount of damages one party can claim from the other under the contract.",
    "Governing Law": "Specifies which jurisdiction's laws will govern the interpretation and enforcement of the contract.",
    "Dispute Resolution": "Outlines the process for resolving disagreements between parties, such as arbitration or mediation.",
    "Payment Terms": "Defines the schedule, method, and conditions for payments under the contract.",
    "Intellectual Property": "Addresses the ownership and licensing of intellectual property created or used in connection with the contract.",
    "Warranties": "Statements or promises made by one party to another, guaranteeing certain facts or conditions.",
    "Entire Agreement": "States that the written contract constitutes the complete and final agreement between the parties, superseding prior discussions.",
    "Assignment": "Governs whether and how parties can transfer their rights and obligations under the contract to a third party.",
    "Notices": "Specifies the method and address for formal communications between the parties.",
    "Severability": "Ensures that if any provision of the contract is found to be invalid, the remaining provisions remain in effect.",
    "Amendments": "Outlines the process for making changes or modifications to the contract.",
    "Waiver": "States that a party's failure to enforce a provision does not constitute a waiver of their right to do so in the future.",
    "Representations and Warranties": "Declarations by each party about the accuracy of certain facts, often made to induce the other party to enter the agreement.",
    "Default": "Defines events or actions that constitute a breach of the contract, often leading to specific remedies or termination rights.",
    "Counterparts": "Allows the contract to be executed in multiple identical copies, each of which is considered an original.",
    "Survival": "Specifies which contractual obligations continue in effect even after the contract's termination or expiration.",
    "Jurisdiction": "Designates the specific courts or tribunals that have authority to hear disputes arising from the contract.",
    "Headings": "Clarifies that clause headings are for convenience only and do not affect the interpretation of the contract's provisions.",
    "Exclusivity": "Grants one party sole rights or access to certain services, products, or markets, restricting the other party from engaging with competitors.",
    "Audit Rights": "Allows one party to review the financial records or operational processes of the other party to ensure compliance with the contract terms.",
    "Subcontracting": "Addresses the ability of a party to delegate its contractual obligations to third-party subcontractors.",
    "Insurance": "Requires parties to maintain specific types and levels of insurance coverage during the contract term.",
    # ... (truncated for brevity, but include all mappings from your reference)
}

explanation_generator = ExplanationGenerator()

def clean_clause_text(text: str) -> str:
    # Remove report artifacts and metadata
    text = re.sub(r'Page \d+ Legal Document Analysis Report', '', text, flags=re.IGNORECASE)
    text = re.sub(r'Category:.*?Risk Level:.*?Key Points:', '', text, flags=re.IGNORECASE)
    text = re.sub(r'\[Content omitted due to layout issue\]', '', text, flags=re.IGNORECASE)
    
    # Fix word breaks (e.g., "termi-\nattion" -> "termination")
    text = re.sub(r'(\w{3,})[\-\s]+\n(\w{2,})', r'\1\2', text, flags=re.MULTILINE)
    
    # Remove extra spaces and leading/trailing whitespace
    return ' '.join(text.split()).strip()

def extract_meaningful_key_points(text: str) -> List[str]:
    clean_text = clean_clause_text(text)
    sentences = re.split(r'(?<=[.!?])\s+', clean_text)
    key_points = []
    for sentence in sentences:
        clean_sentence = sentence.strip()
        if (len(clean_sentence.split()) > 5 and
            not clean_sentence.startswith(('Category:', 'Risk Level:')) and
            re.search(r'\b(shall|must|will|agree|obligat|require)\b', clean_sentence, re.IGNORECASE)):
            key_points.append(clean_sentence)
    return key_points[:3] if key_points else ["No specific key points identified."]

def categorize_clause_accurately(text: str) -> str:
    text_lower = text.lower()
    category_map = {
        'Compensation': ['compensation', 'remuneration', 'salary', 'wages', 'bonus', 'pay grade', 'base pay', 'total compensation'],
        'Payment Terms': ['payment', 'invoice', 'billing', 'fee', 'amount due', 'due date', 'payable', 'reimbursement'],
        'Employment and Non-Discrimination': ['equal employment opportunity', 'harassment', 'discrimination', 'non-discrimination', 'eeo', 'workplace conduct', 'diversity', 'inclusion'],
        'Employment': ['employment', 'employee', 'employer', 'job duties', 'work schedule', 'position', 'role'],
        'Termination': ['terminate', 'termination', 'expire', 'expiration', 'severance', 'end of employment', 'dismissal', 'resignation'],
        'Indemnification': ['indemnify', 'hold harmless', 'defend'],
        'Insurance': ['insurance', 'coverage', 'policy'],
        'General Provisions': ['complete agreement', 'entire agreement', 'governing law'],
        'Compliance': ['comply', 'osha', 'regulations', 'safety'],
        'Intellectual Property': ['work product', 'copyright', 'patent'],
        'Confidentiality': ['confidential', 'proprietary', 'non-disclosure']
    }
    # Prioritize more specific categories first
    priority = [
        'Employment and Non-Discrimination',
        'Compensation',
        'Payment Terms',
        'Employment',
        'Termination',
        'Indemnification',
        'Insurance',
        'General Provisions',
        'Compliance',
        'Intellectual Property',
        'Confidentiality',
    ]
    for category in priority:
        keywords = category_map.get(category, [])
        for kw in keywords:
            if f' {kw} ' in f' {text_lower} ' or kw in text_lower:
                return category
    return "General Contractual Clause"

def assess_clause_risk(category: str, text: str) -> str:
    text_lower = text.lower()

    # Define keywords for different risk levels
    high_risk_keywords = [
        'indemnify', 'indemnification', 'hold harmless', 'liability', 'limit liability',
        'terminate', 'termination', 'breach', 'default', 'damages', 'injunction',
        'intellectual property infringement', 'patent infringement', 'copyright violation',
        'warranty disclaimer', 'no warranty', 'as is' # For high risk related to warranties
    ]
    medium_risk_keywords = [
        'payment', 'invoice', 'fee', 'amount due', 'due date', 'reimbursement',
        'compliance', 'regulation', 'audit', 'license',
        'insurance', 'coverage', 'policy',
        'dispute', 'arbitration', 'mediation', 'litigation',
        'employment', 'salary', 'wages', 'benefits', 'workplace', 'harassment',
        'confidentiality breach', 'non-disclosure agreement' # for more specific confidentiality risks
    ]

    # Assign risk based on category and keywords
    if category in ['Indemnification', 'Termination', 'Limitation of Liability', 'Intellectual Property']:
        return "High"
    
    for keyword in high_risk_keywords:
        if keyword in text_lower:
            return "High"
    
    if category in ['Payment Terms', 'Compliance', 'Insurance', 'Dispute Resolution', 'Employment', 'Confidentiality', 'Warranties']:
        return "Medium"

    for keyword in medium_risk_keywords:
        if keyword in text_lower:
            return "Medium"

    # Default to Low for other general clauses or if no specific keywords are found
    return "Low"

def generate_specific_actions(risk_level: str, category: str) -> List[str]:
    action_map = {
        'High': {
            'Indemnification': [
                "CRITICAL: Review indemnification scope with legal counsel",
                "Verify insurance coverage matches requirements",
                "Consider adding liability caps"
            ],
            'Termination': [
                "Review termination conditions and notice periods",
                "Define material breach conditions precisely",
                "Ensure payment terms upon termination"
            ]
        },
        'Medium': {
            'Payment Terms': [
                "Verify payment amounts and schedules",
                "Confirm invoice submission deadlines",
                "Check for late payment penalties"
            ],
            'Compliance': [
                "Verify all required licenses are valid",
                "Confirm OSHA compliance measures",
                "Review record keeping requirements"
            ]
        }
    }
    if risk_level in action_map and category in action_map[risk_level]:
        return action_map[risk_level][category]
    return [f"Standard review recommended for {category} clause"]

def confidence_score(category: str, text: str) -> int:
    text_lower = text.lower()
    category_map = {
        'Compensation': ['compensation', 'remuneration', 'payment for services'],
        'Termination': ['terminate', 'termination', 'expire', 'expiration'],
        'Indemnification': ['indemnify', 'hold harmless', 'defend'],
        'Insurance': ['insurance', 'coverage', 'policy'],
        'Employment': ['employment', 'equal opportunity', 'harassment', 'discrimination'],
        'General Provisions': ['complete agreement', 'entire agreement', 'governing law'],
        'Compliance': ['comply', 'osha', 'regulations', 'safety'],
        'Intellectual Property': ['work product', 'copyright', 'patent'],
        'Confidentiality': ['confidential', 'proprietary', 'non-disclosure'],
        'Payment Terms': ['payment', 'invoice', 'billing', 'fee']
    }
    keywords = category_map.get(category, [])
    matches = sum(1 for kw in keywords if kw in text_lower)
    if not keywords:
        return 50
    return min(100, 50 + matches * 25)

def validate_clause_content(clause: dict) -> dict:
    high_risk_categories = ['Indemnification', 'Liability', 'Termination']
    if clause['category'] in high_risk_categories and clause['risk_level'] != 'High':
        clause['risk_level'] = 'High'
    clause['key_points'] = [kp for kp in clause['key_points'] if len(kp.split()) > 3]
    if not clause.get('action_required'):
        clause['action_required'] = [f"Standard review recommended for {clause['category']} clause"]
    return clause

def generate_clause_summary(clause_title: str, clause_text: str) -> Dict[str, Any]:
    explanation_generator = ExplanationGenerator()
    category = categorize_clause_accurately(clause_text)
    risk_level = assess_clause_risk(category, clause_text)
    key_points = extract_meaningful_key_points(clause_text)
    actions = generate_specific_actions(risk_level, category)
    try:
        explanation = explanation_generator.generate(query=clause_title, context=clause_text)
    except Exception as e:
        explanation = f"Explanation generation failed: {str(e)}"
    return {
        "title": clause_title,
        "text": clause_text,
        "category": category,
        "risk_level": risk_level,
        "key_points": key_points,
        "action_required": actions,
        "explanation": explanation,
        "confidence": 95
    }

def find_missing_clauses(processed_clauses: list) -> list:
    found_categories = {c['category'] for c in processed_clauses}
    required_clauses = [
        'Indemnification',
        'Liability',
        'Confidentiality',
        'Termination',
        'Governing Law'
    ]
    return [c for c in required_clauses if c not in found_categories]

def clean_clause_10_format(clause_text: str) -> str:
    cleaned_text = re.sub(r'\s+', ' ', clause_text).strip()
    return cleaned_text

def add_payment_consistency_check(contract_text: str) -> List[str]:
    warnings = []
    payment_mentions = re.findall(r'(payment|fee|invoice|amount|due date)', contract_text, re.IGNORECASE)
    if len(payment_mentions) > 1:
        warnings.append("Multiple mentions of payment terms found. Ensure consistency across clauses.")
    return warnings

def fix_spacing_issues(text: str) -> str:
    text = re.sub(r'\s+', ' ', text)
    text = re.sub(r'\s+([.,!?;:])', r'\1', text)
    text = re.sub(r'([.,!?;:])(\S)', r'\1 \2', text)
    return text.strip()

def improve_ledgar_matching(clause_title: str) -> str:
    if clause_title in LEDGAR_MAPPING:
        return clause_title
    for ledgar_term, description in LEDGAR_MAPPING.items():
        if re.search(r'\b' + re.escape(ledgar_term) + r'\b', clause_title, re.IGNORECASE):
            return ledgar_term
        if ledgar_term.lower() in clause_title.lower():
             return ledgar_term
    return "Uncategorized"

def validate_contract_consistency(contract_text: str) -> List[str]:
    warnings = []
    warnings.extend(add_payment_consistency_check(contract_text))
    return warnings

def validate_content_category_match(clause_text: str, inferred_category: str) -> str:
    text_lower = clause_text.lower()
    mismatch_warning = ""
    if "termination" in inferred_category.lower() and not re.search(r'\b(terminate|expiration|expire)\b', text_lower):
        mismatch_warning = f"Content-Category Mismatch: Clause categorized as '{inferred_category}' but lacks typical termination keywords."
    elif "payment" in inferred_category.lower() and not re.search(r'\b(payment|fee|invoice|amount|due)\b', text_lower):
        mismatch_warning = f"Content-Category Mismatch: Clause categorized as '{inferred_category}' but lacks typical payment keywords."
    elif "confidentiality" in inferred_category.lower() and not re.search(r'\b(confidential|disclosure|secret)\b', text_lower):
        mismatch_warning = f"Content-Category Mismatch: Clause categorized as '{inferred_category}' but lacks typical confidentiality keywords."
    return mismatch_warning

def format_key_points_consistently(key_points: List[str]) -> List[str]:
    if isinstance(key_points, str):
        key_points = [key_points]
    if not isinstance(key_points, list):
        return ["Invalid key points format."]
    formatted = []
    for point in key_points:
        p_str = str(point).strip()
        if len(p_str) > 1:
            p_str = p_str[0].upper() + p_str[1:]
            if not p_str.endswith(('.', '!', '?')):
                p_str += '.'
            formatted.append(p_str)
    return formatted if formatted else ["No key points provided."]

def convert_distance_to_percentage(distance):
    return 0

def validate_category_content(clause, category):
    return True

def add_payment_consistency_check(data):
    return {"total_payment_mentions": 0, "payment_keywords": []}

def fix_spacing_issues(clause_text):
    return clause_text

def is_clause_complete(clause_text):
    return True

def format_key_points_consistently(key_points):
    return key_points

def convert_distance_to_percentage(distance):
    return 0

def validate_clause_content(clause: dict) -> dict:
    high_risk_categories = ['Indemnification', 'Liability', 'Termination Provisions']
    if clause['category'] in high_risk_categories and clause['risk_level'] != 'High':
        clause['risk_level'] = 'High'
    clause['key_points'] = [kp for kp in clause['key_points'] if len(kp.split()) > 3]
    if not clause.get('action_required'):
        clause['action_required'] = [f"Standard review recommended for {clause['category']} clause"]
    return clause 