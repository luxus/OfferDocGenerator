#!/usr/bin/env python3
"""
OfferDocGenerator.py (Interactive + -y mode)

This script generates Word .docx files with placeholders replaced by text blocks.
It supports reading placeholders from multiple .txt files named with a language suffix
(e.g. section1EN.txt => placeholder 'section1' for English). It also supports a "-y" mode
to skip interactive prompts. By default:
 - textblock folder is 'textblock'
 - input folder is 'input' (where .dotx templates are stored)
 - output folder is 'output'
 - language is 'all' (process all relevant templates)
 - currency is 'CHF'

Usage:
    python OfferDocGenerator.py                 # Normal interactive mode.
    python OfferDocGenerator.py -y --lang EN    # Non-interactive, skipping prompts.

Example directory layout:

textblock/
  common/
    section1EN.txt
    section1DE.txt
  products/
    MyProduct/
      section1.2EN.txt
      section1.2DE.txt
input/
  baseEN.dotx
  baseDE.dotx

Script logic:
1) Parse command-line arguments with argparse.
2) If "-y" is not provided, prompt user for any missing settings.
3) The script reads all .dotx templates from the input folder.
   - If a template name includes "EN" or "DE", we treat that as the template's language.
   - If the user only wants a single language (e.g. "EN"), we skip templates that mismatch.
4) For each product subfolder in textblock/products, gather .txt placeholders that end in {lang}.txt.
5) Merge placeholders from common + product.
6) Insert a {{CURRENCY}} placeholder as well.
7) Write out a .docx named "Offer_{productName}_{language}_{currency}.docx" in the output folder.

Note: This script depends on 'python-docx-template' (pip install docxtpl).

-- Testing Support --
Below is a minimal unittest demonstrating partial functionality. In practice, you'd keep tests
in a separate file (e.g., test_offerdocgenerator.py) and run with 'python -m unittest'.

"""

import argparse
import os
import sys
from docxtpl import DocxTemplate


def parse_arguments():
    """Parse command-line arguments."""
    parser = argparse.ArgumentParser(description="Generate offers from text blocks.")
    parser.add_argument(
        "-y",
        "--yes",
        action="store_true",
        help="Skip prompts and use defaults or cmdline arguments directly.",
    )
    parser.add_argument("--textblock", default=None, help="Path to textblock folder.")
    parser.add_argument(
        "--input", default=None, help="Path to folder with .dotx templates."
    )
    parser.add_argument("--output", default=None, help="Output folder.")
    parser.add_argument("--lang", default=None, help="Language code or 'all'.")
    parser.add_argument("--currency", default=None, help="Currency code (e.g., 'CHF').")
    return parser.parse_args()


def prompt_for_settings(defaults: dict) -> dict:
    """Prompt user for settings if not provided via command-line."""
    print("\nInteractive Mode (Press Enter to accept defaults if any)")

    textblock_folder = input(
        f"Enter path to textblock folder [default='{defaults['textblock']}']: "
    ).strip()
    if not textblock_folder:
        textblock_folder = defaults["textblock"]

    input_folder = input(
        f"Enter path to folder with .dotx templates [default='{defaults['input']}']: "
    ).strip()
    if not input_folder:
        input_folder = defaults["input"]

    output_folder = input(
        f"Enter output folder [default='{defaults['output']}']: "
    ).strip()
    if not output_folder:
        output_folder = defaults["output"]

    lang = input(
        f"Enter language code (e.g. 'EN', 'DE') or 'all' [default='{defaults['lang']}']: "
    ).strip()
    if not lang:
        lang = defaults["lang"]

    currency = input(
        f"Enter currency code (e.g. 'CHF', 'EUR') [default='{defaults['currency']}']: "
    ).strip()
    if not currency:
        currency = defaults["currency"]

    return {
        "textblock_folder": textblock_folder,
        "input_folder": input_folder,
        "output_folder": output_folder,
        "lang": lang,
        "currency": currency,
    }


def read_txt_file(path: str) -> str:
    """Read content of a text file."""
    if not os.path.isfile(path):
        return ""
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


