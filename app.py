# =============================================================================
# SOKRATES - CYFROWY NAUCZYCIEL AI
# =============================================================================
# Autor: Alan Steinbarth (alan.steinbarth@gmail.com)
# GitHub: https://github.com/AlanSteinbarth/Sokrates
# Wersja: 2.1.0
# Licencja: MIT
# 
# Aplikacja wykorzystująca metodę sokratejską do nauczania przez pytania
# prowadzące zamiast podawania gotowych odpowiedzi. Każdy uczeń ma 
# indywidualny profil z automatycznie wykrywanymi preferencjami nauki.
# =============================================================================

import json
from pathlib import Path
import streamlit as st
from openai import OpenAI
from dotenv import dotenv_values
from typing import List, Dict, Any

# =============================================================================
# KONFIGURACJA APLIKACJI
# =============================================================================

# Cennik modeli OpenAI (USD za token)
model_pricings = {
    "gpt-4o": {
        "input_tokens": 5.00 / 1_000_000,  # per token
        "output_tokens": 15.00 / 1_000_000,  # per token
    },
    "gpt-4o-mini": {
        "input_tokens": 0.150 / 1_000_000,  # per token
        "output_tokens": 0.600 / 1_000_000,  # per token
    }
}

# Konfiguracja globalna
MODEL = "gpt-4o-mini"  # Ekonomiczny model dla edukacji
USD_TO_PLN = 3.92  # Aktualny kurs USD->PLN (aktualizować okresowo)
PRICING = model_pricings[MODEL]

# Inicjalizacja klienta OpenAI

def get_api_key() -> str:
    """
    Pobiera klucz OpenAI API z sesji, pliku .env lub zwraca pusty string.
    Preferuje klucz wpisany przez użytkownika w sidebarze.
    """
    # Najpierw sprawdź czy klucz jest w session_state (wprowadzony przez użytkownika)
    if "openai_api_key" in st.session_state and st.session_state["openai_api_key"]:
        return st.session_state["openai_api_key"]
    # Następnie sprawdź plik .env
    env = dotenv_values(".env")
    value = env.get("OPENAI_API_KEY", "")
    return value if value is not None else ""

def verify_api_key(api_key: str) -> bool:
    """
    Weryfikuje poprawność klucza OpenAI API przez próbę wykonania prostego zapytania.
    Zwraca True jeśli klucz jest poprawny, False w przeciwnym razie.
    """
    try:
        client = OpenAI(api_key=api_key)
        # Minimalne zapytanie do modelu (bardzo krótka wiadomość)
        response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "ping"}]
        )
        return bool(response.choices[0].message.content)
    except Exception:
        return False

# Inicjalizacja klienta OpenAI (dynamicznie na podstawie klucza)
def get_openai_client() -> OpenAI:
    """
    Tworzy klienta OpenAI na podstawie aktualnego klucza API (z sidebaru lub .env).
    """
    api_key = get_api_key()
    return OpenAI(api_key=api_key)

# =============================================================================
# ZARZĄDZANIE PROFILAMI UCZNIÓW
# =============================================================================

def get_student_memory_file(student_name: str) -> Path:
    """
    Zwraca ścieżkę do pliku pamięci dla konkretnego ucznia.
    
    Funkcja tworzy bezpieczną nazwę pliku poprzez sanityzację nazwy ucznia
    i zapewnia istnienie katalogu students/.
    
    Args:
        student_name (str): Imię/nazwa ucznia
        
    Returns:
        Path: Ścieżka do pliku JSON z profilem ucznia
        
    Note:
        Pliki profili są zapisywane lokalnie zgodnie z RODO.
        Format: db/students/{nazwa_ucznia}_memory.json
    """
    students_dir = Path("db/students")
    students_dir.mkdir(parents=True, exist_ok=True)
    
    # Sanityzacja nazwy dla bezpieczeństwa systemu plików
    safe_name = "".join(c for c in student_name if c.isalnum() or c in (' ', '-', '_')).rstrip()
    safe_name = safe_name.replace(' ', '_').lower()
    
    return students_dir / f"{safe_name}_memory.json"

# =============================================================================
# SYSTEM PAMIĘCI DŁUGOTERMINOWEJ
# =============================================================================

