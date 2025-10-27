"""
Pydantic models for validation requests and responses.
"""

from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field, field_validator


class GuardrailConfig(BaseModel):
    """Configuration for a single guardrail validator."""

    name: str = Field(..., description="Name of the guardrail validator")
    config: Dict[str, Any] = Field(
        default_factory=dict,
        description="Configuration parameters for the validator"
    )

    @field_validator('name')
    @classmethod
    def name_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Guardrail name cannot be empty")
        return v.strip()


class ValidationRequest(BaseModel):
    """Request model for text validation."""

    text: str = Field(..., description="Text to validate against guardrails")
    guardrails: List[GuardrailConfig] = Field(
        ...,
        min_length=1,
        description="List of guardrail configurations to apply"
    )

    @field_validator('text')
    @classmethod
    def text_not_empty(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("Text cannot be empty")
        return v

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "text": "Call me at 123-456-7890",
                    "guardrails": [
                        {
                            "name": "RegexMatch",
                            "config": {
                                "regex": "\\(?(\\d{3})\\)?[- ]?(\\d{3})[- ]?(\\d{4})"
                            }
                        }
                    ]
                }
            ]
        }
    }


class FailedGuardrail(BaseModel):
    """Information about a failed guardrail."""

    name: str = Field(..., description="Name of the failed guardrail")
    error: str = Field(..., description="Error message describing the failure")


class ValidationResponse(BaseModel):
    """Response model for validation results."""

    passed: bool = Field(..., description="Whether all validations passed")
    failed_guardrails: List[FailedGuardrail] = Field(
        default_factory=list,
        description="List of failed guardrails with error messages"
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "passed": False,
                    "failed_guardrails": [
                        {
                            "name": "RegexMatch",
                            "error": "Result must match \\(?(\\d{3})\\)?[- ]?(\\d{3})[- ]?(\\d{4})"
                        }
                    ]
                }
            ]
        }
    }


class ErrorResponse(BaseModel):
    """Error response model."""

    detail: str = Field(..., description="Error message")
    guardrail_name: Optional[str] = Field(
        None,
        description="Name of the guardrail that caused the error (if applicable)"
    )

