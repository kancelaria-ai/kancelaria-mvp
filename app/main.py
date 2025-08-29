from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse, StreamingResponse
from fastapi.templating import Jinja2Templates
from docx import Document
from io import BytesIO
import os

from app.analyze_template import analyze_template_with_gpt

app = FastAPI()

# Ścieżka do szablonów HTML
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
templates = Jinja2Templates(directory=os.path.join(BASE_DIR, "templates"))

# ======== STRONA GŁÓWNA ========
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# ======== ANALIZA I WYNIK HTML ========
@app.post("/analyze-template/html")
async def analyze_template_html(request: Request, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        document = Document(BytesIO(contents))
        full_text = "\n".join([para.text for para in document.paragraphs])
        result = analyze_template_with_gpt(full_text)
        return templates.TemplateResponse("analysis_result.html", {"request": request, **result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd analizy (HTML): {str(e)}")

# ======== ANALIZA I WYNIK JSON ========
@app.post("/analyze-template/json")
async def analyze_template_json(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        document = Document(BytesIO(contents))
        full_text = "\n".join([para.text for para in document.paragraphs])
        result = analyze_template_with_gpt(full_text)
        return JSONResponse(content=result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd analizy (JSON): {str(e)}")

# ======== ANALIZA I WYNIK TXT ========
@app.post("/analyze-template/txt")
async def analyze_template_txt(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        document = Document(BytesIO(contents))
        full_text = "\n".join([para.text for para in document.paragraphs])
        result = analyze_template_with_gpt(full_text)

        output = "\n".join([
            f"Rodzaj umowy: {result.get('contract_type', '')}",
            f"Podsumowanie: {result.get('summary', '')}",
            "Najważniejsze postanowienia:",
            *[f"- {item}" for item in result.get('key_clauses', [])],
            "Problemy prawne:",
            *[f"- {item}" for item in result.get('issues_found', [])],
            "Ryzyka:",
            *[f"- {item}" for item in result.get('risks', [])],
            "Rekomendacje:",
            *[f"- {item}" for item in result.get('recommendations', [])],
            "Pola do uzupełnienia:",
            *[f"- {item}" for item in result.get('fields_to_fill', [])],
        ])

        return PlainTextResponse(content=output)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd analizy (TXT): {str(e)}")

# ======== ANALIZA I WYNIK DOCX ========
@app.post("/analyze-template-docx")
async def analyze_template_docx(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        document = Document(BytesIO(contents))
        full_text = "\n".join([para.text for para in document.paragraphs])
        result = analyze_template_with_gpt(full_text)

        from docx import Document as DocxDocument
        from tempfile import NamedTemporaryFile

        doc = DocxDocument()
        doc.add_heading("Wynik analizy dokumentu", level=1)
        doc.add_paragraph(f"Rodzaj umowy: {result.get('contract_type', '')}")
        doc.add_paragraph(f"Podsumowanie: {result.get('summary', '')}")

        sections = [
            ("Najważniejsze postanowienia", result.get("key_clauses", [])),
            ("Problemy prawne", result.get("issues_found", [])),
            ("Ryzyka", result.get("risks", [])),
            ("Rekomendacje", result.get("recommendations", [])),
            ("Pola do uzupełnienia", result.get("fields_to_fill", [])),
        ]

        for title, items in sections:
            doc.add_heading(title, level=2)
            for item in items:
                doc.add_paragraph(item, style="List Bullet")

        temp = NamedTemporaryFile(delete=False, suffix=".docx")
        doc.save(temp.name)
        temp.seek(0)

        return StreamingResponse(
            temp,
            media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
            headers={"Content-Disposition": "attachment; filename=wynik_analizy.docx"}
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd analizy (DOCX): {str(e)}")
