# 🤝 Przewodnik Współpracy - Sokrates

Dziękujemy za zainteresowanie współpracą przy projekcie Sokrates! Ten przewodnik pomoże Ci zacząć.

## 🚀 Szybki Start dla Deweloperów

### Przygotowanie środowiska

1. **Forkuj repozytorium**
```bash
# Sklonuj swój fork
git clone https://github.com/TWOJ_USERNAME/Sokrates.git
cd Sokrates
```

2. **Skonfiguruj lokalne środowisko**
```bash
# Utwórz wirtualne środowisko
python -m venv venv
source venv/bin/activate  # Linux/Mac
# lub
venv\Scripts\activate     # Windows

# Zainstaluj zależności
pip install -r requirements.txt
```

3. **Skonfiguruj zmienne środowiskowe**
```bash
cp .env.example .env
# Dodaj swój klucz OpenAI API do .env
```

4. **Przetestuj aplikację**
```bash
streamlit run app.py
```

## 🎯 Jak Przyczynić się do Projektu

### 🐛 Zgłaszanie Błędów

Znalazłeś błąd? Pomóż nam go naprawić!

1. **Sprawdź czy błąd już nie został zgłoszony** w [Issues](https://github.com/AlanSteinbarth/Sokrates/issues)
2. **Utwórz nowy Issue** z następującymi informacjami:
   - Jasny, opisowy tytuł
   - Kroki do reprodukcji błędu
   - Oczekiwane vs rzeczywiste zachowanie
   - Zrzuty ekranu (jeśli pomocne)
   - Informacje o środowisku (OS, Python, wersja przeglądarki)

#### Szablon zgłoszenia błędu:
```markdown
**Opis błędu**
Krótki opis tego, co się dzieje.

**Kroki do reprodukcji**
1. Przejdź do '...'
2. Kliknij na '...'
3. Przewiń do '...'
4. Zobacz błąd

**Oczekiwane zachowanie**
Jasny opis tego, co powinno się stać.

**Zrzuty ekranu**
Jeśli dotyczy, dodaj zrzuty ekranu wyjaśniające problem.

**Środowisko:**
- OS: [np. Windows 10, macOS Big Sur, Ubuntu 20.04]
- Python: [np. 3.9.0]
- Przeglądarka: [np. Chrome 91, Firefox 89]
```

### ✨ Propozycje Nowych Funkcji

Masz pomysł na ulepszenie? Podziel się nim!

1. **Sprawdź roadmapę** w Issues z etykietą `enhancement`
2. **Otwórz Feature Request** z opisem:
   - Problem, który funkcja rozwiązuje
   - Proponowane rozwiązanie
   - Alternatywne rozwiązania
   - Dodatkowy kontekst

### 🔧 Rozwój Kodu

#### Struktura projektu
```
Sokrates/
├── app.py                 # Główna aplikacja Streamlit
├── requirements.txt       # Zależności Python
├── .env.example          # Przykładowa konfiguracja
├── .gitignore            # Pliki ignorowane przez git
├── README.md             # Dokumentacja główna
├── CONTRIBUTING.md       # Ten plik
├── LICENSE               # Licencja MIT
├── CHANGELOG.md          # Historia zmian
└── db/                   # Lokalna baza danych
    ├── students/         # Profile uczniów (ignorowane przez git)
    └── conversations/    # Historia rozmów (ignorowane przez git)
```

#### Standardy kodowania

**Python (PEP 8)**
- Używaj 4 spacji do wcięć
- Maksymalna długość linii: 88 znaków
- Importy w kolejności: standard library, third-party, local
- Dokumentuj funkcje za pomocą docstrings

**Przykład dobrej funkcji:**
```python
def get_student_memory_file(student_name: str) -> Path:
    """
    Zwraca ścieżkę do pliku pamięci dla konkretnego ucznia.
    
    Args:
        student_name (str): Imię ucznia
        
    Returns:
        Path: Ścieżka do pliku pamięci ucznia
        
    Note:
        Nazwa pliku jest sanityzowana dla bezpieczeństwa systemu plików.
    """
    students_dir = Path("db/students")
    students_dir.mkdir(parents=True, exist_ok=True)
    safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_').lower()
    return students_dir / f"{safe_name}_memory.json"
```

**Streamlit**
- Używaj session_state do przechowywania stanu
- Komentuj sekcje UI wyraźnie
- Testuj responsywność interfejsu

#### Proces Pull Request

1. **Utwórz branch dla swojej funkcji**
```bash
git checkout -b feature/nazwa-funkcji
# lub
git checkout -b bugfix/nazwa-błędu
```

2. **Wprowadź zmiany**
   - Pisz czysty, udokumentowany kod
   - Dodaj komentarze w kluczowych miejscach
   - Testuj zmiany lokalnie

3. **Zatwierdź zmiany**
```bash
git add .
git commit -m "feat: dodaj nową funkcję X"
# lub
git commit -m "fix: napraw błąd Y"
```

**Konwencja commitów:**
- `feat:` - nowa funkcja
- `fix:` - naprawa błędu
- `docs:` - zmiany w dokumentacji
- `style:` - formatowanie, brak zmian w logice
- `refactor:` - refaktoryzacja kodu
- `test:` - dodanie testów
- `chore:` - zmiany w buildzie, zależnościach

4. **Wypchnij zmiany**
```bash
git push origin feature/nazwa-funkcji
```

5. **Utwórz Pull Request**
   - Użyj jasnego, opisowego tytułu
   - Wyjaśnij co i dlaczego zmieniasz
   - Odnośnik do powiązanych Issues
   - Dodaj zrzuty ekranu dla zmian UI

#### Szablon Pull Request:
```markdown
## Opis
Krótki opis zmian i powodu ich wprowadzenia.

## Typ zmiany
- [ ] Naprawa błędu (zmiana, która naprawia problem)
- [ ] Nowa funkcja (zmiana, która dodaje funkcjonalność)
- [ ] Zmiana łamiąca (fix lub feature, która powoduje nieprawidłowe działanie istniejącej funkcjonalności)
- [ ] Aktualizacja dokumentacji

## Jak zostało przetestowane?
Opisz testy, które przeprowadziłeś.

## Checklist:
- [ ] Mój kod jest zgodny ze standardami projektu
- [ ] Dokonałem samodzielnego przeglądu kodu
- [ ] Skomentowałem kod w trudnych do zrozumienia miejscach
- [ ] Zaktualizowałem dokumentację
- [ ] Przetestowałem zmiany lokalnie
```

## 🎨 Obszary Pomocy

### Dla Programistów
- **Backend**: Optymalizacja logiki AI, zarządzanie stanem
- **Frontend**: Ulepszenia UI/UX w Streamlit
- **Dokumentacja**: Poprawki, tłumaczenia, przykłady

### Dla Edukatora/Pedagogów
- **Metodyka**: Ulepszenie metody sokratejskiej
- **Testy**: Testowanie z prawdziwymi uczniami
- **Feedback**: Propozycje pedagogiczne

### Dla Wszystkich
- **Tłumaczenia**: Wersje językowe
- **Testy**: Znajdowanie błędów
- **Feedback**: Propozycje użytkowników

## 📋 Priorytetowe Zadania

### High Priority
1. **Testy jednostkowe** - dodanie podstawowych testów
2. **Obsługa błędów** - lepsza obsługa problemów z API
3. **Performance** - optymalizacja dla większej liczby użytkowników

### Medium Priority
1. **Eksport danych** - możliwość eksportu profilu ucznia
2. **Statystyki nauki** - dashboard z postępami
3. **Tryb offline** - podstawowa funkcjonalność bez API

### Low Priority
1. **Motywów UI** - ciemny/jasny tryb
2. **Integracjie** - Google Classroom, Canvas
3. **Mobile app** - wersja mobilna

## 🤔 Pytania i Pomoc

### Masz pytania?
- **GitHub Discussions**: Najlepsze miejsce na pytania
- **Issues**: Dla konkretnych problemów
- **Email**: alan.steinbarth@gmail.com (dla pilnych spraw)

### Zasoby pomocne
- [Dokumentacja Streamlit](https://docs.streamlit.io/)
- [OpenAI API](https://platform.openai.com/docs/)
- [Python Style Guide](https://peps.python.org/pep-0008/)

## 🙏 Uznanie

Wszyscy współtwórcy będą wymienieni w README.md. Dziękujemy za każdy wkład!

---

**Miłego kodowania! 🚀**

*Zespół Sokrates*
