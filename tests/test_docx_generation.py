import os
from pathlib import Path
import pytest
import yaml
from docx import Document
from src.odg.utils.file_handler import FileHandler
from src.odg.main import ConfigGenerator
from src.config.settings import Config

@pytest.fixture
def config_generator(tmp_path):
    # Create minimal config.yaml with required nested structures
    config_data = {
        "output_dir": str(tmp_path),
        "prefix": "Offer",
        "default_language": "en",
        "supported_languages": ["en", "de", "fr"],
        "customer": {
            "name": "Test Customer Inc.",
            "address": "123 Test St, Testville"
        },
        "sales": {
            "name": "John Doe",
            "email": "john.doe@example.com"
        },
        "offer": {
            "number": "OFF-001",
            "validity": {
                "en": "30 days from the date of issue"
            }
        },
        "variables": {
            "product_name": "Test Product",
            "currency": "EUR"
        }
    }
    config_file = tmp_path / "config.yaml"
    with open(config_file, 'w') as f:
        yaml.dump(config_data, f)
    
    # Create necessary directories
    (tmp_path / "templates").mkdir(parents=True, exist_ok=True)
    (tmp_path / "output").mkdir(parents=True, exist_ok=True)
    (tmp_path / "products").mkdir(parents=True, exist_ok=True)
    
    return ConfigGenerator(output_dir=tmp_path)

def test_generate_base_template_with_jinja_variables(config_generator, tmp_path):
    """Test base template generation with numbered lists"""
    product_name = "Web Application Security Assessment"
    language = "en"
    currency = "EUR"
    
    output_path = config_generator.create_sample_docx(product_name, language, currency)
    assert output_path.exists()
    
    # Get template and output paths
    templates_dir = tmp_path / "templates"
    docx_path = templates_dir / f"base_{language}.docx"
    sample_path = output_path
    
    # Verify template and sample files exist
    assert docx_path.exists()
    assert sample_path.exists()
    
    # Verify Jinja2 variables were replaced
    with open(sample_path, 'rb') as doc_file:
        doc = Document(doc_file)
        doc_text = '\n'.join([paragraph.text for paragraph in doc.paragraphs])
        assert '{{' not in doc_text, "Unrendered Jinja2 variables found in document"
    assert docx_path.is_relative_to(tmp_path)
    assert docx_path.parent == templates_dir
    assert docx_path.name == "base_en.docx"
    
    # Create and verify sample document
    sample_path = config_generator.create_sample_docx("base_en.docx")
    file_handler = FileHandler(Config())
    assert file_handler.has_numbered_lists(sample_path), "Document should contain nested numbered lists"
    
def test_generate_product_templates_with_numbered_lists(config_generator, tmp_path):
    """Test product template generation with numbered lists"""
    product_name = "Web Application Security Assessment"
    language = "en"
    currency = "EUR"
    
    output_path = config_generator.create_sample_docx(product_name, language, currency)
    assert output_path.exists()
    
    # Check for nested numbered lists
    document = Document(str(output_path))
    has_numbered_list = any(p.style.name == 'List Number' for p in document.paragraphs)
    has_nested_list = any(p.style.name == 'List Number 2' for p in document.paragraphs)
    assert has_numbered_list and has_nested_list
        
def test_validate_base_template(config_generator, tmp_path):
    """Verify base template structure and content"""
    product_name = "Web Application Security Assessment"
    language = "en"
    currency = "EUR"
    
    output_path = config_generator.create_sample_docx(product_name, language, currency)
    assert output_path.exists()
    
    file_handler = FileHandler(Config())
    assert file_handler.validate_doc_structure(output_path)
    assert file_handler.has_required_sections(output_path)

def test_merge_documents(config_generator, tmp_path):
    """Test merging multiple DOCX files with continuous numbering."""
    product_name = "Web Application Security Assessment"
    language = "en"
    currency = "EUR"
    
    # Create individual templates
    template1 = config_generator.create_docx_template("section1.docx")
    template2 = config_generator.create_docx_template("section2.docx")
    
    # Merge the documents
    merged_path = tmp_path / "merged.docx"
    config_generator.merge_docx_files([template1, template2], merged_path)
    
    file_handler = FileHandler(Config())
    assert file_handler.validate_merged_doc(merged_path), f"Merged document {merged_path} has invalid numbering"

def test_validate_product_template(config_generator, tmp_path):
    """Verify product template structure and content"""
    product_name = "Web Application Security Assessment"
    language = "en"
    currency = "EUR"
    
    output_path = config_generator.create_sample_docx(product_name, language, currency)
    assert output_path.exists()
    
    file_handler = FileHandler(Config())
    assert file_handler.validate_doc_structure(output_path), f"Invalid document structure: {output_path}"
    assert file_handler.has_required_sections(output_path), f"Missing required sections: {output_path}"
