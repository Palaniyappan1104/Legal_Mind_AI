import os
import json
from sentence_transformers import SentenceTransformer
from datetime import datetime, timedelta
import google.generativeai as genai
from dotenv import load_dotenv, find_dotenv

# Explicitly load .env from the backend directory
load_dotenv(find_dotenv('backend/.env'))
API_KEY = os.getenv("AI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)
else:
    print("Warning: AI_API_KEY not found in .env file in backend directory. AI explanations will not be available.")

# In-memory API usage tracking (resets on server restart)
API_USAGE_COUNT = 0
API_USAGE_LAST_RESET = datetime.now().date()

# Load local embedding model
model = SentenceTransformer('all-MiniLM-L6-v2')

# Canned explanations database
EXPLANATIONS_DB = {
    "indemnification": "Indemnification clauses transfer risk between parties, requiring one party to compensate the other for losses or damages. Key elements include scope of covered claims, defense obligations, and limitations of liability.",
    "insurance": "Insurance clauses specify coverage requirements, policy types, limits, and additional insured status. Critical for risk management and compliance with contractual obligations.",
    "payment terms": "Payment terms define compensation structure, invoicing procedures, payment schedules, and consequences of late payment. Review for clarity on amounts, deadlines, and remedies.",
    "termination": "Termination provisions outline conditions for contract ending, including notice periods, cure rights, and consequences like final payments or transition obligations.",
    "miscellaneous": "This clause covers general contractual provisions not falling into other specific categories. It often includes boilerplate language such as governing law, severability, and entire agreement clauses. Review these to ensure they align with the overall intent and legal jurisdiction of the contract.",
    "governing law": "The governing law clause specifies which jurisdiction's laws will apply to the contract in case of disputes. This is crucial for determining legal interpretation and enforcement. Ensure the chosen jurisdiction is appropriate for all parties involved and the nature of the agreement.",
    "confidentiality": "Confidentiality clauses protect sensitive information shared between parties. They define what constitutes confidential information, obligations regarding its use and disclosure, and exceptions. Verify the scope, duration, and any non-disclosure requirements.",
    "limitation of liability": "Limitation of liability clauses cap the amount of damages one party can claim from another. These are critical for risk management, defining the maximum exposure for breaches or negligence. Pay close attention to the caps, exclusions, and types of damages covered.",
    "intellectual property": "Intellectual property (IP) clauses define ownership, licensing, and usage rights for patents, copyrights, trademarks, and trade secrets. This section is vital for protecting innovations and ensuring proper rights are granted or retained. Review for clarity on ownership, permitted uses, and infringement provisions.",
    "force majeure": "A force majeure clause excuses parties from fulfilling their contractual obligations when unforeseen circumstances beyond their control occur, such as natural disasters, wars, or acts of government. Check the definitions of such events and the procedures for invoking this clause.",
    "warranties": "Warranty clauses specify the assurances made by one party to another regarding the quality, condition, or performance of goods or services. They often define the remedies available if a warranty is breached. Scrutinize the scope, duration, and any disclaimers of warranties.",
    "dispute resolution": "Dispute resolution clauses outline the process for resolving disagreements between parties, such as negotiation, mediation, arbitration, or litigation. This section is important for managing potential conflicts and can significantly impact the cost and speed of resolving disputes. Ensure the chosen method aligns with business priorities.",
    "assignment": "Assignment clauses dictate whether and how a party can transfer its rights and obligations under the contract to a third party. Review these clauses to understand any restrictions or requirements for consent, as they can impact future flexibility.",
    "amendments": "Amendment clauses specify the procedures for modifying the contract, usually requiring written agreement by all parties. This ensures that changes are formally documented and agreed upon.",
    "entire agreement": "An entire agreement clause states that the written contract constitutes the complete and final agreement between the parties, superseding all prior discussions or agreements. This helps prevent claims based on pre-contractual negotiations.",
    "notices": "Notice clauses specify how formal communications between parties must be delivered to be legally effective. This includes methods of delivery (e.g., mail, email) and the addresses for notices. Verify these details for accuracy.",
    "severability": "Severability clauses ensure that if one part of the contract is found to be unenforceable, the remaining parts of the contract remain valid and enforceable. This helps maintain the overall integrity of the agreement.",
    "waiver": "Waiver clauses state that the failure of a party to enforce any provision of the contract does not constitute a waiver of that provision or any other provision. This prevents inadvertent loss of rights due to non-enforcement."
}

def generate_explanation(clause_text, category, risk_level):
    # No cache without Redis
    
    # Check if we should use AI generation
    if should_use_ai(category, risk_level):
        try:
            explanation = ai_generate_with_fallback(clause_text, category)
            return explanation
        except Exception:
            return get_canned_explanation(category)
    
    return get_canned_explanation(category)

def should_use_ai(category, risk_level):
    global API_USAGE_COUNT, API_USAGE_LAST_RESET
    
    # Reset counter daily (in-memory)
    if datetime.now().date() > API_USAGE_LAST_RESET:
        API_USAGE_COUNT = 0
        API_USAGE_LAST_RESET = datetime.now().date()
    
    high_priority = {"indemnification", "liability", "termination", "intellectual property"}
    QUOTA_LIMIT_HIGH_PRIORITY = 190 # 200 daily quota - 10 buffer
    QUOTA_LIMIT_OTHER = 50

    # Prioritize high-risk and important categories
    if risk_level == "High" or category.lower() in high_priority:
        return API_USAGE_COUNT < QUOTA_LIMIT_HIGH_PRIORITY
    
    return API_USAGE_COUNT < QUOTA_LIMIT_OTHER  # Use sparingly for others

def ai_generate_with_fallback(clause_text, category):
    global API_USAGE_COUNT
    API_USAGE_COUNT += 1
    
    try:
        model_ai = genai.GenerativeModel('models/gemini-1.5-flash-latest')
        response = model_ai.generate_content(f"Explain the following clause from a legal document, considering it is categorized as '{category}': {clause_text}")
        return response.text
    except Exception as e:
        print(f"Gemini API call failed: {e}")
        return get_canned_explanation(category)

def get_canned_explanation(category):
    # Find best match in explanations DB
    category_key = category.lower()
    for key, explanation in EXPLANATIONS_DB.items():
        if key in category_key:
            return explanation
    
    # Generic fallback
    return f"This {category} clause contains standard contractual provisions. Review for specific obligations, durations, and compliance requirements." 