def zapisz_do_pamieci(fact: str) -> None:
    """
    Dodaje nowy fakt do profilu aktualnie zalogowanego ucznia.
    
    Args:
        fact (str): Fakt edukacyjny do zapisania (styl nauki, preferencje, etc.)
        
    Note:
        Funkcja sprawdza czy uczeń jest zalogowany przed zapisem.
        Każdy fakt jest zapisywany jako osobna linia JSON.
    """
    if "student_name" not in st.session_state or not st.session_state.get("student_name", ""):
        return
    
    memory_file = get_student_memory_file(st.session_state.get("student_name", ""))
    memory_file.parent.mkdir(exist_ok=True)
    
    with open(memory_file, "a", encoding="utf-8") as f:
        f.write(json.dumps({"fact": fact}, ensure_ascii=False) + "\n")

def wczytaj_pamiec() -> List[str]:
    """
    Ładuje wszystkie fakty z profilu aktualnie zalogowanego ucznia.
    
    Returns:
        List[str]: Lista faktów o uczniu (pusta jeśli brak profilu)
        
    Note:
        Zwraca pustą listę jeśli uczeń nie jest zalogowany lub brak pliku.
    """
    if "student_name" not in st.session_state or not st.session_state.get("student_name", ""):
        return []
    
    memory_file = get_student_memory_file(st.session_state.get("student_name", ""))
    if not memory_file.exists():
        return []
    
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            return [json.loads(line.strip())["fact"] for line in f.readlines() if line.strip()]
    except (json.JSONDecodeError, KeyError):
        return []

def zapisz_pamiec(fakty: List[str]) -> None:
    """
    Przepisuje cały profil ucznia z nową listą faktów.
    
    Args:
        fakty (List[str]): Kompletna lista faktów do zapisania
        
    Note:
        Używane przy edycji/usuwaniu faktów z profilu.
    """
    if "student_name" not in st.session_state or not st.session_state.get("student_name", ""):
        return
    
    memory_file = get_student_memory_file(st.session_state.get("student_name", ""))
    memory_file.parent.mkdir(exist_ok=True)
    
    with open(memory_file, "w", encoding="utf-8") as f:
        for fact in fakty:
            f.write(json.dumps({"fact": fact}, ensure_ascii=False) + "\n")

def usun_fact(index: int) -> None:
    """
    Usuwa fakt o podanym indeksie z profilu ucznia.
    
    Args:
        index (int): Indeks faktu do usunięcia (0-based)
        
    Note:
        Funkcja automatycznie przeładowuje i zapisuje profil bez usuniętego faktu.
    """
    fakty = wczytaj_pamiec()
    if 0 <= index < len(fakty):
        del fakty[index]
        zapisz_pamiec(fakty)

# =============================================================================
# EKSTRAKCJA FAKTÓW Z TEKSTU (AI)
# =============================================================================

def wyciagnij_fakty_z_tekstu(text: str) -> List[str]:
    """
    Wykorzystuje AI do wydobycia faktów edukacyjnych z tekstu ucznia.
    
    Analizuje wypowiedzi ucznia i identyfikuje informacje przydatne
    dla personalizacji procesu nauczania.
    
    Args:
        text (str): Tekst do analizy (pytanie/odpowiedź ucznia)
        
    Returns:
        List[str]: Lista wykrytych faktów edukacyjnych
        
    Note:
        Wykorzystuje model GPT do inteligentnej analizy stylu nauki.
    """
    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": """Wydobądź z tekstu fakty o uczniu, które warto zapamiętać dla procesu nauczania:
