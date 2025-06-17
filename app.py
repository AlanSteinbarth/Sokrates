# =============================================================================
# 🧠 Sokrates - Twój cyfrowy nauczyciel 🤖
# =============================================================================
# Autor: Alan Steinbarth (alan.steinbarth@gmail.com)
# GitHub: https://github.com/AlanSteinbarth/Sokrates
# Wersja: 2.2.0
# Licencja: MIT
# 
# Aplikacja wykorzystująca metodę sokratejską do nauczania przez pytania
# prowadzące zamiast podawania gotowych odpowiedzi. Każdy uczeń ma 
# indywidualny profil z automatycznie wykrywanymi preferencjami nauki.
# =============================================================================
#
# SPIS TREŚCI (TOC):
# 1. Importy i konfiguracja globalna
# 2. Inicjalizacja stanu sesji Streamlit
# 3. Konfiguracja aplikacji i cennik modeli
# 4. Obsługa klucza API i klienta OpenAI
# 5. Zarządzanie profilami uczniów (pliki, pamięć)
# 6. System pamięci długoterminowej (zapis/odczyt faktów)
# 7. Ekstrakcja faktów z tekstu (AI)
# 8. Główna logika chatbota sokratejskiego
# 9. Sidebar: klucz API, liczniki, FAQ
# 10. Blokada funkcji do czasu weryfikacji klucza
# 11. Logowanie ucznia i główny interfejs
# 12. Interfejs czatu i obsługa rozmowy
#
# Każda funkcja posiada docstring z opisem działania i argumentów.
# =============================================================================

# USUNIĘTO: import os, glob, pandas as pd
import json
from pathlib import Path
import streamlit as st
from openai import OpenAI
from dotenv import dotenv_values
from typing import List, Dict, Any

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
get_state('cost_total_pln', 0.0)
get_state('show_admin_panel', False)

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
    env_local = dotenv_values(".env")  # zmiana nazwy zmiennej
    value = env_local.get("OPENAI_API_KEY", "")
    return value if value is not None else ""

