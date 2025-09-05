FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
RUN pip install --no-cache-dir \
    fastapi==0.104.1 \
    uvicorn==0.24.0 \
    pymongo==4.5.0 \
    boto3==1.28.85 \
    azure-storage-blob==12.19.0 \
    azure-cognitiveservices-speech==1.33.0 \
    google-cloud-speech==2.22.0 \
    pydantic==2.5.0 \
    python-multipart==0.0.6 \
    requests==2.31.0

# Copy application code
COPY src/ ./src/

# Expose port
EXPOSE 8000

# Run the application with auto-reload for development
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]