import os
import time
import json
import re
import fitz  # PyMuPDF
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

def download_bill(consumer_no, password, download_folder):
    options = webdriver.ChromeOptions()
    prefs = {"download.default_directory": download_folder}
    options.add_experimental_option("prefs", prefs)
    driver = webdriver.Chrome(options=options)
    driver.get("https://www.bescom.co.in/bescom/login")
    wait = WebDriverWait(driver, 30)

    # Login
    wait.until(EC.presence_of_element_located((By.NAME, "userId"))).send_keys(consumer_no)
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
    login_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnSubmit")))
    login_button.click()

    # Handle potential pop-up
    try:
        pop_up = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]")))
        pop_up.click()
    except:
        print("No pop-up found")

    # Download bill
    download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download Bill')]")))
    driver.execute_script("arguments[0].click();", download_button)
    time.sleep(5)
    driver.quit()

    # Find the downloaded file
    for file in os.listdir(download_folder):
        if file.endswith(".pdf"):
            return os.path.join(download_folder, file)
    return None

def extract_bill_details(pdf_path):
    doc = fitz.open(pdf_path)
    bill_details = {"Bill Number": "Not Found", "Bill Date": "Not Found", "Due Date": "Not Found", "Amount": "Not Found", "Power Factor": "0"}

    for page in doc:
        text_instances = []
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_instances.append({"text": span["text"], "x": span["bbox"][0], "y": span["bbox"][1]})

        header_positions = {}
        for item in text_instances:
            if "Bill No" in item["text"]:
                header_positions["Bill Number"] = item
            elif "Bill Date" in item["text"]:
                header_positions["Bill Date"] = item
            elif "Due Date" in item["text"]:
                header_positions["Due Date"] = item
            elif "Current Bill Amount" in item["text"]:
                header_positions["Amount"] = item
            elif "Power Factor" in item["text"] or "PF" in item["text"]:
                header_positions["Power Factor"] = item

        for key, header in header_positions.items():
            for item in text_instances:
                if item["y"] > header["y"] and abs(item["x"] - header["x"]) < 50:
                    bill_details[key] = item["text"]
                    break

    return bill_details

# Main execution
consumer_no = "3914302000"
password = "Buildint@123"
download_folder = os.path.join(os.getcwd(), "BESCOM_Bills")
os.makedirs(download_folder, exist_ok=True)

pdf_path = download_bill(consumer_no, password, download_folder)
if pdf_path:
    bill_details = extract_bill_details(pdf_path)
    bill_date = bill_details.get("Bill Date", "unknown").replace("/", "-")
    new_pdf_name = f"{consumer_no}_{bill_date}.pdf"
    new_pdf_path = os.path.join(download_folder, new_pdf_name)
    os.rename(pdf_path, new_pdf_path)

    json_path = new_pdf_path.replace(".pdf", ".json")
    with open(json_path, "w") as json_file:
        json.dump(bill_details, json_file, indent=4)
    print(f"Bill downloaded and extracted: {new_pdf_path}")
else:
    print("Bill download failed.")