def collect_placeholders_for_language(folder: str, language: str) -> dict:
    """Collect placeholders from files ending with {language}.txt."""
    placeholders = {}
    if not os.path.isdir(folder):
        return placeholders

    lang_upper = language.upper()
    for filename in os.listdir(folder):
        if filename.upper().endswith(f"{lang_upper}.TXT"):
            base_name = os.path.splitext(filename)[0]
            if base_name.upper().endswith(lang_upper):
                placeholder_name = base_name[: -len(lang_upper)]
            else:
                placeholder_name = base_name
            placeholder_name = placeholder_name.strip()

            file_path = os.path.join(folder, filename)
            placeholders[placeholder_name] = read_txt_file(file_path)

    return placeholders


def generate_offers(settings: dict):
    """Generate .docx files based on settings."""
    textblock_folder = settings["textblock_folder"]
    input_folder = settings["input_folder"]
    output_folder = settings["output_folder"]
    chosen_lang = settings["lang"]
    chosen_currency = settings["currency"]

    # Gather templates
    templates = [f for f in os.listdir(input_folder) if f.lower().endswith(".dotx")]
    if not templates:
        print(f"No .dotx templates found in {input_folder}")
        return

    os.makedirs(output_folder, exist_ok=True)

    for template_filename in templates:
        # Guess language from filename
        lang_in_name = None
        if "EN" in template_filename.upper():
            lang_in_name = "EN"
        elif "DE" in template_filename.upper():
            lang_in_name = "DE"
        else:
            lang_in_name = "EN"  # Fallback

        if (
            chosen_lang.lower() != "all"
            and lang_in_name.lower() != chosen_lang.lower()
        ):
            print(f"Skipping {template_filename}; doesn't match {chosen_lang}.")
            continue

        full_template_path = os.path.join(input_folder, template_filename)

        # Find product folders in 'products/'
        products_folder = os.path.join(textblock_folder, "products")
        if not os.path.isdir(products_folder):
            print(f"No 'products' folder found in {textblock_folder}.")
            return

        for product_name in os.listdir(products_folder):
            product_path = os.path.join(products_folder, product_name)
            if not os.path.isdir(product_path):
                continue

            # Gather placeholders
            common_folder = os.path.join(textblock_folder, "common")
            common_ph = collect_placeholders_for_language(common_folder, lang_in_name)
            product_ph = collect_placeholders_for_language(product_path, lang_in_name)

            placeholders = {}
            placeholders.update(common_ph)
            placeholders.update(product_ph)

            placeholders["CURRENCY"] = chosen_currency

            doc_title = f"Offer for {product_name} ({lang_in_name}-{chosen_currency})"
            placeholders["DOC_TITLE"] = doc_title

            # Render template with placeholders
            tpl = DocxTemplate(full_template_path)
            tpl.render(placeholders)

            out_filename = f"Offer_{product_name}_{lang_in_name}_{chosen_currency}.docx"
            out_path = os.path.join(output_folder, out_filename)
            tpl.save(out_path)
            print(f"Generated: {out_path}")


def main():
    """Main entry point."""
    args = parse_arguments()

    # Default settings
    defaults = {
        "textblock": "textblock",  # Folder containing common/ and products/
        "input": "input",  # Folder containing .dotx templates
        "output": "output",  # Folder to save .docx files
        "lang": "all",  # Process all languages found in template filenames
        "currency": "CHF",  # Default currency
    }

    # Override defaults if provided
    if args.textblock is not None:
        defaults["textblock"] = args.textblock
    if args.input is not None:
        defaults["input"] = args.input
    if args.output is not None:
        defaults["output"] = args.output
    if args.lang is not None:
        defaults["lang"] = args.lang
    if args.currency is not None:
        defaults["currency"] = args.currency

    if args.yes:
        # Skip prompts, use defaults directly
        settings = {
            "textblock_folder": defaults["textblock"],
            "input_folder": defaults["input"],
            "output_folder": defaults["output"],
            "lang": defaults["lang"],
            "currency": defaults["currency"],
        }
    else:
        # Interactive mode
        if not defaults["input"]:
            defaults["input"] = "input"

        settings = prompt_for_settings(defaults)

    generate_offers(settings)


if __name__ == "__main__":
    main()
