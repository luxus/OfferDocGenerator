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
