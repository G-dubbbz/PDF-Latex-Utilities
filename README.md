# LaTeX Utilities

A collection of Python scripts for common tasks when writing LaTeX reports.

## Setup

```bash
pip install -r requirements.txt
```

> **macOS only:** `pdf2image` also requires Poppler:
> ```bash
> brew install poppler
> ```

---

## Scripts

### `wordcount.py`
Counts words in a compiled LaTeX PDF. Automatically skips front matter (title page, abstract, TOC) by detecting arabic page numbering, and stops before the bibliography.

**Usage:**
```bash
python3 wordcount.py             # counts words in ./Input/*.pdf
python3 wordcount.py --verbose   # includes per-page breakdown
```

---

### `doi_to_bibtex.py`
Fetches BibTeX entries from DOIs using the CrossRef API and appends them to `./Output/references.bib`. Skips entries that already exist.

> Set your email in `EMAIL` at the top of the script for faster API responses.

**Usage:**
```bash
python3 doi_to_bibtex.py                        # interactive mode
python3 doi_to_bibtex.py 10.xxxx/xxxxx          # single DOI
python3 doi_to_bibtex.py ./Input/dois.txt       # file with one DOI per line
```

---

### `citation_formatter.py`
Cleans and formats `.bib` files. Reads from `./Input/`, writes to `./Output/`.

- Removes duplicate entries (by key or DOI)
- Standardizes field order and indentation
- Generates clean citation keys (`AuthorYEARWord`)
- Fixes Norwegian/special characters (`ø`, `æ`, `å`, etc.) to LaTeX encoding
- Always creates a timestamped backup before modifying

**Usage:**
```bash
python3 citation_formatter.py                      # formats all .bib files in ./Input/
python3 citation_formatter.py --check ./path       # also reports unused entries vs .tex files
```

---

### `pdfFlattener.py`
Flattens PDF form fields using `pypdf`, baking filled values into the page. Use this for simple forms. If the result doesn't render correctly in LaTeX, use `pdfFlattenerImage.py` instead.

Reads from `./Input/`, writes to `./Output/`, deletes originals from `./Input/`.

**Usage:**
```bash
python3 pdfFlattener.py
```

---

### `pdfFlattenerImage.py`
Flattens PDFs by rendering each page to an image and saving back as a PDF. More reliable than `pdfFlattener.py` for complex or interactive forms. Guaranteed to work with `\includepdf` in LaTeX.

Reads from `./Input/`, writes to `./Output/`, deletes originals from `./Input/`.

**Usage:**
```bash
python3 pdfFlattenerImage.py
```

---

## Folder structure

```
.
├── Input                   ← drop input files here
├── Output                  ← output files land here
├── README.md
├── citation_formatter.py
├── doi_to_bibtex.py
├── pdfFlattener.py
├── pdfFlattenerImage.py
├── requirements.txt
└── wordcount.py                  
```
