#!/bin/bash

# FastAPI Guardrails Validator Service - Startup Script

echo "Starting FastAPI Guardrails Validator Service..."
echo ""
echo "Make sure you have:"
echo "1. Installed dependencies: pip install -r requirements.txt"
echo "2. Configured Guardrails Hub: guardrails configure"
echo "3. Installed desired validators: guardrails hub install hub://guardrails/<validator-name>"
echo ""
echo "Starting server on http://0.0.0.0:8000"
echo "API Documentation: http://localhost:8000/docs"
echo ""

uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

