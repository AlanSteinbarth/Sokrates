# Security Policy

## 🔒 Zgłaszanie luk bezpieczeństwa

Bezpieczeństwo Sokratesa i danych użytkowników to nasz priorytet. Jeśli odkryłeś lukę bezpieczeństwa, prosimy o odpowiedzialne zgłoszenie.

### ✅ Wspierane wersje

| Wersja | Wsparcie         |
| ------ | ---------------- |
| 2.0.x  | ✅ Pełne wsparcie |
| 1.x.x  | ❌ Brak wsparcia  |

### 🚨 Jak zgłosić lukę bezpieczeństwa

**NIE** zgłaszaj luk bezpieczeństwa przez publiczne issues GitHub!

Zamiast tego:

1. **Email:** Wyślij raport na `alan.steinbarth@gmail.com` z tematem `[SECURITY] Sokrates Security Issue`
2. **Zawartość raportu poinna zawierać:**
   - Opis luki bezpieczeństwa
   - Kroki do odtworzenia
   - Potencjalny wpływ
   - Sugerowane rozwiązanie (jeśli masz)
   - Twoje dane kontaktowe

### ⏱️ Czas odpowiedzi

- **24 godziny:** Potwierdzenie otrzymania zgłoszenia
- **72 godziny:** Wstępna ocena luki
- **7 dni:** Plan naprawy lub info dlaczego nie jest to luka
- **30 dni:** Implementacja poprawki (w zależności od złożoności)

### 🏆 Uznanie

Doceniamy odpowiedzialne zgłaszanie luk bezpieczeństwa. Jeśli zgłosisz prawdziwą lukę:

- Zostaniesz wymieniony w CHANGELOG.md (jeśli chcesz)
- Otrzymasz podziękowania w kolejnym release
- Możemy skontaktować się z Tobą w sprawie szczegółów poprawki

### 🛡️ Zakres bezpieczeństwa

**W zakresie:**
- Luki w kodzie aplikacji
- Problemy z walidacją danych
- Potencjalne injections (SQL, command, etc.)
- Problemy z autoryzacją/autentykacją
- Eksponowanie wrażliwych danych
- Problemy z RODO/prywatnością

**Poza zakresem:**
- Problemy z infrastrukturą GitHub
- Luki w zależnościach (zgłoś je do odpowiednich projektów)
- Social engineering
- Physical attacks
- DoS/DDoS ataki na publiczne instancje

### 🔧 Najlepsze praktyki bezpieczeństwa

Jeśli hostujesz Sokratesa publicznie:

1. **Zawsze** używaj HTTPS
2. **Nigdy** nie commituj kluczy API
3. Używaj najnowszej wersji zależności
4. Regularnie aktualizuj Sokratesa
5. Monitoruj logi pod kątem podejrzanej aktywności
6. Ogranicz dostęp do plików konfiguracyjnych

### 📋 Polityka odpowiedzialnego ujawniania

1. Zgłoś lukę prywatnie
2. Daj nam czas na naprawę (max 90 dni)
3. Nie eksploatuj luki w szkodliwy sposób
4. Nie ujawniaj luki publicznie przed naprawą
5. Działaj w dobrej wierze

### 📞 Kontakt

**Email bezpieczeństwa:** alan.steinbarth@gmail.com  
**Temat:** `[SECURITY] Sokrates Security Issue`

Dziękujemy za pomoc w utrzymaniu bezpieczeństwa Sokratesa! 🙏
