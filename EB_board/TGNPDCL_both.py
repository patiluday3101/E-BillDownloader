import os
import time
import json
import re
import fitz  
import pytesseract
import cv2
import numpy as np
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

FOLDER_NAME = "TGNPDCL_Bills"
os.makedirs(FOLDER_NAME, exist_ok=True)

options = webdriver.ChromeOptions()
options.add_experimental_option("detach", True)
prefs = {"download.default_directory": os.path.abspath(FOLDER_NAME)}
options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=options)

consumer_numbers = ["15625373","17995112","16570728","15875076"]

def process_consumer(consumer_number):
   
    driver.get("https://tgnpdcl.com/Menu/KnowYourBillLT")

    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "uscno"))).send_keys(consumer_number)
    driver.find_element(By.ID, "getBill").click()

    pdf_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable((By.ID, "PDF1")))
    driver.execute_script("arguments[0].click();", pdf_button)

    time.sleep(5)  

    pdf_filename = find_latest_pdf(FOLDER_NAME, consumer_number)
    if not pdf_filename:
        print(f"PDF not found for {consumer_number}")
        return

    pdf_path = os.path.join(FOLDER_NAME, pdf_filename)

    bill_details = extract_bill_details(pdf_path)

    if bill_details:
        bill_date = bill_details.get("Bill Date", "unknown").replace("/", "-")
        final_pdf_name = os.path.join(FOLDER_NAME, f"{consumer_number}_{bill_date}.pdf")
        os.rename(pdf_path, final_pdf_name)

        json_path = final_pdf_name.replace(".pdf", ".json")
        with open(json_path, "w", encoding="utf-8") as json_file:
            json.dump(bill_details, json_file, indent=4)

        print(f"Bill saved as: {final_pdf_name}")
        print(f"Extracted details saved in: {json_path}")

def find_latest_pdf(folder, consumer_number):
    files = [f for f in os.listdir(folder) if f.endswith(".pdf")]
    if files:
        return max(files, key=lambda f: os.path.getctime(os.path.join(folder, f)))
    return None

def extract_bill_details(pdf_path):
    
    text = extract_text_from_pdf(pdf_path)

    bill_details = {
        "Bill Number": "N/A",
        "Bill Date": "N/A",
        "Due Date": "N/A",
        "Amount Due": "N/A",
        "Power Factor": "0"
    }

    patterns = {
        "Bill Number": r"Bill\s*No[:\-]?\s*(\d+)",
        "Bill Date": r"(?:Bill\s*Date|Dt)[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|\d{8})",
        "Due Date": r"Due\s*Date[:\-]?\s*(\d{2}[-/]\d{2}[-/]\d{4})",
        "Amount Due": r"Bill\s*Amount[:\-]?\s*([\d,.]+)",
        "Power Factor": r"Power\s*Factor[:\-]?\s*([\d.]+)"
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            bill_details[key] = match.group(1).strip()

    return bill_details

def extract_text_from_pdf(pdf_path):
    doc = fitz.open(pdf_path)
    full_text = ""

    for page in doc:
        text = page.get_text("text")
        if text.strip():
            full_text += text + "\n"

    if not full_text.strip():
        full_text = extract_text_with_ocr(pdf_path)

    return full_text.strip()

def extract_text_with_ocr(pdf_path):
    doc = fitz.open(pdf_path)
    ocr_text = ""

    for page in doc:
        pix = page.get_pixmap()
        img = np.frombuffer(pix.samples, dtype=np.uint8).reshape(pix.h, pix.w, pix.n)
        img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        text = pytesseract.image_to_string(img_gray)
        ocr_text += text + "\n"

    return ocr_text.strip()

for consumer in consumer_numbers:
    process_consumer(consumer)

driver.quit()
