# Test Dockerfile for running integration tests
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements
COPY requirements.txt pyproject.toml ./

# Install Python dependencies including test dependencies
RUN pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir pytest pytest-asyncio pytest-cov pytest-mock requests-mock

# Create non-root user
RUN useradd -m -u 1000 speecher && \
    chown -R speecher:speecher /app

USER speecher

# Default command runs tests
CMD ["pytest", "tests/", "-v", "--tb=short"]