# 🧠 Legal Mind AI

**Legal Mind AI** is an AI-powered legal clause analysis system designed to simplify legal document processing. Using advanced clause extraction, classification, and matching models, the system identifies key clauses, matches them with a legal index (LEDGAR), and provides human-understandable explanations.

---

## 📌 Project Overview

This project allows users to upload legal documents (PDFs), extract and classify clauses using machine learning models, and receive plain-language explanations. It features a FastAPI backend and a simple, intuitive frontend interface.

---

## ✨ Features

- 📄 Upload legal PDFs for clause analysis
- 📑 Extracts meaningful clauses using NLP techniques
- 📚 Classifies clauses using a pretrained model
- 🔍 Matches clauses against LEDGAR clause index
- 🧾 Generates natural language explanations for each clause
- 🚀 Frontend interface to upload, analyze, and view results
- 📦 Modular backend organized by services
- 🔐 API key protected Gemini usage

---

## 🌐 Live Demo

> 🔗 **Click to open the live app:**  
[https://legalmind.streamlit.app/](https://legalmind.streamlit.app/)  
*(Update this with your actual deployed URL if available)*

---

## 🛠️ Tech Stack

| Frontend         | Backend         | AI & NLP Models      | Others                  |
|------------------|------------------|----------------------|--------------------------|
| HTML, CSS, JS     | FastAPI          | Gemini / Clause Models | Python, Base64 Encoding |
| Streamlit (optional) | Uvicorn | LEDGAR Index Matching | PyPDF2, dotenv |

---

## 🧪 Installation & Running Locally

### 🔻 Clone the repository:
```bash
git clone https://github.com/Palaniyappan1104/Legal_Mind_AI.git
cd Legal_Mind_AI
```
### 📦 Install dependencies:
```bash
cd backend
pip install -r requirements.txt
```
### 🔑 Configure Gemini API Key:
In `.env`:

```env
GEMINI_API_KEY="your_gemini_api_key"
```
(Replace `"your_gemini_api_key"` with your actual API key.)

### ▶️ Run the backend server:
```bash
uvicorn app:app --reload
```

### ▶️ Run the frontend server:
```bash
cd ../frontend
http-server -p 3000
```

---

## 💡 How to Use the App (With Screenshots)
1️⃣ Upload the Document
📷 [Insert screenshot here]

Drag and drop or select a PDF legal document for analysis.

2️⃣ Extract Clauses
📷 [Insert screenshot here]

The app will extract and identify clauses from your legal text.

3️⃣ Classification & Matching
📷 [Insert screenshot here]

It classifies each clause and matches it with a standard legal clause from LEDGAR.

4️⃣ View Explanations
📷 [Insert screenshot here]

Natural language explanations will help you understand the purpose of each clause.

5️⃣ Download Analysis
📷 [Insert screenshot here]

Export the results or save the explanations as a document (optional).

---

## 🧾 Folder Structure
```bash
Legal_Mind_AI/
│
├── frontend/              # HTML/CSS/JS frontend files
├── backend/               # FastAPI backend
│   ├── services/          # Core NLP and classification services
│   ├── .env               # API key and environment config
│   ├── app.py             # Main FastAPI app
│   └── requirements.txt   # Python dependencies
│
├── gemini_quota.json      # Gemini usage tracker
└── README.md              # This file
```

---

## 📸 Code Snapshots

### `backend/app.py`
📷 [Insert image of code snippet]

### `clause_classification.py`
📷 [Insert image of code snippet]

### `explanation_service.py`
📷 [Insert image of code snippet]

---

## 📄 License
This project is licensed under the MIT License.

---

## 🙋‍♂️ Author
Palaniyappan S
🔗 GitHub: @Palaniyappan1104 