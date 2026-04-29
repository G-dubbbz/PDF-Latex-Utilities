# wordcount.py
# Counts words in a LaTeX-compiled PDF, only for main matter pages
# (arabic numeral pages, up to but not including the bibliography).
#
# Place your compiled PDF in ./Input/ and run:
#   python3 wordcount.py
#   python3 wordcount.py --verbose   # show per-page breakdown

import sys
import re
import glob
import os
import pdfplumber

INPUT_DIR = "./Input"

BIBLIOGRAPHY_TRIGGERS = [
    "referanser", "references", "bibliography", "litteratur", "kilder"
]


def get_page_number(page) -> str | None:
    words = page.extract_words()
    if not words:
        return None

    height = page.height
    margin_words = [
        w for w in words
        if w["top"] > height * 0.92 or w["bottom"] < height * 0.08
    ]

    for w in margin_words:
        if re.fullmatch(r"\d+", w["text"]):
            return w["text"]

    return None


def is_arabic(page_label: str) -> bool:
    return page_label is not None and re.fullmatch(r"\d+", page_label) is not None


def is_bibliography_page(page) -> bool:
    text = page.extract_text() or ""
    first_lines = "\n".join(text.strip().splitlines()[:4]).lower()
    return any(trigger in first_lines for trigger in BIBLIOGRAPHY_TRIGGERS)


def count_words(text: str) -> int:
    text = re.sub(r"-\n", "", text)
    return len(re.findall(r"\b\w+\b", text))


def process_pdf(pdf_path: str, verbose: bool):
    try:
        pdf = pdfplumber.open(pdf_path)
    except FileNotFoundError:
        print(f"✗ File not found: {pdf_path}")
        return

    print(f"Reading {os.path.basename(pdf_path)} ({len(pdf.pages)} pages total)...\n")

    total_words = 0
    counted_pages = 0
    first_arabic = None
    last_arabic = None
    page_results = []

    for i, page in enumerate(pdf.pages):
        label = get_page_number(page)

        if not is_arabic(label):
            continue

        if is_bibliography_page(page):
            print(f"  Stopped at bibliography (PDF page {i + 1}, labelled '{label}')")
            break

        if first_arabic is None:
            first_arabic = label

        text = page.extract_text() or ""
        words = count_words(text)
        total_words += words
        counted_pages += 1
        last_arabic = label
        page_results.append((i + 1, label, words))

    if verbose and page_results:
        print(f"  {'PDF page':<10} {'Label':<8} {'Words'}")
        print(f"  {'-'*30}")
        for pdf_page, label, words in page_results:
            print(f"  {pdf_page:<10} {label:<8} {words}")
        print()

    if counted_pages == 0:
        print("✗ No arabic-numbered pages found. Is this the right PDF?")
        return

    print(f"  Pages counted : {counted_pages}  (labelled {first_arabic}–{last_arabic})")
    print(f"  ✓ Word count  : {total_words:,}\n")


def main():
    verbose = "--verbose" in sys.argv

    os.makedirs(INPUT_DIR, exist_ok=True)

    pdf_files = glob.glob(os.path.join(INPUT_DIR, "*.pdf"))

    if not pdf_files:
        print(f"✗ No PDF files found in {INPUT_DIR}/")
        sys.exit(1)

    if len(pdf_files) > 1:
        print(f"Found {len(pdf_files)} PDFs in {INPUT_DIR}/:\n")

    for pdf_path in pdf_files:
        process_pdf(pdf_path, verbose)


if __name__ == "__main__":
    main()
