from selenium import webdriver
import time
import cv2
import pytesseract
import requests
from selenium.webdriver.common.by import By

pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

driver = webdriver.Chrome()
driver.get("https://bps.dgvcl.co.in/BillDetail/index.php")
time.sleep(2)

consumer_input = driver.find_element(By.ID, "consumerno")
consumer_input.send_keys("45951040892")

captcha_element = driver.find_element(By.ID, "captcha")
captcha_element.screenshot("captcha.png")

image = cv2.imread("captcha.png", cv2.IMREAD_GRAYSCALE)

def ocr_with_methods(img):
    results = {}
    
    simple_thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)[1]
    text_simple = pytesseract.image_to_string(simple_thresh, config="--psm 7").strip()
    results["Simple"] = text_simple
    
    blurred = cv2.GaussianBlur(img, (3, 3), 0)
    adaptive_thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    text_adaptive = pytesseract.image_to_string(adaptive_thresh, config="--psm 7").strip()
    results["Adaptive"] = text_adaptive
    
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (2, 2))
    morph = cv2.morphologyEx(adaptive_thresh, cv2.MORPH_OPEN, kernel)
    text_morph = pytesseract.image_to_string(morph, config="--psm 7").strip()
    results["Morphological"] = text_morph
    
    inverted = cv2.bitwise_not(img)
    inverted_thresh = cv2.threshold(inverted, 127, 255, cv2.THRESH_BINARY)[1]
    text_inverted = pytesseract.image_to_string(inverted_thresh, config="--psm 7").strip()
    results["Inverted"] = text_inverted
    
    return results

results = ocr_with_methods(image)

for method, text in results.items():
    print(f"{method} method OCR output: {text}")

captcha_text = results["Morphological"]
print("Using CAPTCHA text:", captcha_text)

captcha_input = driver.find_element(By.ID, "verificationcode")
captcha_input.send_keys(captcha_text)

submit_button = driver.find_element(By.ID, "btnSearch")
submit_button.click()
# final_submit= driver.find_element(By.ID, "Img1") 
# final_submit.click()



# pdf_link = driver.find_element(By.ID, "lbllTitle")
# pdf_link.click()





time.sleep(10)
driver.quit()
