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
    # Najpierw pobierz z .env
    env = dotenv_values(".env")
    env_api_key = env.get("OPENAI_API_KEY", "")
    # Następnie pobierz z sidebaru (może nadpisać .env)
    api_key_input = st.text_input(
        "Podaj swój OpenAI API Key",
        type="password",
        value=st.session_state.get("openai_api_key", env_api_key),
        help="Wprowadź swój klucz OpenAI API lub dodaj go do pliku .env jako OPENAI_API_KEY. Klucz jest wymagany do działania aplikacji."
    )
    # Jeśli użytkownik coś wpisał, użyj tego, w przeciwnym razie użyj z .env
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

    st.markdown("---")
    # Licznik "nie wiem"
    nie_wiem_counter = st.session_state.get("nie_wiem_counter", 0)
    st.markdown(f"""
    <style>
    .sokrates-tooltip-box {{
      position: relative;
      display: block;
      overflow: visible !important;
    }}
    .sokrates-tooltip-icon {{
      position: absolute;
      top: 10px;
      right: 14px;
      z-index: 1002;
      cursor: help;
      font-size: 1.1em;
      color: #1976d2;
      background: #fff;
      border-radius: 50%;
      border: 1.5px solid #1976d2;
      width: 18px;
      height: 18px;
      text-align: center;
      line-height: 16px;
      display: flex;
      align-items: center;
      justify-content: center;
      overflow: visible !important;
    }}
    .sokrates-tooltip-icon .sokrates-tooltiptext {{
      visibility: hidden;
      opacity: 0;
      background-color: #222;
      color: #fff;
      text-align: left;
      border-radius: 7px;
      padding: 7px 14px;
      position: fixed;
      z-index: 99999;
      left: 320px;
      font-size: 0.98em;
      white-space: nowrap;
      box-shadow: 0 2px 8px #888;
      min-width: 180px;
      max-width: none;
      width: max-content;
      text-align: left;
      pointer-events: none;
    }}
    .sokrates-tooltip-icon.niewiem .sokrates-tooltiptext {{
      top: 390px;
    }}
    .sokrates-tooltip-icon.koszt .sokrates-tooltiptext {{
      top: 500px;
    }}
    .sokrates-tooltip-icon:hover .sokrates-tooltiptext {{
      visibility: visible;
      opacity: 1;
    }}
    /* Ulepszenia responsywności dla urządzeń mobilnych */
    @media (max-width: 600px) {{
      .sokrates-tooltip-box {{
        padding: 8px 4vw 14px 4vw !important;
        font-size: 1em !important;
      }}
      .sokrates-tooltip-icon {{
        right: 6vw !important;
        width: 22px !important;
        height: 22px !important;
        font-size: 1.3em !important;
      }}
      .sokrates-tooltip-icon .sokrates-tooltiptext {{
        left: 10vw !important;
        min-width: 120px !important;
        font-size: 0.95em !important;
        padding: 7px 8px !important;
      }}
      .sokrates-tooltip-icon.niewiem .sokrates-tooltiptext {{
        top: 120vw !important;
      }}
      .sokrates-tooltip-icon.koszt .sokrates-tooltiptext {{
        top: 150vw !important;
      }}
      .element-container, .stTextInput, .stTextArea, .stButton, .stForm {{
        font-size: 1.08em !important;
      }}
      .stTextInput input, .stTextArea textarea {{
        font-size: 1.08em !important;
        padding: 10px !important;
      }}
      .stButton button {{
        font-size: 1.08em !important;
        padding: 10px 18px !important;
      }}
      .stMarkdown, .stSubheader, .stHeader {{
        font-size: 1.08em !important;
      }}
    }}
    </style>
    <div class='sokrates-tooltip-box' style='background: #e0e0e0; border-radius: 10px; padding: 10px 16px 18px 16px; margin-bottom: 8px; box-shadow: 0 1px 4px #bdbdbd; position: relative; overflow: visible !important;'>
        <b style='color: #333;'>Licznik 'nie wiem:'</b>
        <span style='font-size: 1.3em; font-weight: bold; color: #333; display: block; margin-top: 4px;'>
            {nie_wiem_counter} / 4
        </span>
        <span class="sokrates-tooltip-icon niewiem">?
            <span class="sokrates-tooltiptext">Licznik zwiększa się, gdy odpowiadasz 'nie wiem' lub podobnie. Po 4 razach Sokrates poda pełną odpowiedź.</span>
        </span>
    </div>
    <hr style='margin: 12px 0; border: none; border-top: 1px solid #bbb;'>
    <div class='sokrates-tooltip-box' style='background: #e0e0e0; border-radius: 10px; padding: 10px 16px 18px 16px; margin-bottom: 8px; box-shadow: 0 1px 4px #bdbdbd; position: relative; overflow: visible !important;'>
        <b style='color: #333;'>Szacowany koszt rozmowy:</b>
        <span style='font-size: 1.3em; font-weight: bold; color: #333; display: block; margin-top: 4px;'>
            {st.session_state['cost_total_pln']:.4f} zł
        </span>
        <span class="sokrates-tooltip-icon koszt">?
            <span class="sokrates-tooltiptext">Koszt liczony na podstawie liczby tokenów zużytych przez model OpenAI (input/output) i aktualnego kursu USD/PLN. To tylko szacunkowa wartość.</span>
        </span>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")
    # FAQ
    if st.button("FAQ / Jak to działa?"):
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
        <p>Podaj swoje imię, aby rozpocząć naukę metodą sokratejską!</p>
    </div>
    """, unsafe_allow_html=True)
    col1, col2 = st.columns([3, 1])
    with col1:
        student_input = st.text_input("Podaj swoje imię:", placeholder="np. Anna, Tomek...", key="student_name_input")
    with col2:
        st.markdown("<div style='height: 1.7em'></div>", unsafe_allow_html=True)  # Wyrównanie do środka pola tekstowego
        if st.button("🚀 Start") and student_input.strip():
            st.session_state["student_name"] = student_input.strip()
            st.session_state["messages"] = []  # Reset rozmowy dla nowego ucznia
            st.session_state["nie_wiem_counter"] = 0
            st.rerun()
    st.stop()

