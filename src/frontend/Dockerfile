FROM python:3.11-slim

WORKDIR /app

# Install required packages
RUN pip install --no-cache-dir \
    streamlit==1.28.0 \
    requests==2.31.0 \
    pandas==2.1.2 \
    python-multipart==0.0.6

# Copy application
COPY app.py .

# Expose Streamlit port
EXPOSE 8501

# Run Streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]