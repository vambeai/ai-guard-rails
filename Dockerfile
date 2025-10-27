# FastAPI Guardrails Validator - Production Dockerfile

# Use Python 3.11 slim image as base
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies (including git for guardrails hub)
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install common Guardrails validators from Hub
# These will be available for use in the API
RUN echo "Installing Guardrails validators..." && \
    guardrails hub install hub://guardrails/regex_match --quiet || echo "Failed to install regex_match" && \
    guardrails hub install hub://guardrails/competitor_check --quiet || echo "Failed to install competitor_check" && \
    guardrails hub install hub://guardrails/toxic_language --quiet || echo "Failed to install toxic_language" && \
    guardrails hub install hub://guardrails/detect_pii --quiet || echo "Failed to install detect_pii" && \
    guardrails hub install hub://guardrails/restrict_to_topic --quiet || echo "Failed to install restrict_to_topic" && \
    guardrails hub install hub://guardrails/secrets_present --quiet || echo "Failed to install secrets_present" && \
    guardrails hub install hub://guardrails/valid_url --quiet || echo "Failed to install valid_url" && \
    echo "Validator installation complete"

# Copy application code
COPY ./app ./app

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

