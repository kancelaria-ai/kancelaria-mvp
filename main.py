from typing import List, Tuple
import re
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from settings import settings
from fastapi import File, UploadFile, HTTPException
from io import BytesIO
import mimetypes

import pdfplumber          # PDF → tekst
from docx import Document  # DOCX → tekst

app = FastAPI(title=settings.APP_NAME, version=settings.VERSION)

# ===== Schematy =====
class AnalyzeTextRequest(BaseModel):
    text: str

class AnalyzeTextResponse(BaseModel):
    anonymized_text: str
    entities_found: List[str]

# ===== proste wzorce (MVP) =====
PL = {
    "EMAIL": "EMAIL", "TELEFON": "TELEFON", "NIP": "NIP",
    "PESEL": "PESEL", "KRS": "KRS", "FIRMA": "FIRMA",
    "ADRES": "ADRES", "OSOBA": "OSOBA",
}

def _compile() -> List[Tuple[str, re.Pattern]]:
    flags = re.IGNORECASE | re.UNICODE

    return [
        ("EMAIL",   re.compile(r"\b[a-z0-9._%+-]+@[a-z0-9.-]+\.[a-z]{2,}\b", flags)),
        # najpierw specyficzne cyfrowe, potem telefon:
        ("PESEL",   re.compile(r"\b\d{11}\b", flags)),
        ("NIP", re.compile(r"\b\d{3}[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}\b", flags)),
        ("TELEFON", re.compile(r"(?:\+?\d{1,3}[\s-]?)?(?:\(?\d{2,3}\)?[\s-]?)?\d{3}[\s-]?\d{3}[\s-]?\d{3,4}\b", flags)),
    ]

PATTERNS: List[Tuple[str, re.Pattern]] = _compile()

@app.get("/health")
def health():
    return {"ok": True}

def anonymize(text: str) -> AnalyzeTextResponse:
    entities_found: set[str] = set()
    anonymized_text = text

    def replace_and_mark(entity: str, pattern: re.Pattern, s: str) -> str:
        def _sub(m: re.Match) -> str:
            entities_found.add(entity)
            return f"[{entity}]"
        return pattern.sub(_sub, s)

    for entity, pattern in PATTERNS:
        anonymized_text = replace_and_mark(entity, pattern, anonymized_text)

    return AnalyzeTextResponse(
        anonymized_text=anonymized_text,
        entities_found=sorted(list(entities_found), key=str.upper),
    )
# ====== Ekstrakcja tekstu z plików ======

MAX_FILE_MB = 15  # prosty limit wielkości (możesz zmienić)

PDF_MIMES = {
    "application/pdf", "application/x-pdf", "application/acrobat",
    "applications/pdf", "text/pdf"
}

DOCX_MIMES = {
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/msword"
}

PLAIN_MIMES = {"text/plain", "application/octet-stream"}


def _extract_text_from_pdf(binary: bytes) -> str:
    """PDF → tekst (działa na „tekstowych” PDF-ach; skany = OCR później)."""
    with pdfplumber.open(BytesIO(binary)) as pdf:
        pages = []
        for p in pdf.pages:
            try:
                pages.append(p.extract_text() or "")
            except Exception:
                pages.append("")
        return "\n".join(pages)


def _extract_text_from_docx(binary: bytes) -> str:
    """DOCX → tekst."""
    doc = Document(BytesIO(binary))
    return "\n".join([p.text for p in doc.paragraphs])


def _guess_content_type(filename: str, declared: str | None) -> str | None:
    """Ustal MIME: najpierw z UploadFile, a jak brak – po rozszerzeniu."""
    if declared:
        return declared
    guessed, _ = mimetypes.guess_type(filename)
    return guessed

@app.post("/analyze-text", response_model=AnalyzeTextResponse, summary="Analyze Text")
def analyze_text(request: AnalyzeTextRequest) -> AnalyzeTextResponse:
    return anonymize(request.text)

# /analyze-file dodamy jutro (PDF/DOCX -> tekst -> anonymize)
@app.post("/analyze-file", response_model=AnalyzeTextResponse, summary="Analyze file (PDF/DOCX/TXT)")
async def analyze_file(file: UploadFile = File(...)) -> AnalyzeTextResponse:
    # rozmiar
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Plik jest pusty.")
    if len(data) > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Plik > {MAX_FILE_MB} MB.")

    # typ pliku
    ctype = _guess_content_type(file.filename, file.content_type)

    # ekstrakcja
    text = ""
    if ctype in PDF_MIMES or (file.filename or "").lower().endswith(".pdf"):
        text = _extract_text_from_pdf(data)
    elif ctype in DOCX_MIMES or (file.filename or "").lower().endswith(".docx"):
        text = _extract_text_from_docx(data)
    elif ctype in PLAIN_MIMES or (file.filename or "").lower().endswith(".txt"):
        text = data.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(
            status_code=415,
            detail=f"Nieobsługiwany typ pliku: {ctype or 'nieznany'}. Dopuszczalne: PDF, DOCX, TXT."
        )

    if not text or not text.strip():
        raise HTTPException(status_code=422, detail="Nie udało się wyodrębnić tekstu z pliku.")

    # ponowne użycie naszej logiki
    return anonymize(text)
@app.post("/analyze-file", response_model=AnalyzeTextResponse, summary="Analyze file (PDF/DOCX/TXT)")
async def analyze_file(file: UploadFile = File(...)) -> AnalyzeTextResponse:
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="Plik jest pusty.")

    if len(data) > MAX_FILE_MB * 1024 * 1024:
        raise HTTPException(status_code=413, detail=f"Plik > {MAX_FILE_MB} MB.")

    ctype = _guess_content_type(file.filename, file.content_type)

    if ctype in PDF_MIMES or (file.filename or "").lower().endswith(".pdf"):
        text = _extract_text_from_pdf(data)
    elif ctype in DOCX_MIMES or (file.filename or "").lower().endswith(".docx"):
        text = _extract_text_from_docx(data)
    elif ctype in PLAIN_MIMES or (file.filename or "").lower().endswith(".txt"):
        text = data.decode("utf-8", errors="ignore")
    else:
        raise HTTPException(
            status_code=415,
            detail=f"Nieobsługiwany typ pliku: {ctype or 'nieznany'}. Dopuszczalne: PDF, DOCX, TXT."
        )

    if not text or not text.strip():
        raise HTTPException(status_code=422, detail="Nie udało się wyodrębnić tekstu z pliku.")

    return anonymize(text)
