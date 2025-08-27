# kancelaria-mvp

Prosty agent AI analizujący szablony umów.

## 🔍 Opis

Ten projekt to prototyp agenta AI, który:

1. Generuje podsumowanie dokumentu.
2. Wypunktowuje potencjalne problemy prawne.
3. Wskazuje miejsca wymagające uzupełnienia (np. daty, strony).

Działa lokalnie w środowisku FastAPI z integracją OpenAI GPT-4o.

## 📁 Pliki

- `main.py` – logika analizy dokumentu `.docx`
- `.env` – zmienne środowiskowe (API key)
- `.gitignore` – ignorowane pliki
- `venv/` – środowisko wirtualne (lokalnie)

## 🧠 Wymagania

- Python 3.10+
- FastAPI
- Uvicorn
- OpenAI SDK

## 🛠️ Uruchomienie

```bash
uvicorn main:app --reload