# Po zalogowaniu - główny interfejs chatbota
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.subheader(f"👋 Cześć {st.session_state['student_name']}!")
    st.write("Zadawaj pytania, a poprowadzę Cię do odpowiedzi przez przemyślane pytania!")
with col3:
    if st.button("🚪 Wyloguj"):
        st.session_state["student_name"] = ""
        st.session_state["messages"] = []
        st.session_state["nie_wiem_counter"] = 0
        st.rerun()

# ===============================
# GŁÓWNY INTERFEJS CHATBOTA (po zalogowaniu)
# ===============================
if st.session_state.get("student_name", ""):
    st.markdown("---")
    st.subheader("💬 Rozmowa z Sokratesem")
    # Wyświetl historię rozmowy z wyróżnieniem
    for msg in st.session_state["messages"]:
        if msg["role"] == "user":
            user_name = st.session_state.get("student_name", "Ty")
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-end;'>
                    <div style='background: #e0f7fa; color: #000; border-radius: 12px; padding: 10px 16px; margin: 4px 0; max-width: 70%; box-shadow: 0 2px 8px #bdbdbd;'>
                        <span style='font-size: 1.2em;'>🧑‍💻 <b>{user_name}:</b></span><br>{msg['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
        elif msg["role"] == "assistant":
            st.markdown(
                f"""
                <div style='display: flex; justify-content: flex-start;'>
                    <div style='background: #fff3e0; color: #000; border-radius: 12px; padding: 10px 16px; margin: 4px 0; max-width: 70%; box-shadow: 0 2px 8px #ffe0b2;'>
                        <span style='font-size: 1.2em;'>🧑‍🏫 <b>Sokrates:</b></span><br>{msg['content']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
    # Formularz do wpisywania pytania
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_area("Zadaj pytanie Sokratesowi:", height=70, key="chat_input",
                                 placeholder="Wpisz pytanie i naciśnij Enter lub kliknij Wyślij...")
        submitted = st.form_submit_button("Wyślij")
        # Dodaj obsługę wysyłania przez Enter (JS dla st.text_area)
        import streamlit.components.v1 as components
        components.html('''
        <script>
        const textarea = window.parent.document.querySelector('textarea[data-testid="stTextArea"]');
        if (textarea) {
            textarea.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' && !e.shiftKey) {
                    e.preventDefault();
                    const btns = window.parent.document.querySelectorAll('button[kind="primary"]');
                    if (btns.length > 0) btns[0].click();
                }
            });
        }
        </script>
        ''', height=0)
    if submitted and user_input.strip():
        # Dodaj pytanie użytkownika do historii
        st.session_state["messages"].append({"role": "user", "content": user_input.strip()})
        # Wywołaj AI i dodaj odpowiedź
        response = chatbot_reply(user_input.strip(), st.session_state["messages"])
        st.session_state["messages"].append({"role": "assistant", "content": response["content"]})
        # Liczenie kosztu
        usage = response.get("usage")
        if usage and hasattr(usage, "prompt_tokens") and hasattr(usage, "completion_tokens"):
            input_tokens = usage.prompt_tokens
            output_tokens = usage.completion_tokens
            cost = (input_tokens * PRICING["input_tokens"] + output_tokens * PRICING["output_tokens"]) * USD_TO_PLN
            st.session_state["cost_total_pln"] += cost
        # Wyciągnij fakty z wypowiedzi użytkownika i zapisz do profilu
        fakty = wyciagnij_fakty_z_tekstu(user_input.strip())
        for fact in fakty:
            zapisz_do_pamieci(fact)
        st.rerun()

