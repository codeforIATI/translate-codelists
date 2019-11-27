# Translation for replicated codelists

This repository contains a helper script to support translation of replicated codelists. The idea is to generate Excel files which can then easily be translated into target languages, and then merged back into the existing XML files.

## Installation

1. Clone the repository:
   ```
   git clone git@github.com:codeforIATI/translate-codelists.git
   ```
2. Set up a virtualenv and install dependencies:
   ```
   virtualenv ./pyenv
   pip install -r requirements.txt
   ```

## Generate a translation file

1. Prerequisites: you need a codelist XML file (e.g. `Sector.xml`).
2. Generate a translation file by providing:
   * `--existing_codelist_filename`: The filename of the existing XML codelists file, e.g. 'Sector.xml'.
   * `--output_filename`: The output filename of the Excel translations into the desired language.
   * `--lang`: The language of the translations file in lowercase, e.g. 'fr' for French.

   Example:
   ```
   python translate.py generate-translations --existing_codelist_filename="Sector.xml" --output_filename="Sector_FR.xls" --lang="fr"
   ```

## Merge a translation file back into an existing codelist

1. Prerequisites: you need a codelist XML file (e.g. `Sector.xml` and a translation file (e.g. `Sector_FR.xls`).
2. Merge the translation file by providing:
   * `--existing_codelist_filename`: The filename of the existing XML codelists file, e.g. 'Sector.xml'.
   * `--output_filename`: The output filename of the new XML codelists file incorporating the translations.
   * `--new_translation_filename`: The filename of the Excel translation of the existing codelists file.
   * `--lang`: The language of the translations file in lowercase, e.g. 'fr' for French.

   Example:
   ```
   python translate.py merge-translations --existing_codelist_filename="Sector.xml" --output_filename="Sector_FR.xml" --new_translation_filename="Sector_FR.xls" --lang="fr"
   ```
