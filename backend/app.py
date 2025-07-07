import os
import sys
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import JSONResponse, StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Any
import io
from datetime import datetime, timedelta

from backend.clause_extraction import extract_clauses_from_pdf
from backend.clause_classification import classify_clause
from backend.clause_matching import ClauseMatcher
from backend.explanation_generator import ExplanationGenerator
import backend.prepare_ledgar_index
from backend.document_analyzer import (
    generate_clause_summary,
    categorize_clause_accurately,
    find_missing_clauses,
    validate_category_content,
    add_payment_consistency_check,
    fix_spacing_issues,
    is_clause_complete,
    format_key_points_consistently,
    convert_distance_to_percentage,
    clean_clause_text
)
from backend.services.explanation_service import generate_explanation
from fpdf import FPDF
from fpdf.enums import Align
import re

app = FastAPI()

# Allow CORS for local frontend development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class Clause(BaseModel):
    title: str
    text: str
    category: str = ""
    risk_level: str = ""

class ClauseRequest(BaseModel):
    text: str
    category: str
    risk_level: str

@app.post("/extract_clauses/")
async def extract_clauses(file: UploadFile = File(...)):
    if file.content_type != "application/pdf":
        return JSONResponse(status_code=400, content={"error": "Only PDF files are supported."})
    try:
        contents = await file.read()
        pdf_buffer = io.BytesIO(contents)
        clauses = extract_clauses_from_pdf(pdf_buffer)
        return {"clauses": clauses}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/classify_clause/")
async def classify_clause_api(clause_text: str = Form(...)):
    try:
        # Use the advanced document_analyzer logic for clause analysis
        # For now, use the clause text as both the title and text
        result = generate_clause_summary(clause_text, clause_text)
        # Map to the expected frontend keys
        return {
            "category": result["category"],
            "risk_level": result["risk_level"],
            "key_points": result["key_points"],
            "action_required": result["action_required"],
            "summary": result.get("summary", ""),
        }
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/match_clause/")
async def match_clause_api(clause_text: str = Form(...)):
    try:
        matcher = ClauseMatcher()
        match_result = matcher.match(clause_text)
        return match_result
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

@app.post("/generate_explanation")
async def generate_explanation_endpoint(clause: ClauseRequest):
    try:
        explanation = generate_explanation(
            clause.text,
            clause.category,
            clause.risk_level
        )
        return {"explanation": explanation}
    except Exception as e:
        raise HTTPException(500, f"Explanation failed: {str(e)}")

@app.post("/analyze_document/")
async def analyze_document_api(clauses: List[Clause]):
    try:
        # Placeholder: just return the number of clauses and a dummy risk
        summary = {
            "total_clauses": len(clauses),
            "overall_risk": "Unknown",
            "missing_clauses": [],
        }
        return {"summary": summary}
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})

def add_clause_section(pdf, clause):
    pdf.set_font('Arial', 'B', 12)
    pdf.multi_cell(0, 8, clause.get('title', 'Untitled'), align=Align.L, new_x="LMARGIN", new_y="CURRENT")
    # Category, Risk, Confidence
    pdf.set_font('Arial', '', 10)
    pdf.cell(0, 8, f"Category: {clause.get('category', '-')} | Risk Level: {clause.get('risk_level', '-').title()} | Confidence: {clause.get('confidence', 0)}%", ln=True)
    # Key Points
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 8, "Key Points:", ln=True)
    pdf.set_font('Arial', '', 10)
    for point in clause.get('key_points', []):
        clean_point = re.sub(r'Category:.*?Risk Level:.*?Key Points:', '', point, flags=re.IGNORECASE)
        clean_point = re.sub(r'Page \d+ Legal Document Analysis Report', '', clean_point, flags=re.IGNORECASE)
        clean_point = re.sub(r'\[Content omitted due to layout issue\]', '', clean_point, flags=re.IGNORECASE)
        pdf.multi_cell(0, 5, f"- {clean_point.strip()}", align=Align.L, new_x="LMARGIN", new_y="CURRENT")
    # Action Required
    pdf.set_font('Arial', 'B', 10)
    pdf.cell(0, 8, "Actions Required:", ln=True)
    pdf.set_font('Arial', '', 10)
    for action in clause.get('action_required', []):
        pdf.multi_cell(0, 5, f"- {action}", align=Align.L, new_x="LMARGIN", new_y="CURRENT")
    # Explanation
    if clause.get('explanation'):
        pdf.set_font('Arial', 'B', 10)
        pdf.cell(0, 8, "Explanation:", ln=True)
        pdf.set_font('Arial', '', 10)
        pdf.multi_cell(0, 5, clause.get('explanation', ''), align=Align.L, new_x="LMARGIN", new_y="CURRENT")
    if clause.get('confidence') is not None:
        pdf.set_font("helvetica", "B", 10)
        pdf.multi_cell(0, 5, f"Confidence Score: {clause['confidence']}%")
    pdf.ln(2)

@app.post("/generate_report/")
async def generate_report_api(analysis: dict):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)
    pdf.cell(0, 10, "Legal Document Analysis Report", ln=True, align="C")
    pdf.ln(10)
    for clause in analysis.get("clauses", []):
        add_clause_section(pdf, clause)
    buf = io.BytesIO()
    pdf.output(buf)
    buf.seek(0)
    return StreamingResponse(buf, media_type="application/pdf", headers={"Content-Disposition": "attachment; filename=Legal_Document_Analysis_Report.pdf"}) 