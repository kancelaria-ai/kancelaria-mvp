from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
from openai import OpenAI
from dotenv import load_dotenv

import os
import logging
from io import BytesIO
import docx
import tiktoken

def truncate_text_to_tokens(text: str, max_tokens: int = 6000) -> str:
    """Skraca tekst tak, aby nie przekroczyć limitu tokenów modelu GPT."""
    encoding = tiktoken.encoding_for_model("gpt-4o")
    tokens = encoding.encode(text)
    if len(tokens) > max_tokens:
        truncated = tokens[:max_tokens]
        return encoding.decode(truncated)
    return text
def count_tokens(text: str, model: str = "gpt-4o") -> int:
    encoding = tiktoken.encoding_for_model(model)
    return len(encoding.encode(text))

# === Init FastAPI + load env ===
app = FastAPI()
load_dotenv()

# === OpenAI client ===
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("Brakuje klucza OPENAI_API_KEY w pliku .env")

client = OpenAI(api_key=api_key)

# === Pydantic response model ===
class TemplateAnalysisResponse(BaseModel):
    summary: str
    issues_found: list[str]
    fields_to_fill: list[str]

# === DOCX to text ===
def extract_text_from_docx(file_binary: bytes) -> str:
    doc = docx.Document(BytesIO(file_binary))
    return "\n".join([p.text for p in doc.paragraphs if p.text.strip()])

# === GPT-4o analysis ===
def analyze_template_with_gpt(text: str) -> TemplateAnalysisResponse:
    prompt = f"""
Przeanalizuj poniższy szablon umowy. Podaj:
1. Krótkie podsumowanie, czego dotyczy dokument.
2. Wypunktuj potencjalne problemy prawne.
3. Wypunktuj miejsca do uzupełnienia (np. daty, dane stron).

Szablon:
{text}
"""
    # Count and print number of tokens before truncation
    print("🔎 Tokeny w oryginalnym dokumencie:", count_tokens(text))

    # Truncate long text
    text = truncate_text_to_tokens(text)

    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "Jesteś prawnikiem analizującym umowy."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    content = response.choices[0].message.content

    # Parsuj odpowiedź – tymczasowo po prostu splituj
    summary, *rest = content.split("\n\n", 2)
    issues_found = rest[0].split("\n") if len(rest) > 0 else []
    fields_to_fill = rest[1].split("\n") if len(rest) > 1 else []

    return TemplateAnalysisResponse(
        summary=summary.strip(),
        issues_found=[s.strip("-• ").strip() for s in issues_found if s.strip()],
        fields_to_fill=[s.strip("-• ").strip() for s in fields_to_fill if s.strip()],
    )

# === Endpoint ===
@app.post("/analyze-template", response_model=TemplateAnalysisResponse)
async def analyze_template(file: UploadFile = File(...)):
    if not file.filename.lower().endswith(".docx"):
        raise HTTPException(status_code=400, detail="Wymagany plik .docx")

    try:
        binary = await file.read()
        text = extract_text_from_docx(binary)
        result = analyze_template_with_gpt(text)
        return result

    except Exception as e:
        logging.exception("Błąd analizy")
        raise HTTPException(status_code=500, detail=f"Błąd serwera: {str(e)}")

# === Health-check ===
@app.get("/health")
def health():
    return {"ok": True}

