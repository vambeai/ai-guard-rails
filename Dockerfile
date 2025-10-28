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
# Note: Requires GUARDRAILS_TOKEN environment variable to be set
# Set this in Railway: Variables -> GUARDRAILS_TOKEN=your_token
ARG GUARDRAILS_TOKEN
ENV GUARDRAILS_TOKEN=${GUARDRAILS_TOKEN}

RUN if [ -n "$GUARDRAILS_TOKEN" ]; then \
        echo "🔧 Configuring Guardrails Hub with token..." && \
        echo "token=$GUARDRAILS_TOKEN" > /root/.guardrailsrc && \
        echo "✅ Token configured" && \
        echo "" && \
        echo "📦 Installing Guardrails validators..." && \
        guardrails hub install hub://guardrails/regex_match --quiet && echo "  ✓ regex_match installed" || echo "  ⚠️  regex_match failed" && \
        guardrails hub install hub://guardrails/competitor_check --quiet && echo "  ✓ competitor_check installed" || echo "  ⚠️  competitor_check failed" && \
        guardrails hub install hub://guardrails/toxic_language --quiet && echo "  ✓ toxic_language installed" || echo "  ⚠️  toxic_language failed" && \
        guardrails hub install hub://guardrails/detect_pii --quiet && echo "  ✓ detect_pii installed" || echo "  ⚠️  detect_pii failed" && \
        guardrails hub install hub://guardrails/secrets_present --quiet && echo "  ✓ secrets_present installed" || echo "  ⚠️  secrets_present failed" && \
        guardrails hub install hub://guardrails/gibberish_text --quiet && echo "  ✓ gibberish_text installed" || echo "  ⚠️  gibberish_text failed" && \
        echo "" && \
        echo "✅ Validator installation complete!"; \
    else \
        echo "⚠️  GUARDRAILS_TOKEN not set - skipping validator installation" && \
        echo "ℹ️  Set GUARDRAILS_TOKEN in Railway Variables to enable validators"; \
    fi

# Copy application code
COPY ./app ./app

# Create a non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Download required NLTK data for GibberishText validator
# Download to /usr/local/share/nltk_data which is accessible to all users
RUN python -c "import nltk; nltk.download('punkt', download_dir='/usr/local/share/nltk_data'); nltk.download('punkt_tab', download_dir='/usr/local/share/nltk_data'); nltk.download('stopwords', download_dir='/usr/local/share/nltk_data')" && \
    chmod -R 755 /usr/local/share/nltk_data

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import requests; requests.get('http://localhost:8000/health')" || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

