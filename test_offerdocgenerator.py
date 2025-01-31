import os
import tempfile
import unittest
from main import collect_placeholders, read_txt_file, generate_offers


class TestOfferDocGenerator(unittest.TestCase):
    def setUp(self):
        """Set up temporary directories and test files."""
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
        with open(
            os.path.join(self.textblock_dir, "products", "MyProduct", "section1.2EN.txt"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write("English product-specific content for section 1.2.")
        with open(
            os.path.join(self.textblock_dir, "products", "MyProduct", "section1.2DE.txt"),
            "w",
            encoding="utf-8",
        ) as f:
            f.write("Deutscher produktbezogener Inhalt für Abschnitt 1.2.")

        # Create test .dotx templates
        with open(os.path.join(self.input_dir, "baseEN.dotx"), "w", encoding="utf-8") as f:
            f.write(
                "{{ DOC_TITLE }}\n\nCommon Section 1: {{ section1 }}"
                "\n\nProduct Section 1.2: {{ section1.2 }}\n\nCurrency: {{ CURRENCY }}"
            )
        with open(os.path.join(self.input_dir, "baseDE.dotx"), "w", encoding="utf-8") as f:
            f.write(
                "{{ DOC_TITLE }}\n\nAllgemeiner Abschnitt 1: {{ section1 }}"
                "\n\nProdukt Abschnitt 1.2: {{ section1.2 }}\n\nWährung: {{ CURRENCY }}"
            )

    def tearDown(self):
        """Clean up temporary directory."""
        self.test_dir.cleanup()

    def test_read_txt_file(self):
        """Test reading a valid file and a nonexistent file."""
        content = read_txt_file(os.path.join(self.textblock_dir, "common", "section1EN.txt"))
        self.assertEqual(content, "English content for section 1.")

        content = read_txt_file("nonexistent.txt")
        self.assertEqual(content, "")

    def test_collect_placeholders_for_language(self):
        """Test collecting placeholders for different languages."""
        placeholders = collect_placeholders(os.path.join(self.textblock_dir, "common"), "EN")
        self.assertIn("section1", placeholders)
        self.assertEqual(placeholders["section1"], "English content for section 1.")

        placeholders = collect_placeholders(os.path.join(self.textblock_dir, "common"), "DE")
        self.assertIn("section1", placeholders)
        self.assertEqual(placeholders["section1"], "Deutscher Inhalt für Abschnitt 1.")

        placeholders = collect_placeholders(os.path.join(self.textblock_dir, "common"), "FR")
        self.assertEqual(placeholders, {})

    def test_generate_offers(self):
        """Test generating .docx files."""
        settings = {
            "textblock_folder": self.textblock_dir,
            "input_folder": self.input_dir,
            "output_folder": self.output_dir,
            "lang": "all",
            "currency": "CHF",
        }

        generate_offers(settings)

        expected_files = [
            "Offer_MyProduct_EN_CHF.docx",
            "Offer_MyProduct_DE_CHF.docx",
        ]
        for filename in expected_files:
            filepath = os.path.join(self.output_dir, filename)
            self.assertTrue(os.path.isfile(filepath), f"File {filename} was not generated.")


if __name__ == "__main__":
    unittest.main()
