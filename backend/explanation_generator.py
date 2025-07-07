import google.generativeai as genai
import re
from functools import lru_cache

# Initialize Gemini with your API key (replace with your key)
genai.configure(api_key="AIzaSyB7NMEMFGLS_aKK_JUy6IxZufqB4_i8JCA")

CANNED_EXPLANATIONS = {
    "Indemnification": "This clause outlines indemnity obligations where one party agrees to compensate the other for losses or damages. Typically includes defense costs and liability coverage.",
    "Insurance": "Specifies insurance requirements the consultant must maintain, including coverage types, limits, and duration of coverage.",
    "Payment Terms": "Details compensation structure, invoicing procedures, payment schedules, and any financial obligations between parties.",
    "Termination": "This clause outlines the conditions under which the agreement may be ended by either party.",
    "Liability": "This clause defines the extent to which each party is responsible for damages or losses.",
    "Confidentiality": "This clause protects sensitive information shared between the parties.",
    "Employment": "This clause pertains to the terms and conditions of employment, including roles, responsibilities, and workplace conduct.",
    "Employment and Non-Discrimination": "This clause addresses fair employment practices and prohibits discrimination based on protected characteristics.",
    "General Provisions": "These are standard terms and conditions that apply broadly to the entire contract, such as governing law and dispute resolution.",
    "Compliance": "This clause outlines the requirements for adhering to relevant laws, regulations, and industry standards.",
    "Intellectual Property": "This clause defines the ownership, use, and protection of intellectual property rights related to the agreement.",
    "Force Majeure": "This clause excuses parties from liability for non-performance due to unforeseen circumstances beyond their control.",
    "Governing Law": "Specifies the jurisdiction whose laws will govern the interpretation and enforcement of the contract.",
    "Dispute Resolution": "Outlines the process for resolving disagreements, often including negotiation, mediation, or arbitration.",
    "Representations and Warranties": "Statements of fact made by one party to induce another to enter into a contract, ensuring certain conditions are true.",
    "Entire Agreement": "States that the written contract constitutes the complete and final agreement between the parties, superseding all prior discussions.",
    # Add more as needed
}

class ExplanationGenerator:
    def __init__(self, model_name="gemini-2.0-flash"):
        self.model = genai.GenerativeModel(model_name)

    @lru_cache(maxsize=200)
    def cached_generate(self, query, context):
        prompt = (
            "You are a legal expert. Provide a very concise summary of the clause below. The explanation must be a maximum of 5-6 sentences and contain no bullet points. Focus only on critical risks and actions.\n\n"
            f"Clause Title: {query}\n"
            f"Clause Text: {context[:2000]}\n\n"
            "Explanation:"
        )
        response = self.model.generate_content(prompt)
        if response.text and response.text.strip():
            return response.text.strip()
        else:
            return f"This clause covers {query.lower()}. Please review carefully."

    def generate(self, query, context, category=None):
        try:
            return self.cached_generate(query, context)
        except Exception as e:
            # If quota exceeded, return canned explanation if available
            if "429" in str(e) or "quota" in str(e).lower():
                if category and category in CANNED_EXPLANATIONS:
                    return CANNED_EXPLANATIONS[category]
                return "Explanation unavailable due to quota limits."
            return f"Explanation generation failed: {str(e)}" 