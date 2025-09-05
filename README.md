# 🎙️ Speecher - Zaawansowane narzędzie transkrypcji audio

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Speecher to profesjonalne narzędzie do transkrypcji plików audio z automatycznym rozpoznawaniem mówców, obsługujące wielu dostawców chmury (AWS, Azure, Google Cloud). Dostępne jako aplikacja CLI, REST API oraz interfejs webowy.

## ✨ Główne funkcje

- 🌐 **Multi-cloud** - obsługa AWS Transcribe, Azure Speech i Google Speech-to-Text
- 🗣️ **Diaryzacja mówców** - automatyczne rozpoznawanie do 10 różnych osób
- 🌍 **11 języków** - polski, angielski, niemiecki, hiszpański, francuski i więcej
- ⏱️ **Znaczniki czasu** - dokładne czasy wypowiedzi każdego mówcy
- 💰 **Szacowanie kosztów** - kalkulacja przed rozpoczęciem transkrypcji
- 📊 **Wiele formatów** - eksport do TXT, SRT, JSON, VTT, PDF
- 🐳 **Docker ready** - pełna konteneryzacja z docker-compose
- 📝 **Historia transkrypcji** - MongoDB do przechowywania wyników

## 🚀 Szybki start (Docker)

### 1. Klonowanie repozytorium
```bash
git clone https://github.com/yourusername/speecher.git
cd speecher
```

### 2. Konfiguracja
```bash
cp .env.example .env
# Edytuj .env i dodaj klucze API dla wybranych dostawców
```

### 3. Uruchomienie
```bash
docker-compose up --build
```

### 4. Dostęp do aplikacji
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **Dokumentacja API**: http://localhost:8000/docs

## 💻 Instalacja lokalna (CLI)

### Wymagania
- Python 3.11+
- Poetry lub pip
- Konto w AWS/Azure/GCP (przynajmniej jedno)

### Instalacja
```bash
# Z Poetry
poetry install

# Lub z pip
pip install -r requirements.txt
```

### Użycie CLI
```bash
# Podstawowa transkrypcja
python -m speecher.cli --audio-file audio.wav --language pl-PL

# Z zapisem do pliku
python -m speecher.cli --audio-file audio.wav --output-file transcript.txt

# Z szacowaniem kosztów
python -m speecher.cli --audio-file audio.wav --show-cost

# Z diaryzacją mówców (max 4 osoby)
python -m speecher.cli --audio-file audio.wav --enable-speaker-identification --max-speakers 4
```

## 🏗️ Architektura

```
speecher/
├── src/
│   ├── speecher/           # Główna biblioteka
│   │   ├── cli.py          # Interfejs CLI
│   │   ├── main.py         # Główna logika
│   │   ├── aws.py          # Integracja AWS Transcribe
│   │   ├── azure.py        # Integracja Azure Speech
│   │   ├── gcp.py          # Integracja Google Speech
│   │   └── transcription.py # Przetwarzanie wyników
│   ├── backend/            # REST API (FastAPI)
│   │   └── main.py         # Endpointy API
│   └── frontend/           # Interfejs webowy (Streamlit)
│       └── app.py          # Aplikacja frontend
├── docker-compose.yml      # Konfiguracja Docker
├── Dockerfile             # Obraz backend
└── tests/                 # Testy jednostkowe
```

## 🔧 Konfiguracja dostawców

### AWS Transcribe
1. Utwórz konto AWS
2. Wygeneruj klucze dostępu (IAM)
3. Utwórz bucket S3
4. Nadaj uprawnienia do Transcribe i S3

```bash
# W .env lub eksportuj
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=eu-central-1
S3_BUCKET_NAME=your-bucket
```

### Azure Speech Services
1. Utwórz konto Azure
2. Utwórz Storage Account
3. Włącz Cognitive Services - Speech
4. Pobierz klucze

```bash
AZURE_STORAGE_ACCOUNT=your_account
AZURE_STORAGE_KEY=your_key
AZURE_SPEECH_KEY=your_speech_key
AZURE_SPEECH_REGION=westeurope
```

### Google Cloud Speech-to-Text
1. Utwórz projekt w GCP
2. Włącz Speech-to-Text API
3. Utwórz Service Account
4. Pobierz plik credentials JSON

```bash
GCP_PROJECT_ID=your_project
GCP_BUCKET_NAME=your-bucket
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
```

## 📊 REST API

### Główne endpointy

#### Transkrypcja
```http
POST /transcribe
Content-Type: multipart/form-data

file: audio.wav
provider: aws|azure|gcp
language: pl-PL
enable_diarization: true
max_speakers: 4
```

#### Historia
```http
GET /history?search=file&provider=aws&limit=50
```

#### Statystyki
```http
GET /stats
```

### Przykład użycia (Python)
```python
import requests

# Upload i transkrypcja
with open("audio.wav", "rb") as f:
    response = requests.post(
        "http://localhost:8000/transcribe",
        files={"file": f},
        data={
            "provider": "aws",
            "language": "pl-PL",
            "enable_diarization": True
        }
    )
    
result = response.json()
print(result["transcript"])
```

## 🎨 Frontend - Funkcje

### Panel konfiguracji
- Wybór dostawcy chmury (AWS/Azure/GCP)
- Wybór języka (11 języków)
- Konfiguracja diaryzacji (2-10 mówców)
- Formaty eksportu (TXT, SRT, JSON, VTT, PDF)
- Szacowanie kosztów przed transkrypcją

### Historia transkrypcji
- Tabela z filtrowaniem
- Wyszukiwanie po nazwie
- Filtrowanie po dacie i dostawcy
- Podgląd pełnej transkrypcji
- Pobieranie w różnych formatach
- Usuwanie rekordów

### Monitoring
- Status połączenia z API
- Status bazy danych MongoDB
- Statystyki użycia
- Ostatnie transkrypcje

## 🧪 Testowanie

```bash
# Uruchom wszystkie testy
pytest

# Testy z coverage
pytest --cov=speecher

# Tylko testy jednostkowe
pytest tests/unit

# Tylko testy integracyjne
pytest tests/integration
```

## 📈 Wydajność

| Dostawca | Czas przetwarzania | Dokładność | Koszt/min |
|----------|-------------------|------------|-----------|
| AWS      | ~30% czasu audio  | 95-98%     | $0.024    |
| Azure    | ~25% czasu audio  | 94-97%     | $0.016    |
| GCP      | ~35% czasu audio  | 93-96%     | $0.018    |

*Dane przybliżone dla języka polskiego

## 🤝 Współpraca

Zachęcamy do współpracy! Zobacz [CONTRIBUTING.md](CONTRIBUTING.md) dla szczegółów.

### Jak pomóc
1. Fork repozytorium
2. Utwórz branch (`git checkout -b feature/AmazingFeature`)
3. Commit zmiany (`git commit -m 'Add AmazingFeature'`)
4. Push do branch (`git push origin feature/AmazingFeature`)
5. Otwórz Pull Request

## 📝 Licencja

Projekt dostępny na licencji MIT. Zobacz [LICENSE](LICENSE) dla szczegółów.

## 🙏 Podziękowania

- [AWS Transcribe](https://aws.amazon.com/transcribe/)
- [Azure Speech Services](https://azure.microsoft.com/services/cognitive-services/speech-services/)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [MongoDB](https://www.mongodb.com/)

## 📞 Kontakt

Nazwa Projektu: Speecher  
Link: [https://github.com/yourusername/speecher](https://github.com/yourusername/speecher)

---

⭐ Jeśli projekt Ci się podoba, zostaw gwiazdkę na GitHub!