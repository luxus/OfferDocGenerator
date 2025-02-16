import os
import sys
from pathlib import Path
import yaml
import pytest
import shutil
import tempfile
import tempfile

# Add src directory to Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))
from odg.main import ConfigGenerator

@pytest.fixture
def cli_test_directory():
    # Create a temporary directory for CLI tests using pytest's tmp_path
    with tempfile.TemporaryDirectory() as tmpdir:
        temp_dir = Path(tmpdir)
        yield temp_dir

@pytest.fixture(scope="function")
def config_generator():
    """Fixture providing a ConfigGenerator instance with a temporary directory"""
    with tempfile.TemporaryDirectory() as tmpdir:
        os.environ["TESTING"] = "True"
        tmpdir_path = Path(tmpdir).resolve()
        print(f"Creating test ConfigGenerator with tmpdir: {tmpdir_path}")
        cg = ConfigGenerator(output_dir=str(tmpdir_path))
        yield cg
        # Cleanup happens automatically when context exits
        if Path(tmpdir).exists():
            shutil.rmtree(tmpdir, ignore_errors=True)
        os.environ["TESTING"] = "False"

def test_valid_config_generation(config_generator):
    """Test valid config generation and validation process"""
    # Generate config file
    config_path = config_generator.generate_config()
    
    # Validate paths exist
    required_paths = [
        Path(config_generator.output_dir / "templates"),
        Path(config_generator.output_dir / "common"),
        Path(config_generator.output_dir / "products"),
        Path(config_generator.output_dir / "output")
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
    
    # Verify required settings exist
    settings = loaded_config["settings"]
    # Verify base structure
    assert "base_path" in settings, "Missing base_path in settings"
    
    # Verify folders dictionary contains expected paths
    assert "folders" in settings, "Missing folders configuration"
    folders = settings["folders"]
    required_folders = ["templates", "common", "products", "output"]
    for folder in required_folders:
        assert folder in folders, f"Missing {folder} in folders configuration"
    assert "output_prefix" in settings, "Missing output_prefix in settings"

@pytest.mark.parametrize("language,expected", [
    ("en", "Hello"),
    ("de", "Hallo")
])
def test_multi_language_support(config_generator, language, expected):
    """Test multi-language support"""
    # This would require more complex setup but demonstrates pytest's capabilities
    pass

def test_cli_create_folder_structure(cli_test_directory):
    output_dir = cli_test_directory / "offers"
    
    # Run CLI command to create structure
    config_gen = ConfigGenerator(output_dir=str(output_dir))
    config_path = config_gen.generate_config()
    assert config_path.exists(), f"Config file not created at: {config_path}"
    
    # Check required directories exist
    required_dirs = [
        output_dir,
        output_dir / "templates",
        output_dir / "common",
        output_dir / "products",
        output_dir / "output"
    ]
    
    for dir_ in required_dirs:
        assert dir_.exists(), f"Directory {dir_} does not exist"

def test_cli_config_contents(cli_test_directory):
    # Create a new project structure
    output_dir = cli_test_directory / "test_project"
    
    # Generate config and update base_path as per CLI functionality
    config_gen = ConfigGenerator(output_dir=str(output_dir))
    config_path = config_gen.generate_config()
    
    with open(config_path, 'r') as f:
        loaded_config = yaml.safe_load(f)
        
    # Verify that base_path is set correctly
    assert "base_path" in loaded_config["settings"], "Missing base_path"
    expected_base_path = str(output_dir.resolve())
    assert loaded_config["settings"]["base_path"] == expected_base_path, f"Base path not set to: {expected_base_path}"

def test_cli_output(cli_test_directory):
    # Test CLI output and validation
    config_gen = ConfigGenerator(output_dir=cli_test_directory / "test_project")
    config_path = config_gen.generate_config()
    
    # Ensure that the validation occurs
    assert config_gen.validate_config(config_path), "Config validation failed during CLI test"
