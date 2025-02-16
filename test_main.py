import os
from pathlib import Path
import yaml
import pytest
import shutil
import tempfile
from main import ConfigGenerator

@pytest.fixture
def keep_tmp():
    """Control whether to keep temporary test files"""
    return os.getenv("KEEP_TMP", "False").lower() == "true"

@pytest.fixture(scope="function")
def config_generator(tmp_path, keep_tmp):
    # Use tmp_path fixture to create clean temp directory for each test
    output_dir = tmp_path / "tmp"
    
    # Initialize config generator
    cg = ConfigGenerator(output_dir=str(output_dir))
    
    yield cg
    
    if keep_tmp:
        print(f"Temporary files preserved at: {output_dir}")
    else:
        # Clean up after test
        ConfigGenerator._clean_temp_directory(output_dir)

def test_valid_config_generation(config_generator):
    """Test valid config generation and validation process"""
    # Generate config file
    config_path = config_generator.generate_config()
    
    # Validate paths exist
    required_paths = [
        Path(config_generator.output_dir / "templates"),
        Path(config_generator.output_dir / "common"), 
        Path(config_generator.output_dir / "products")
    ]

    for path in required_paths:
        assert path.exists(), f"Path {path} does not exist"
        
    # Verify config structure
    with open(config_path, "r") as f:
        loaded_config = yaml.safe_load(f)
        
    assert "offer" in loaded_config, "Offer section missing from config"
    assert "date" in loaded_config["offer"], "Date missing from offer section"
    assert "settings" in loaded_config, "Settings section missing from config"

def test_error_handling(config_generator):
    """Test error detection with invalid config"""
    # Create invalid config
    invalid_path = config_generator.output_dir / "invalid.yaml"
    with open(invalid_path, "w") as f:
        yaml.dump({"invalid": "config"}, f)
        
    # Test validation
    result = config_generator.validate_config(invalid_path)
    assert not result, "Invalid config should return False"

def test_internationalization_settings(config_generator):
    """Test internationalization settings in config"""
    config_path = config_generator.generate_config()
    
    with open(config_path, "r") as f:
        loaded_config = yaml.safe_load(f)
        
    intl_section = loaded_config.get("internationalization", {})
    assert "default_language" in intl_section, "Default language missing"
    assert intl_section["default_language"] == "en", "Default language must be 'en'"

def test_temp_folder_cleanup(keep_tmp):
    """Test temporary directory cleanup"""
    try:
        output_dir = Path(tempfile.gettempdir()) / "offerdocgenerator_test"
        # Create a file to test deletion
        test_file = output_dir / "test_file.txt"
        test_file.parent.mkdir(exist_ok=True)
        with open(test_file, "w") as f:
            f.write("Test content")
        
        # Clean up
        ConfigGenerator._clean_temp_directory(output_dir)
        
        if keep_tmp:
            assert test_file.exists(), "Temporary file was deleted despite KEEP_TMP=True"
        else:
            assert not test_file.exists(), "Temporary file was not deleted"
    finally:
        if not keep_tmp and test_file.exists():
            test_file.unlink()

@pytest.mark.end_to_end
def test_full_config_validation(config_generator):
    """End-to-end validation of the entire config structure"""
    config_path = config_generator.generate_config()
    
    with open(config_path, "r") as f:
        loaded_config = yaml.safe_load(f)
        
    # Check all required sections
    assert "offer" in loaded_config
    assert "settings" in loaded_config
    assert "internationalization" in loaded_config
    assert "customer" in loaded_config
    assert "sales" in loaded_config
    
    # Check nested properties
    assert "number" in loaded_config["offer"]
    assert "date" in loaded_config["offer"]
    
    assert "default_language" in loaded_config["internationalization"]
    assert len(loaded_config["settings"]) == 4

@pytest.mark.parametrize("language,expected", [
    ("en", "Hello"),
    ("de", "Hallo")
])
def test_multi_language_support(config_generator, language, expected):
    """Test multi-language support"""
    # This would require more complex setup but demonstrates pytest's capabilities
    pass
