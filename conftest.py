import sys
import os
import logging
import pytest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class EmojiFormatter(logging.Formatter):
    """Custom formatter to add emojis based on log level and message content."""
    def format(self, record):
        # Base emoji from log level
        base_emoji = {
            logging.DEBUG: "🐛",
            logging.INFO: "📢",
            logging.WARNING: "⚠️",
            logging.ERROR: "❌",
            logging.CRITICAL: "🚨",
        }.get(record.levelno, "")
        
        # Additional emojis based on message content using regex patterns
        import re
        msg = record.getMessage()
        additional_emoji = ""
        
        if re.search(r'Creating directory|Creating output directory', msg):
            additional_emoji += "📁"
        elif 'Deleting file' in msg:
            additional_emoji += "🗑️"
        
        full_emoji = base_emoji + additional_emoji
        formatted_message = super().format(record)
        return f"{formatted_message} {full_emoji}" if full_emoji else formatted_message

def pytest_configure(config):
    """Configure test environment and logging"""
    # Configure logging for tests to avoid duplication
    root_logger = logging.getLogger()
    
    # Remove existing handlers to prevent duplicates
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set up a single handler for all test logging
    formatter = EmojiFormatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    root_logger.addHandler(stream_handler)
    root_logger.setLevel(logging.DEBUG)
    
    # Mark that we're in testing mode
    os.environ["TESTING"] = "True"
    
    config.addinivalue_line(
        "markers",
        "end_to_end: mark tests as end-to-end integration tests"
    )
    
@pytest.fixture(autouse=True)
def setup_testing_env():
    """Set up and clean test environment."""
    os.environ["TESTING"] = "True"
    temp_dir = Path("tests") / "tmp"
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    yield
    
    # Cleanup if KEEP_TMP is not set
    keep_tmp = os.getenv("KEEP_TMP", "False").lower() == "true"
    if not keep_tmp and temp_dir.exists():
        import shutil
        for file in temp_dir.glob('*'):
            try:
                if file.is_file():
                    file.unlink()
                else:
                    shutil.rmtree(file)
            except Exception as e:
                print(f"Error cleaning up {file}: {e}")
    
    os.environ["TESTING"] = "False"
    os.environ["KEEP_TMP"] = "False"
