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
env = dotenv_values(".env")
openai_client = OpenAI(api_key=env["OPENAI_API_KEY"])

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
    if "student_name" not in st.session_state or not st.session_state["student_name"]:
        return
    
    memory_file = get_student_memory_file(st.session_state["student_name"])
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
    if "student_name" not in st.session_state or not st.session_state["student_name"]:
        return []
    
    memory_file = get_student_memory_file(st.session_state["student_name"])
    if not memory_file.exists():
        return []
    
    try:
        with open(memory_file, "r", encoding="utf-8") as f:
            return [json.loads(l.strip())["fact"] for l in f.readlines() if l.strip()]
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
    if "student_name" not in st.session_state or not st.session_state["student_name"]:
        return
    
    memory_file = get_student_memory_file(st.session_state["student_name"])
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
        response = openai_client.chat.completions.create(
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
        # Wywołanie API OpenAI
        response = openai_client.chat.completions.create(
            model=MODEL,
            messages=messages,
            temperature=0.7,  # Balans między kreatywnością a spójnością
            max_tokens=500    # Limit długości odpowiedzi
        )
        
        # Zbieranie statystyk użycia
        usage = {}
        if response.usage:
            usage = {
                "completion_tokens": response.usage.completion_tokens,
                "prompt_tokens": response.usage.prompt_tokens,
                "total_tokens": response.usage.total_tokens,
            }

        return {
            "role": "assistant",
            "content": response.choices[0].message.content,
            "usage": usage,
        }
        
    except Exception as e:
        st.error(f"Błąd podczas komunikacji z AI: {e}")
        return {
            "role": "assistant",
            "content": "Przepraszam, wystąpił problem z połączeniem. Spróbuj ponownie.",
            "usage": {}
        }

# =============================================================================
# INICJALIZACJA STREAMLIT I STANU SESJI
# =============================================================================
# Inicjalizacja wszystkich zmiennych stanu sesji Streamlit
# UWAGA: Te inicjalizacje MUSZĄ być na początku, przed jakimkolwiek UI!

if "messages" not in st.session_state:
    st.session_state["messages"] = []

if "facts_to_confirm" not in st.session_state:
    st.session_state["facts_to_confirm"] = []

if "student_name" not in st.session_state:
    st.session_state["student_name"] = ""

if "nie_wiem_counter" not in st.session_state:
    st.session_state["nie_wiem_counter"] = 0

if "current_topic" not in st.session_state:
    st.session_state["current_topic"] = None

if "show_faq" not in st.session_state:
    st.session_state["show_faq"] = False

if "chatbot_personality" not in st.session_state:
    st.session_state["chatbot_personality"] = """Jesteś Sokratesem - mądrym filozofem i nauczycielem. 
Twoim celem jest pomóc uczniowi w nauce przez zadawanie pytań prowadzących.

ZASADY METODY SOKRATEJSKIEJ:
1. Normalnie NIE udzielaj bezpośrednich odpowiedzi - zadawaj pytania prowadzące
2. Zadawaj pytania, które pomagają uczniowi myśleć i dochodzić do wniosków
3. Gdy licznik "nie wiem" osiągnie 4 - MUSISZ udzielić jasnej, konkretnej odpowiedzi
4. Po udzieleniu odpowiedzi, wyjaśnij dlaczego ta odpowiedź jest prawidłowa
5. Bądź cierpliwy, zachęcający i mądry
6. Gratuluj gdy uczeń dochodzi do prawidłowych wniosków samodzielnie
7. Dostosowuj poziom trudności pytań do profilu ucznia"""

# =============================================================================
# GŁÓWNY INTERFEJS UŻYTKOWNIKA
# =============================================================================

# Konfiguracja strony Streamlit
st.set_page_config(
    page_title="Sokrates - Cyfrowy Nauczyciel",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Nagłówek główny aplikacji
st.title("🧠 Sokrates - Twój cyfrowy nauczyciel")
st.markdown("""
*"Wiem, że nic nie wiem"* - Sokrates

Witaj w aplikacji, która uczy metodą sokratejską! 
""")

# =============================================================================
# SEKCJA LOGOWANIA UCZNIÓW
# =============================================================================
if not st.session_state["student_name"]:
    st.subheader("👤 Zaloguj się")
    col1, col2 = st.columns([3, 1])
    with col1:
        student_input = st.text_input("Podaj swoje imię:", placeholder="np. Anna, Tomek...")
    with col2:
        if st.button("🚀 Start") and student_input.strip():
            st.session_state["student_name"] = student_input.strip()
            st.session_state["messages"] = []  # Reset rozmowy dla nowego ucznia
            st.session_state["nie_wiem_counter"] = 0
            st.rerun()
    
    # FAQ dla niezalogowanych
    if st.button("❓ Jak to działa?"):
        st.session_state["show_faq"] = not st.session_state["show_faq"]
    
    if st.session_state["show_faq"]:
        st.subheader("❓ Najczęściej zadawane pytania")
        
        with st.expander("🤔 Jak działa metoda sokratejska?"):
            st.write("""
            **Metoda sokratejska** to sposób uczenia przez zadawanie pytań prowadzących, zamiast podawania gotowych odpowiedzi.
            
            **Jak to działa:**
            1. Zadajesz pytanie Sokratesowi
            2. Zamiast odpowiedzi, otrzymujesz pytania, które mają Cię naprowadzić na właściwą odpowiedź
            3. Próbujesz odpowiadać na te pytania
            4. Przez ten proces sam dochodzisz do prawidłowej odpowiedzi!
            """)
        
        with st.expander("❓ Co oznacza 'nie wiem' i licznik?"):
            st.write("""
            **Licznik "nie wiem"** to system pomocy:
            
            - **0-2 razy:** Sokrates zadaje tylko pytania prowadzące
            - **3 razy:** Otrzymujesz wskazówki i częściowe odpowiedzi  
            - **4+ razy:** Otrzymujesz pełną odpowiedź z wyjaśnieniem
            
            **Jak używać:**
            - Gdy naprawdę nie wiesz jak odpowiedzieć, napisz "nie wiem"
            - Możesz też kliknąć przycisk "Udziel odpowiedzi teraz" aby przeskoczyć do pełnej odpowiedzi
            """)
        
        with st.expander("👤 Co to jest profil ucznia?"):
            st.write("""
            **Profil ucznia** to Twoja osobista karta nauki, która zawiera:
            
            - Poziom wiedzy w różnych dziedzinach
            - Sposób, w jaki najlepiej się uczysz
            - Trudności, z jakimi się zmagasz
            - Postępy w nauce
            - Zainteresowania naukowe
            
            Sokrates wykorzystuje te informacje, aby dostosować pytania i metody nauczania do Twoich potrzeb.
            """)
        
        with st.expander("🎯 Jak działa profil nauki?"):
            st.write("""
            **Profil nauki** automatycznie zapisuje informacje o Tobie podczas rozmów:
            
            1. **Automatyczne wykrywanie:** System analizuje Twoje odpowiedzi i wydobywa ważne fakty
            2. **Potwierdzanie:** Możesz zatwierdzić, które informacje chcesz zapisać
            3. **Personalizacja:** Sokrates dostosowuje swoje pytania na podstawie Twojego profilu
            4. **Postęp:** Możesz śledzić swój rozwój w czasie
            """)
        
        with st.expander("🔒 Jak przechowywane są moje dane? (RODO)"):
            st.write("""
            **Ochrona Twoich danych osobowych:**
            
            - **Lokalne przechowywanie:** Wszystkie Twoje dane są zapisywane lokalnie na Twoim komputerze w folderze `db/students/`
            - **Brak wysyłania:** Dane nie są wysyłane na żadne zewnętrzne serwery (poza zapytaniami do OpenAI z Twoimi pytaniami)
            - **Kontrola:** Masz pełną kontrolę nad swoimi danymi - możesz je przeglądać, edytować i usuwać
            - **Plik profilu:** Twój profil jest zapisany jako `{twoje_imie}_memory.json` w folderze `db/students/`
            - **Usuwanie danych:** Możesz usunąć swój profil całkowicie, kasując odpowiedni plik
            
            **Co jest zapisywane:**
            - Poziom wiedzy w różnych dziedzinach
            - Sposób uczenia się i preferencje
            - Trudności w nauce i postępy
            - Zainteresowania naukowe
            
            **Co NIE jest zapisywane:**
            - Dane osobowe (adres, telefon, email)
            - Informacje wrażliwe
            - Historia rozmów (tylko fakty edukacyjne)
            """)
    
    st.stop()  # Zatrzymaj wykonywanie reszty kodu jeśli nie zalogowany

# Nagłówek dla zalogowanego ucznia
col1, col2, col3 = st.columns([3, 1, 1])
with col1:
    st.subheader(f"👋 Cześć {st.session_state['student_name']}!")
    st.write("Zadawaj pytania, a poprowadzę Cię do odpowiedzi przez przemyślane pytania!")
with col2:
    if st.button("❓ FAQ"):
        st.session_state["show_faq"] = not st.session_state["show_faq"]
with col3:
    if st.button("🚪 Wyloguj"):
        st.session_state["student_name"] = ""
        st.session_state["messages"] = []
        st.session_state["nie_wiem_counter"] = 0
        st.rerun()

# FAQ dla zalogowanych
if st.session_state["show_faq"]:
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
            
            st.write("**💡 Wskazówka:**")
            st.write("Używaj przycisku 'Udziel odpowiedzi teraz' gdy chcesz przeskoczyć do rozwiązania!")
    
    with st.expander("🔒 Bezpieczeństwo Twoich danych (RODO)"):
        st.write("""
        **Jak chronię Twoje dane:**
        
        - **📁 Lokalne przechowywanie:** Twój profil jest zapisany tylko na tym komputerze w `db/students/{}_memory.json`
        - **🚫 Brak wysyłania:** Dane nie opuszczają tego urządzenia (poza pytaniami do OpenAI)
        - **✋ Twoja kontrola:** Możesz w każdej chwili usunąć fakty z profilu przyciskiem 🗑️
        - **🗂️ Tylko edukacja:** Zapisuję wyłącznie informacje o Twoim stylu nauki i preferencjach
        - **🔄 Transparentność:** Widzisz wszystko co o Tobie wiem w bocznym panelu
        
        Twoje dane są bezpieczne i pod Twoją kontrolą!
        """.format(st.session_state["student_name"]))

# Status panel
col1, col2, col3 = st.columns(3)
with col1:
    st.metric("Licznik 'nie wiem'", f"{st.session_state['nie_wiem_counter']}/4")
with col2:
    if st.session_state["nie_wiem_counter"] >= 4:
        st.success("✅ Udzielam pełnej odpowiedzi!")
    elif st.session_state["nie_wiem_counter"] >= 3:
        st.success("💡 Mogę udzielić wskazówek!")
    else:
        st.info("🤔 Zadaję pytania prowadzące")
with col3:
    if st.button("🔄 Reset licznika"):
        st.session_state["nie_wiem_counter"] = 0
        st.rerun()

# Przycisk "Udziel odpowiedzi teraz"
if st.session_state["nie_wiem_counter"] < 4 and len(st.session_state["messages"]) > 0:
    if st.button("💡 Udziel odpowiedzi teraz", help="Przejdź od razu do udzielenia odpowiedzi"):
        st.session_state["nie_wiem_counter"] = 4
        st.rerun()

# Pętla wyświetlająca wiadomości
for message in st.session_state["messages"]:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

prompt = st.chat_input("Zadaj pytanie lub powiedz 'nie wiem' jeśli potrzebujesz wskazówek...")
if prompt:
    with st.chat_message("user"):
        st.markdown(prompt)
    st.session_state["messages"].append({"role": "user", "content": prompt})

    with st.chat_message("assistant"):
        response = chatbot_reply(prompt, st.session_state["messages"][-10:])
        st.markdown(response["content"])

    st.session_state["messages"].append({"role": "assistant", "content": response["content"], "usage": response["usage"]})

    # === wyciąganie faktów ===
    nowe_fakty = wyciagnij_fakty_z_tekstu(prompt)
    nowe_fakty = [f.strip("-• ") for f in nowe_fakty if f.strip()]
    st.session_state["facts_to_confirm"] = nowe_fakty

# ======== SIDEBAR - FAKTY ========
with st.sidebar:
    st.header(f"📚 Profil: {st.session_state['student_name']}")
    
    # Uproszczony status nauki
    if st.session_state["nie_wiem_counter"] == 0:
        st.info("🤔 Tryb eksploracji")
    elif st.session_state["nie_wiem_counter"] < 3:
        st.warning("🧭 Prowadzenie do odpowiedzi")  
    elif st.session_state["nie_wiem_counter"] < 4:
        st.success("💡 Gotowy do wskazówek")
    else:
        st.success("✅ Udzielanie pełnej odpowiedzi")

    # Nowe fakty - uproszczone
    if st.session_state["facts_to_confirm"]:
        st.subheader("📋 Nowe informacje o Tobie")
        st.caption("Zaznacz, które informacje chcesz zapisać do swojego profilu:")
        wybrane = []
        for i, fact in enumerate(st.session_state["facts_to_confirm"]):
            if st.checkbox(fact, key=f"fact_{i}"):
                wybrane.append(fact)

        if st.button("💾 Zapisz do profilu"):
            for fact in wybrane:
                zapisz_do_pamieci(fact)
            st.session_state["facts_to_confirm"] = []
            st.success("Profil zaktualizowany!")

    # Historia faktów - skrócona
    st.subheader("🎯 Twój profil nauki")
    st.caption("Co o Tobie wiem:")
    pamiec = wczytaj_pamiec()
    if pamiec:
        # Pokaż tylko ostatnie 3 fakty
        for i, fact in enumerate(pamiec[-3:][::-1]):
            col1, col2 = st.columns([8, 1])
            with col1:
                st.text(fact[:50] + "..." if len(fact) > 50 else fact)
            with col2:
                if st.button("🗑️", key=f"usun_{i}", help="Usuń"):
                    actual_index = len(pamiec) - 1 - i
                    usun_fact(actual_index)
                    st.rerun()
        
        if len(pamiec) > 3:
            st.caption(f"... i {len(pamiec) - 3} więcej informacji")
    else:
        st.caption("Twój profil będzie się budował podczas naszych rozmów")

    # Koszty - uproszczone i w PLN
    st.subheader("💰 Koszty sesji")
    total_input_tokens = sum([message.get("usage", {}).get("prompt_tokens", 0) for message in st.session_state["messages"]])
    total_output_tokens = sum([message.get("usage", {}).get("completion_tokens", 0) for message in st.session_state["messages"]])
    
    koszt_usd = total_input_tokens * PRICING['input_tokens'] + total_output_tokens * PRICING['output_tokens']
    koszt_pln = koszt_usd * USD_TO_PLN
    
    st.metric("Koszt sesji", f"{koszt_pln:.4f} PLN")
    st.caption(f"Tokeny: {total_input_tokens + total_output_tokens}")

