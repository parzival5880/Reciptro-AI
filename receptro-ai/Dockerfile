# Dockerfile for Receptro.AI Pipeline
FROM python:3.9-slim

# Install system dependencies
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-eng \
    ffmpeg \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements and install Python dependencies
COPY requirements-simple.txt .
RUN pip install --no-cache-dir -r requirements-simple.txt

# Copy application code
COPY . .

# Create necessary directories
RUN mkdir -p outputs demo_outputs inputs

# Set environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1

# Default command
CMD ["python3", "run_full_demo.py"]