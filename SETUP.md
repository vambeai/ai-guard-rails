# Setup Guide

This guide will help you set up and run the FastAPI Guardrails Validator Service.

## Step-by-Step Setup

### 1. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure Guardrails Hub

You need to configure access to the Guardrails Hub to download validators:

```bash
guardrails configure
```

This will prompt you for your Guardrails Hub API token. If you don't have one:

- Visit https://hub.guardrailsai.com/
- Sign up or log in
- Get your API token from your account settings

### 3. Install Validators

Install the validators you want to use. Here are some commonly used ones:

```bash
# Install individual validators
guardrails hub install hub://guardrails/regex_match
guardrails hub install hub://guardrails/competitor_check
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/detect_pii
guardrails hub install hub://guardrails/restrict_to_topic

# Check installed validators
guardrails hub list
```

### 4. Start the Server

Option A - Using the startup script:

```bash
./run.sh
```

Option B - Using uvicorn directly:

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

Option C - Using Python:

```bash
python -m app.main
```

### 5. Test the Service

Open your browser and visit:

- API Documentation: http://localhost:8000/docs
- Alternative Docs: http://localhost:8000/redoc
- Health Check: http://localhost:8000/health

## Quick Test Examples

### Test 1: RegexMatch Validator

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "123-456-7890",
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

Expected response:

```json
{
  "passed": true,
  "failed_guardrails": []
}
```

### Test 2: Multiple Validators

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Our product is great!",
    "guardrails": [
      {
        "name": "CompetitorCheck",
        "config": {
          "competitors": ["Apple", "Microsoft", "Google"]
        }
      },
      {
        "name": "ToxicLanguage",
        "config": {
          "threshold": 0.5,
          "validation_method": "sentence"
        }
      }
    ]
  }'
```

## Troubleshooting

### Issue: "Validator not found"

**Problem:** You get an error saying a validator is not found.

**Solution:** Make sure you've installed the validator:

```bash
guardrails hub install hub://guardrails/<validator-name>
```

### Issue: "Missing required configuration parameters"

**Problem:** The API returns a 400 error about missing config.

**Solution:** Check the validator documentation for required parameters. Common ones:

- `RegexMatch`: requires `regex`
- `CompetitorCheck`: requires `competitors` (list)
- `ToxicLanguage`: requires `threshold` and `validation_method`

### Issue: Import errors

**Problem:** Python can't find the modules.

**Solution:** Make sure you're in the project root directory and have installed all dependencies:

```bash
cd /Users/matiasperez/Desktop/VambeCode/ai-guard-rails
pip install -r requirements.txt
```

### Issue: Guardrails Hub authentication

**Problem:** Can't access Guardrails Hub.

**Solution:** Re-run the configuration:

```bash
guardrails configure
```

## Environment Variables (Optional)

You can customize the service using environment variables:

```bash
# Set custom host and port
export HOST=127.0.0.1
export PORT=8080

# Then start the service
uvicorn app.main:app --host $HOST --port $PORT
```

## Production Deployment

For production deployment, consider:

1. **Use production server settings:**

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --workers 4
```

2. **Use a process manager like systemd or supervisor**

3. **Set up a reverse proxy (nginx/Apache)**

4. **Enable HTTPS**

5. **Configure proper CORS settings** in `app/config.py`

6. **Set up monitoring and logging**

## Next Steps

- Read the full documentation in `README.md`
- Explore the interactive API docs at `/docs`
- Check out [Guardrails Hub](https://hub.guardrailsai.com/) for more validators
- Review the [Guardrails Index](https://index.guardrailsai.com) for performance benchmarks
