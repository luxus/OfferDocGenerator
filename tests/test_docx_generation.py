import os
from pathlib import Path
import pytest
from docx import Document
from src.odg.utils.file_handler import FileHandler
from src.odg.main import ConfigGenerator

@pytest.fixture
def config_generator(tmp_path):
    return ConfigGenerator(output_dir=tmp_path)

def test_generate_base_template_with_jinja_variables(config_generator, tmp_path):
    """Test base template generation with numbered lists"""
    product_name = "Web Application Security Assessment"
    language = "en"
    currency = "EUR"
    
    output_path = config_generator.create_sample_docx(product_name, language, currency)
    assert output_path.exists()
    
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
