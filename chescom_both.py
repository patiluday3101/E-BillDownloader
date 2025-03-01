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
    driver.get("https://cescmysore.in/cesc/login")
    wait = WebDriverWait(driver, 30)

    # Login
    wait.until(EC.presence_of_element_located((By.NAME, "userId"))).send_keys(consumer_no)
    wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys(password)
    login_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnSubmit"))).click()

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

def extract_bill_details(pdf_path, output_json):
    doc = fitz.open(pdf_path)

    bill_details = {
        "Bill Number": "Not Found",
        "Bill Date": "Not Found",
        "Due Date": "Not Found",
        "Amount": "Not Found",
        "Power Factor": "0"  # Default to 0 if not found
    }

    for page in doc:
        text_instances = []
        for block in page.get_text("dict")["blocks"]:
            if "lines" in block:
                for line in block["lines"]:
                    for span in line["spans"]:
                        text_instances.append({
                            "text": span["text"].strip(),
                            "x": span["bbox"][0],  # X-coordinate
                            "y": span["bbox"][1]   # Y-coordinate (top of the text)
                        })

        # Identify header positions
        header_positions = {}
        for item in text_instances:
            if "Bill No" in item["text"]:
                header_positions["Bill Number"] = item
            elif "Billing Period" in item["text"]:
                header_positions["Billing Period"] = item
            elif "Due Date" in item["text"]:
                header_positions["Due Date"] = item
            elif "Current Bill Amount" in item["text"]:  
                header_positions["Amount"] = item
            elif "Power Factor" in item["text"] or "PF" in item["text"]:
                header_positions["Power Factor"] = item

        # Extract values below headers
        for key, header in header_positions.items():
            for item in text_instances:
                if item["y"] > header["y"] and abs(item["x"] - header["x"]) < 50:
                    bill_details[key] = item["text"]
                    break

        # Extract Bill Date (First date from Billing Period)
        if "Billing Period" in bill_details and bill_details["Billing Period"] != "Not Found":
            date_match = re.findall(r'\d{2}-\d{2}-\d{4}', bill_details["Billing Period"])
            if len(date_match) > 1:
                bill_details["Bill Date"] = date_match[1]

        # Extract Net Payable Amount (if found)
        for item in text_instances:
            if "Net Payable Amount" in item["text"]:
                amount_index = text_instances.index(item) + 1  # Get next item
                if amount_index < len(text_instances):
                    bill_details["Amount"] = text_instances[amount_index]["text"].replace(",", "").strip()
                    break

        # Extract Power Factor (correctly)
        if "Power Factor" in header_positions:
            pf_y = header_positions["Power Factor"]["y"]  # Y-coordinate of Power Factor label
            pf_candidates = []
            
            for item in text_instances:
                if item["y"] >= pf_y and abs(item["x"] - header_positions["Power Factor"]["x"]) < 80:
                    pf_match = re.findall(r'\b\d+\.\d+\b', item["text"])  # Find decimal values
                    if pf_match:
                        pf_candidates.extend(pf_match)

            if pf_candidates:
                bill_details["Power Factor"] = pf_candidates[0]  # Pick first valid PF value
            else:
                bill_details["Power Factor"] = "0"  # Default to 0 if not found

        # Ensure Power Factor is a valid numeric value (avoid text like "Disconnection")
        if not re.match(r'^\d+\.\d+$', bill_details["Power Factor"]):
            bill_details["Power Factor"] = "0"

    # Remove "Billing Period" from the output since it's not needed
    bill_details.pop("Billing Period", None)

    # Save the extracted details
    with open(output_json, 'w') as json_file:
        json.dump(bill_details, json_file, indent=4)

    print("Extracted details saved to", output_json)
    return bill_details

# Main execution
consumer_no = "9093050000"
password = "Buildint@123"
download_folder = os.path.join(os.getcwd(), "CESCOM_Bills")
os.makedirs(download_folder, exist_ok=True)
pdf_path = download_bill(consumer_no, password, download_folder)
if pdf_path:
    # Step 2: Extract bill details from the downloaded PDF
    bill_details = extract_bill_details(pdf_path, "temp.json")

    # Step 3: Rename the JSON and PDF based on the bill date
    bill_date = bill_details.get("Bill Date", "unknown").replace("/", "-")
    json_name = f"{consumer_no}_{bill_date}.json"
    output_json = os.path.join(download_folder, json_name)
    extract_bill_details(pdf_path, output_json)

    new_pdf_name = f"{consumer_no}_{bill_date}.pdf"
    new_pdf_path = os.path.join(download_folder, new_pdf_name)
    os.rename(pdf_path, new_pdf_path)

    print(f"Bill downloaded and extracted: {new_pdf_path}")
else:
    print("Bill download failed.")
