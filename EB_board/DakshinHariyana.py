from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
from datetime import datetime
import pdfplumber
import json

# Credentials
ACCOUNT_NUMBER = "1269340000"
PASSWORD = "Buildint@123"

# Set up the folder for saving the bill and extracted JSON
SAVE_FOLDER = os.path.join(os.getcwd(), "Dakshin Hariyana")

# Create folder if it doesn't exist
if not os.path.exists(SAVE_FOLDER):
    os.makedirs(SAVE_FOLDER)
    print(f"Folder Created: {SAVE_FOLDER}")

# Configure Chrome to download files into the correct folder
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--start-maximized")
prefs = {
    "download.default_directory": SAVE_FOLDER,  
    "download.prompt_for_download": False,  
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,  
}
chrome_options.add_experimental_option("prefs", prefs)
driver = webdriver.Chrome(options=chrome_options)

try:
    # Step 1: Open DHBVN Login Page
    driver.get("https://www.dhbvn.org.in/web/portal/auth")
    time.sleep(3)  

    # Step 2: Enter Account Number
    account_field = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "accountNo"))
    )
    account_field.send_keys(ACCOUNT_NUMBER)

    # Step 3: Enter Password
    password_field = WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "password"))
    )
    password_field.send_keys(PASSWORD)

    # Step 4: Click on Login Button
    login_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.ID, "submit"))
    )
    login_button.click()
    print("Login successful!")

    # Step 5: Click on "Bill Information"
    bill_info_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='bill-information']"))
    )
    bill_info_button.click()
    print("Clicked on 'Bill Information'!")

    # Step 6: Extract Bill Date
    try:
        bill_date_element = WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.XPATH, "//td[contains(text(), 'Bill Date')]/following-sibling::td"))
        )
        bill_date = bill_date_element.text.strip()

        if bill_date:
            bill_date = datetime.strptime(bill_date, "%d-%m-%Y").strftime("%Y-%m-%d")  
        else:
            raise ValueError("Bill Date is empty")

    except Exception as e:
        print("⚠ Could not extract Bill Date, using today's date.")
        bill_date = datetime.today().strftime("%Y-%m-%d")

    print(f"Bill Date: {bill_date}")

    # Step 7: Click on "View Bill"
    view_bill_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[@href='view-bill']"))
    )
    view_bill_button.click()
    print("Clicked on 'View Bill'!")

    # Step 8: Click on "Download PDF"
    download_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//a[contains(@href, 'javascript:displayPdf')]"))
    )
    download_button.click()
    print("Bill download initiated!")

    # Step 9: Wait for the PDF download
    print("Waiting for PDF to be downloaded...")
    timeout = 30  
    start_time = time.time()

    while time.time() - start_time < timeout:
        list_of_files = [f for f in os.listdir(SAVE_FOLDER) if f.endswith(".pdf")]
        if list_of_files:
            break
        time.sleep(2)  

    # Step 10: Rename the Downloaded File
    list_of_files = [os.path.join(SAVE_FOLDER, f) for f in os.listdir(SAVE_FOLDER) if f.endswith(".pdf")]

    if list_of_files:
        latest_file = max(list_of_files, key=os.path.getctime)
        pdf_filename = os.path.join(SAVE_FOLDER, f"{ACCOUNT_NUMBER}_{bill_date}.pdf")

        os.rename(latest_file, pdf_filename)
        print(f"File saved as: {pdf_filename}")
    else:
        print("No PDF file was found in the directory.")
        driver.quit()
        exit()

    # Step 11: Extract Data from the PDF
    bill_details = {"account_number": ACCOUNT_NUMBER}

    try:
        with pdfplumber.open(pdf_filename) as pdf:
            text = "\n".join([page.extract_text() for page in pdf.pages if page.extract_text()])

        # Extracting required details using keywords
        if "Bill No:" in text:
            bill_details["bill_number"] = text.split("Bill No:")[1].split("\n")[0].strip()

        if "Issue Date:" in text:
            bill_details["bill_date"] = text.split("Issue Date:")[1].split("\n")[0].strip()

        if "Due Date:" in text:
            bill_details["due_date"] = text.split("Due Date:")[1].split("\n")[0].strip()

        if "Net Payable Amount on or before Due Date (`):" in text:
            bill_details["amount_due"] = text.split("Net Payable Amount on or before Due Date (`):")[1].split("\n")[0].strip()

        # Save extracted data to JSON file
        json_filename = os.path.join(SAVE_FOLDER, f"{ACCOUNT_NUMBER}_{bill_date}.json")
        with open(json_filename, "w") as json_file:
            json.dump(bill_details, json_file, indent=4)

        print(f"Bill details extracted and saved as: {json_filename}")
        print(json.dumps(bill_details, indent=4))

    except Exception as e:
        print(f"Error extracting data from PDF: {e}")

except Exception as e:
    print("An error occurred:", e)

finally:
    driver.quit()
    print("Automation completed successfully.")