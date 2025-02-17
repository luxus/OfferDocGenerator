import os
import sys
import logging
import re
from enum import StrEnum
from typing import Final
import pytest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class LogLevel(StrEnum):
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"

class LogEmoji(StrEnum):
    DEBUG = "🐛"
    INFO = "📢"
    WARNING = "⚠️"
    ERROR = "❌"
    CRITICAL = "🚨"

class EmojiFormatter(logging.Formatter):
    """Custom formatter to add emojis based on log level and message content."""
    EMOJI_MAP: Final[dict[LogLevel, str]] = {
        LogLevel.DEBUG: LogEmoji.DEBUG,
        LogLevel.INFO: LogEmoji.INFO,
        LogLevel.WARNING: LogEmoji.WARNING,
        LogLevel.ERROR: LogEmoji.ERROR,
        LogLevel.CRITICAL: LogEmoji.CRITICAL,
    }

    def format(self, record: logging.LogRecord) -> str:
        level = LogLevel(record.levelname)
        base_emoji = self.EMOJI_MAP[level]
        
        msg = record.getMessage()
        processed_msg = self._replace_keywords_with_emojis(msg)
        
        formatted_message = super().format(record)
        formatted_parts = formatted_message.split(' - ')
        
        match len(formatted_parts):
            case 0 | 1:
                return f"{base_emoji} {processed_msg}"
            case 2:
                return f"{formatted_parts[0]} - {base_emoji} {processed_msg}"
            case _:
                timestamp = formatted_parts[0]
                level_info = formatted_parts[1]
                return f"{timestamp} - {level_info} - {base_emoji} {processed_msg}"

    def _replace_keywords_with_emojis(self, msg: str) -> str:
        patterns = {
            r'created?(?:\s+file)?\s+([^\s]+)': r'📝: \1',
            r'generat(?:ed|ing)\s+([^\s]+)': r'⚙️: \1',
            r'delet(?:ed|ing)\s+([^\s]+)': r'🗑️: \1',
            r'error[:\s]\s*(.+)': r'❌: \1',
            r'warn(?:ing)?[:\s]\s*(.+)': r'⚠️: \1',
            r'success[:\s]\s*(.+)': r'✅: \1',
        }
        
        processed = msg
        for pattern, replacement in patterns.items():
            processed = re.sub(pattern, replacement, processed, flags=re.IGNORECASE)
        
        return processed

def pytest_configure(config: pytest.Config) -> None:
    """Configure test environment and logging"""
    root_logger = logging.getLogger()
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    formatter = EmojiFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    root_logger.setLevel(logging.DEBUG)
    
    os.environ["TESTING"] = "True"
    if "TEST_OUTPUT_DIR" in os.environ:
        del os.environ["TEST_OUTPUT_DIR"]
    
    config.addinivalue_line(
        "markers",
        "integration: mark test as integration test"
    )
    
@pytest.fixture(autouse=True)
def setup_testing_env(tmp_path):
    """Set up and clean test environment."""
    os.environ["TESTING"] = "True"
    
    # Store original TEST_OUTPUT_DIR if it exists
    original_test_output_dir = os.environ.get("TEST_OUTPUT_DIR")
    
    yield
    
    # Always clean up the test output directory
    test_output_dir = Path(os.getenv("TEST_OUTPUT_DIR", ""))
    if test_output_dir.exists() and test_output_dir.is_relative_to(tmp_path):
        for item in test_output_dir.iterdir():
            if item.is_dir():
                shutil.rmtree(item, ignore_errors=True)
            else:
                item.unlink(missing_ok=True)
    
    # Restore original TEST_OUTPUT_DIR if it existed
    if original_test_output_dir:
        os.environ["TEST_OUTPUT_DIR"] = original_test_output_dir
    elif "TEST_OUTPUT_DIR" in os.environ:
        del os.environ["TEST_OUTPUT_DIR"]
    
    os.environ["TESTING"] = "False"
