# OfferDocGenerator

This repository contains a Python script (**OfferDocGenerator.py**) that generates `.docx` offers from Word `.dotx` templates.
It replaces placeholders with text read from `.txt` files.

## Overview

1. **Reduced Folder Structure**: Instead of having separate folders by language, you can suffix the `.txt` filenames (e.g. `section1EN.txt`, `section1DE.txt`) to indicate the language.
2. **Script**: The script can prompt for paths interactively, or accept command-line arguments and run in non-interactive (`-y`) mode.
3. **Placeholders**:
   - The script merges placeholders from `textblock/common` and `textblock/products/<productName>` for the specified language.
   - It also inserts a `CURRENCY` placeholder, so `{{CURRENCY}}` in your Word template gets replaced with a user-provided currency (default: `CHF`).
4. **Output**: The generated `.docx` files are saved with a filename pattern like `Offer_{productName}_{language}_{currency}.docx` in an output folder (default: `output`).

## Directory Structure

Below is an example project layout:

```
.
├─ OfferDocGenerator.py        # The main Python script
├─ textblock/
│   ├─ common/
│   │   ├─ section1EN.txt
│   │   ├─ section1DE.txt
│   │   └─ ...
│   └─ products/
│       ├─ MyProduct/
│       │   ├─ section1.2EN.txt
│       │   ├─ section1.2DE.txt
│       │   └─ ...
├─ input/
│   ├─ baseEN.dotx
│   ├─ baseDE.dotx
│   └─ ...
├─ output/
│   └─ (generated .docx files)
└─ README.md
```

- **`textblock/common`**: Contains `.txt` files that apply to all products. Filenames end with `EN.txt` or `DE.txt` depending on the language.
- **`textblock/products/MyProduct`**: Product-specific `.txt` files.
- **`input`**: Holds `.dotx` templates named in a way that hints at their language (e.g., `baseEN.dotx`, `baseDE.dotx`).
- **`output`**: Destination folder where `.docx` files get saved.

## Usage

### Interactive Mode

Run the script without `-y`:

```bash
python OfferDocGenerator.py
```

You’ll be prompted for:

1. **Textblock folder** (default: `textblock`)
2. **Input folder** (default: `input`)
3. **Output folder** (default: `output`)
4. **Language** (default: `all` — processes all matching templates, e.g., baseEN.dotx & baseDE.dotx)
5. **Currency** (default: `CHF`)

### Non-Interactive / -y Mode

```bash
python OfferDocGenerator.py -y --textblock <folder> --input <folder> --output <folder> \
    --lang <EN|DE|all> --currency <CHF|EUR|...>
```

If you omit an argument, it uses the default. For example:

```bash
python OfferDocGenerator.py -y --lang EN
```

Uses defaults (`textblock=textblock`, `input=input`, `output=output`, `currency=CHF`) but processes only language **EN**.

### Placeholder Rules

1. If a template is named `baseEN.dotx`, we treat it as `EN`. If you specified `--lang DE`, the script skips it.
2. `.txt` files in `textblock/common` or `textblock/products/<productName>` must end with `EN.txt` or `DE.txt`.
   - For instance, `section1EN.txt` → placeholder key `section1` (for English).
   - `section1DE.txt` → placeholder key `section1` (for German).
3. The Word templates can contain placeholders like `{{section1}}`, which gets replaced by the file content.
4. A special placeholder `{{CURRENCY}}` is replaced by the user-supplied currency (e.g., `CHF`, `EUR`).
5. The script also sets `{{DOC_TITLE}}` to `"Offer for {productName} ({language}-{currency})"`.

## Running Tests

A test suite is included in `test_offerdocgenerator.py`. To run:

```bash
python -m unittest test_offerdocgenerator.py
```

## Requirements

- **Python 3.7+**
- **`python-docx-template`**: `pip install docxtpl`

## Contributing

1. Fork or clone this repo.
2. Adjust the script to your environment (folder names, placeholders, etc.).
3. Submit PRs or open issues for improvements.

## License

[MIT License](https://opensource.org/licenses/MIT)
