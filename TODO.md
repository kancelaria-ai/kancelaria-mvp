# ✅ TODO – Agent AI do analizy szablonów umów

Ostatnia aktualizacja: 2025-08-27

---

## 🔧 Status projektu

- ✅ Backend działa lokalnie (FastAPI)
- ✅ Analiza pliku `.docx` zwraca JSON z podsumowaniem, problemami prawnymi i miejscami do uzupełnienia
- ✅ Klucz API poprawnie używany (OpenAI GPT-4o)
- ✅ Projekt jest zsynchronizowany z repozytorium GitHub (`kancelaria-mvp`)
- 🔜 Brak prostego frontendowego interfejsu dla użytkownika

---

## 🔜 Do zrobienia (backend)

- [ ] Wprowadzenie ograniczeń długości tekstu wejściowego (tokenizacja)
- [ ] Walidacja typów dokumentów (odrzucanie .pdf, .odt itd.)
- [ ] Obsługa błędów API (np. brak klucza, timeout)
- [ ] Dodanie limitu rozmiaru pliku
- [ ] Zmiana kodu na nową wersję OpenAI SDK (`openai.ChatCompletion.create` ➝ `openai.chat.completions.create`)

---

## 🔜 Do zrobienia (frontend)

- [ ] Prosty interfejs użytkownika (upload .docx + przycisk „analizuj”)
- [ ] Wyświetlanie odpowiedzi modelu (3 sekcje: podsumowanie, problemy, pola do uzupełnienia)
- [ ] Obsługa błędów (np. brak pliku, zły format)
- [ ] Dodanie stylizacji (np. Tailwind lub prosty CSS)
- [ ] Integracja wielojęzyczna (PL / EN)

---

## 📄 Szablony i źródła

- [ ] Dodać listę przykładowych szablonów umów (najpierw prosty aneks, potem inne)
- [ ] Dodać linki do źródeł zewnętrznych (np. gov.pl, ngo.pl)
- [ ] Umieścić zastrzeżenie prawne: „Nie stanowi porady prawnej…”

---

## 🌍 Strona internetowa

- Domeny: `ai4firms.io`, `ai4firms.pl`
- Hosting: Hostinger (plan do rozszerzenia)
- Planowany frontend: WordPress + Polylang (PL / EN)
- Motyw: Astra lub podobny minimalistyczny

---

## 💡 Pomysły na później

- [ ] Google Docs jako źródło dokumentu (OAuth + API)
- [ ] Podświetlanie fragmentów wymagających uwagi w podglądzie `.docx`
- [ ] Eksport poprawionego dokumentu (z gotowymi polami do uzupełnienia)
- [ ] Lista lokalnych kancelarii prawnych (prosty katalog wyszukiwany po kodzie pocztowym)
- [ ] Chatbot AI wspierający tworzenie umowy od podstaw

---

## 📌 Autor

Projekt tworzony przez [JBTtranslateMe / AI4Firms.io] – z myślą o małych kancelariach prawnych i mikrofirmach szukających prostych rozwiązań z zakresu automatyzacji dokumentów.