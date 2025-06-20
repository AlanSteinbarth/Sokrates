<p align="center">
  <img src="Screenshots/okladka_sokrates2.png" alt="Okładka projektu Sokrates" width="900"/>
</p>

# 🧠 Sokrates - Twój cyfrowy nauczyciel 🤖

![Python](https://img.shields.io/badge/python-v3.8+-blue.svg)
![Streamlit](https://img.shields.io/badge/streamlit-v1.28+-red.svg)
![OpenAI](https://img.shields.io/badge/openai-gpt--4o--mini-green.svg)
![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Status](https://img.shields.io/badge/status-production-brightgreen.svg)
![Commits](https://img.shields.io/github/commit-activity/m/AlanSteinbarth/Sokrates)
![Last Commit](https://img.shields.io/github/last-commit/AlanSteinbarth/Sokrates)

> *"Wiem, że nic nie wiem"* - Sokrates

🧠 Sokrates - Twój cyfrowy nauczyciel 🤖 to inteligentna aplikacja nauczająca wykorzystująca metodę sokratejską. Zamiast podawać gotowe odpowiedzi, prowadzi uczniów do samodzielnego odkrywania wiedzy przez przemyślane pytania prowadzące.

## 🎬 Demo & Live Preview

<!-- - **🔗 Live Demo:** [Uruchom aplikację](http://localhost:8501) (po instalacji lokalnej) -->
<!-- - **📺 Video Demo:** [Zobacz jak działa Sokrates](https://youtu.be/your-demo-video) *(dodaj link do wideo)* -->
- **⚡ Quick Start:** Aplikacja gotowa w 2 minuty - zobacz [Szybki Start](#-szybki-start)

## ✨ Funkcje

### 🎯 Metoda Sokratejska
- **Pytania prowadzące** zamiast gotowych odpowiedzi
- **Progresywny system pomocy** z licznikiem "nie wiem" (0-4)
- **Personalizowane nauczanie** dostosowane do stylu uczenia się

### 👤 Profile Uczniów
- **Indywidualne konta** z osobną pamięcią dla każdego ucznia
- **Automatyczne wykrywanie** faktów o stylu nauki
- **Lokalne przechowywanie** danych zgodnie z RODO

### 💡 Inteligentny System Pomocy
- **0-2 "nie wiem"**: Tylko pytania prowadzące
- **3 "nie wiem"**: Wskazówki i częściowe odpowiedzi
- **4+ "nie wiem"**: Pełna odpowiedź z wyjaśnieniem
- **Przycisk "Udziel odpowiedzi teraz"** do omijania procesu

### 📊 Monitoring i Analityka
- **Śledzenie kosztów** API w PLN
- **Historia nauki** z możliwością edycji
- **Przejrzysty interfejs** z intuicyjną nawigacją

## 🚀 Szybki Start

### Wymagania
- Python 3.8+
- Klucz API OpenAI
- Streamlit

### Instalacja

1. **Sklonuj repozytorium:**
```bash
git clone https://github.com/AlanSteinbarth/Sokrates.git
cd Sokrates
```

2. **Zainstaluj zależności:**
```bash
pip install -r requirements.txt
```

3. **Skonfiguruj zmienne środowiskowe:**
```bash
cp .env.example .env
# Edytuj .env i dodaj swój klucz OpenAI API
```

4. **Uruchom aplikację:**
```bash
streamlit run app.py
```

5. **Otwórz w przeglądarce:**
```
http://localhost:8501
```

## 🎓 Jak używać

### Logowanie
1. Podaj swoje imię na stronie głównej
2. Kliknij "🚀 Start" aby rozpocząć naukę

### Nauka metodą sokratejską
1. **Zadaj pytanie** w polu czatu
2. **Odpowiadaj na pytania** prowadzące Sokratesa
3. **Powiedz "nie wiem"** gdy potrzebujesz pomocy
4. **Używaj przycisku "Udziel odpowiedzi teraz"** do pominięcia procesu

### Zarządzanie profilem
- **Automatyczne wykrywanie**: System analizuje Twoje odpowiedzi
- **Potwierdzanie faktów**: Wybierz, co chcesz zapisać
- **Edycja profilu**: Usuń nieaktualne informacje przyciskiem 🗑️

## 🔧 Konfiguracja

### Zmienne środowiskowe (.env)
```bash
OPENAI_API_KEY=sk-your-api-key-here
```

### Struktura projektu
```
Sokrates/
├── app.py                 # Główna aplikacja
├── requirements.txt       # Zależności Python
├── .env.example          # Przykładowa konfiguracja
├── README.md             # Dokumentacja
├── LICENSE               # Licencja MIT
└── db/                   # Baza danych
    ├── students/         # Profile uczniów
    └── conversations/    # Historia rozmów
```

## 🏗️ Architektura Techniczna

### Stack Technologiczny
- **Frontend:** Streamlit (Python web framework)
- **Backend:** Python 3.8+
- **AI/ML:** OpenAI GPT-4o-mini API
- **Data Storage:** JSON files (RODO-compliant)
- **Environment:** Cross-platform (Windows, macOS, Linux)

### Kluczowe Komponenty
- **Socratic Engine:** Logika pytań prowadzących z progresywnym systemem pomocy
- **Memory System:** Personalizacja na podstawie profilu ucznia
- **Cost Tracker:** Monitoring kosztów API w czasie rzeczywistym
- **Admin Panel:** Zarządzanie użytkownikami i statystyki

## 📑 Spis treści
- [Demo & Live Preview](#-demo--live-preview)
- [Funkcje](#-funkcje)
- [Szybki Start](#-szybki-start)
- [Jak używać](#-jak-używać)
- [Architektura Techniczna](#️-architektura-techniczna)
- [Konfiguracja](#-konfiguracja)
- [Kompatybilność z systemami operacyjnymi](#️-kompatybilność-z-systemami-operacyjnymi)
- [Prywatność i RODO](#-prywatność-i-rodo)
- [Roadmapa Rozwoju](#-roadmapa-rozwoju)
- [Zrzuty ekranu](#️-przykładowe-zrzuty-ekranu)
- [Współpraca](#-współpraca)
- [Licencja](#-licencja)
- [Autor](#️-autor)
- [Podziękowania](#-podziękowania)
- [Statystyki](#-statystyki)

## 🖥️ Kompatybilność z systemami operacyjnymi

Aplikacja Sokrates działa na wszystkich głównych systemach operacyjnych: **Windows, Linux, macOS**.
- Do obsługi plików wykorzystywany jest `pathlib`, co zapewnia przenośność ścieżek.
- Pliki zapisywane są w kodowaniu UTF-8.
- Testy automatyczne sprawdzają poprawność zapisu/odczytu profilu ucznia na różnych OS.

### Testowanie kompatybilności

Aby uruchomić testy sprawdzające działanie na Twoim systemie:
```bash
pip install pytest
pytest test_cross_os.py
```

Wszelkie błędy zgłaszaj przez [GitHub Issues](https://github.com/AlanSteinbarth/Sokrates/issues).

## 🔒 Prywatność i RODO

### Bezpieczeństwo danych
- **Lokalne przechowywanie**: Wszystkie dane pozostają na Twoim urządzeniu
- **Brak wysyłania**: Dane nie są przekazywane na zewnętrzne serwery
- **Pełna kontrola**: Możesz przeglądać, edytować i usuwać swoje dane
- **Transparentność**: Widzisz wszystko, co system o Tobie wie

### Co jest zapisywane
- Poziom wiedzy w różnych dziedzinach
- Sposób uczenia się i preferencje
- Trudności w nauce i postępy
- Zainteresowania naukowe

### Co NIE jest zapisywane
- Dane osobowe (adres, telefon, email)
- Informacje wrażliwe
- Pełna historia rozmów

## 🤝 Współpraca

Chcesz pomóc w rozwoju projektu? Świetnie! Zobacz [CONTRIBUTING.md](CONTRIBUTING.md) po szczegóły.

### Zgłaszanie błędów
Użyj [GitHub Issues](https://github.com/AlanSteinbarth/Sokrates/issues) do zgłoszenia problemu.

### Propozycje funkcji
Prześlij [Pull Request](https://github.com/AlanSteinbarth/Sokrates/pulls) lub otwórz Issue z opisem.

## 📝 Licencja

Ten projekt jest licencjonowany na licencji MIT - zobacz plik [LICENSE](LICENSE) po szczegóły.

## 👨‍💻 Autor

**Alan Steinbarth**
- Email: [alan.steinbarth@gmail.com](mailto:alan.steinbarth@gmail.com)
- GitHub: [@AlanSteinbarth](https://github.com/AlanSteinbarth)

## 🙏 Podziękowania

- OpenAI za API GPT-4o-mini
- Streamlit za framework UI
- Społeczność Python za niesamowite biblioteki

## 📊 Statystyki

- **Wersja**: 2.3.0
- **Status**: Produkcyjna
- **Język**: Polski
- **Framework**: Streamlit
- **AI Model**: GPT-4o-mini
- **Data wydania**: 17.06.2025

---

> 💡 **Wskazówka**: Sokrates działa najlepiej gdy jesteś otwarty na myślenie i eksplorację! Nie bój się powiedzieć "nie wiem" - to właśnie napędza proces nauki.

## 🚀 Roadmapa Rozwoju

### Planowane Funkcje
- [ ] Export profilu ucznia (JSON, CSV, PDF)
- [ ] Dashboard z wykresami postępów
- [ ] Tryb offline z podstawową funkcjonalnością  
- [ ] API dla integracji z LMS
- [ ] Wsparcie dla większej liczby modeli AI
- [ ] Testy jednostkowe i integracyjne

### Zrealizowane w v2.3.0
- [x] ✅ Panel administracyjny z statystykami
- [x] ✅ System zarządzania profilami uczniów
- [x] ✅ Monitoring kosztów API
- [x] ✅ Cross-platform compatibility

## 🖼️ Przykładowe zrzuty ekranu

<p align="center">
  <img src="Screenshots/Zrzut%20ekranu%202025-06-17%20o%2022.45.50.png" width="700"/>
</p>
<p align="center">
  <img src="Screenshots/Zrzut%20ekranu%202025-06-17%20o%2022.46.22.png" width="700"/>
</p>
<p align="center">
  <img src="Screenshots/Zrzut%20ekranu%202025-06-17%20o%2022.46.42.png" width="700"/>
</p>
<p align="center">
  <img src="Screenshots/Zrzut%20ekranu%202025-06-17%20o%2022.48.05.png" width="700"/>
</p>
<p align="center">
  <img src="Screenshots/Zrzut%20ekranu%202025-06-17%20o%2022.48.30.png" width="700"/>
</p>
<p align="center">
  <img src="Screenshots/Zrzut%20ekranu%202025-06-17%20o%2022.49.51.png" width="700"/>
</p>
