#!/usr/bin/env python3
"""
OfferDocGenerator.py

This script generates Word .docx files by replacing placeholders in .dotx templates with text blocks from .txt files.
Placeholders are replaced based on the specified language and currency.

Usage:
    python OfferDocGenerator.py                 # Interactive mode
    python OfferDocGenerator.py -y --lang EN    # Non-interactive mode

Directory Structure:
    textblock/
        common/                 # Common text blocks for all products
            section1EN.txt      # English placeholder for 'section1'
            section1DE.txt      # German placeholder for 'section1'
        products/               # Product-specific text blocks
            MyProduct/          # Example product folder
                section1.2EN.txt  # English placeholder for 'section1.2'
                section1.2DE.txt  # German placeholder for 'section1.2'
    input/                      # Folder containing .dotx templates
        baseEN.dotx             # Template for English offers
        baseDE.dotx             # Template for German offers
    output/                     # Output folder for generated .docx files

Generated Files:
    Offer_MyProduct_EN_CHF.docx  # Example output file for English offers in CHF
    Offer_MyProduct_DE_EUR.docx  # Example output file for German offers in EUR
"""

import argparse
import os
from docxtpl import DocxTemplate


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate offers from text blocks.")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip interactive prompts and use defaults or provided arguments.",
    )
    parser.add_argument("--textblock", default=None, help="Path to the textblock folder.")
    parser.add_argument("--input", default=None, help="Path to the input folder with .dotx templates.")
    parser.add_argument("--output", default=None, help="Path to the output folder for generated .docx files.")
    parser.add_argument("--lang", default=None, help="Language code (e.g., 'EN', 'DE') or 'all'.")
    parser.add_argument("--currency", default=None, help="Currency code (e.g., 'CHF', 'EUR').")
    return parser.parse_args()


def prompt_for_settings(defaults):
    """Prompt the user for settings if not provided via command-line."""
    print("\nInteractive Mode (Press Enter to accept defaults):")

    textblock_folder = input(f"Enter path to textblock folder [default='{defaults['textblock']}']: ").strip()
    textblock_folder = textblock_folder or defaults["textblock"]

    input_folder = input(f"Enter path to input folder [default='{defaults['input']}']: ").strip()
    input_folder = input_folder or defaults["input"]

    output_folder = input(f"Enter path to output folder [default='{defaults['output']}']: ").strip()
    output_folder = output_folder or defaults["output"]

    lang = input(f"Enter language code (e.g., 'EN', 'DE') or 'all' [default='{defaults['lang']}']: ").strip()
    lang = lang or defaults["lang"]

    currency = input(f"Enter currency code (e.g., 'CHF', 'EUR') [default='{defaults['currency']}']: ").strip()
    currency = currency or defaults["currency"]

    return {
        "textblock_folder": textblock_folder,
        "input_folder": input_folder,
        "output_folder": output_folder,
        "lang": lang,
        "currency": currency,
    }


def read_txt_file(path):
    """Read the content of a text file. Return an empty string if the file does not exist."""
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read().strip()


def collect_placeholders(folder, language):
    """Collect placeholders from .txt files ending with {language}.txt."""
    placeholders = {}
    if not os.path.isdir(folder):
        return placeholders

    lang_upper = language.upper()
    for filename in os.listdir(folder):
        if filename.upper().endswith(f"{lang_upper}.TXT"):
            base_name = os.path.splitext(filename)[0]
            placeholder_name = base_name[:-len(lang_upper)].strip() if base_name.upper().endswith(lang_upper) else base_name.strip()
            file_path = os.path.join(folder, filename)
            placeholders[placeholder_name] = read_txt_file(file_path)

    return placeholders


def generate_offers(settings):
    """Generate .docx files based on the provided settings."""
    textblock_folder = settings["textblock_folder"]
    input_folder = settings["input_folder"]
    output_folder = settings["output_folder"]
    chosen_lang = settings["lang"]
    chosen_currency = settings["currency"]

    # Ensure the output folder exists
    os.makedirs(output_folder, exist_ok=True)

    # Gather all .dotx templates from the input folder
    templates = [f for f in os.listdir(input_folder) if f.lower().endswith(".dotx")]
    if not templates:
        print(f"No .dotx templates found in {input_folder}")
        return

    for template_filename in templates:
        # Determine the language of the template from its filename
        lang_in_name = None
        if "EN" in template_filename.upper():
            lang_in_name = "EN"
        elif "DE" in template_filename.upper():
            lang_in_name = "DE"
        else:
            lang_in_name = "EN"  # Default fallback

        if chosen_lang.lower() != "all" and lang_in_name.lower() != chosen_lang.lower():
            print(f"Skipping {template_filename}; language mismatch ({lang_in_name} vs {chosen_lang}).")
            continue

        template_path = os.path.join(input_folder, template_filename)

        # Process each product folder in textblock/products
        products_folder = os.path.join(textblock_folder, "products")
        if not os.path.isdir(products_folder):
            print(f"No 'products' folder found in {textblock_folder}. Skipping...")
            continue

        for product_name in os.listdir(products_folder):
            product_path = os.path.join(products_folder, product_name)
            if not os.path.isdir(product_path):
                continue

            # Collect placeholders from common and product-specific folders
            common_folder = os.path.join(textblock_folder, "common")
            common_placeholders = collect_placeholders(common_folder, lang_in_name)
            product_placeholders = collect_placeholders(product_path, lang_in_name)

            placeholders = {**common_placeholders, **product_placeholders}
            placeholders["CURRENCY"] = chosen_currency
            placeholders["DOC_TITLE"] = f"Offer for {product_name} ({lang_in_name}-{chosen_currency})"

            # Render the template with placeholders
            tpl = DocxTemplate(template_path)
            tpl.render(placeholders)

            # Save the generated .docx file
            output_filename = f"Offer_{product_name}_{lang_in_name}_{chosen_currency}.docx"
            output_path = os.path.join(output_folder, output_filename)
            tpl.save(output_path)
            print(f"Generated: {output_path}")


def main():
    """Main entry point."""
    args = parse_arguments()

    # Default settings
    defaults = {
        "textblock": "textblock",
        "input": "input",
        "output": "output",
        "lang": "all",
        "currency": "CHF",
    }

    # Override defaults with command-line arguments
    if args.textblock:
        defaults["textblock"] = args.textblock
    if args.input:
        defaults["input"] = args.input
    if args.output:
        defaults["output"] = args.output
    if args.lang:
        defaults["lang"] = args.lang
    if args.currency:
        defaults["currency"] = args.currency

    # Use defaults directly in non-interactive mode
    if args.yes:
        settings = {
            "textblock_folder": defaults["textblock"],
            "input_folder": defaults["input"],
            "output_folder": defaults["output"],
            "lang": defaults["lang"],
            "currency": defaults["currency"],
        }
    else:
        settings = prompt_for_settings(defaults)

    # Generate offers
    generate_offers(settings)


if __name__ == "__main__":
    main()
