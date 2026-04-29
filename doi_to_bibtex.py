import sys
import re
import os
import urllib.request
import urllib.error

INPUT_DIR  = "./Input"
OUTPUT_DIR = "./Output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "references.bib")
EMAIL = "your@email.com"  # Polite pool: faster API responses from CrossRef


def fetch_bibtex(doi: str) -> str | None:
    doi = doi.strip().removeprefix("https://doi.org/").removeprefix("http://doi.org/")
    url = f"https://doi.org/{doi}"
    req = urllib.request.Request(
        url,
        headers={
            "Accept": "application/x-bibtex",
            "User-Agent": f"doi_to_bibtex/1.0 (mailto:{EMAIL})",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as response:
            return response.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"  ✗ HTTP {e.code} for DOI: {doi}")
        return None
    except urllib.error.URLError as e:
        print(f"  ✗ Network error for DOI {doi}: {e.reason}")
        return None


def clean_bibtex(raw: str) -> str:
    return raw.strip() + "\n"


def already_exists(bibtex: str, output_file: str) -> bool:
    match = re.search(r"@\w+\{(\S+),", bibtex)
    if not match:
        return False
    key = match.group(1).rstrip(",")
    if not os.path.exists(output_file):
        return False
    with open(output_file, "r", encoding="utf-8") as f:
        return key in f.read()


def append_to_bib(bibtex: str, output_file: str):
    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    with open(output_file, "a", encoding="utf-8") as f:
        f.write("\n" + clean_bibtex(bibtex))


def process_doi(doi: str):
    doi = doi.strip()
    if not doi or doi.startswith("#"):
        return
    print(f"Fetching: {doi}")
    bibtex = fetch_bibtex(doi)
    if not bibtex:
        return
    if already_exists(bibtex, OUTPUT_FILE):
        match = re.search(r"@\w+\{(\S+),", bibtex)
        key = match.group(1).rstrip(",") if match else "?"
        print(f"  ↷ Already in references.bib: {key}")
        return
    append_to_bib(bibtex, OUTPUT_FILE)
    match = re.search(r"@\w+\{(\S+),", bibtex)
    key = match.group(1).rstrip(",") if match else "?"
    print(f"  ✓ Added: {key}")


def main():
    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    if len(sys.argv) == 1:
        # Interactive mode
        print("DOI to BibTeX — enter DOIs one per line, empty line to finish:")
        while True:
            doi = input("  DOI: ").strip()
            if not doi:
                break
            process_doi(doi)
    elif len(sys.argv) == 2:
        arg = sys.argv[1]
        if os.path.isfile(arg):
            with open(arg, "r", encoding="utf-8") as f:
                dois = f.readlines()
            count = len([d for d in dois if d.strip() and not d.startswith("#")])
            print(f"Processing {count} DOIs from {arg}...")
            for doi in dois:
                process_doi(doi)
        else:
            process_doi(arg)
    else:
        print("Usage:")
        print("  python3 doi_to_bibtex.py                        # interactive")
        print("  python3 doi_to_bibtex.py 10.xxxx/xxxxx          # single DOI")
        print("  python3 doi_to_bibtex.py ./Input/dois.txt       # file with one DOI per line")

    print(f"\nDone! Results saved to {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
