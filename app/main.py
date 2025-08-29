from fastapi import FastAPI, UploadFile, File, HTTPException, Request
from fastapi.responses import HTMLResponse, JSONResponse, PlainTextResponse
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
from docx import Document
from io import BytesIO
import os

app = FastAPI()

# Ścieżka do szablonów HTML
templates = Jinja2Templates(directory="app/templates")

# ======= FORMULARZ STARTOWY =======
@app.get("/", response_class=HTMLResponse)
async def form_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# =============== FUNKCJA ANALIZUJĄCA SZABLON ===============
def analyze_template_with_gpt(text: str):
    # ⚠️ Tymczasowe dane testowe (na później zastąpi GPT)
    return {
        "contract_type": "Umowa najmu okazjonalnego lokalu mieszkalnego",
        "summary": "Umowa regulująca zasady najmu lokalu mieszkalnego z opcją uproszczonej egzekucji po jej rozwiązaniu.",
        "key_clauses": [
            "Obowiązek opróżnienia lokalu po rozwiązaniu umowy",
            "Załącznik z oświadczeniem najemcy",
            "Czas trwania umowy – maksymalnie 10 lat",
        ],
        "issues_found": [
            "Brak klauzuli RODO",
            "Nieaktualna data wejścia w życie"
        ],
        "risks": [
            "Brak możliwości jednostronnego wypowiedzenia",
            "Zbyt wysokie kary umowne dla najemcy"
        ],
        "recommendations": [
            "Rozważyć dodanie zapisu o waloryzacji czynszu",
            "Zamienić 'kara umowna' na 'odszkodowanie zryczałtowane'"
        ],
        "fields_to_fill": [
            "[imię i nazwisko]",
            "[data]",
            "[nazwa firmy]"
        ]
    }


# ========== ENDPOINT: ANALIZA I WYNIK HTML ==========
@app.post("/analyze-template/html", response_class=HTMLResponse)
async def analyze_template_html(request: Request, file: UploadFile = File(...)):
    try:
        contents = await file.read()
        document = Document(BytesIO(contents))
        full_text = "\n".join([para.text for para in document.paragraphs])

        analysis = analyze_template_with_gpt(full_text)

        return templates.TemplateResponse("analysis_result.html", {
            "request": request,
            "contract_type": analysis["contract_type"],
            "summary": analysis["summary"],
            "key_clauses": analysis["key_clauses"],
            "issues_found": analysis["issues_found"],
            "risks": analysis["risks"],
            "recommendations": analysis["recommendations"],
            "fields_to_fill": analysis["fields_to_fill"],
        })

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Błąd analizy: {str(e)}")


# ========== ENDPOINT TECHNICZNY ==========
@app.get("/health")
def health_check():
    return {"status": "ok"}
