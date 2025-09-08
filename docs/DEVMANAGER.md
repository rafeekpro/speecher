# Speecher DevManager

Kompleksowe narzędzie do zarządzania środowiskiem developerskim Speecher.

## ⚠️ Wymagania

1. **Docker Desktop** - musi być zainstalowany i uruchomiony
   - macOS: Otwórz Docker Desktop z Applications
   - Poczekaj aż ikona Docker w pasku menu pokaże "Docker Desktop is running"
   
2. **Docker Compose** - zwykle instalowany razem z Docker Desktop

## 🚀 Szybki Start

### Tryb Interaktywny (Menu)
```bash
./dm
# lub
python3 devmanager.py
```

### Tryb Komend
```bash
./dm start          # Uruchom wszystkie usługi
./dm stop           # Zatrzymaj usługi
./dm status         # Pokaż status
./dm test           # Uruchom testy
./dm logs backend   # Pokaż logi
```

## 📋 Funkcje

### 1. Zarządzanie Docker

#### Start/Stop
```bash
./dm start                    # Uruchom wszystkie usługi
./dm stop                     # Zatrzymaj usługi
./dm restart                  # Restart wszystkich usług
./dm restart backend          # Restart konkretnej usługi
```

#### Status i Monitoring
```bash
./dm status                   # Status wszystkich usług
./dm health                   # Szybki health check
./dm logs                     # Logi wszystkich usług
./dm logs backend             # Logi konkretnej usługi
./dm logs backend -f          # Logi na żywo (follow)
```

#### Budowanie
```bash
./dm build                    # Przebuduj obrazy Docker
./dm build --no-cache         # Przebuduj bez cache
```

### 2. Baza Danych

#### Backup/Restore
```bash
./dm backup                   # Utwórz backup MongoDB
./dm restore                  # Przywróć z listy backupów
./dm restore /path/to/backup  # Przywróć konkretny backup
```

#### Dostęp do MongoDB
```bash
./dm shell mongodb            # Otwórz shell MongoDB
```

### 3. Development

#### Testy
```bash
./dm test                     # Uruchom testy integracyjne
```

#### Shell w Kontenerach
```bash
./dm shell backend            # Shell w kontenerze backend
./dm shell frontend           # Shell w kontenerze frontend
./dm shell mongodb            # MongoDB shell
```

### 4. System

#### Czyszczenie
```bash
./dm clean                    # Wyczyść nieużywane zasoby Docker
```

#### Monitoring Zasobów
W trybie interaktywnym (opcja 14) pokazuje:
- Użycie CPU i pamięci przez kontenery
- Użycie miejsca na dysku
- Status sieci

## 🎯 Tryb Interaktywny

Uruchom bez argumentów dla pełnego menu:

```bash
./dm
```

### Menu Główne

```
========================================================
                    Speecher DevManager                    
========================================================

Docker Management:
  1. Start all services
  2. Stop all services
  3. Restart a service
  4. Show service status
  5. View logs
  6. Rebuild services

Database:
  7. Backup database
  8. Restore database
  9. Open MongoDB shell

Development:
  10. Run tests
  11. Open backend shell
  12. Open frontend shell
  13. Configure API keys

System:
  14. Show resource usage
  15. Clean Docker system
  16. Setup environment (.env)

Quick Actions:
  20. Full restart (stop + start)
  21. View backend logs (follow)
  22. Quick health check

  0. Exit
```

## 🔧 Konfiguracja API Keys

### Przez Menu (opcja 13)
1. Wybierz dostawcę (AWS/Azure/GCP)
2. Wprowadź klucze API
3. Automatyczny zapis do bazy danych

### Przez API
```bash
curl -X POST http://localhost:8000/api/keys/aws \
  -H "Content-Type: application/json" \
  -d '{
    "provider": "aws",
    "keys": {
      "access_key_id": "YOUR_KEY",
      "secret_access_key": "YOUR_SECRET",
      "region": "us-east-1",
      "s3_bucket_name": "your-bucket"
    }
  }'
```

## 📁 Struktura Backupów

