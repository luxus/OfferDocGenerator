import sys
import os
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def pytest_configure(config):
    # Configure logging for tests
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    config.addinivalue_line(
        "markers",
        "end_to_end: mark tests as end-to-end integration tests"
    )
    
def pytest_sessionstart(session):
    """Set up test environment variables."""
    os.environ["TESTING"] = "True"
    os.environ["KEEP_TMP"] = "False"

def pytest_sessionfinish(session, exitstatus):
    """Clean up after all tests complete."""
    # Reset environment variables
    os.environ["TESTING"] = "False"
    os.environ["KEEP_TMP"] = "False"
