import os
import glob
from pypdf import PdfWriter, PdfReader

input_dir = "./Input/*.pdf"
output_dir = "./Output"

os.makedirs(output_dir, exist_ok=True)

pdf_files = glob.glob(input_dir)

if not pdf_files:
    print("No PDFs found in InputPDFs/")
else:
    for reader_path in pdf_files:
        filename = os.path.basename(reader_path)
        output_path = os.path.join(output_dir, filename)

        writer = PdfWriter()
        writer.clone_reader_document_root(PdfReader(reader_path))
        writer._flatten()

        with open(output_path, "wb") as f:
            writer.write(f)

        os.remove(reader_path)
        print(f"Flattened and moved: {filename}")

    print("Done!")