import pytest
from src.odg.utils.file_handler import FileHandler
from src.odg.main import ConfigGenerator
from src.config.settings import Config

def test_generate_base_template_with_numbered_lists(tmp_path):
    """Test base template generation with numbered lists"""
    output_dir = tmp_path / "base_templates"
    output_dir.mkdir()
    
    # Generate base template
    config_generator = ConfigGenerator(output_dir=str(output_dir))
    docx_path = config_generator.create_docx_template("base_en.docx")
    
    assert docx_path.exists()
    file_handler = FileHandler(Config())
    assert file_handler.has_numbered_lists(docx_path)
    
def test_generate_product_templates_with_numbered_lists(tmp_path):
    """Test product template generation with numbered lists"""
    output_dir = tmp_path / "product_templates"
    output_dir.mkdir()
    
    # Generate sample product config
    products_config = {
        "products": [
            {"name": "Product 1", "sections": ["Section A", "Section B"]},
            {"name": "Product 2", "sections": ["Section C", "Section D"]}
        ]
    }
    
    # Generate DOCX templates for each product
    config_generator = ConfigGenerator(output_dir=str(output_dir))
    file_handler = FileHandler(Config())
    
    for product in products_config["products"]:
        try:
            docx_path = config_generator.create_sample_docx(template_name=product["name"])
            assert docx_path is not None, f"Failed to create sample for {product['name']}"
            assert docx_path.exists(), f"Sample file does not exist: {docx_path}"
            assert file_handler.has_numbered_lists(docx_path), f"Missing numbered lists in {docx_path}"
        except Exception as e:
            pytest.fail(f"Failed to process {product['name']}: {str(e)}")
        
def test_validate_base_template(tmp_path):
    """Verify base template structure and content"""
    output_dir = tmp_path / "base_templates"
    output_dir.mkdir()
    
    # Generate base template
    config_generator = ConfigGenerator(output_dir=str(output_dir))
    docx_path = config_generator.create_docx_template("base_en.docx")
    
    file_handler = FileHandler(Config())
    assert file_handler.validate_doc_structure(docx_path)
    assert file_handler.has_required_sections(docx_path)

def test_validate_product_template(tmp_path):
    """Verify product template structure and content"""
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
    file_handler = FileHandler(Config())
    
    try:
        docx_path = config_generator.create_sample_docx(template_name=products_config["products"][0]["name"])
        assert docx_path is not None, "Failed to create sample document"
        assert docx_path.exists(), f"Sample file does not exist: {docx_path}"
        assert file_handler.validate_doc_structure(docx_path), f"Invalid document structure: {docx_path}"
        assert file_handler.has_required_sections(docx_path, is_product=True), f"Missing required sections: {docx_path}"
    except Exception as e:
        pytest.fail(f"Failed to validate product template: {str(e)}")
