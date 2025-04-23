import pymupdf  


def pdf_to_txt(input_path, output_path):
    doc = pymupdf.open(input_path)
    output = []

    for page_num in range(doc.page_count):  
        page = doc.load_page(page_num)
        text = page.get_text("text")

        output.append(f"--- PAGE {page_num + 1} ---\n")
        output.append(text.strip() + "\n\n")


    with open(output_path, 'w', encoding='utf-8') as f:
        f.writelines(output)

    print(f"✅ Extracted text page-by-page to: {output_path}")

pdf_to_txt(
    input_path= r"F:\3rd year 2nd sem\IS 2\LexiLearn\26_Using_figures_of_Seech_grade6.pdf",
    output_path="grade6_content.txt"
)

