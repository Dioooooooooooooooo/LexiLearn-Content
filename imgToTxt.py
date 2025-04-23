import os
from pdf2image import convert_from_path
import pytesseract
from PIL import Image
import cv2
import numpy as np



def extract_text_with_pdf2image(pdf_path, output_txt_path=None):
    try:
        pages = convert_from_path(pdf_path, 300, poppler_path=r'C:\Users\admin\Downloads\Release-24.08.0-0\poppler-24.08.0\Library\bin')
    except Exception as e:
        print(f"Error converting PDF to images: {e}")
        return None
    
    full_text = ""
    
    for i, page in enumerate(pages):
        try:
            open_cv_image = np.array(page) 
            open_cv_image = open_cv_image[:, :, ::-1].copy() 
            
            page.save(f"page_{i+1}.png")
            
            gray = cv2.cvtColor(open_cv_image, cv2.COLOR_BGR2GRAY)
            
            pil_gray = Image.fromarray(gray)
            page_text = pytesseract.image_to_string(
                pil_gray, 
                config='--psm 6 --oem 3'
            )
            
            if len(page_text.strip()) < 50:
                binary = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                              cv2.THRESH_BINARY, 11, 2)
                
                cv2.imwrite(f"binary_page_{i+1}.png", binary)
                
                pil_binary = Image.fromarray(binary)
                page_text = pytesseract.image_to_string(
                    pil_binary, 
                    config='--psm 6 --oem 3'
                )
            
            full_text += f"--- Page {i+1} ---\n{page_text}\n\n"
            print(f"Processed page {i+1}")
            
        except Exception as e:
            print(f"Error on page {i+1}: {e}")
    
    if output_txt_path and full_text:
        with open(output_txt_path, "w", encoding="utf-8") as text_file:
            text_file.write(full_text)
        print(f"Text extracted and saved to {output_txt_path}")
    
    return full_text

extract_text_with_pdf2image(r"LexiLearn/The_Forgiving_Crocodile_Deshery_Gabatino.pdf", r"LexiLearn/ExtractedText.txt")