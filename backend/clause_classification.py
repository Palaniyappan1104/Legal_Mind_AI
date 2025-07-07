import requests
import json
import re
import logging

GEMINI_API_KEY = "AIzaSyB7NMEMFGLS_aKK_JUy6IxZufqB4_i8JCA"
GEMINI_API_URL = "https://generativelanguage.googleapis.com/v1/models/gemini-1.5-flash:generateContent?key=" + GEMINI_API_KEY

logging.basicConfig(level=logging.INFO)

class ClauseClassifier:
    def __init__(self):
        pass

    def classify(self, clause_text):
        # Placeholder logic
        return "Uncategorized"

def extract_json(text):
    match = re.search(r'\{[\s\S]*\}', text)
    if match:
        return match.group(0)
    return None

def classify_clause(clause_text):
    prompt = (
        "Classify the following legal clause into a category (e.g., Indemnification, Payment Terms, Confidentiality, etc.), "
        "assess its risk level (High, Medium, Low), extract 2-4 key points, and suggest 1-2 action items for a business user. "
        "Respond ONLY in valid JSON with keys: category, risk_level, key_points, action_required. Do not include any explanation or text before or after the JSON. "
        "Never use 'Unknown' or 'Uncategorized' as a value. If unsure, make your best guess.\n\n"
        f"Clause: {clause_text}\n\nJSON:"
    )
    data = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    response = requests.post(GEMINI_API_URL, json=data)
    if response.status_code == 200:
        result = response.json()
        try:
            text = result["candidates"][0]["content"]["parts"][0]["text"]
            logging.info(f"Gemini raw response: {text}")
            json_str = extract_json(text)
            logging.info(f"Extracted JSON: {json_str}")
            if json_str:
                data = json.loads(json_str)
                # Fallback logic: never allow 'Unknown' or 'Uncategorized'
                if data.get('category', '').lower() in ['unknown', 'uncategorized', '']:
                    data['category'] = 'General'
                if data.get('risk_level', '').lower() in ['unknown', '']:
                    data['risk_level'] = 'Medium'
                if not isinstance(data.get('key_points'), list):
                    data['key_points'] = []
                if not isinstance(data.get('action_required'), list):
                    data['action_required'] = []
                return data
        except Exception as e:
            logging.error(f"Error parsing Gemini response: {e}")
            logging.error(f"Full Gemini response: {result}")
    else:
        logging.error(f"Gemini API error: {response.status_code} {response.text}")
    return {
        "category": "General",
        "risk_level": "Medium",
        "key_points": [],
        "action_required": [],
    } 