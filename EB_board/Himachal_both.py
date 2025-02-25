from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pdfplumber
import requests
import time
import os
import re
import json

def setup_driver():
    chrome_options = webdriver.ChromeOptions()
    download_dir = os.path.join(os.getcwd(), "Himachal")
    os.makedirs(download_dir, exist_ok=True)
    prefs = {"download.default_directory": download_dir,  
             "plugins.always_open_pdf_externally": True}  
    chrome_options.add_experimental_option("prefs", prefs)
    return webdriver.Chrome(options=chrome_options), download_dir

def extract_bill_details(pdf_path):
    with pdfplumber.open(pdf_path) as pdf:
        text = "\n".join(page.extract_text() for page in pdf.pages if page.extract_text())
    
    bill_details = {
        "Bill Issue Date": re.search(r"(\d{2}\.\d{2}\.\d{4})", text).group(1) if re.search(r"(\d{2}\.\d{2}\.\d{4})", text) else "N/A",
        "Bill Number": re.search(r"Bill No\.\s*(\d+)", text).group(1) if re.search(r"Bill No\.\s*(\d+)", text) else "N/A",
        "Cash/Draft Due Date": re.search(r"Cash/Draft Due Date\s*(\d{2}\.\d{2}\.\d{4})", text).group(1) if re.search(r"Cash/Draft Due Date\s*(\d{2}\.\d{2}\.\d{4})", text) else "N/A",
        "Total Amount Payable": re.search(r"Total Amount Payable.?(\d{1,6}\.\d{2})", text).group(1) if re.search(r"Total Amount Payable.?(\d{1,6}\.\d{2})", text) else "N/A",
        "Power Factor": re.search(r"Power Factor\s*(\d+\.\d+)", text).group(1) if re.search(r"Power Factor\s*(\d+\.\d+)", text) else "0"
    }
    return bill_details

def wait_for_download(directory, timeout=30):
    start_time = time.time()
    while time.time() - start_time < timeout:
        files = [f for f in os.listdir(directory) if f.endswith(".pdf")]
        if files:
            return os.path.join(directory, files[0])
        time.sleep(1)
    return None

def process_consumer(consumer_number, driver, download_dir):
    try:
        driver.get("https://app.hpseb.in/BillViewApp/")
        time.sleep(3)
        
        consumer_input = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "conID"))
        )
        consumer_input.send_keys(consumer_number)

        submit_button = driver.find_element(By.XPATH, "//input[@type='submit' and @value='Search']")
        submit_button.click()
        time.sleep(3)

        view_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.ID, "imgIpDVBill"))
        )
        view_button.click()
        time.sleep(5)

        downloaded_pdf = wait_for_download(download_dir)
        if downloaded_pdf:
            bill_data = extract_bill_details(downloaded_pdf)
            bill_issue_date = bill_data["Bill Issue Date"].replace(".", "-")  
            
            pdf_filename = os.path.join(download_dir, f"{consumer_number}_{bill_issue_date}.pdf")
            json_filename = os.path.join(download_dir, f"{consumer_number}_{bill_issue_date}.json")
            
            os.rename(downloaded_pdf, pdf_filename)
            print(f"PDF saved as {pdf_filename}")
            
            with open(json_filename, "w", encoding="utf-8") as json_file:
                json.dump(bill_data, json_file, indent=4, ensure_ascii=False)
            print(f"JSON saved: {json_filename}")
        else:
            print(f"PDF download failed for {consumer_number}")

    except Exception as e:
        print(f"Error processing {consumer_number}: {e}")

# Main execution
driver, download_dir = setup_driver()
consumer_numbers = ["100002173774"]
for consumer in consumer_numbers:
    process_consumer(consumer, driver, download_dir)
driver.quit()
