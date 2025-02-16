import os
from pathlib import Path
import pytest
from docx import Document
from src.odg.utils.file_handler import FileHandler
from src.odg.main import ConfigGenerator
from src.config.settings import Config

def test_generate_base_template_with_jinja_variables(tmp_path):
    """Test base template generation with numbered lists"""
    output_dir = tmp_path / "base_templates"
    
    config_generator = ConfigGenerator(output_dir=str(output_dir))
    # Generate the config.yaml file
    config_path = config_generator.generate_config()
    assert config_path.exists(), f"Config file not generated at {config_path}"
    
    docx_path = config_generator.create_docx_template("base_en.docx")
    
    # Create sample document with variables
    sample_path = config_generator.create_sample_docx("base_en.docx")
    
    # Verify template and sample files exist
    assert docx_path.exists()
    assert sample_path.exists()
    
    # Verify Jinja2 variables were replaced
    with open(sample_path, 'rb') as doc_file:
        doc = Document(doc_file)
        doc_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        assert '{{' not in doc_text, "Unrendered Jinja2 variables found in document"
    assert docx_path.is_relative_to(tmp_path)
    assert docx_path.parent == output_dir / "templates"
    assert docx_path.name == "base_en.docx"
    
    # Create and verify sample document
    sample_path = config_generator.create_sample_docx("base_en.docx")
    file_handler = FileHandler(Config())
    assert file_handler.has_numbered_lists(sample_path), "Document should contain nested numbered lists"
    
def test_generate_product_templates_with_numbered_lists(tmp_path):
    """Test product template generation with numbered lists"""
    output_dir = tmp_path / "product_templates"
    
    # Generate sample product config with .docx extension
    products_config = {
        "products": [
            {"name": "Product1.docx", "sections": ["Section A", "Section B"]},
            {"name": "Product2.docx", "sections": ["Section C", "Section D"]}
        ]
    }

    # Verify tmp_path is set
    assert tmp_path.exists(), "Temporary test directory not created"
    
    # Generate DOCX templates for each product
    config_generator = ConfigGenerator(output_dir=str(output_dir))
    # Generate the config.yaml file
    config_path = config_generator.generate_config()
    assert config_path.exists(), f"Config file not generated at {config_path}"
    
    file_handler = FileHandler(Config())
    
    for product in products_config["products"]:
        try:
            docx_path = config_generator.create_sample_docx(template_name=product['name'])
            assert docx_path is not None, f"Failed to create sample for {product['name']}"
            assert docx_path.exists(), f"Sample file does not exist: {docx_path}"
            
            # Adjust the expected path based on the actual output directory
            expected_filename = product['name'].replace('.docx', '')
            expected_path = output_dir / "generated" / f"sample_{expected_filename}.docx"
            assert expected_path.exists(), f"Expected file not found at: {expected_path}"
            assert expected_path.is_relative_to(tmp_path), f"Generated file {expected_path} not within {tmp_path}"
            assert file_handler.has_numbered_lists(docx_path), f"Missing numbered lists in {docx_path}"
        except Exception as e:
            pytest.fail(f"Failed to process {product['name']}: {str(e)}")
        
def test_validate_base_template(tmp_path):
    """Verify base template structure and content"""
    # Set TESTING environment variable for cleanup checks
    os.environ["TESTING"] = "True"
    
    output_dir = tmp_path / "base_templates"
    output_dir.mkdir()
    
    # Generate base template
    config_generator = ConfigGenerator(output_dir=str(output_dir))
    docx_path = config_generator.create_docx_template("base_en.docx")
    
    file_handler = FileHandler(Config())
    assert file_handler.validate_doc_structure(docx_path)
    assert file_handler.has_required_sections(docx_path)

def test_merge_documents(tmp_path):
    """Test merging multiple DOCX files with continuous numbering."""
    output_dir = tmp_path / "merge_test"
    config_generator = ConfigGenerator(output_dir=str(output_dir))
    
    # Create individual templates
    template1 = config_generator.create_docx_template("section1.docx")
    template2 = config_generator.create_docx_template("section2.docx")
    
    # Merge the documents
    merged_path = output_dir / "merged.docx"
    config_generator.merge_docx_files([template1, template2], merged_path)
    
    file_handler = FileHandler(Config())
    assert file_handler.validate_merged_doc(merged_path), f"Merged document {merged_path} has invalid numbering"

def test_validate_product_template(tmp_path):
    """Verify product template structure and content"""
    # Set TESTING environment variable for cleanup checks
    os.environ["TESTING"] = "True"
    
    output_dir = tmp_path / "product_templates"
    output_dir.mkdir()
    
    # Generate sample product config
    products_config = {
        "products": [
            {"name": "Product Test", "sections": ["Introduction", "Product Overview", "Technical Specifications"]}
        ]
    }
    
    # Generate DOCX template for test product
    config_generator = ConfigGenerator(output_dir=str(output_dir))
    # Generate the config.yaml file
    config_path = config_generator.generate_config()
    assert config_path.exists(), f"Config file not generated at {config_path}"
    
    file_handler = FileHandler(Config())
    
    try:
        docx_path = config_generator.create_sample_docx(template_name=products_config["products"][0]["name"])
        assert docx_path is not None, "Failed to create sample document"
        assert docx_path.exists(), f"Sample file does not exist: {docx_path}"
        assert file_handler.validate_doc_structure(docx_path), f"Invalid document structure: {docx_path}"
        assert file_handler.has_required_sections(docx_path, is_product=True), f"Missing required sections: {docx_path}"
    except Exception as e:
        pytest.fail(f"Failed to validate product template: {str(e)}")
