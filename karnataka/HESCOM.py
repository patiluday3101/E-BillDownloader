from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Initialize WebDriver
driver = webdriver.Chrome()
driver.get("https://hescom.co.in/hescom/login")

wait = WebDriverWait(driver, 30)

# Enter Login Credentials
wait.until(EC.presence_of_element_located((By.NAME, "userId"))).send_keys("4589657120")
wait.until(EC.presence_of_element_located((By.NAME, "password"))).send_keys("Buildint@123")

# Click Login Button
login_button = wait.until(EC.element_to_be_clickable((By.NAME, "btnSubmit")))
login_button.click()

# Handle Pop-up if it appears
try:
    pop_up = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Close')]")))
    pop_up.click()
except:
    print("No pop-up found")

# Find the Download Bill button
download_button = wait.until(EC.element_to_be_clickable((By.XPATH, "//button[contains(text(), 'Download Bill')]")))

# Scroll and Click
driver.execute_script("arguments[0].scrollIntoView();", download_button)
driver.execute_script("arguments[0].click();", download_button)

import time
time.sleep(5)  
driver.quit()
