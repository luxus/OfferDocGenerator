from typing import TypedDict, NotRequired, Required
from dataclasses import dataclass
import json
import logging

class LogMetadata(TypedDict):
    user_id: Required[str]
    session_id: Required[str]
    operation: Required[str]
    details: NotRequired[dict[str, str]]

@dataclass(frozen=True, slots=True)
class LogEntry:
    message: str
    metadata: LogMetadata
    level: int
    timestamp: float

class StructuredLogger:
    def __init__(self, name: str) -> None:
        self.logger = logging.getLogger(name)
        self._setup_structured_logging()

    def _setup_structured_logging(self) -> None:
        formatter = logging.Formatter(
            lambda record: json.dumps(
                LogEntry(
                    message=record.msg,
                    metadata=record.metadata,
                    level=record.levelno,
                    timestamp=record.created
                ).__dict__
            )
        )
        handler = logging.StreamHandler()
        handler.setFormatter(formatter)
        self.logger.addHandler(handler)

    def log_operation(
        self,
        message: str,
        metadata: LogMetadata,
        level: int = logging.INFO
    ) -> None:
        """Log with structured metadata."""
        extra = {'metadata': metadata}
        self.logger.log(level, message, extra=extra)
