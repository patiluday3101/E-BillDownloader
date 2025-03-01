import os
import re
import json
import time
import base64
import cv2
import pytesseract
import fitz  
from pdf2image import convert_from_path
from selenium import webdriver  # for set up the webdriver refer this like - https://www.youtube.com/watch?v=jglQpvPI58A
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe" 
# for setup the pytesseract refer this like - https://www.youtube.com/watch?v=HNCypVfeTdw&t=149s
OUTPUT_DIR = "Dakshin Gujrat"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def solve_captcha(driver):
    """Solves CAPTCHA using OCR and retries if incorrect."""
    while True:
        captcha_element = driver.find_element(By.ID, "captcha")
        captcha_element.screenshot("captcha.png")
        image = cv2.imread("captcha.png", cv2.IMREAD_GRAYSCALE)
        captcha_text = pytesseract.image_to_string(image, config="--psm 7").strip()
        
        captcha_input = driver.find_element(By.ID, "verificationcode")
        captcha_input.clear()
        captcha_input.send_keys(captcha_text)
        
        driver.find_element(By.ID, "btnSearch").click()
        time.sleep(2)  # Give time for validation
        
        if len(driver.find_elements(By.XPATH, "//a[contains(text(),'Click here to view Bill')]") )> 0:
            return True
        print("Retrying CAPTCHA...")
        driver.find_element(By.ID, "consumerno").clear()
        driver.find_element(By.ID, "consumerno").send_keys(consumer_no)

def download_bill(consumer_no):
    """Downloads bill PDF for a given consumer number and returns the file path."""
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(options=options)
    driver.get("https://bps.dgvcl.co.in/BillDetail/index.php")
    time.sleep(2)
    
    # Enter consumer number
    driver.find_element(By.ID, "consumerno").send_keys(consumer_no)
    
    # Solve CAPTCHA correctly before proceeding
    if not solve_captcha(driver):
        driver.quit()
        return None
    
    try:
        bill_button = WebDriverWait(driver, 15).until(
            EC.element_to_be_clickable((By.XPATH, "//a[contains(text(),'Click here to view Bill')]") )
        )
        bill_button.click()
    except Exception as e:
        print("Error finding bill button:", e)
        driver.quit()
        return None
    
    # Switch to bill tab and save as PDF
    time.sleep(5)
    if len(driver.window_handles) > 1:
        driver.switch_to.window(driver.window_handles[1])
    
    pdf_name = f"{consumer_no}_temp.pdf"
    pdf_path = os.path.join(OUTPUT_DIR, pdf_name)
    
    try:
        chrome_devtools = driver.execute_cdp_cmd("Page.printToPDF", {})
        pdf_data = base64.b64decode(chrome_devtools['data'])
        with open(pdf_path, "wb") as f:
            f.write(pdf_data)
    except Exception as e:
        print("Error saving PDF:", e)
        driver.quit()
        return None
    
    driver.quit()
    return pdf_path

def extract_text_from_pdf(pdf_path):
    """Extracts text from a PDF using PyMuPDF. If it fails, uses OCR."""
    text = ""
    try:
        doc = fitz.open(pdf_path)
        for page in doc:
            text += page.get_text("text") + "\n"
        
        if not text.strip():
            images = convert_from_path(pdf_path)
            text = " ".join([pytesseract.image_to_string(img) for img in images])
    except Exception as e:
        print(f"Error extracting text: {e}")
    return text

def extract_bill_details(pdf_path):
    text = extract_text_from_pdf(pdf_path)
    
    bill_no_match = re.search(r"Bill\s*No[:\-]?\s*([\d/]+)", text, re.IGNORECASE)
    bill_date_match = re.search(r"Bill\s*Date[:\-]?\s*([\d\-]+)", text, re.IGNORECASE)
    due_date_match = re.search(r"Due\s*Date[:\-]?\s*([\d\-]+)", text, re.IGNORECASE)
    amount_due_match = re.search(r"(?:Amount Due|ભરવાપાત્ર રકમ)\s*[:\-]?\s*Rs\.?\s*([\d,]+\.\d+)", text, re.IGNORECASE)
    
    bill_date = bill_date_match.group(1).strip() if bill_date_match else "Unknown"
    due_date = due_date_match.group(1).strip() if due_date_match else "Not found"
    
    bill_details = {
        "Bill Number": bill_no_match.group(1).strip() if bill_no_match else "Not found",
        "Bill Date": bill_date,
        "Due Date": due_date,
        "Amount Due": amount_due_match.group(1).replace(",", "").strip() if amount_due_match else "Not found"
    }
    
    return bill_details, bill_date

def main(consumer_no):
    pdf_path = download_bill(consumer_no)
    if not pdf_path:
        print("Bill download failed.")
        return
    
    details, bill_date = extract_bill_details(pdf_path)
    new_pdf_name = f"{consumer_no}_{bill_date}.pdf"
    new_pdf_path = os.path.join(OUTPUT_DIR, new_pdf_name)
    os.rename(pdf_path, new_pdf_path)
    
    json_path = os.path.join(OUTPUT_DIR, f"{consumer_no}_{bill_date}.json")
    with open(json_path, "w", encoding="utf-8") as json_file:
        json.dump(details, json_file, indent=4, ensure_ascii=False)
    
    print(f"Bill saved as: {new_pdf_path}")
    print(f"Details saved as: {json_path}")

if __name__ == "__main__":
    consumer_no = "13219042481"
    main(consumer_no)

# 45951040892
# 42803011433
# 13219042481
# 03801156788
# 13502257817
# 13234350418
# 13219045243
# 08602047703
# 40243011415
# 40243011407