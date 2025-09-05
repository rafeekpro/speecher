# Speecher - Docker Setup Guide

## 🚀 Szybki start

### 1. Przygotuj konfigurację

```bash
# Skopiuj przykładowy plik konfiguracji
cp .env.example .env

# Edytuj plik .env i uzupełnij dane dostępowe do chmury
nano .env
```

### 2. Uruchom aplikację

```bash
# Zbuduj i uruchom wszystkie kontenery
docker-compose up --build

# Lub uruchom w tle
docker-compose up -d --build
```

### 3. Dostęp do aplikacji

- **Frontend (Streamlit)**: http://localhost:8501
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs
- **MongoDB**: localhost:27017

## 📋 Wymagania

- Docker 20.10+
- Docker Compose 1.29+
- Min. 4GB RAM
- 10GB wolnego miejsca na dysku

## ⚙️ Konfiguracja dostawców chmury

### AWS
1. Utwórz konto AWS i wygeneruj klucze dostępu
2. Utwórz bucket S3 lub użyj istniejącego
3. Upewnij się, że masz uprawnienia do Amazon Transcribe
4. Uzupełnij w `.env`:
   ```
   AWS_ACCESS_KEY_ID=your_key
   AWS_SECRET_ACCESS_KEY=your_secret
   AWS_DEFAULT_REGION=eu-central-1
   S3_BUCKET_NAME=your-bucket
   ```

### Azure
1. Utwórz konto Azure i Storage Account
2. Włącz Azure Speech Services
3. Pobierz klucze dostępu
4. Uzupełnij w `.env`:
   ```
   AZURE_STORAGE_ACCOUNT=your_account
   AZURE_STORAGE_KEY=your_key
   AZURE_SPEECH_KEY=your_speech_key
   AZURE_SPEECH_REGION=westeurope
   ```

### Google Cloud
1. Utwórz projekt w GCP
2. Włącz Speech-to-Text API
3. Pobierz plik credentials JSON
4. Umieść plik jako `gcp-credentials.json` w głównym katalogu
5. Uzupełnij w `.env`:
   ```
   GCP_PROJECT_ID=your_project
   GCP_BUCKET_NAME=your-bucket
   GCP_CREDENTIALS_FILE=./gcp-credentials.json
   ```

## 🎨 Funkcje aplikacji

### Frontend - Panel konfiguracji
- **Wybór dostawcy chmury**: AWS, Azure, lub GCP
- **Wybór języka**: 11 języków (PL, EN, DE, ES, FR, IT, PT, RU, ZH, JA)
- **Diaryzacja mówców**: Automatyczne rozpoznawanie do 10 mówców
- **Formaty eksportu**: TXT, SRT (napisy), JSON, VTT, PDF
- **Szacowanie kosztów**: Przed transkrypcją

### Historia transkrypcji
- Przeglądanie wszystkich transkrypcji
- Filtrowanie po nazwie, dacie, dostawcy
- Podgląd i pobieranie wyników
- Usuwanie niepotrzebnych rekordów

### API Endpoints
- `POST /transcribe` - Nowa transkrypcja
- `GET /history` - Historia z filtrowaniem
- `GET /transcription/{id}` - Szczegóły transkrypcji
- `DELETE /transcription/{id}` - Usuwanie
- `GET /stats` - Statystyki użycia
- `GET /health` - Status API
- `GET /db/health` - Status MongoDB

## 🔧 Zarządzanie kontenerami

```bash
# Zatrzymaj wszystkie kontenery
docker-compose down

# Zatrzymaj i usuń wolumeny (UWAGA: usuwa dane!)
docker-compose down -v

# Zobacz logi
docker-compose logs -f

# Logi konkretnego serwisu
docker-compose logs -f backend
docker-compose logs -f frontend
docker-compose logs -f mongo

# Restart serwisu
docker-compose restart backend

# Skalowanie (uruchom wiele instancji backend)
docker-compose up -d --scale backend=3
```

## 📊 Monitorowanie

```bash
# Status kontenerów
docker-compose ps

# Użycie zasobów
docker stats

# Sprawdź health API
curl http://localhost:8000/health

# Sprawdź połączenie z MongoDB
curl http://localhost:8000/db/health

# Zobacz statystyki
curl http://localhost:8000/stats
```

## 🐛 Rozwiązywanie problemów

### Backend nie może połączyć się z MongoDB
```bash
# Sprawdź logi MongoDB
docker-compose logs mongo

# Zrestartuj MongoDB
docker-compose restart mongo
```

### Frontend nie łączy się z backend
```bash
# Sprawdź czy backend działa
curl http://localhost:8000/health

# Sprawdź logi
docker-compose logs backend
docker-compose logs frontend
```

### Błędy uprawnień do chmury
- Sprawdź poprawność kluczy w `.env`
- Upewnij się, że konto ma wymagane uprawnienia
- Dla GCP sprawdź czy plik credentials istnieje

## 🔒 Bezpieczeństwo

1. **Nigdy nie commituj pliku `.env`** - dodaj go do `.gitignore`
2. **Użyj silnych haseł** dla MongoDB
3. **Ogranicz dostęp** do portów w produkcji
4. **Regularnie aktualizuj** obrazy Docker
5. **Szyfruj połączenia** używając reverse proxy (np. Nginx)

## 📦 Deployment produkcyjny

Dla środowiska produkcyjnego:

1. Zmień hasła domyślne
2. Użyj Docker Swarm lub Kubernetes
3. Dodaj SSL/TLS (np. przez Traefik)
4. Skonfiguruj backupy MongoDB
5. Monitoruj logi (np. ELK Stack)
6. Ustaw limity zasobów w docker-compose

```yaml
# Przykład limitów w docker-compose.yml
services:
  backend:
    deploy:
      resources:
        limits:
          cpus: '2'
          memory: 2G
        reservations:
          cpus: '1'
          memory: 1G
```

## 📝 Licencja

Ten projekt jest dostępny na licencji MIT.