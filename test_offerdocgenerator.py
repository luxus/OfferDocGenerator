import sys
import os
import unittest
import tempfile
import shutil
from pathlib import Path
import yaml
import docx
from unittest import mock
from docxtpl import DocxTemplate
import offerdocgenerator

class TestOfferDocGenerator(unittest.TestCase):
    # Control whether to cleanup test files
    CLEANUP = False  # Set to True to enable test file cleanup

    def setUp(self):
        """Set up test fixtures in test_data subdirectory"""
        # Set up test directories under test_data
        self.test_data = Path(__file__).parent / "test_data"
        self.test_data.mkdir(exist_ok=True)
        
        self.config_file = self.test_data / "test_config.yaml"
        self.templates_dir = self.test_data / "templates" 
        self.output_dir = self.test_data / "output"
        self.textblocks_dir = self.test_data / "textblocks"
        self.product_name = "Web Application Security Assessment"

        # Only clean if CLEANUP enabled
        if self.CLEANUP:
            shutil.rmtree(self.templates_dir, ignore_errors=True)
            shutil.rmtree(self.textblocks_dir, ignore_errors=True)
        
        # Create output dir if needed but don't clean it
        self.output_dir.mkdir(exist_ok=True)

        # Create necessary directories
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
                "sections": ["1_1", "1_1_1"],
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
                "folder": str(self.output_dir)
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
        """Conditional cleanup based on CLEANUP flag"""
        if self.CLEANUP:
            # Clean up all test files
            shutil.rmtree(self.test_data, ignore_errors=True)
        else:
            # Print location of preserved files
            print(f"\nTest files preserved in: {self.test_data.absolute()}")

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
        """Test loading of textblocks from both product-specific and common directories."""
        config = offerdocgenerator.load_config(self.config_file)
        sections = ["1_1", "1_1_1"]

        # Test German textblocks
        textblocks_de = offerdocgenerator.load_textblocks(config, sections, self.product_name, "DE")
        self.assertIn("section_1_1", textblocks_de)
        self.assertIn("section_1_1_1", textblocks_de)
        self.assertIn("Sicherheitsbewertung", str(textblocks_de["section_1_1"]))
        self.assertIn("Schwachstellenscanning", str(textblocks_de["section_1_1_1"]))

        # Test English textblocks
        textblocks_en = offerdocgenerator.load_textblocks(config, sections, self.product_name, "EN")
        self.assertIn("section_1_1", textblocks_en)
        self.assertIn("section_1_1_1", textblocks_en)
        self.assertIn("comprehensive evaluation", str(textblocks_en["section_1_1"]))
        self.assertIn("Vulnerability scanning", str(textblocks_en["section_1_1_1"]))

    def test_template_variable_detection(self):
        """Test that template variables are properly detected"""
        # Create a test template with known variables
        test_template = self.templates_dir / "test_template.docx"
        doc = docx.Document()
        doc.add_paragraph("{{ test_var }}")
        doc.add_paragraph("{% if condition %}")
        doc.add_paragraph("{{r rich_text }}")
        doc.save(str(test_template))

        # Load template and detect variables
        doc = DocxTemplate(str(test_template))
        detected_vars = doc.get_undeclared_template_vars()
        
        # Verify expected variables
        expected_vars = {'test_var', 'condition', 'rich_text'}
        self.assertEqual(set(detected_vars), expected_vars,
                         f"Detected variables mismatch. Expected {expected_vars}, got {detected_vars}")

        # Cleanup if enabled
        if self.CLEANUP:
            test_template.unlink()

    def test_render_offer(self):
        """Test rendering for all language/currency combinations."""
        config = offerdocgenerator.load_config(self.config_file)
        products = offerdocgenerator.get_product_names(self.textblocks_dir)
        
        # Verify files per product
        for product in products:
            for lang in ["EN", "DE"]:
                for currency in ["CHF", "EUR"]:
                    with self.subTest(product=product, language=lang, currency=currency):
                        # Build context with currency
                        context = offerdocgenerator.build_context(config, lang, product, currency)
                        textblocks = offerdocgenerator.load_textblocks(config, config.offer["sections"], product, lang)
                        context.update(textblocks)
                        
                        # Select template
                        template = self.template_file_en if lang == "EN" else self.template_file_de
                        output_file = self.output_dir / f"Offer_{product}_{lang}_{currency}.docx"
                        
                        # Render and verify
                        offerdocgenerator.render_offer(template, context, output_file)
                        self.assertTrue(output_file.exists())
                        
                        # Verify currency in document
                        doc = docx.Document(str(output_file))
                        full_text = "\n".join(para.text for para in doc.paragraphs)
                        self.assertIn(currency, full_text)
                        self.assertIn(config.offer["number"], full_text)
                        self.assertIn(config.customer["name"], full_text)
                        self.assertIn(config.customer["address"], full_text)
                        self.assertIn(config.sales["email"], full_text)
                        self.assertIn(config.sales["phone"], full_text)
        
        # Verify total file count (2 products * 2 langs * 2 currencies = 8 files)
        generated_files = list(self.output_dir.glob("Offer_*.docx"))
        self.assertEqual(len(generated_files), 8,
                        f"Expected 8 files for 2 products, found {len(generated_files)}")

if __name__ == '__main__':
    unittest.main()