def verify_api_key(api_key: str) -> bool:
    """
    Weryfikuje poprawność klucza OpenAI API przez próbę wykonania prostego zapytania.
    Zwraca True jeśli klucz jest poprawny, False w przeciwnym razie.
    """
    try:
        client = OpenAI(api_key=api_key)
        api_response = client.chat.completions.create(
            model=MODEL,
            messages=[{"role": "user", "content": "ping"}]
        )
        return bool(api_response.choices[0].message.content)
    except (ValueError, KeyError, AttributeError, Exception) as e:
        st.error(f"Błąd weryfikacji klucza API: {e}")
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
        ai_response = client.chat.completions.create(
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
        content = ai_response.choices[0].message.content
        if content is None:
            return []
        return [line.strip() for line in content.split("\n") if line.strip()]
    except (ValueError, KeyError, AttributeError, Exception) as e:
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
        chat_response = client.chat.completions.create(
            model=MODEL,
            messages=messages,
            stream=False
        )
        return {
            "content": chat_response.choices[0].message.content if chat_response.choices else "",
            "usage": getattr(chat_response, "usage", None),
            "raw": chat_response
        }
    except (ValueError, KeyError, AttributeError, Exception) as e:
        st.error(f"Błąd podczas komunikacji z AI: {e}")
        return {"content": "", "usage": None, "raw": None}

# ===============================
# SIDEBAR: WPROWADZANIE KLUCZA API
# ===============================
with st.sidebar:
    st.header("🔑 OpenAI API Key")
    env_sidebar = dotenv_values(".env")  # zmiana nazwy zmiennej
    env_api_key = env_sidebar.get("OPENAI_API_KEY", "")
    api_key_input = st.text_input(
        "Podaj swój OpenAI API Key",
        type="password",
        value=st.session_state.get("openai_api_key", env_api_key),
        help="Wprowadź swój klucz OpenAI API lub dodaj go do pliku .env jako OPENAI_API_KEY. Klucz jest wymagany do działania aplikacji."
    )
    if api_key_input:
        st.session_state["openai_api_key"] = api_key_input
    else:
        st.session_state["openai_api_key"] = env_api_key
    api_key_status = ""
    prev_verified = st.session_state.get("api_key_verified", False)
    if st.session_state["openai_api_key"]:
        if verify_api_key(st.session_state["openai_api_key"]):
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

    # Pokaż resztę sidebaru dopiero po podaniu imienia
    if st.session_state.get("api_key_verified", False) and st.session_state.get("student_name", ""):
        nie_wiem_counter = st.session_state.get("nie_wiem_counter", 0)
        st.markdown(f"""
        <style>
        .sokrates-tooltip-box {{ position: relative; display: block; overflow: visible !important; }}
        .sokrates-tooltip-icon {{ position: absolute; top: 10px; right: 14px; z-index: 1002; cursor: help; font-size: 1.1em; color: #1976d2; background: #fff; border-radius: 50%; border: 1.5px solid #1976d2; width: 18px; height: 18px; text-align: center; line-height: 16px; display: flex; align-items: center; justify-content: center; overflow: visible !important; }}
        .sokrates-tooltip-icon .sokrates-tooltiptext {{ visibility: hidden; opacity: 0; background-color: #222; color: #fff; text-align: left; border-radius: 7px; padding: 7px 14px; position: fixed; z-index: 99999; left: 320px; font-size: 0.98em; white-space: nowrap; box-shadow: 0 2px 8px #888; min-width: 180px; max-width: none; width: max-content; text-align: left; pointer-events: none; }}
        .sokrates-tooltip-icon.niewiem .sokrates-tooltiptext {{ top: 390px; }}
        .sokrates-tooltip-icon.koszt .sokrates-tooltiptext {{ top: 500px; }}
        .sokrates-tooltip-icon:hover .sokrates-tooltiptext {{ visibility: visible; opacity: 1; }}
        @media (max-width: 600px) {{ .sokrates-tooltip-box {{ padding: 8px 4vw 14px 4vw !important; font-size: 1em !important; }} .sokrates-tooltip-icon {{ right: 6vw !important; width: 22px !important; height: 22px !important; font-size: 1.3em !important; }} .sokrates-tooltip-icon .sokrates-tooltiptext {{ left: 10vw !important; min-width: 120px !important; font-size: 0.95em !important; padding: 7px 8px !important; }} .sokrates-tooltip-icon.niewiem .sokrates-tooltiptext {{ top: 120vw !important; }} .sokrates-tooltip-icon.koszt .sokrates-tooltiptext {{ top: 150vw !important; }} .element-container, .stTextInput, .stTextArea, .stButton, .stForm {{ font-size: 1.08em !important; }} .stTextInput input, .stTextArea textarea {{ font-size: 1.08em !important; padding: 10px !important; }} .stButton button {{ font-size: 1.08em !important; padding: 10px 18px !important; }} .stMarkdown, .stSubheader, .stHeader {{ font-size: 1.08em !important; }} }}
        </style>
        <div class='sokrates-tooltip-box' style='background: #e0e0e0; border-radius: 10px; padding: 10px 16px 18px 16px; margin-bottom: 8px; box-shadow: 0 1px 4px #bdbdbd; position: relative; overflow: visible !important;'>
            <b style='color: #333;'>Licznik 'nie wiem:'</b>
            <span style='font-size: 1.3em; font-weight: bold; color: #333; display: block; margin-top: 4px;'>
                {nie_wiem_counter} / 4
            </span>
            <span class=\"sokrates-tooltip-icon niewiem\">?
                <span class=\"sokrates-tooltiptext\">Licznik zwiększa się, gdy odpowiadasz 'nie wiem' lub podobnie. Po 4 razach Sokrates poda pełną odpowiedź.</span>
            </span>
        </div>
        <hr style='margin: 12px 0; border: none; border-top: 1px solid #bbb;'>
        <div class='sokrates-tooltip-box' style='background: #e0e0e0; border-radius: 10px; padding: 10px 16px 18px 16px; margin-bottom: 8px; box-shadow: 0 1px 4px #bdbdbd; position: relative; overflow: visible !important;'>
            <b style='color: #333;'>Szacowany koszt rozmowy:</b>
            <span style='font-size: 1.3em; font-weight: bold; color: #333; display: block; margin-top: 4px;'>
                {st.session_state['cost_total_pln']:.4f} zł
            </span>
            <span class=\"sokrates-tooltip-icon koszt\">?
                <span class=\"sokrates-tooltiptext\">Koszt liczony na podstawie liczby tokenów zużytych przez model OpenAI (input/output) i aktualnego kursu USD/PLN. To tylko szacunkowa wartość.</span>
            </span>
        </div>
        """, unsafe_allow_html=True)
        # Panel administracyjny - przycisk na całą szerokość i wyśrodkowany
        st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; width: 100%;'>
        <div style='flex:1; max-width: 100%;'>
        """, unsafe_allow_html=True)
        admin_clicked = st.button("🛡️ Panel administracyjny (Enterprise Preview)", key="admin_btn_sidebar", use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
        if admin_clicked:
            st.session_state["show_admin_panel"] = not st.session_state.get("show_admin_panel", False)
        if st.session_state.get("show_admin_panel", False):
            st.markdown("""
            <div style='background: #33393f; color: #f2f2f2; border-radius: 10px; padding: 20px 18px; margin: 12px 0; box-shadow: 0 1px 4px #bdbdbd;'>
                <b style='font-size:1.15em;'>Panel administracyjny (Enterprise Preview)</b><br><br>
                <ul style='margin-top: 8px; margin-bottom: 0;'>
                  <li><b>Statystyki użytkowników:</b> <span style='color:#ffb300;'>Wkrótce</span></li>
                  <li><b>Zarządzanie kontami:</b> <span style='color:#ffb300;'>Wkrótce</span></li>
                  <li><b>Eksport danych:</b> <span style='color:#ffb300;'>Wkrótce</span></li>
                  <li><b>Logi aktywności i audyt:</b> <span style='color:#ffb300;'>Wkrótce</span></li>
                  <li><b>Integracje SSO (Google, Microsoft, LDAP):</b> <span style='color:#ffb300;'>Wkrótce</span></li>
                  <li><b>API do integracji z zewnętrznymi systemami:</b> <span style='color:#ffb300;'>Wkrótce</span></li>
                  <li><b>System zgłoszeń i wsparcia:</b> <span style='color:#ffb300;'>Wkrótce</span></li>
                  <li><b>Pełna dokumentacja techniczna:</b> <span style='color:#ffb300;'>Wkrótce</span></li>
                </ul>
                <hr style='margin:14px 0; border: none; border-top: 1px solid #555;'>
                <b>Podstawowe informacje:</b><br>
                <ul style='margin-top: 6px; margin-bottom: 0;'>
                  <li><b>Liczba aktywnych użytkowników:</b> <span style='color:#90caf9;'>demo</span></li>
                  <li><b>Wersja aplikacji:</b> 2.2.0</li>
                  <li><b>Data builda:</b> 16.06.2025</li>
                  <li><b>Tryb:</b> <span style='color:#ffb300;'>Enterprise Preview</span></li>
                </ul>
                <hr style='margin:14px 0; border: none; border-top: 1px solid #555;'>
                <b>Bezpieczeństwo i zgodność:</b><br>
                <ul style='margin-top: 6px; margin-bottom: 0;'>
                  <li>RODO/GDPR, FERPA, COPPA <span style='color:#43e97b;'>Ready</span></li>
                  <li>Szyfrowanie danych <span style='color:#ffb300;'>Wkrótce</span></li>
                  <li>Audyt logów <span style='color:#ffb300;'>Wkrótce</span></li>
                  <li>Certyfikaty bezpieczeństwa <span style='color:#ffb300;'>Wkrótce</span></li>
                </ul>
                <hr style='margin:14px 0; border: none; border-top: 1px solid #555;'>
                <span style='font-size:0.97em;color:#bbb;'>To tylko podgląd funkcji enterprise. Skontaktuj się z administratorem, aby uzyskać dostęp do pełnej wersji.</span>
            </div>
            """, unsafe_allow_html=True)
        # FAQ wyśrodkowany i na całą szerokość
        st.markdown("""
        <div style='display: flex; justify-content: center; align-items: center; width: 100%;'>
        <div style='flex:1; max-width: 100%;'>
        """, unsafe_allow_html=True)
        faq_clicked = st.button("FAQ / Jak to działa?", key="faq_btn_sidebar", use_container_width=True)
        st.markdown("</div></div>", unsafe_allow_html=True)
        if faq_clicked:
            st.session_state["show_faq"] = not st.session_state.get("show_faq", False)
        if st.session_state.get("show_faq", False):
            with st.expander("🤔 Jak działa metoda sokratejska?", expanded=True):
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
        <p>Odkrywaj wiedzę z pomocą AI, która prowadzi Cię pytaniami – ucz się skuteczniej, myśl samodzielnie i rozwijaj swój potencjał!</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        student_input = st.text_input("Podaj swoje imię:", placeholder="np. Anna, Tomek...", key="student_name_input")
    with col2:
        st.markdown("<div style='height: 1.7em'></div>", unsafe_allow_html=True)
        if st.button("🚀 Start") and student_input.strip():
            st.session_state["student_name"] = student_input.strip()
            st.session_state["messages"] = []  # Reset rozmowy dla nowego ucznia
            st.session_state["nie_wiem_counter"] = 0
            st.rerun()
    st.stop()

# =============================================================================
# INTERFEJS CZATU I OBSŁUGA ROZMOWY
# =============================================================================

st.markdown("""
<h2 style='text-align: center;'>🧠 Sokrates - Twój cyfrowy nauczyciel</h2>
<div style='text-align: center;'>
    <p>Zadaj pytanie lub napisz, czego chcesz się nauczyć. Sokrates poprowadzi Cię pytaniami!</p>
</div>
""", unsafe_allow_html=True)

# Wyświetlanie historii rozmowy
for msg in st.session_state["messages"]:
    if msg["role"] == "user":
        st.chat_message("user").write(msg["content"])
    else:
        st.chat_message("assistant").write(msg["content"])

# Pole do wpisania nowej wiadomości
with st.form(key="chat_form", clear_on_submit=True):
    user_input = st.text_area("Napisz czego będziesz się uczyć z Sokratesem:", height=70, key="user_input")
    submit = st.form_submit_button("Wyślij")

# --- AKTUALIZACJA KOSZTU ROZMOWY ---
# W sekcji obsługi czatu, po uzyskaniu odpowiedzi AI:
if submit and user_input.strip():
    st.session_state["messages"].append({"role": "user", "content": user_input.strip()})
    response = chatbot_reply(user_input.strip(), st.session_state["messages"])
    ai_content = response.get("content", "[Brak odpowiedzi od AI]")
    # --- koszt rozmowy ---
    usage = response.get("usage")
    if usage and hasattr(usage, 'prompt_tokens') and hasattr(usage, 'completion_tokens'):
        input_tokens = usage.prompt_tokens
        output_tokens = usage.completion_tokens
        cost = (input_tokens * PRICING["input_tokens"] + output_tokens * PRICING["output_tokens"]) * USD_TO_PLN
        st.session_state["cost_total_pln"] += cost
    st.session_state["messages"].append({"role": "assistant", "content": ai_content})
    st.rerun()