- poziom wiedzy w różnych dziedzinach
- zainteresowania naukowe  
- sposób uczenia się
- trudności w nauce
- postępy w nauce
- preferowane metody wyjaśniania
Wypisz jako listę wypunktowaną, krótko i konkretnie."""},
                {"role": "user", "content": text}
            ]
        )
        content = response.choices[0].message.content
        if content is None:
            return []
        return [line.strip() for line in content.split("\n") if line.strip()]
    except Exception as e:
        st.error(f"Błąd podczas analizy tekstu: {e}")
        return []

# =============================================================================
# GŁÓWNA LOGIKA CHATBOTA SOKRATEJSKIEGO
# =============================================================================
def chatbot_reply(user_prompt: str, memory: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Główna funkcja generująca odpowiedzi Sokratesa.
    
    Implementuje metodę sokratejską - zadaje pytania prowadzące zamiast
    podawać bezpośrednie odpowiedzi. System progresywnie zwiększa pomoc
    w zależności od liczby "nie wiem" od ucznia.
    
    Args:
        user_prompt (str): Pytanie/wypowiedź ucznia
        memory (List[Dict]): Ostatnie wiadomości z konwersacji
        
    Returns:
        Dict[str, Any]: Odpowiedź zawierająca treść i statystyki użycia API
        
    Note:
        - Licznik "nie wiem" 0-2: tylko pytania prowadzące
        - Licznik "nie wiem" 3: wskazówki i częściowe odpowiedzi  
        - Licznik "nie wiem" 4+: pełna odpowiedź z wyjaśnieniem
    """
    # Wczytanie profilu ucznia dla personalizacji
    facts = wczytaj_pamiec()
    memory_context = "\n".join(facts) if facts else "Brak informacji o uczniu."
    
    # Wykrywanie frazy "nie wiem" i jej wariantów
    nie_wiem_phrases = ["nie wiem", "nie mam pojęcia", "bez pojęcia", "nie znam", "nie umiem"]
    user_said_nie_wiem = any(phrase in user_prompt.lower() for phrase in nie_wiem_phrases)
    
    # Aktualizacja licznika pomocy
    if user_said_nie_wiem:
        st.session_state["nie_wiem_counter"] += 1
    else:
        # Reset licznika jeśli użytkownik nie prosi o pomoc
        help_phrases = ["pytanie", "pomocy", "wyjaśnij"]
        if not any(phrase in user_prompt.lower() for phrase in help_phrases):
            st.session_state["nie_wiem_counter"] = 0
    
    # Przygotowanie kontekstu dla modelu AI
    socratic_context = f"""
Licznik "nie wiem": {st.session_state["nie_wiem_counter"]}/4
Aktualny temat: {st.session_state.get("current_topic", "Nieokreślony")}

INSTRUKCJE ZACHOWANIA:
- Jeśli licznik "nie wiem" < 3: Zadawaj pytania prowadzące, NIE udzielaj bezpośredniej odpowiedzi
- Jeśli licznik "nie wiem" = 3: Udziel wskazówki lub częściowej odpowiedzi
- Jeśli licznik "nie wiem" >= 4: MUSISZ udzielić pełnej, jasnej odpowiedzi na pytanie ucznia. Zakończ proces sokratejski i podaj konkretne wyjaśnienie.

Profil ucznia: {memory_context}
"""

    # Budowanie listy wiadomości dla API
    messages = [
        {"role": "system", "content": st.session_state["chatbot_personality"] + "\n" + socratic_context},
        *[{"role": m["role"], "content": m["content"]} 
          for m in memory[-6:] if "role" in m and "content" in m],  # Ostatnie 6 wiadomości dla kontekstu
        {"role": "user", "content": user_prompt},
    ]

    try:
        client = get_openai_client()
        response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=False
        )
        # Zwracamy tylko najważniejsze dane jako dict
        return {
            "content": response.choices[0].message.content if response.choices else "",
            "usage": getattr(response, "usage", None),
            "raw": response
        }
    except Exception as e:
        st.error(f"Błąd podczas komunikacji z AI: {e}")
        return {"content": "", "usage": None, "raw": None}

# ===============================
# SIDEBAR: WPROWADZANIE KLUCZA API
# ===============================
with st.sidebar:
    st.header("🔑 OpenAI API Key")
    api_key_input = st.text_input(
        "Podaj swój OpenAI API Key",
        type="password",
        value=st.session_state.get("openai_api_key", ""),
        help="Wprowadź swój klucz OpenAI API lub dodaj go do pliku .env jako OPENAI_API_KEY. Klucz jest wymagany do działania aplikacji."
    )
    st.session_state["openai_api_key"] = api_key_input
    api_key_status = ""
    prev_verified = st.session_state.get("api_key_verified", False)
    if api_key_input:
        if verify_api_key(api_key_input):
            api_key_status = "✅ Klucz API jest prawidłowy. Możesz korzystać z aplikacji."
            st.success(api_key_status)
            st.session_state["api_key_verified"] = True
            if not prev_verified:
                st.rerun()
        else:
            api_key_status = "❌ Klucz API jest nieprawidłowy lub wygasł."
            st.error(api_key_status)
            st.session_state["api_key_verified"] = False
    else:
        st.info("Podaj swój klucz OpenAI API lub dodaj go do pliku .env.")
        st.session_state["api_key_verified"] = False

# ===============================
# BLOKADA FUNKCJI DO CZASU WERYFIKACJI KLUCZA
# ===============================
if not st.session_state.get("api_key_verified", False):
    st.markdown("""
    <h2 style='text-align: center;'>🧠 Sokrates - Twój cyfrowy nauczyciel</h2>
    <div style='text-align: center;'>
        <p>Odkrywaj wiedzę z pomocą AI, która prowadzi Cię pytaniami – ucz się skuteczniej, myśl samodzielnie i rozwijaj swój potencjał!</p>
    </div>
    """, unsafe_allow_html=True)
    st.stop()

