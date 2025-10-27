# FastAPI Guardrails Validator Service

A FastAPI service that validates text against [Guardrails AI](https://www.guardrailsai.com/) validators. This service provides a single endpoint that can validate text against multiple guardrails simultaneously, returning detailed information about any failures.

## Features

- ✅ Single `/validate` endpoint for all guardrail validations
- ✅ Supports all validators from [Guardrails Hub](https://hub.guardrailsai.com/)
- ✅ Validates against all specified guardrails (doesn't stop at first failure)
- ✅ Returns detailed error messages for each failed guardrail
- ✅ Request body validation with helpful error messages
- ✅ OpenAPI/Swagger documentation at `/docs`
- ✅ CORS enabled for cross-origin requests

## Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. Clone the repository:

```bash
git clone <repository-url>
cd ai-guard-rails
```

2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Configure Guardrails Hub (required for accessing validators):

```bash
guardrails configure
```

4. Install the guardrails you want to use. Examples:

```bash
# Install specific validators
guardrails hub install hub://guardrails/regex_match
guardrails hub install hub://guardrails/competitor_check
guardrails hub install hub://guardrails/toxic_language
guardrails hub install hub://guardrails/detect_pii

# Or install commonly used validators
guardrails hub install hub://guardrails/competitor_check
guardrails hub install hub://guardrails/toxic_language
```

### Running the Service

Start the FastAPI server:

```bash
# Using uvicorn directly
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

# Or using Python
python -m app.main
```

The service will be available at `http://localhost:8000`

- API documentation: `http://localhost:8000/docs`
- Alternative docs: `http://localhost:8000/redoc`

### Docker Deployment

For production deployment, you can use Docker:

```bash
# Build and start with Docker Compose
docker-compose up -d

# Or build manually
docker build -t guardrails-validator .
docker run -d -p 8000:8000 guardrails-validator
```

**Development with hot reload:**

```bash
docker-compose -f docker-compose.dev.yml up
```

See [DOCKER.md](DOCKER.md) for complete Docker deployment documentation.

## API Usage

### Endpoint: `POST /validate`

Validates text against specified guardrails and returns a list of failed guardrails with error messages.

#### Request Body

```json
{
  "text": "string (required) - Text to validate",
  "guardrails": [
    {
      "name": "string (required) - Name of the guardrail validator",
      "config": {
        "key": "value (optional) - Configuration parameters for the validator"
      }
    }
  ]
}
```

#### Response

```json
{
  "passed": "boolean - True if all validations passed",
  "failed_guardrails": [
    {
      "name": "string - Name of the failed guardrail",
      "error": "string - Error message describing the failure"
    }
  ]
}
```

## Examples

### Example 1: Regex Validation

Validate that text contains a phone number in the correct format.

**Request:**

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Call me at 123-456-7890",
    "guardrails": [
      {
        "name": "RegexMatch",
        "config": {
          "regex": "\\(?(\\d{3})\\)?[- ]?(\\d{3})[- ]?(\\d{4})"
        }
      }
    ]
  }'
```

**Response (Success):**

```json
{
  "passed": true,
  "failed_guardrails": []
}
```

**Request (Invalid format):**

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Call me at 1234567890",
    "guardrails": [
      {
        "name": "RegexMatch",
        "config": {
          "regex": "\\(?(\\d{3})\\)?[- ]?(\\d{3})[- ]?(\\d{4})"
        }
      }
    ]
  }'
```

**Response (Failure):**

```json
{
  "passed": false,
  "failed_guardrails": [
    {
      "name": "RegexMatch",
      "error": "Result must match \\(?(\\d{3})\\)?[- ]?(\\d{3})[- ]?(\\d{4})"
    }
  ]
}
```

### Example 2: Multiple Guardrails (Competitor Check + Toxic Language)

Validate text doesn't mention competitors or contain toxic language.

**Request:**

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Our product is better than what you will find anywhere else!",
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

**Response (Success):**

```json
{
  "passed": true,
  "failed_guardrails": []
}
```

**Request (With violations):**

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Shut up! Apple makes terrible products!",
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

**Response (Multiple failures):**

```json
{
  "passed": false,
  "failed_guardrails": [
    {
      "name": "CompetitorCheck",
      "error": "Found the following competitors: [['Apple']]. Please avoid naming those competitors next time"
    },
    {
      "name": "ToxicLanguage",
      "error": "The following sentences in your response were found to be toxic:\n- Shut up!"
    }
  ]
}
```

### Example 3: PII Detection

Detect personally identifiable information in text.

**Request:**

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "My email is john.doe@example.com and my SSN is 123-45-6789",
    "guardrails": [
      {
        "name": "DetectPII",
        "config": {}
      }
    ]
  }'
```

**Response (Failure - PII detected):**

```json
{
  "passed": false,
  "failed_guardrails": [
    {
      "name": "DetectPII",
      "error": "The following PII entities were detected: EMAIL_ADDRESS, US_SSN"
    }
  ]
}
```

### Example 4: Topic Restriction

Ensure text stays on specified topics.

**Request:**

```bash
curl -X POST "http://localhost:8000/validate" \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Let me tell you about my favorite recipe for chocolate cake.",
    "guardrails": [
      {
        "name": "RestrictToTopic",
        "config": {
          "valid_topics": ["technology", "programming", "software"]
        }
      }
    ]
  }'
