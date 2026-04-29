import sys
import os
import re
import glob
import shutil
from datetime import datetime


INPUT_DIR  = "./Input"
OUTPUT_DIR = "./Output"

FIELD_ORDER = [
    "author", "title", "journal", "booktitle", "year", "volume",
    "number", "pages", "publisher", "address", "editor", "edition",
    "url", "doi", "note", "abstract"
]

SPECIAL_CHARS = {
    "ø": "{\\o}", "Ø": "{\\O}",
    "æ": "{\\ae}", "Æ": "{\\AE}",
    "å": "{\\aa}", "Å": "{\\AA}",
    "ü": '{\\"u}', "Ü": '{\\"U}',
    "ö": '{\\"o}', "Ö": '{\\"O}',
    "ä": '{\\"a}', "Ä": '{\\"A}',
    "é": "{\\'e}", "è": "{\\`e}",
    "ñ": "{\\~n}",
}


def parse_bib_file(filepath: str) -> list[dict]:
    with open(filepath, "r", encoding="utf-8") as f:
        content = f.read()

    entries = []
    pattern = re.compile(r"@(\w+)\s*\{\s*([^,\s]+)\s*,\s*(.*?)\n\}", re.DOTALL)

    for match in pattern.finditer(content):
        entry_type = match.group(1).lower()
        key = match.group(2).strip()
        fields_raw = match.group(3)

        fields = {}
        field_pattern = re.compile(r"(\w+)\s*=\s*(\{(?:[^{}]|\{[^{}]*\})*\}|\"[^\"]*\"|[\w\d]+)\s*,?")
        for fm in field_pattern.finditer(fields_raw):
            field_name = fm.group(1).lower()
            field_value = fm.group(2).strip()
            if field_value.startswith('"') and field_value.endswith('"'):
                field_value = "{" + field_value[1:-1] + "}"
            fields[field_name] = field_value

        entries.append({"type": entry_type, "key": key, "fields": fields})

    return entries


def generate_key(fields: dict, existing_keys: set) -> str:
    author = fields.get("author", "{Unknown}")
    year = fields.get("year", "{0000}").strip("{}")
    title = fields.get("title", "{Untitled}").strip("{}")

    author_clean = author.strip("{}")
    first_author = author_clean.split(" and ")[0].strip()
    if "," in first_author:
        last_name = first_author.split(",")[0].strip()
    else:
        parts = first_author.split()
        last_name = parts[-1] if parts else "Unknown"
    last_name = re.sub(r"[^a-zA-Z]", "", last_name)

    stop_words = {"a", "an", "the", "of", "in", "on", "for", "and", "or", "to", "with"}
    title_words = [w for w in re.split(r"\W+", title.lower()) if w and w not in stop_words]
    first_word = title_words[0].capitalize() if title_words else "Untitled"

    base_key = f"{last_name}{year}{first_word}"
    key = base_key
    suffix = 97  # 'a'
    while key in existing_keys:
        key = base_key + chr(suffix)
        suffix += 1

    return key


def fix_special_chars(value: str) -> str:
    for char, replacement in SPECIAL_CHARS.items():
        value = value.replace(char, replacement)
    return value


def format_entry(entry: dict) -> str:
    lines = [f"@{entry['type']}{{{entry['key']},"]
    written = set()
    ordered_fields = [(f, entry["fields"][f]) for f in FIELD_ORDER if f in entry["fields"]]
    remaining_fields = [(f, v) for f, v in entry["fields"].items() if f not in FIELD_ORDER]

    for field, value in ordered_fields + remaining_fields:
        fixed_value = fix_special_chars(value)
        lines.append(f"    {field:<12} = {fixed_value},")
        written.add(field)

    lines.append("}")
    return "\n".join(lines)


def remove_duplicates(entries: list[dict]) -> tuple[list[dict], int]:
    seen_keys = set()
    seen_dois = set()
    unique = []
    removed = 0

    for entry in entries:
        doi = entry["fields"].get("doi", "").strip("{} ").lower()
        key = entry["key"]
        if key in seen_keys or (doi and doi in seen_dois):
            removed += 1
            continue
        seen_keys.add(key)
        if doi:
            seen_dois.add(doi)
        unique.append(entry)

    return unique, removed


def find_unused_entries(entries: list[dict], tex_dir: str) -> list[str]:
    tex_files = glob.glob(os.path.join(tex_dir, "**/*.tex"), recursive=True)
    all_tex_content = ""
    for tf in tex_files:
        with open(tf, "r", encoding="utf-8") as f:
            all_tex_content += f.read()

    return [e["key"] for e in entries if e["key"] not in all_tex_content]


def process_bib(bib_file: str, check_dir: str | None):
    filename = os.path.basename(bib_file)
    output_file = os.path.join(OUTPUT_DIR, filename)

    print(f"\nProcessing {filename}...")
    entries = parse_bib_file(bib_file)
    print(f"  Found {len(entries)} entries")

    entries, removed = remove_duplicates(entries)
    if removed:
        print(f"  Removed {removed} duplicate(s)")

    existing_keys = set()
    for entry in entries:
        new_key = generate_key(entry["fields"], existing_keys)
        if new_key != entry["key"]:
            print(f"  Key: {entry['key']} → {new_key}")
            entry["key"] = new_key
        existing_keys.add(entry["key"])

    if check_dir:
        unused = find_unused_entries(entries, check_dir)
        if unused:
            print(f"  ⚠ Unused entries ({len(unused)}):")
            for key in unused:
                print(f"    - {key}")
        else:
            print("  ✓ All entries are cited in your .tex files")

    # Backup original
    backup = bib_file.replace(".bib", f"_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.bib")
    shutil.copy(bib_file, backup)
    print(f"  Backup saved to {backup}")

    os.makedirs(OUTPUT_DIR, exist_ok=True)
    output = "\n\n".join(format_entry(e) for e in entries) + "\n"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(output)

    print(f"  ✓ Written to {output_file}")


def main():
    check_mode = "--check" in sys.argv
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    check_dir = args[0] if check_mode and args else None

    os.makedirs(INPUT_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    bib_files = glob.glob(os.path.join(INPUT_DIR, "*.bib"))
    if not bib_files:
        print(f"No .bib files found in {INPUT_DIR}/")
        sys.exit(1)

    print(f"Found {len(bib_files)} .bib file(s) in {INPUT_DIR}/")
    for bib_file in bib_files:
        process_bib(bib_file, check_dir)

    print("\nDone!")


if __name__ == "__main__":
    main()
