from selenium import webdriver
import time
import cv2
import pytesseract

driver = webdriver.Chrome()  # Ensure chromedriver.exe is in the project folder
driver.get("https://wss.mahadiscom.in/wss/wss?uiActionName=getViewPayBill")
time.sleep(2)  
driver.quit()

# from selenium.webdriver.common.by import By
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR"

# driver = webdriver.Chrome()
# driver.get("https://wss.mahadiscom.in/wss/wss?uiActionName=getViewPayBill")
# time.sleep(2)

# consumer_input = driver.find_element(By.ID, "consumerNo")  
# consumer_input.send_keys("272510104552")

# captcha_element = driver.find_element(By.ID, "captcha") 
# captcha_element.screenshot("captcha.png")


# image = cv2.imread("captcha.png", cv2.IMREAD_GRAYSCALE)
# image = cv2.threshold(image, 127, 255, cv2.THRESH_BINARY)[1]
# captcha_text = pytesseract.image_to_string(image, config="--psm 6").strip()
# print("Extracted CAPTCHA:", captcha_text)
# submit_button = driver.find_element(By.ID, "lblSubmit") 
# submit_button.click()

# time.sleep(10)  
# driver.quit()

# # captcha fill model was remaining 