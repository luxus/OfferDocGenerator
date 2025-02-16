import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

def pytest_configure(config):
    config.addinivalue_line(
        "markers",
        "end_to_end: mark tests as end-to-end integration tests"
    )
    
def pytest_sessionstart(session):
    """Set up test environment variables."""
    os.environ["TESTING"] = "True"
    os.environ["KEEP_TMP"] = "False"
