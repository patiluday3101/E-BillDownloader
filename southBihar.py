# from selenium import webdriver
# import time
# import cv2
# import pytesseract
# import requests
# from selenium.webdriver.common.by import By

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# driver = webdriver.Chrome()
# driver.get("https://www.sbpdcl.co.in/(S(2iy0w0lt5ka0e4mqykw4iml1))/frmQuickBillPaymentAll.aspx")
# time.sleep(2)

# consumer_input = driver.find_element(By.ID, "MainContent_txtCANO")
# consumer_input.send_keys("108770574")

# submit_button = driver.find_element(By.ID, "MainContent_btnSubmit")
# submit_button.click()

# submit_button = driver.find_element(By.ID, "MainContent_lnkView1")
# submit_button.click()



# time.sleep(10)
# driver.quit()

from selenium import webdriver
import time
import cv2
import pytesseract
import requests
from selenium.webdriver.common.by import By

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

consumer_numbers = ["108770574","226108860490","108694572","108508837","108571785","108694461","108770574","236510069436"]  

driver = webdriver.Chrome()

def process_consumer(consumer_number):
    driver.get("https://www.sbpdcl.co.in/(S(2iy0w0lt5ka0e4mqykw4iml1))/frmQuickBillPaymentAll.aspx")
    time.sleep(2)
    
    consumer_input = driver.find_element(By.ID, "MainContent_txtCANO")
    consumer_input.send_keys(consumer_number)
    
    submit_button = driver.find_element(By.ID, "MainContent_btnSubmit")
    submit_button.click()
    
    try:
        view_button = driver.find_element(By.ID, "MainContent_lnkView1")
        view_button.click()
        time.sleep(5)  
    except:
        print(f"No bill found for consumer number {consumer_number}")

for consumer in consumer_numbers:
    process_consumer(consumer)

driver.quit()

# from selenium import webdriver
# import time
# import os
# import cv2
# import pytesseract
# import requests
# from selenium.webdriver.common.by import By

# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

# consumer_numbers = ["108770574"] # , "244210369306", "108716640","108717642","226108860490","108694572","108508837","108571785","108694461","108770574","236510069436"]  

# bill_folder = "SouthBihar_bill"
# os.makedirs(bill_folder, exist_ok=True)

# driver = webdriver.Chrome()

# def process_consumer(consumer_number):
#     driver.get("https://www.sbpdcl.co.in/(S(2iy0w0lt5ka0e4mqykw4iml1))/frmQuickBillPaymentAll.aspx")
#     time.sleep(2)
    
#     consumer_input = driver.find_element(By.ID, "MainContent_txtCANO")
#     consumer_input.send_keys(consumer_number)
    
#     submit_button = driver.find_element(By.ID, "MainContent_btnSubmit")
#     submit_button.click()
    
#     try:
#         view_button = driver.find_element(By.ID, "MainContent_lnkView1")
#         view_button.click()
#         time.sleep(5)  
        
    
#         pdf_url = driver.current_url  
#         response = requests.get(pdf_url)
#         pdf_path = os.path.join(bill_folder, f"{consumer_number}.pdf")
#         with open(pdf_path, "wb") as file:
#             file.write(response.content)
#         print(f"Bill saved: {pdf_path}")
        
#     except:
#         print(f"No bill found for consumer number {consumer_number}")

# for consumer in consumer_numbers:
#     process_consumer(consumer)

# driver.quit()