# ===============================
# LOGOWANIE UCZNIA I INTERFEJS GŁÓWNY
# ===============================
if not st.session_state.get("student_name", ""):
    st.markdown("""
    <h2 style='text-align: center;'>🧠 Sokrates - Twój cyfrowy nauczyciel</h2>
    <div style='text-align: center;'>
        <p>Podaj swoje imię, aby rozpocząć naukę metodą sokratejską!</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        student_input = st.text_input("Podaj swoje imię:", placeholder="np. Anna, Tomek...")
    with col2:
        if st.button("🚀 Start") and student_input.strip():
            st.session_state["student_name"] = student_input.strip()
            st.session_state["messages"] = []  # Reset rozmowy dla nowego ucznia
            st.session_state["nie_wiem_counter"] = 0
            st.rerun()
    if st.button("❓ Jak to działa?"):
        st.session_state["show_faq"] = not st.session_state.get("show_faq", False)
    if st.session_state.get("show_faq", False):
        st.subheader("❓ Najczęściej zadawane pytania")
        with st.expander("🤔 Jak działa metoda sokratejska?"):
            st.write("""
            **Metoda sokratejska** to sposób uczenia przez zadawanie pytań prowadzących, zamiast podawania gotowych odpowiedzi.
            1. Zadajesz pytanie Sokratesowi
            2. Otrzymujesz pytania, które mają Cię naprowadzić na odpowiedź
            3. Próbujesz odpowiadać na te pytania
            4. Samodzielnie dochodzisz do rozwiązania!
            """)
        with st.expander("❓ Co oznacza 'nie wiem' i licznik?"):
            st.write("""
            **Licznik 'nie wiem'** to system pomocy:
            - 0-2 razy: pytania prowadzące
            - 3 razy: wskazówki i częściowe odpowiedzi
            - 4+ razy: pełna odpowiedź z wyjaśnieniem
            """)
        with st.expander("👤 Co to jest profil ucznia?"):
            st.write("""
            **Profil ucznia** to Twoja osobista karta nauki, która zawiera:
            - Poziom wiedzy
            - Sposób, w jaki najlepiej się uczysz
            - Trudności, z jakimi się zmagasz
            - Postępy w nauce
            - Zainteresowania naukowe
            """)
    st.stop()

# Po zalogowaniu - główny interfejs chatbota
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.subheader(f"👋 Cześć {st.session_state['student_name']}!")
    st.write("Zadawaj pytania, a poprowadzę Cię do odpowiedzi przez przemyślane pytania!")
with col2:
    if st.button("❓ FAQ"):
        st.session_state["show_faq"] = not st.session_state.get("show_faq", False)
with col3:
    if st.button("🚪 Wyloguj"):
        st.session_state["student_name"] = ""
        st.session_state["messages"] = []
        st.session_state["nie_wiem_counter"] = 0
        st.rerun()

if st.session_state.get("show_faq", False):
    with st.expander("❓ Przypomnienie - jak korzystać z Sokratesa", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            st.write("**🤔 Metoda sokratejska:**")
            st.write("• Zadaję pytania zamiast podawać odpowiedzi")
            st.write("• Prowadzę Cię do samodzielnego odkrycia")
            st.write("• Uczysz się przez myślenie!")
            st.write("**❓ System 'nie wiem':**")
            st.write("• 0-2 razy: tylko pytania prowadzące")
            st.write("• 3 razy: wskazówki")  
            st.write("• 4+ razy: pełna odpowiedź")
        with col2:
            st.write("**👤 Twój profil ucznia:**")
            st.write("• Automatycznie zapisuję Twoje preferencje")
            st.write("• Dostosowuję pytania do Twojego stylu")
            st.write("• Śledzę Twój postęp w nauce")

# ===============================
# INICJALIZACJA STANU SESJI (musi być tuż po importach!)
# ===============================
def get_state(key, default):
    if key not in st.session_state:
        st.session_state[key] = default
    return st.session_state[key]

get_state('student_name', '')
get_state('messages', [])
get_state('facts_to_confirm', [])
get_state('nie_wiem_counter', 0)
get_state('current_topic', None)
get_state('show_faq', False)
get_state('chatbot_personality', "Jesteś Sokratesem - mądrym filozofem i nauczycielem. Twoim celem jest prowadzić ucznia do samodzielnego myślenia poprzez pytania.")
get_state('openai_api_key', '')
get_state('api_key_verified', False)

# ...tu możesz dodać chatbota i dalszą logikę...

