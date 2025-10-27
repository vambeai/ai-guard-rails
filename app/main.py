"""
FastAPI application with /validate endpoint for guardrails validation.
"""

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.models import ValidationRequest, ValidationResponse, ErrorResponse
from app.validators import guardrail_validator
from app.config import settings


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description=settings.APP_DESCRIPTION,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.ALLOW_ORIGINS,
    allow_credentials=settings.ALLOW_CREDENTIALS,
    allow_methods=settings.ALLOW_METHODS,
    allow_headers=settings.ALLOW_HEADERS,
)


@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "description": settings.APP_DESCRIPTION,
        "endpoints": {
            "validate": "/validate",
            "health": "/health",
            "docs": "/docs"
        }
    }


@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}


@app.post(
    "/validate",
    response_model=ValidationResponse,
    responses={
        200: {
            "description": "Validation completed",
            "model": ValidationResponse,
        },
        400: {
            "description": "Invalid request or configuration",
            "model": ErrorResponse,
        },
        422: {
            "description": "Validation error in request body",
        },
        500: {
            "description": "Internal server error",
            "model": ErrorResponse,
        }
    },
    summary="Validate text against guardrails",
    description=(
        "Validates the provided text against all specified guardrails. "
        "Returns a list of failed guardrails with error messages. "
        "All guardrails are checked even if some fail."
    )
)
async def validate_text(request: ValidationRequest):
    """
    Validate text against specified guardrails.

    The endpoint accepts a text string and a list of guardrail configurations.
    Each guardrail configuration must include:
    - name: The name of the guardrail validator
    - config: A dictionary of configuration parameters required by that validator

    Example request:
    ```json
    {
        "text": "Call me at 123-456-7890",
        "guardrails": [
            {
                "name": "RegexMatch",
                "config": {
                    "regex": "\\\\(?(\\\\d{3})\\\\)?[- ]?(\\\\d{3})[- ]?(\\\\d{4})"
                }
            }
        ]
    }
    ```

    Returns:
    - passed: Boolean indicating if all validations passed
    - failed_guardrails: List of failed guardrails with error messages (empty if all passed)
    """
    try:
        # Step 1: Validate all guardrail configurations first
        configs_valid, config_errors = guardrail_validator.validate_all_configs(
            request.guardrails
        )

        if not configs_valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={
                    "message": "Invalid guardrail configuration(s)",
                    "errors": config_errors
                }
            )

        # Step 2: Run validation against all guardrails
        all_passed, failed_guardrails = guardrail_validator.validate_text(
            request.text,
            request.guardrails
        )

        # Step 3: Return results
        return ValidationResponse(
            passed=all_passed,
            failed_guardrails=failed_guardrails
        )

    except HTTPException:
        # Re-raise HTTP exceptions
        raise

    except Exception as e:
        # Handle unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail={
                "message": "Internal server error during validation",
                "error": str(e)
            }
        )


# Custom exception handler for better error responses
@app.exception_handler(HTTPException)
async def http_exception_handler(request, exc: HTTPException):
    """Custom handler for HTTP exceptions."""
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail}
    )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

