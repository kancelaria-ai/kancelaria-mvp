from openai import OpenAI
import logging
import os
from dotenv import load_dotenv

# Wczytaj zmienne środowiskowe
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Konfiguracja logowania
logging.basicConfig(
    filename="analysis.log",
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

def analyze_template_with_gpt(text: str) -> dict:
    prompt = f"""
Zanalizuj następujący tekst umowy i wygeneruj analizę w formacie JSON zawierającym:
- "contract_type": Typ umowy
- "summary": Krótkie podsumowanie umowy
- "key_clauses": Lista najważniejszych postanowień
- "issues_found": Lista potencjalnych problemów prawnych
- "risks": Lista ryzyk dla klienta
- "recommendations": Lista rekomendacji

Tekst umowy:
{text}
"""

    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Jesteś prawnikiem analizującym umowy."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.3,
        )

        content = response.choices[0].message.content

        # Loguj prompt i odpowiedź
        logging.info(f"PROMPT:\n{prompt}")
        logging.info(f"RESPONSE:\n{content}")

        import json
        return json.loads(content)

    except Exception as e:
        logging.error(f"GPT ERROR: {str(e)}")

        # Fallback - prosta analiza offline
        return {
            "contract_type": "Nieznany typ umowy",
            "summary": "Nie udało się przeprowadzić analizy za pomocą GPT.",
            "key_clauses": [],
            "issues_found": [],
            "risks": [],
            "recommendations": [],
        }
