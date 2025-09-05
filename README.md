# 🎙️ Speecher - Advanced Audio Transcription Tool

[![Python](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com/)
[![Docker](https://img.shields.io/badge/Docker-Ready-blue.svg)](https://www.docker.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

Speecher is a professional audio transcription tool with automatic speaker recognition, supporting multiple cloud providers (AWS, Azure, Google Cloud). Available as CLI application, REST API, and web interface.

## ✨ Key Features

- 🌐 **Multi-cloud** - supports AWS Transcribe, Azure Speech, and Google Speech-to-Text
- 🗣️ **Speaker diarization** - automatic recognition of up to 10 different speakers
- 🌍 **11 languages** - Polish, English, German, Spanish, French, and more
- ⏱️ **Timestamps** - precise timing for each speaker's utterances
- 💰 **Cost estimation** - calculation before starting transcription
- 📊 **Multiple formats** - export to TXT, SRT, JSON, VTT, PDF
- 🐳 **Docker ready** - full containerization with docker-compose
- 📝 **Transcription history** - MongoDB for storing results

## 🚀 Quick Start (Docker)

### 1. Clone Repository
```bash
git clone https://github.com/yourusername/speecher.git
cd speecher
```

### 2. Configuration
```bash
cp .env.example .env
# Edit .env and add API keys for selected providers
```

### 3. Launch
```bash
docker-compose up --build
```

### 4. Access Application
- **Frontend**: http://localhost:8501
- **API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs

## 💻 Local Installation (CLI)

### Requirements
- Python 3.11+
- Poetry or pip
- Account with AWS/Azure/GCP (at least one)

### Installation
```bash
# With Poetry
poetry install

# Or with pip
pip install -r requirements.txt
```

### CLI Usage
```bash
# Basic transcription
python -m speecher.cli --audio-file audio.wav --language pl-PL

# With file output
python -m speecher.cli --audio-file audio.wav --output-file transcript.txt

# With cost estimation
python -m speecher.cli --audio-file audio.wav --show-cost

# With speaker diarization (max 4 speakers)
python -m speecher.cli --audio-file audio.wav --enable-speaker-identification --max-speakers 4
```

## 🏗️ Architecture

```
speecher/
├── src/
│   ├── speecher/           # Core library
│   │   ├── cli.py          # CLI interface
│   │   ├── main.py         # Main logic
│   │   ├── aws.py          # AWS Transcribe integration
│   │   ├── azure.py        # Azure Speech integration
│   │   ├── gcp.py          # Google Speech integration
│   │   └── transcription.py # Results processing
│   ├── backend/            # REST API (FastAPI)
│   │   └── main.py         # API endpoints
│   └── frontend/           # Web interface (Streamlit)
│       └── app.py          # Frontend application
├── docker-compose.yml      # Docker configuration
├── Dockerfile             # Backend image
└── tests/                 # Unit tests
```

## 🔧 Provider Configuration

### AWS Transcribe
1. Create AWS account
2. Generate access keys (IAM)
3. Create S3 bucket
4. Grant permissions for Transcribe and S3

```bash
# In .env or export
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_DEFAULT_REGION=eu-central-1
S3_BUCKET_NAME=your-bucket
```

### Azure Speech Services
1. Create Azure account
2. Create Storage Account
3. Enable Cognitive Services - Speech
4. Get keys

```bash
AZURE_STORAGE_ACCOUNT=your_account
AZURE_STORAGE_KEY=your_key
AZURE_SPEECH_KEY=your_speech_key
AZURE_SPEECH_REGION=westeurope
```

### Google Cloud Speech-to-Text
1. Create GCP project
2. Enable Speech-to-Text API
3. Create Service Account
4. Download credentials JSON file

```bash
GCP_PROJECT_ID=your_project
GCP_BUCKET_NAME=your-bucket
GOOGLE_APPLICATION_CREDENTIALS=./gcp-credentials.json
```

## 📊 REST API

### Main Endpoints

#### Transcription
```http
POST /transcribe
Content-Type: multipart/form-data

file: audio.wav
provider: aws|azure|gcp
language: pl-PL
enable_diarization: true
max_speakers: 4
```

#### History
```http
GET /history?search=file&provider=aws&limit=50
```

#### Statistics
```http
GET /stats
```

### Usage Example (Python)
```python
import requests

# Upload and transcribe
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

## 🎨 Frontend Features

### Configuration Panel
- Cloud provider selection (AWS/Azure/GCP)
- Language selection (11 languages)
- Diarization configuration (2-10 speakers)
- Export formats (TXT, SRT, JSON, VTT, PDF)
- Cost estimation before transcription

### Transcription History
- Filterable table
- Search by filename
- Filter by date and provider
- Full transcription preview
- Download in various formats
- Record deletion

### Monitoring
- API connection status
- MongoDB database status
- Usage statistics
- Recent transcriptions

## 🧪 Testing

```bash
# Run all tests
pytest

# Tests with coverage
pytest --cov=speecher

# Unit tests only
pytest tests/unit

# Integration tests only
pytest tests/integration
```

## 📈 Performance

| Provider | Processing Time | Accuracy | Cost/min |
|----------|-----------------|----------|----------|
| AWS      | ~30% of audio   | 95-98%   | $0.024   |
| Azure    | ~25% of audio   | 94-97%   | $0.016   |
| GCP      | ~35% of audio   | 93-96%   | $0.018   |

*Approximate data for Polish language

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](CONTRIBUTING.md) for details.

### How to Contribute
1. Fork the repository
2. Create branch (`git checkout -b feature/AmazingFeature`)
3. Commit changes (`git commit -m 'Add AmazingFeature'`)
4. Push to branch (`git push origin feature/AmazingFeature`)
5. Open Pull Request

## 📝 License

This project is available under MIT license. See [LICENSE](LICENSE) for details.

## 🙏 Acknowledgments

- [AWS Transcribe](https://aws.amazon.com/transcribe/)
- [Azure Speech Services](https://azure.microsoft.com/services/cognitive-services/speech-services/)
- [Google Cloud Speech-to-Text](https://cloud.google.com/speech-to-text)
- [FastAPI](https://fastapi.tiangolo.com/)
- [Streamlit](https://streamlit.io/)
- [MongoDB](https://www.mongodb.com/)

## 📞 Contact

Project Name: Speecher  
Link: [https://github.com/yourusername/speecher](https://github.com/yourusername/speecher)

---

⭐ If you like this project, leave a star on GitHub!