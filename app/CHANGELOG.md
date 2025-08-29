# Changelog — AI4Firms MVP (analiza szablonów umów)

## [2025-08-29] Integracja GPT-4o + Rozszerzona analiza

### Nowe funkcje:
- 🔗 Połączono aplikację z OpenAI GPT-4o (via `analyze_template_with_gpt`)
- ✅ Dynamiczna analiza treści dokumentu `.docx` z wykrywaniem typu umowy i kluczowych elementów
- 📄 Dodano pełne wsparcie dla formatów:
  - HTML (`/analyze-template/html`)
  - JSON (`/analyze-template/json`)
  - TXT (`/analyze-template/txt`)
  - DOCX (generacja nowego dokumentu z wynikami analizy)

### Dodane sekcje w analizie:
- Rodzaj umowy (contract_type)
- Krótkie podsumowanie typu umowy (summary)
- Najważniejsze postanowienia (key_clauses)
- Problemy prawne (issues_found)
- Ryzyka dla klienta (risks)
- Rekomendacje AI (recommendations)
- Pola do uzupełnienia (fields_to_fill)

### Dodatkowe:
- 🪵 Logging: zapis pełnych promptów i odpowiedzi do pliku `analysis.log`
- 🛡️ Fallback do "analizy lokalnej" przy błędach połączenia z API
- 📦 Zaktualizowano zależności (`openai==1.102.0`)

---

## [2025-08-28] MVP v1 — podstawowy szkielet aplikacji

- ✅ Strona startowa z formularzem przesyłania pliku
- ✅ Analiza lokalna oparta na rozpoznaniu słów kluczowych
- 🧪 Proste szablony wynikowe w HTML, TXT i JSON

