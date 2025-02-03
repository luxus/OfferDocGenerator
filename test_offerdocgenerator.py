import sys
import os
import unittest
import shutil
import random
import zipfile
from pathlib import Path
from pathlib import Path
import yaml
import docx
from unittest import mock
from docxtpl import DocxTemplate, RichText
import offerdocgenerator

class TestOfferDocGenerator(unittest.TestCase):
    CLEANUP = False  # Set to False to keep generated files
    
    def test_directory_creation(self):
        """Verify test directory structure is created"""
        self.assertTrue(self.templates_dir.exists())
        self.assertTrue(self.textblocks_dir.exists())
        self.assertTrue((self.textblocks_dir / "common").exists())
        self.assertTrue((self.textblocks_dir / "products" / self.product_name).exists())

    CLEANUP = False  # Set to False to keep generated files
    TEST_DIR_NAME = "test_data"  # Fixed directory name
    
    def setUp(self):
        """Set up test fixtures in shared directory"""
        # Base test directory
        self.script_dir = Path(__file__).parent
        self.test_root = self.script_dir / "test_output" 
        self.test_run_dir = self.test_root / self.TEST_DIR_NAME
        
        # Clean existing test data if cleanup enabled
        if self.CLEANUP and self.test_run_dir.exists():
            shutil.rmtree(self.test_run_dir)
            
        # Create fresh directory structure
        self.test_run_dir.mkdir(parents=True, exist_ok=True)
        
        # Now create subdirectories
        self.config_file = self.test_run_dir / "test_config.yaml"
        self.templates_dir = self.test_run_dir / "templates"
        self.output_dir = self.test_run_dir / "output"
        self.textblocks_dir = self.test_run_dir / "textblocks"
        self.product_name = "Web Application Security Assessment"

        # Create required subdirectories
        self.templates_dir.mkdir(exist_ok=True)
        self.output_dir.mkdir(exist_ok=True)
        (self.textblocks_dir / "common").mkdir(parents=True, exist_ok=True)
        (self.textblocks_dir / "products" / self.product_name).mkdir(parents=True, exist_ok=True)

        # Create common textblocks
        self._create_textblock_file(
            self.textblocks_dir / "common" / "section_1_1_EN.docx",
            "Our standard security assessment provides a comprehensive evaluation of your web application's security posture."
        )
        self._create_textblock_file(
            self.textblocks_dir / "common" / "section_1_1_DE.docx",
            "Unsere Standard-Sicherheitsbewertung bietet eine umfassende Evaluation der Sicherheitslage Ihrer Webanwendung."
        )

        # Create product-specific textblocks for first product
        self._create_textblock_file(
            self.textblocks_dir / "products" / self.product_name / "section_1_1_1_EN.docx",
            """The Web Application Security Assessment includes:

- Vulnerability scanning
- Manual penetration testing
- Code review"""
        )
        self._create_textblock_file(
            self.textblocks_dir / "products" / self.product_name / "section_1_1_1_DE.docx",
            """Die Web Application Security Assessment beinhaltet:

- Schwachstellenscanning
- Manuelle Penetrationstests
- Code-Review"""
        )

        # Create second product and its textblocks
        self.product_name2 = "Network Security Audit"
        (self.textblocks_dir / "products" / self.product_name2).mkdir(parents=True, exist_ok=True)
        self._create_textblock_file(
            self.textblocks_dir / "products" / self.product_name2 / "section_1_1_1_EN.docx",
            """The Network Security Audit includes:

- Firewall configuration review
- Intrusion detection system testing
- Security policy evaluation"""
        )
        self._create_textblock_file(
            self.textblocks_dir / "products" / self.product_name2 / "section_1_1_1_DE.docx",
            """Die Netzwerksicherheitsprüfung umfasst:

- Überprüfung der Firewall-Konfiguration
- Test des Intrusion Detection Systems
- Bewertung der Sicherheitsrichtlinien"""
        )

        # Create base templates for EN and DE
        # English template
        self.template_file_en = self.templates_dir / "base_EN.docx"
        doc = docx.Document()
        doc.add_heading('Offer: {{ Config.offer.number }}', 0)
        doc.add_paragraph('Date: {{ Config.offer.date }}')
        doc.add_paragraph('Valid for: {{ Config.offer.validity[LANGUAGE] }}')
        doc.add_heading('Customer Information', 1)
        doc.add_paragraph('{{ Config.customer.name }}')
        doc.add_paragraph('{{ Config.customer.address }}')
        doc.add_paragraph('{{ Config.customer.city }}, {{ Config.customer.zip }}')
        doc.add_paragraph('{{ Config.customer.country }}')
        doc.add_heading('Product Description', 1)
        p = doc.add_paragraph()
        p.add_run('{{r section_1_1 }}')
        doc.add_heading('Detailed Scope', 2)
        p = doc.add_paragraph()
        p.add_run('{{r section_1_1_1 }}')
        doc.add_paragraph('Total Price: {{ CURRENCY }} 10,000')
        doc.add_heading('Sales Contact', 1)
        doc.add_paragraph('{{ Config.sales.name }}')
        doc.add_paragraph('{{ Config.sales.email }}')
        doc.add_paragraph('{{ Config.sales.phone }}')
        doc.save(str(self.template_file_en))

        # German template
        self.template_file_de = self.templates_dir / "base_DE.docx"
        doc = docx.Document()
        doc.add_heading('Angebot: {{ Config.offer.number }}', 0)
        doc.add_paragraph('Datum: {{ Config.offer.date }}')
        doc.add_paragraph('Gültig für: {{ Config.offer.validity[LANGUAGE] }}')
        doc.add_heading('Kundeninformationen', 1)
        doc.add_paragraph('{{ Config.customer.name }}')
        doc.add_paragraph('{{ Config.customer.address }}')
        doc.add_paragraph('{{ Config.customer.city }}, {{ Config.customer.zip }}')
        doc.add_paragraph('{{ Config.customer.country }}')
        doc.add_heading('Produktbeschreibung', 1)
        p = doc.add_paragraph()
        p.add_run('{{r section_1_1 }}')
        doc.add_heading('Detaillierter Umfang', 2)
        p = doc.add_paragraph()
        p.add_run('{{r section_1_1_1 }}')
        doc.add_paragraph('Gesamtpreis: {{ CURRENCY }} 10.000')
        doc.add_heading('Vertriebskontakt', 1)
        doc.add_paragraph('{{ Config.sales.name }}')
        doc.add_paragraph('{{ Config.sales.email }}')
        doc.add_paragraph('{{ Config.sales.phone }}')
        doc.save(str(self.template_file_de))

        # Create config file
        config = {
            "offer": {
                "template": str(self.templates_dir),
                "number": "2025-001",
                "date": "2025-02-02",
                "validity": {
                    "EN": "30 days",
                    "DE": "30 Tage"
                }
            },
            "textblocks": {
                "common": {
                    "folder": str(self.textblocks_dir / "common")
                },
                "products_dir": str(self.textblocks_dir / "products")
            },
            "output": {
                "folder": str(self.output_dir),
                "format": "docx",  # Force tests to use DOCX
                "prefix": "TestOffer_"
            },
            "customer": {
                "name": "Example Corp",
                "address": "123 Example Street",
                "city": "Example City",
                "zip": "12345",
                "country": "Example Country"
            },
            "sales": {
                "name": "John Doe",
                "email": "john.doe@example.com",
                "phone": "+1 234 567 890"
            }
        }
        with open(self.config_file, 'w') as f:
            yaml.dump(config, f)

    def _create_textblock_file(self, file_path: Path, content: str):
        """Helper method to create a docx file with given content."""
        doc = docx.Document()
        # Add each paragraph with proper styling
        for paragraph in content.split('\n\n'):
            if paragraph.strip():
                p = doc.add_paragraph()
                # If it's a bullet point, use a list style
                if paragraph.strip().startswith('-'):
                    p.style = 'List Bullet'
                    p.text = paragraph.strip()[2:]  # Remove the '- ' prefix
                else:
                    p.text = paragraph.strip()
        doc.save(str(file_path))

    def tearDown(self):
        """Conditional cleanup of test output directory"""
        if self.CLEANUP:
            shutil.rmtree(self.test_run_dir)
        else:
            print(f"\nTest files preserved in: {self.test_run_dir}")

    def test_get_product_names(self):
        """Test that product names are correctly detected from the directory structure."""
        products = offerdocgenerator.get_product_names(self.textblocks_dir)
        self.assertEqual(len(products), 2)
        self.assertIn(self.product_name, products)
        self.assertIn(self.product_name2, products)

    def test_load_config(self):
        """Test that the YAML configuration is loaded correctly."""
        config = offerdocgenerator.load_config(self.config_file)
        self.assertIsInstance(config, offerdocgenerator.Config)
        self.assertEqual(config.offer["sections"], ["1_1", "1_1_1"])
        self.assertIn("common", config.textblocks)
        self.assertEqual(config.textblocks["common"]["folder"], str(self.textblocks_dir / "common"))

    def test_load_textblocks(self):
        """Test dynamic loading of textblocks from product directory"""
        config = offerdocgenerator.load_config(self.config_file)
        
        # Test German textblocks
        textblocks_de = offerdocgenerator.load_textblocks(config, self.product_name, "DE")
        self.assertGreaterEqual(len(textblocks_de), 2)
        self.assertIn("section_1_1", textblocks_de)
        self.assertIn("section_1_1_1", textblocks_de)
        self.assertIn("Sicherheitsbewertung", str(textblocks_de["section_1_1"]))
        self.assertIn("Schwachstellenscanning", str(textblocks_de["section_1_1_1"]))
        
        # Test English textblocks 
        textblocks_en = offerdocgenerator.load_textblocks(config, self.product_name, "EN")
        self.assertGreaterEqual(len(textblocks_en), 2)
        self.assertIn("section_1_1", textblocks_en)
        self.assertIn("section_1_1_1", textblocks_en)
        self.assertIn("comprehensive evaluation", str(textblocks_en["section_1_1"]))
        self.assertIn("Vulnerability scanning", str(textblocks_en["section_1_1_1"]))

    def test_template_variable_detection(self):
        """Test that template variables are properly detected"""
        # Create a test template in the temporary directory
        test_template = self.templates_dir / "test.docx"
        doc = docx.Document()
        doc.add_paragraph('{{ sales_name }}')
        doc.add_paragraph('{{ sales_email }}')
        doc.add_paragraph('{{ sales_phone }}')
        doc.save(str(test_template))
        
        # Load template and detect variables
        doc = DocxTemplate(str(test_template))
        detected_vars = doc.get_undeclared_template_variables()
        
        # Verify expected variables are detected
        required_vars = {'sales_name', 'sales_email', 'sales_phone'}
        self.assertTrue(required_vars.issubset(detected_vars),
                       f"Missing sales fields in template variables: {required_vars - detected_vars}")

    def test_error_handling(self):
        """Test error handling for missing files"""
        with self.assertRaises(SystemExit):
            offerdocgenerator.load_config(Path("/non/existent/config.yaml"))

    def test_flattened_config_vars(self):
        """Verify flattened config variables exist in context"""
        config = offerdocgenerator.load_config(self.config_file)
        context = offerdocgenerator.build_context(config, "EN", self.product_name, "CHF")
        
        # Test flattened variables
        self.assertIn("offer_number", context)
        self.assertEqual(context["offer_number"], "2025-001")
        self.assertIn("customer_name", context)
        self.assertEqual(context["customer_name"], "Example Corp")
        self.assertIn("sales_email", context)
        self.assertEqual(context["sales_email"], "john.doe@example.com")

    @unittest.skip("Temporarily disabled - needs investigation of DOTX template handling")
    def test_dotx_generation(self):
        """Verify DOTX template creation with correct content type
        TODO: Investigate proper way to test DOTX template generation and usage
        Current issue: DocxTemplate cannot properly handle DOTX files
        Possible solutions:
        1. Use different library for DOTX testing
        2. Modify test to verify content type without opening template
        3. Convert DOTX to DOCX before testing content
        """
        config = offerdocgenerator.load_config(self.config_file)
        
        # Override output format for this test
        config.output["format"] = "dotx"
        product = self.product_name
        lang = "EN"
        currency = "EUR"
        
        # Generate DOTX file
        context = offerdocgenerator.build_context(config, lang, product, currency)
        textblocks = offerdocgenerator.load_textblocks(config, config.offer["sections"], product, lang)
        context.update(textblocks)
        
        output_file = self.output_dir / product / f"TEST_DOTX_{product}_{lang}_{currency}.dotx"
        output_file.parent.mkdir(parents=True, exist_ok=True)
        offerdocgenerator.render_offer(self.template_file_en, context, output_file)
        
        # Verify file properties
        self.assertTrue(output_file.exists())
        
        # Check ZIP package content type
        with zipfile.ZipFile(output_file) as z:
            content_type = z.read('[Content_Types].xml').decode()
            self.assertIn('application/vnd.openxmlformats-officedocument.wordprocessingml.template.main+xml', content_type)
        
        # Verify template can be used to create new documents
        test_output = output_file.with_name("test_from_template.docx")
        try:
            # Create new document FROM TEMPLATE using docxtpl
            template = DocxTemplate(str(output_file))
            template.render({"test_content": "Test added via template"})
            template.save(str(test_output))
            self.assertTrue(test_output.exists())
            
            # Verify the new document is valid
            test_doc = docx.Document(str(test_output))
            self.assertIn("Test added via template", test_doc.paragraphs[0].text)
        finally:
            if test_output.exists():
                test_output.unlink()

    def test_special_characters_in_templates(self):
        """Test templates with special characters"""
        # Create test template with special chars
        special_template = self.templates_dir / "special_chars.docx"
        doc = docx.Document()
        doc.add_paragraph('Test & Company © 2024')
        doc.add_paragraph('{{ sales_email }}')
        doc.save(str(special_template))
        
        # Render and verify
        config = offerdocgenerator.load_config(self.config_file)
        context = offerdocgenerator.build_context(config, "EN", self.product_name, "CHF")
        output_path = self.output_dir / "special_chars_test.docx"
        
        offerdocgenerator.render_offer(special_template, context, output_path)
        
        # Verify output
        doc = docx.Document(str(output_path))
        self.assertIn("Test & Company © 2024", doc.paragraphs[0].text)
        self.assertIn("john.doe@example.com", doc.paragraphs[1].text)

    def test_richtext_format_preservation(self):
        """Verify bold/italic/underline formatting in textblocks"""
        # Create formatted test file with correct section prefix
        test_file = self.textblocks_dir / "common" / "section_formatted_EN.docx"
        doc = docx.Document()
        p = doc.add_paragraph()
        p.add_run('Bold text').bold = True
        p.add_run(' Italic').italic = True
        p.add_run(' Underlined').underline = True
        doc.save(str(test_file))

        # Update config to include formatted section
        config = offerdocgenerator.load_config(self.config_file)
        config.offer["sections"].append("formatted")
        
        # Load and verify textblocks
        textblocks = offerdocgenerator.load_textblocks(config, self.product_name, "EN")
        self.assertIn("section_formatted", textblocks)  # Verify section exists
        
        rt = textblocks["section_formatted"]
        
        # Check formatting preserved in XML
        self.assertIn("Bold text", rt.xml)
        self.assertIn("<w:b/>", rt.xml)  # Bold tag
        self.assertIn("<w:i/>", rt.xml)  # Italic tag
        self.assertIn('<w:u w:val="single"/>', rt.xml)  # Underline tag

    def test_invalid_config_sections(self):
        """Test handling of config with missing required sections"""
        invalid_config = {
            "offer": {"number": "123"},  # Missing other required fields
            "textblocks": {}
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        with self.assertRaises(ValueError) as cm:
            offerdocgenerator.load_config(self.config_file)
        self.assertIn("Missing required config sections: ['output', 'customer', 'sales']", str(cm.exception))

    def test_invalid_config_fields(self):
        """Test missing required fields within existing sections"""
        invalid_config = {
            "offer": {
                "sections": ["1_1"],
                "template": "templates/",
                # Missing number/date/validity
            },
            "textblocks": {
                "common": {"folder": str(self.textblocks_dir / "common")},
                "products_dir": str(self.textblocks_dir / "products")
            },
            "output": {"folder": str(self.output_dir)},
            "customer": {
                "name": "Test Corp",
                "address": "Test St",
                "city": "Test City",
                "zip": "12345",
                "country": "Test Country"
            },
            "sales": {
                "name": "Test Sales",
                "email": "test@example.com",
                "phone": "123456"
            }
        }
        
        with open(self.config_file, 'w') as f:
            yaml.dump(invalid_config, f)
        
        with self.assertRaises(ValueError) as cm:
            offerdocgenerator.load_config(self.config_file)
        self.assertIn("Missing required fields in offer", str(cm.exception))

    def test_render_offer(self):
        """Test rendering for all language/currency combinations in both DOCX and DOTX formats."""
        # Load fresh config for each format test
        for output_format in ["docx", "dotx"]:
            config = offerdocgenerator.load_config(self.config_file)
            config.output["format"] = output_format
            
            products = offerdocgenerator.get_product_names(self.textblocks_dir)
            prefix = config.output.get("prefix", "Offer_")

            # Add validity text to templates for nested config testing
            for template in [self.template_file_en, self.template_file_de]:
                doc = docx.Document(str(template))
                doc.add_paragraph('Validity: {{ Config.offer.validity[LANGUAGE] }}')
                doc.save(str(template))

            # Verify files per product
            for product in products:
                for lang in ["EN", "DE"]:
                    for currency in ["CHF", "EUR"]:
                        with self.subTest(product=product, language=lang, currency=currency, format=output_format):
                            # Build context with currency
                            context = offerdocgenerator.build_context(config, lang, product, currency)
                            textblocks = offerdocgenerator.load_textblocks(config, product, lang)
                            context.update(textblocks)
                            
                            # Select template
                            template = self.template_file_en if lang == "EN" else self.template_file_de
                            output_file = self.output_dir / product / f"{prefix}{product}_{lang}_{currency}.{output_format}"
                            
                            # Create product subdirectory
                            output_file.parent.mkdir(parents=True, exist_ok=True)
                            
                            # Render and verify
                            offerdocgenerator.render_offer(template, context, output_file)
                            self.assertTrue(output_file.exists())
                            
                            # Only validate DOCX content - skip for DOTX
                            if output_format == "docx":
                                doc = docx.Document(str(output_file))
                                full_text = "\n".join(para.text for para in doc.paragraphs)
                                self.assertIn(currency, full_text)
                                self.assertIn(config.offer["number"], full_text)
                                self.assertIn(config.customer["name"], full_text)
                                self.assertIn(config.customer["address"], full_text)
                                self.assertIn(config.sales["email"], full_text)
                                self.assertIn(config.sales["phone"], full_text)

            # Verify file count for this format
            generated_files = list(self.output_dir.glob(f"**/{prefix}*.{output_format}"))
            self.assertEqual(len(generated_files), 8,
                           f"Expected 8 files for {output_format}, found {len(generated_files)}")

if __name__ == '__main__':
    unittest.main()
