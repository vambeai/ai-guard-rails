# Quick Start Guide

Get the FastAPI Guardrails Validator service running in under 5 minutes!

## 🐳 Docker (Recommended - Fastest)

### Prerequisites

- Docker installed
- Docker Compose installed

### Start the Service

```bash
# 1. Build and start (production mode)
docker-compose up -d --build

# 2. Wait a few seconds for the service to start, then test
curl http://localhost:8000/health
```

**That's it!** The service is now running at `http://localhost:8000`

Visit `http://localhost:8000/docs` for interactive API documentation.

### Test the Service

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a test message",
    "guardrails": [
      {
        "name": "ValidLength",
        "config": {
          "min": 5,
          "max": 100
        }
      }
    ]
  }'
```

### Stop the Service

```bash
docker-compose down
```

---

## 🐍 Python (Local Development)

### Prerequisites

- Python 3.9 or higher
- pip

### Start the Service

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Start the server
uvicorn app.main:app --reload
```

**That's it!** The service is now running at `http://localhost:8000`

---

## 📝 Using Make (Simplified Commands)

If you have `make` installed:

```bash
# Docker production
make prod

# Local development
make dev

# Run tests
make test

# View all available commands
make help
```

---

## 🎯 Next Steps

### Install Guardrails Validators

To use specific validators, you need to install them:

```bash
# Configure Guardrails Hub
guardrails configure

# Install validators
guardrails hub install hub://guardrails/regex_match
guardrails hub install hub://guardrails/competitor_check
guardrails hub install hub://guardrails/toxic_language
```

**Note:** Some validators may require additional setup or API keys.

### Example Requests

**1. Regex Match (Phone Number)**

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Call me at 123-456-7890",
    "guardrails": [
      {
        "name": "RegexMatch",
        "config": {
          "regex": "\\d{3}-\\d{3}-\\d{4}"
        }
      }
    ]
  }'
```

**2. Competitor Check**

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Our product is excellent!",
    "guardrails": [
      {
        "name": "CompetitorCheck",
        "config": {
          "competitors": ["Apple", "Microsoft", "Google"]
        }
      }
    ]
  }'
```

**3. Multiple Guardrails**

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "This is a great product!",
    "guardrails": [
      {
        "name": "ValidLength",
        "config": {
          "min": 10,
          "max": 100
        }
      },
      {
        "name": "CompetitorCheck",
        "config": {
          "competitors": ["Apple", "Microsoft"]
        }
      }
    ]
  }'
```

---

## 📚 More Information

- **Full Documentation:** [README.md](README.md)
- **Docker Guide:** [DOCKER.md](DOCKER.md)
- **Setup Guide:** [SETUP.md](SETUP.md)
- **API Docs:** http://localhost:8000/docs (when running)

## 🆘 Troubleshooting

**Port 8000 already in use?**

```bash
# Use different port with Docker
docker run -p 9000:8000 guardrails-validator

# Or with Python
uvicorn app.main:app --port 9000
```

**Validator not found?**
Make sure you've installed it:

```bash
guardrails hub install hub://guardrails/<validator-name>
```

**Service won't start?**

```bash
# Check logs (Docker)
docker-compose logs

# Check Python errors
python -c "from app.main import app; print('OK')"
```

## 🎉 You're Ready!

Start validating text with Guardrails AI! 🚀
