"""
Configuration settings for the FastAPI Guardrails service.
"""

from typing import Dict, Set


class Settings:
    """Application settings."""

    # API Settings
    APP_NAME: str = "Guardrails Validator API"
    APP_VERSION: str = "1.0.0"
    APP_DESCRIPTION: str = (
        "A FastAPI service that validates text against Guardrails AI validators. "
        "Supports all validators from the Guardrails Hub."
    )

    # Server Settings
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # CORS Settings
    ALLOW_ORIGINS: list = ["*"]
    ALLOW_CREDENTIALS: bool = True
    ALLOW_METHODS: list = ["*"]
    ALLOW_HEADERS: list = ["*"]


class ValidatorConfig:
    """Configuration for validator requirements and registry."""

    # Map of validator names to their required configuration parameters
    REQUIRED_CONFIGS: Dict[str, Set[str]] = {
        "RegexMatch": {"regex"},
        "CompetitorCheck": {"competitors"},
        "ToxicLanguage": {"threshold", "validation_method"},
        "RestrictToTopic": {"valid_topics"},
        "ReadingTime": {"max_time"},
        "DetectPII": set(),  # No required params, but may have optional ones
        "ExcludeSqlPredicates": set(),
        "ValidLength": {"min", "max"},
        "ValidRange": {"min", "max"},
        "ValidChoices": {"choices"},
        "BugFreePython": set(),
        "BugFreeSQL": set(),
        "ExtractedSummarySentencesMatch": set(),
        "IsHighQualityTranslation": set(),
        "LowerCase": set(),
        "OneLine": set(),
        "TwoWords": set(),
        "UpperCase": set(),
        "ValidURL": set(),
        "SimilarToDocument": {"document", "threshold"},
        "SimilarToList": {"standard_list", "threshold"},
        "Provenance": {"validation_method"},
        "ValidJson": set(),
        "SecretsPresent": set(),
        "ToxicityMetrics": set(),
    }

    # Validators that are commonly available
    COMMON_VALIDATORS: Set[str] = {
        "RegexMatch",
        "CompetitorCheck",
        "ToxicLanguage",
        "DetectPII",
        "RestrictToTopic",
        "ReadingTime",
        "ValidLength",
        "ValidRange",
        "ValidChoices",
        "ValidURL",
        "ValidJson",
        "SecretsPresent",
        "LowerCase",
        "UpperCase",
        "OneLine",
        "TwoWords",
    }

    @classmethod
    def get_required_configs(cls, validator_name: str) -> Set[str]:
        """Get required configuration parameters for a validator."""
        return cls.REQUIRED_CONFIGS.get(validator_name, set())

    @classmethod
    def validate_config(cls, validator_name: str, config: dict) -> tuple[bool, str]:
        """
        Validate that a configuration has all required parameters.

        Returns:
            tuple: (is_valid, error_message)
        """
        required = cls.get_required_configs(validator_name)

        if not required:
            return True, ""

        missing = required - set(config.keys())
        if missing:
            return False, f"Missing required configuration parameters: {', '.join(missing)}"

        return True, ""


# Create singleton instances
settings = Settings()
validator_config = ValidatorConfig()

