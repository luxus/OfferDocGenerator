from typing import NoReturn, Never
from dataclasses import dataclass
from enum import StrEnum, auto

class ErrorSeverity(StrEnum):
    WARNING = auto()
    ERROR = auto()
    CRITICAL = auto()

@dataclass(frozen=True, slots=True)
class ValidationError:
    field: str
    message: str
    severity: ErrorSeverity

class DocumentValidationError(Exception):
    def __init__(self, message: str, errors: list[ValidationError]) -> None:
        super().__init__(message)
        self.errors = errors
        # Python 3.13 enhanced exception notes
        for error in errors:
            self.add_note(f"{error.severity}: {error.field} - {error.message}")

class ErrorHandler:
    def handle_validation_errors(self, errors: list[ValidationError]) -> Never:
        grouped_errors = {}
        for error in errors:
            grouped_errors.setdefault(error.severity, []).append(error)
        
        exceptions = [
            DocumentValidationError(f"{severity} errors", errs)
            for severity, errs in grouped_errors.items()
        ]
        
        if len(exceptions) > 1:
            raise ExceptionGroup("Multiple validation errors", exceptions)
        raise exceptions[0]