```

## Supported Guardrails

The service supports all validators available in the Guardrails Hub. Here are some commonly used ones:

| Validator         | Required Config                  | Description                                  |
| ----------------- | -------------------------------- | -------------------------------------------- |
| `RegexMatch`      | `regex`                          | Validates text matches a regex pattern       |
| `CompetitorCheck` | `competitors` (list)             | Detects mentions of competitor names         |
| `ToxicLanguage`   | `threshold`, `validation_method` | Detects toxic/offensive language             |
| `DetectPII`       | None                             | Detects personally identifiable information  |
| `RestrictToTopic` | `valid_topics` (list)            | Ensures text stays on specified topics       |
| `ReadingTime`     | `max_time`                       | Validates text can be read within time limit |
| `ValidLength`     | `min`, `max`                     | Validates text length is within range        |
| `ValidURL`        | None                             | Validates text contains valid URLs           |
| `ValidJson`       | None                             | Validates text is valid JSON                 |
| `SecretsPresent`  | None                             | Detects secrets/API keys in text             |

For a complete list of available validators, visit [Guardrails Hub](https://hub.guardrailsai.com/).

## Error Responses

### 400 Bad Request - Invalid Guardrail Configuration

```json
{
  "detail": {
    "message": "Invalid guardrail configuration(s)",
    "errors": ["RegexMatch: Missing required configuration parameters: regex"]
  }
}
```

### 400 Bad Request - Validator Not Found

```json
{
  "detail": {
    "message": "Invalid guardrail configuration(s)",
    "errors": [
      "UnknownValidator: Validator 'UnknownValidator' not found. Make sure it's installed from Guardrails Hub."
    ]
  }
}
```

### 422 Unprocessable Entity - Validation Error

```json
{
  "detail": [
    {
      "type": "value_error",
      "loc": ["body", "text"],
      "msg": "Text cannot be empty",
      "input": ""
    }
  ]
}
```

## Development

### Project Structure

```
ai-guard-rails/
├── app/
│   ├── __init__.py          # Package initialization
│   ├── main.py              # FastAPI application and endpoints
│   ├── models.py            # Pydantic models for request/response
│   ├── validators.py        # Guardrails validator logic
│   └── config.py            # Configuration settings
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── .gitignore              # Git ignore patterns
```

### Running in Development Mode

```bash
uvicorn app.main:app --reload
```

### Testing the API

Use the interactive API documentation at `http://localhost:8000/docs` to test endpoints directly in your browser.

Or use curl/httpie/Postman with the examples above.

## Configuration

Configuration settings can be modified in `app/config.py`:

- `HOST`: Server host (default: `0.0.0.0`)
- `PORT`: Server port (default: `8000`)
- `ALLOW_ORIGINS`: CORS allowed origins (default: `["*"]`)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See LICENSE file for details.

## Resources

- [Guardrails AI Documentation](https://www.guardrailsai.com/docs)
- [Guardrails Hub](https://hub.guardrailsai.com/)
- [Guardrails Index - Performance Benchmark](https://index.guardrailsai.com)
- [FastAPI Documentation](https://fastapi.tiangolo.com/)

## Support

For issues related to:

- **This API service**: Open an issue in this repository
- **Guardrails AI framework**: Visit [Guardrails AI GitHub](https://github.com/guardrails-ai/guardrails)
- **Specific validators**: Check [Guardrails Hub](https://hub.guardrailsai.com/)
