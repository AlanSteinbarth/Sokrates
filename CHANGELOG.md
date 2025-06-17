# Changelog

Wszystkie istotne zmiany w projekcie 🧠 Sokrates - Twój cyfrowy nauczyciel 🤖 będą dokumentowane w tym pliku.

Format oparty na [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
a projekt stosuje [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planowane
- Testy jednostkowe dla głównych funkcji
- Eksport profilu ucznia do JSON/PDF
- Dashboard z statystykami postępów
- Tryb offline z podstawową funkcjonalnością

### Dodane
- Test automatyczny `test_cross_os.py` sprawdzający kompatybilność z Windows, Linux, macOS
- Dokumentacja: sekcja o kompatybilności systemowej i uruchamianiu testów cross-OS

## [2.3.0] - 2025-06-17

### Dodane
- Wersja produkcyjna: czyste środowisko, usunięte logi i profile testowe
- Spójna dokumentacja, aktualizacja wersji w README.md, CHANGELOG.md, app.py
- Poprawki lintera, docstringi, porządek w kodzie
- Ostateczne testy i przygotowanie do wdrożenia

### Usunięte
- Wszystkie pliki pamięci i logi testowe
- Niepotrzebne katalogi cache
- Placeholdery funkcji enterprise

## [2.2.0] - 2025-06-16

### Dodane
- Szczegółowy spis treści (TOC) i podział na sekcje w app.py
- Docstringi i opisy dla wszystkich funkcji
- Uporządkowanie kodu i sekcji w pliku głównym
- Aktualizacja dokumentacji (README, CONTRIBUTING, CHANGELOG)
- Status: produkcyjny, przygotowanie do wydania

### Usunięte
- Pliki tymczasowe, cache, testowe profile uczniów, logi

## [2.1.0] - 2025-05-25

### Dodane
- **GitHub Actions CI/CD**: Automatyczne testy jakości kodu, bezpieczeństwa i deploju
- **Issue Templates**: Profesjonalne szablony dla bug reportów, feature requestów i pytań
- **Pull Request Template**: Standardowy szablon dla pull requestów
- **Security Policy**: Instrukcje zgłaszania luk bezpieczeństwa
- **Code of Conduct**: Kodeks postępowania dla społeczności
- **Automatyczne release**: GitHub Actions tworzące automatyczne wydania

### Ulepszone
- **CI/CD Pipeline**: Pełna automatyzacja testów i kontroli jakości
- **Dokumentacja**: Profesjonalne templates dla współpracy open-source
- **Bezpieczeństwo**: Skanowanie zależności i kodu pod kątem vulnerabilities

## [2.0.0] - 2025-05-25

### Dodane
- **System logowania uczniów**: Każdy uczeń ma teraz osobny profil i plik pamięci
- **Metoda sokratejska**: Pełna implementacja nauczania przez pytania prowadzące
- **Licznik "nie wiem"**: Progresywny system pomocy (0-4 poziomy)
- **Profil ucznia**: Automatyczne wykrywanie i zapisywanie faktów o stylu nauki
- **FAQ/Pomoc**: Komprehensywne sekcje wyjaśniające działanie aplikacji
- **RODO compliance**: Informacje o przechowywaniu danych zgodnie z RODO
- **Lokalne przechowywanie**: Dane uczniów zapisywane lokalnie w `db/students/`
- **Koszty w PLN**: Przeliczenie kosztów API z USD na złotówki
- **Przycisk "Udziel odpowiedzi teraz"**: Możliwość pominięcia procesu sokratejskiego

### Zmienione
- **Interfejs użytkownika**: Kompletnie przeprojektowany sidebar i główny interfejs
- **Osobowość chatbota**: Sokratejska metoda nauczania zamiast bezpośrednich odpowiedzi
- **System pamięci**: Przejście z globalnej pamięci na indywidualne profile uczniów
- **Walidacja danych**: Lepsza sanityzacja nazw plików i obsługa błędów

### Naprawione
- **Obsługa None values**: Poprawiono błędy z wartościami None w odpowiedziach API
- **Type checking**: Dodano sprawdzanie typów dla stabilności
- **Session management**: Lepsze zarządzanie stanem sesji Streamlit

### Usunięte
- **Globalna pamięć**: Usunięto system globalnej pamięci na rzecz profili uczniów
- **Bezpośrednie odpowiedzi**: Chatbot nie udziela już gotowych odpowiedzi (chyba że po 4x "nie wiem")

## [1.0.0] - 2025-05-24

### Dodane
- **Podstawowa aplikacja ChatGPT**: Prostą interfejs do rozmowy z AI
- **Pamięć konwersacji**: Podstawowe przechowywanie historii rozmów
- **Streamlit UI**: Interfejs użytkownika oparty na Streamlit
- **OpenAI integration**: Integracja z API OpenAI (GPT-4o-mini)
- **Koszty API**: Podstawowe śledzenie kosztów użycia API

### Techniczne
- **Python 3.8+**: Kompatybilność z nowymi wersjami Python
- **Streamlit 1.28+**: Wykorzystanie najnowszych funkcji Streamlit
- **OpenAI API**: Integracja z oficjalnym SDK OpenAI

---

## Legenda

- **Dodane**: Nowe funkcje
- **Zmienione**: Zmiany w istniejącej funkcjonalności
- **Przestarzałe**: Funkcje, które będą usunięte w przyszłych wersjach
- **Usunięte**: Usunięte funkcje
- **Naprawione**: Naprawy błędów
- **Bezpieczeństwo**: Poprawki związane z bezpieczeństwem

## Wersjonowanie

Projekt używa [Semantic Versioning](https://semver.org/):
- **MAJOR**: Zmiany łamiące kompatybilność wsteczną
- **MINOR**: Nowe funkcje zachowujące kompatybilność wsteczną
- **PATCH**: Naprawy błędów zachowujące kompatybilność wsteczną

## Zgłaszanie problemów

Problemy i sugestie można zgłaszać przez:
- [GitHub Issues](https://github.com/AlanSteinbarth/Sokrates/issues)
- Email: alan.steinbarth@gmail.com
