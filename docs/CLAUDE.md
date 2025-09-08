# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Important Instructions

- **NEVER** add "Co-Authored-By: Claude <noreply@anthropic.com>" to git commits
- Do not add any AI-related authorship attributions to commits

## Project Overview

Speecher is an audio transcription tool that supports multiple cloud providers (AWS, Azure, GCP) for converting WAV audio files to text with speaker identification. The project provides both a CLI tool and a web application with FastAPI backend and Streamlit frontend.

## Development Commands

### Setup & Installation
```bash
# Install dependencies
poetry install

# Optional: Add pydub for cost estimation
poetry add pydub
```

### Testing
```bash
# Run all tests
pytest

# Run with custom test runners (includes detailed output)
python run_tests.py
python run_detailed_tests.py

# Run specific test file
pytest tests/test_aws.py
```

### Running the Application

#### CLI Usage
```bash
# Basic transcription
poetry run python -m speecher.cli --audio-file audio.wav --language pl-PL

# With output file
poetry run python -m speecher.cli --audio-file audio.wav --output-file transcript.txt

# Show cost estimation
poetry run python -m speecher.cli --audio-file audio.wav --show-cost
```

#### Docker Deployment
```bash
# Start full application stack (MongoDB, Backend, Frontend)
docker-compose up

# Build backend Docker image
docker build -t speecher-backend .
```

### Linting & Type Checking
```bash
# Run linting (if configured in pyproject.toml)
poetry run pylint src/

# Type checking (if mypy is configured)
poetry run mypy src/
```

## High-Level Architecture

### Component Structure

```
src/
├── speecher/           # Core library with cloud provider integrations
│   ├── cli.py         # Command-line interface
│   ├── main.py        # Main entry point and orchestration
│   ├── aws.py         # AWS S3 + Transcribe integration
│   ├── azure.py       # Azure Blob + Speech Service integration  
│   ├── gcp.py         # Google Cloud Speech-to-Text integration
│   ├── transcription.py # Results processing with speaker diarization
│   └── utils.py       # Shared utilities and helpers
├── backend/           # FastAPI REST API
│   └── main.py        # API endpoints, MongoDB integration
└── frontend/          # Streamlit web UI
    └── app.py         # User interface for file upload and results
```

### Data Flow

1. **Audio Input**: User uploads WAV file via CLI or web interface
2. **Cloud Upload**: File is uploaded to chosen cloud storage (S3/Blob/GCS)
3. **Transcription**: Cloud service processes audio with speaker diarization
4. **Processing**: Results are parsed and formatted with timestamps
5. **Storage**: Transcriptions saved to MongoDB (web) or file (CLI)
6. **Cleanup**: Temporary cloud resources are deleted (unless --keep-resources)

### Key Design Patterns

- **Multi-Cloud Abstraction**: Each cloud provider (AWS, Azure, GCP) implements consistent interface for upload/transcribe/cleanup operations
- **Speaker Diarization**: All providers support automatic speaker identification with configurable max speakers
- **Cost Calculation**: Built-in estimation of cloud service costs based on audio duration
- **Async Processing**: Backend API uses FastAPI's async capabilities for non-blocking operations
- **Resource Management**: Automatic cleanup of cloud resources with optional preservation flag

### Environment Configuration

The application uses environment variables for cloud credentials and service configuration:

- **AWS**: Requires AWS CLI configuration or environment variables (AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION)
- **MongoDB**: Connection URI and database/collection names for web deployment
- **Docker Compose**: Full environment variables defined in docker-compose.yml

### Testing Approach

- Tests are organized by module in `tests/` directory
- Mock implementations for cloud services to avoid API calls
- Test data stored in `tests/test_data/`
- Result logging to `test_results/` directory
- Custom test runners for detailed output and debugging