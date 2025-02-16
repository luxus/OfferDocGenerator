import sys
import os
import logging
import pytest
from pathlib import Path

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

class EmojiFormatter(logging.Formatter):
    """Custom formatter to add emojis based on log level."""
    def format(self, record):
        # Add specific emojis for different log levels
        emoji = {
            logging.DEBUG: "🐛",
            logging.INFO: "📢",
            logging.WARNING: "⚠️",
            logging.ERROR: "❌",
            logging.CRITICAL: "🚨",
        }.get(record.levelno, "")
        
        # Optionally add more dynamic emojis based on message content
        msg = record.getMessage()
        if 'folder' in msg:
            emoji += "📁"
        elif 'delete' in msg:
            emoji += "🗑️"
        
        # Format the original message with the emoji
        formatted_message = super().format(record)
        return f"{formatted_message} {emoji}"

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
    
    # Add colors to log levels using the pytest logging plugin
    logging_plugin = config.pluginmanager.get_plugin("logging-plugin")
    if logging_plugin:
        cli_handler = logging_plugin.log_cli_handler
        formatter = cli_handler.formatter
        
        # Define colors for each level
        formatter.add_color_level(logging.DEBUG, "green")
        formatter.add_color_level(logging.INFO, "cyan")
        formatter.add_color_level(logging.WARNING, "yellow")
        formatter.add_color_level(logging.ERROR, "red")
        formatter.add_color_level(logging.CRITICAL, "magenta")
        
        # Add color to custom log level SPAM
        logging.SPAM = 5  # Define the SPAM level if not already defined
        logging.addLevelName(logging.SPAM, "SPAM")
        formatter.add_color_level(logging.SPAM, "blue")
    
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
