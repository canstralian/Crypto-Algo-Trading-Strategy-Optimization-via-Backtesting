# Multi-stage Dockerfile for production deployment

# Build stage
FROM python:3.11-slim as builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir --user -r requirements.txt

# Production stage
FROM python:3.11-slim

WORKDIR /app

# Create non-root user
RUN useradd -m -u 1000 trader && \
    mkdir -p /app/data /app/logs /app/cache && \
    chown -R trader:trader /app

# Copy Python dependencies from builder
COPY --from=builder /root/.local /home/trader/.local

# Copy application code
COPY --chown=trader:trader . .

# Switch to non-root user
USER trader

# Add local Python packages to PATH
ENV PATH=/home/trader/.local/bin:$PATH
ENV PYTHONPATH=/app:$PYTHONPATH

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["python", "-m", "uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
