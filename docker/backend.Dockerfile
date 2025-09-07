# Backend Dockerfile for development with hot-reload
FROM python:3.11-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    curl \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements files
COPY requirements/base.txt requirements/
COPY pyproject.toml ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements/base.txt && \
    pip install --no-cache-dir uvicorn[standard] watchfiles

# Create non-root user
RUN useradd -m -u 1000 speecher && \
    chown -R speecher:speecher /app

USER speecher

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Default command (can be overridden in docker-compose.yml)
CMD ["uvicorn", "src.backend.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]