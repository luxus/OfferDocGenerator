import os
import tempfile
import unittest
from main import collect_placeholders_for_language, read_txt_file, generate_offers

class TestOfferDocGenerator(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = tempfile.TemporaryDirectory()
        self.textblock_dir = os.path.join(self.test_dir.name, "textblock")
        self.input_dir = os.path.join(self.test_dir.name, "input")
        self.output_dir = os.path.join(self.test_dir.name, "output")
        os.makedirs(os.path.join(self.textblock_dir, "common"), exist_ok=True)
        os.makedirs(os.path.join(self.textblock_dir, "products", "MyProduct"), exist_ok=True)
        os.makedirs(self.input_dir, exist_ok=True)

        # Create test .txt files
        with open(os.path.join(self.textblock_dir, "common", "section1EN.txt"), "w", encoding="utf-8") as f:
            f.write("English content for section 1.")
        with open(os.path.join(self.textblock_dir, "common", "section1DE.txt"), "w", encoding="utf-8") as f:
            f.write("Deutscher Inhalt für Abschnitt 1.")
        with open(os.path.join(self.textblock_dir, "products", "MyProduct", "section1.2EN.txt"), "w", encoding="utf-8") as f:
            f.write("English product-specific content for section 1.2.")
        with open(os.path.join(self.textblock_dir, "products", "MyProduct", "section1.2DE.txt"), "w", encoding="utf-8") as f:
            f.write("Deutscher produktbezogener Inhalt für Abschnitt 1.2.")

        # Create test .dotx templates
        with open(os.path.join(self.input_dir, "baseEN.dotx"), "w", encoding="utf-8") as f:
            f.write("{{ DOC_TITLE }}\n\nCommon Section 1: {{ section1 }}\n\nProduct Section 1.2: {{ section1.2 }}\n\nCurrency: {{ CURRENCY }}")
        with open(os.path.join(self.input_dir, "baseDE.dotx"), "w", encoding="utf-8") as f:
            f.write("{{ DOC_TITLE }}\n\nAllgemeiner Abschnitt 1: {{ section1 }}\n\nProdukt Abschnitt 1.2: {{ section1.2 }}\n\nWährung: {{ CURRENCY }}")

    def tearDown(self):
        # Clean up the temporary directory
        self.test_dir.cleanup()

    def test_read_txt_file(self):
        # Test reading a valid file
        content = read_txt_file(os.path.join(self.textblock_dir, "common", "section1EN.txt"))
        self.assertEqual(content, "English content for section 1.")

        # Test reading a nonexistent file
        content = read_txt_file("nonexistent.txt")
        self.assertEqual(content, "")

    def test_collect_placeholders_for_language(self):
        # Test collecting placeholders for English
        placeholders = collect_placeholders_for_language(os.path.join(self.textblock_dir, "common"), "EN")
        self.assertIn("section1", placeholders)
        self.assertEqual(placeholders["section1"], "English content for section 1.")

        # Test collecting placeholders for German
        placeholders = collect_placeholders_for_language(os.path.join(self.textblock_dir, "common"), "DE")
        self.assertIn("section1", placeholders)
        self.assertEqual(placeholders["section1"], "Deutscher Inhalt für Abschnitt 1.")

        # Test collecting placeholders for a nonexistent language
        placeholders = collect_placeholders_for_language(os.path.join(self.textblock_dir, "common"), "FR")
        self.assertEqual(placeholders, {})

    def test_generate_offers(self):
        # Mock settings
        settings = {
            "textblock_folder": self.textblock_dir,
            "input_folder": self.input_dir,
            "output_folder": self.output_dir,
            "lang": "all",
            "currency": "CHF",
        }

        # Generate offers
        generate_offers(settings)

        # Check if output files were created
        expected_files = [
            "Offer_MyProduct_EN_CHF.docx",
            "Offer_MyProduct_DE_CHF.docx",
        ]
        for filename in expected_files:
            filepath = os.path.join(self.output_dir, filename)
            self.assertTrue(os.path.isfile(filepath), f"File {filename} was not generated.")

        # Optionally, validate the content of the generated files
        # This requires extracting text from .docx files, which can be done using python-docx


if __name__ == "__main__":
    unittest.main()