Backupy są zapisywane w:
```
backups/
├── 20240307_143022/
│   ├── speecher/
│   └── admin/
└── 20240307_150000/
    ├── speecher/
    └── admin/
```

## 🛠️ Rozwiązywanie Problemów

### Docker nie działa
```bash
# macOS: Uruchom Docker Desktop
open -a Docker

# Poczekaj 30 sekund i spróbuj ponownie
./dm status

# Jeśli Docker działa ale DevManager go nie wykrywa
./dm --skip-check start
```

### Usługi nie startują
```bash
./dm health           # Sprawdź health check
./dm logs             # Sprawdź logi
./dm clean           # Wyczyść i spróbuj ponownie
```

### Port zajęty
```bash
# Znajdź proces używający portu
lsof -i :8000
# Zabij proces lub zmień port w docker-compose.yml
```

### MongoDB nie odpowiada
```bash
./dm restart mongodb  # Restart MongoDB
./dm shell mongodb    # Sprawdź połączenie ręcznie
```

## ⚡ Skróty Klawiszowe

W trybie interaktywnym:
- `Ctrl+C` - Wyjście
- `Enter` - Kontynuuj po akcji

## 🔄 Workflow Developerski

### Standardowy Flow
```bash
# 1. Start środowiska
./dm start

# 2. Sprawdź status
./dm status

# 3. Rozwój (kod jest montowany przez volumes - hot reload)
# ... edytuj pliki ...

# 4. Testy
./dm test

# 5. Logi jeśli potrzebne
./dm logs backend -f

# 6. Stop na koniec
./dm stop
```

### Debug Flow
```bash
# 1. Logi na żywo
./dm logs backend -f

# 2. Shell w kontenerze
./dm shell backend

# 3. MongoDB shell
./dm shell mongodb
```

### Backup Flow
```bash
# Przed ważnymi zmianami
./dm backup

# Po problemach
./dm restore
```

## 📊 Monitoring

### Health Check
```bash
./dm health
```
Pokazuje:
- ✓ mongodb: healthy
- ✓ backend: healthy
- ✓ frontend: healthy

### Resource Usage
```bash
# W menu interaktywnym - opcja 14
```
Pokazuje:
- CPU % każdego kontenera
- Użycie pamięci
- Transfer sieciowy
- Użycie dysku

## 🎨 Kolory w Terminalu

- 🟢 Zielony - Sukces
- 🔴 Czerwony - Błąd
- 🟡 Żółty - Ostrzeżenie
- 🔵 Niebieski - Informacja

## 📝 Wszystkie Komendy

```bash
# Zarządzanie
./dm start              # Start usług
./dm stop               # Stop usług
./dm restart [service]  # Restart
./dm status            # Status
./dm health            # Health check

# Logi
./dm logs [service]    # Pokaż logi
./dm logs -f           # Follow logs

# Development
./dm test              # Testy
./dm shell <service>   # Shell w kontenerze
./dm build             # Rebuild
./dm build --no-cache  # Clean rebuild

# Baza danych
./dm backup            # Backup
./dm restore [path]    # Restore

# System
./dm clean             # Czyszczenie

# Pomoc
./dm help              # Pomoc
```

## 🔐 Bezpieczeństwo

- API keys są szyfrowane w bazie danych
- MongoDB wymaga autentykacji
- Wrażliwe dane są maskowane w odpowiedziach API
- Backupy zawierają pełne dane - przechowuj bezpiecznie

## 💡 Tips

1. **Hot Reload**: Kod źródłowy jest montowany jako volume - zmiany są widoczne od razu
2. **Logs**: Użyj `-f` flag do śledzenia logów na żywo
3. **Backups**: Regularnie twórz backupy przed ważnymi zmianami
4. **Clean**: Okresowo czyść system Docker aby zwolnić miejsce
5. **Health**: Zawsze sprawdź health przed testami

## 🚨 Ważne

- DevManager wymaga Docker i docker-compose
- Pierwsze uruchomienie może potrwać dłużej (pobieranie obrazów)
- Volumes zachowują dane między restartami
- Użyj `./dm stop` zamiast `Ctrl+C` dla czystego zamknięcia