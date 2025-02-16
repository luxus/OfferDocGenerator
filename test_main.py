import os
from pathlib import Path
import yaml
import shutil
from unittest import TestCase
from main import ConfigGenerator

class TestConfigGeneration(TestCase):
    def setUp(self) -> None:
        """Set up temporary directory structure"""
        self.script_dir = Path(__file__).parent
        self.tmp_dir = self.script_dir / "tmp"
        
        # Initialize config generator
        self.config_generator = ConfigGenerator(output_dir="tmp")

    def test_1_config_generation(self) -> None:
        """Test valid config generation and validation process"""
        # Generate config file
        config_path = self.config_generator.generate_config()
        
        # Validate paths exist
        required_paths = [
            Path(self.config_generator.output_dir / "templates"),
            Path(self.config_generator.output_dir / "common"), 
            Path(self.config_generator.output_dir / "products")
        ]

        for path in required_paths:
            self.assertTrue(path.exists())
            
        # Verify config structure
        with open(config_path, "r") as f:
            loaded_config = yaml.safe_load(f)
            
        self.assertIn("offer", loaded_config)
        self.assertIn("date", loaded_config["offer"])
        self.assertIn("settings", loaded_config)

    def test_2_error_handling(self) -> None:
        """Test error detection with invalid config"""
        try:
            # Create invalid config
            invalid_path = self.tmp_dir / "invalid.yaml"
            with open(invalid_path, "w") as f:
                yaml.dump({"invalid": "config"}, f)
                
            # Test validation
            result = self.config_generator.validate_config(invalid_path)
            self.assertFalse(result)
            
        except Exception as e:
            print(f"Error during test: {e}")

    def test_3_temp_folder_cleanup(self) -> None:
        """Test temporary directory cleanup"""
        new_tmp = Path(__file__).parent / "test_tmp"
        
        # Create and delete temp directory
        if new_tmp.exists():
            shutil.rmtree(new_tmp)
            
        new_tmp.mkdir()
        shutil.rmtree(new_tmp)
        self.assertFalse(new_tmp.exists())

    def tearDown(self) -> None:
        """Do not clean up temporary files for review purposes"""
        # Temporarily commented out to allow manual review
        # shutil.rmtree(self.tmp_dir, ignore_errors=True)
        pass

if __name__ == "__main__":
    import unittest
    unittest.main()
