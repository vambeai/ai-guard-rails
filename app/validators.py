"""
Guardrails validator registry and validation logic.
"""

import importlib
from typing import List, Dict, Any, Tuple, Optional
from guardrails import Guard, OnFailAction
from guardrails.errors import ValidationError

from app.models import GuardrailConfig, FailedGuardrail
from app.config import validator_config


class GuardrailValidator:
    """Handles dynamic loading and validation of guardrails."""

    def __init__(self):
        self.validator_cache: Dict[str, Any] = {}

    def _load_validator_class(self, validator_name: str) -> Optional[Any]:
        """
        Dynamically load a validator class from guardrails.hub.

        Args:
            validator_name: Name of the validator to load

        Returns:
            Validator class or None if not found
        """
        # Check cache first
        if validator_name in self.validator_cache:
            return self.validator_cache[validator_name]

        try:
            # Try to import from guardrails.hub
            hub_module = importlib.import_module("guardrails.hub")
            validator_class = getattr(hub_module, validator_name, None)

            if validator_class:
                self.validator_cache[validator_name] = validator_class
                return validator_class
        except (ImportError, AttributeError):
            pass

        # Try alternative import patterns
        try:
            # Convert CamelCase to snake_case for module name
            module_name = self._camel_to_snake(validator_name)
            module = importlib.import_module(f"guardrails.hub.{module_name}")
            validator_class = getattr(module, validator_name, None)

            if validator_class:
                self.validator_cache[validator_name] = validator_class
                return validator_class
        except (ImportError, AttributeError):
            pass

        return None

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """Convert CamelCase to snake_case."""
        import re
        name = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])([A-Z])', r'\1_\2', name).lower()

    def validate_guardrail_config(
        self,
        guardrail: GuardrailConfig
    ) -> Tuple[bool, str]:
        """
        Validate that a guardrail configuration is valid.

        Args:
            guardrail: Guardrail configuration to validate

        Returns:
            tuple: (is_valid, error_message)
        """
        # Check if validator exists
        validator_class = self._load_validator_class(guardrail.name)
        if validator_class is None:
            return False, f"Validator '{guardrail.name}' not found. Make sure it's installed from Guardrails Hub."

        # Validate required configuration parameters
        is_valid, error_msg = validator_config.validate_config(
            guardrail.name,
            guardrail.config
        )

        return is_valid, error_msg

    def validate_text(
        self,
        text: str,
        guardrails: List[GuardrailConfig]
    ) -> Tuple[bool, List[FailedGuardrail]]:
        """
        Validate text against all specified guardrails.

        Args:
            text: Text to validate
            guardrails: List of guardrail configurations

        Returns:
            tuple: (all_passed, list_of_failed_guardrails)
        """
        failed_guardrails: List[FailedGuardrail] = []

        # Validate each guardrail individually to collect all failures
        for guardrail_config in guardrails:
            try:
                # Create a new Guard for each guardrail
                guard = Guard()

                # Load validator class
                validator_class = self._load_validator_class(guardrail_config.name)
                if validator_class is None:
                    failed_guardrails.append(
                        FailedGuardrail(
                            name=guardrail_config.name,
                            error=f"Validator '{guardrail_config.name}' not found"
                        )
                    )
                    continue

                # Initialize validator with config and OnFailAction.EXCEPTION
                try:
                    validator_instance = validator_class(
                        **guardrail_config.config,
                        on_fail=OnFailAction.EXCEPTION
                    )
                except TypeError as e:
                    # Handle case where on_fail is not a valid parameter
                    try:
                        validator_instance = validator_class(**guardrail_config.config)
                        # Manually set on_fail if the class supports it
                        if hasattr(validator_instance, 'on_fail'):
                            validator_instance.on_fail = OnFailAction.EXCEPTION
                    except Exception as init_error:
                        failed_guardrails.append(
                            FailedGuardrail(
                                name=guardrail_config.name,
                                error=f"Error initializing validator: {str(init_error)}"
                            )
                        )
                        continue

                # Add validator to guard
                guard.use(validator_instance)

                # Validate the text
                guard.validate(text)

            except ValidationError as e:
                # Validation failed - extract error message
                error_message = str(e)
                failed_guardrails.append(
                    FailedGuardrail(
                        name=guardrail_config.name,
                        error=error_message
                    )
                )
            except Exception as e:
                # Handle any other unexpected errors
                error_message = f"Unexpected error during validation: {str(e)}"
                failed_guardrails.append(
                    FailedGuardrail(
                        name=guardrail_config.name,
                        error=error_message
                    )
                )

        all_passed = len(failed_guardrails) == 0
        return all_passed, failed_guardrails

    def validate_all_configs(
        self,
        guardrails: List[GuardrailConfig]
    ) -> Tuple[bool, List[str]]:
        """
        Validate all guardrail configurations before running validation.

        Args:
            guardrails: List of guardrail configurations to validate

        Returns:
            tuple: (all_valid, list_of_error_messages)
        """
        errors = []

        for guardrail in guardrails:
            is_valid, error_msg = self.validate_guardrail_config(guardrail)
            if not is_valid:
                errors.append(f"{guardrail.name}: {error_msg}")

        return len(errors) == 0, errors


# Create a singleton instance
guardrail_validator = GuardrailValidator()

