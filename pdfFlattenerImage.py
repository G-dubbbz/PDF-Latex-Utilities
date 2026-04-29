import os
import glob
from pdf2image import convert_from_path
from PIL import Image
 
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
 
        # Render each page to image (bakes in all form field values visually)
        pages = convert_from_path(reader_path, dpi=200)
 
        # Save all pages back as a single flat PDF
        if len(pages) == 1:
            pages[0].save(output_path, "PDF", resolution=200)
        else:
            pages[0].save(
                output_path, "PDF", resolution=200,
                save_all=True, append_images=pages[1:]
            )
 
        os.remove(reader_path)
        print(f"Flattened and moved: {filename}")
 
    print("Done!")