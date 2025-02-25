import os
import time
import cv2
import pytesseract
import base64
import json
import re
import pdfplumber
from selenium import webdriver
from selenium.webdriver.common.by import By

# Set up Tesseract path
pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"


def ocr_with_methods(img):
    """Applies OCR techniques to extract text from an image."""
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(img, cv2.MORPH_OPEN, kernel)
    text = pytesseract.image_to_string(morph, config="--psm 6").strip()
    return text

def extract_bill_details(pdf_path):
    """Extracts bill details from the PDF and returns them as a dictionary."""
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    
    bill_details = {
        "Invoice Number": re.search(r"BILL NO.*?(\d+)", text, re.IGNORECASE).group(1) if re.search(r"BILL NO.*?(\d+)", text, re.IGNORECASE) else "N/A",
        "Billing Date": re.search(r"देयक िदनांक:\s*(\d{2}-[A-Z]{3}-\d{2})", text).group(1) if re.search(r"देयक िदनांक:\s*(\d{2}-[A-Z]{3}-\d{2})", text) else "N/A",
        "Due Date": re.search(r"देय िदनांक:\s*(\d{2}-[A-Z]{3}-\d{2})", text).group(1) if re.search(r"देय िदनांक:\s*(\d{2}-[A-Z]{3}-\d{2})", text) else "N/A",
        "Amount Due": re.search(r"देयक रक्कम रु:\s*([\d,.]+)", text).group(1) if re.search(r"देयक रक्कम रु:\s*([\d,.]+)", text) else "N/A",
        "Power Factor": "0"
    }
    return bill_details

def main(consumer_no):
    driver = webdriver.Chrome()
    driver.get("https://wss.mahadiscom.in/wss/wss?uiActionName=getViewPayBill")
    time.sleep(2)

    driver.find_element(By.ID, "consumerNo").send_keys(consumer_no)
    captcha_element = driver.find_element(By.ID, "captcha")
    captcha_element.screenshot("captcha.png")
    
    image = cv2.imread("captcha.png", cv2.IMREAD_GRAYSCALE)
    captcha_text = ocr_with_methods(image)
    
    driver.find_element(By.ID, "txtInput").send_keys(captcha_text)
    driver.find_element(By.ID, "lblSubmit").click()
    driver.find_element(By.ID, "Img1").click()
    driver.find_element(By.ID, "lbllTitle").click()
    time.sleep(10)
    
    pdf_data = base64.b64decode(driver.execute_cdp_cmd("Page.printToPDF", {})['data'])
    driver.quit()
    
    temp_pdf = "temp_bill.pdf"
    with open(temp_pdf, "wb") as f:
        f.write(pdf_data)
    
    bill_details = extract_bill_details(temp_pdf)
    bill_date = bill_details["Billing Date"].replace("/", "-")
    folder_name = "Mahavitaran_Bills"
    os.makedirs(folder_name, exist_ok=True)
    
    pdf_filename = os.path.join(folder_name, f"{consumer_no}_{bill_date}.pdf")
    json_filename = os.path.join(folder_name, f"{consumer_no}_{bill_date}.json")
    
    os.rename(temp_pdf, pdf_filename)
    with open(json_filename, "w", encoding="utf-8") as json_file:
        json.dump(bill_details, json_file, indent=4, ensure_ascii=False)
    
    print(f"Bill saved: {pdf_filename}")
    print(f"JSON saved: {json_filename}")

if __name__ == "__main__":
    main("272510104552")
