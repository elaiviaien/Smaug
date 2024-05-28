# Improved example from https://www.selenium.dev/selenium/docs/api/py/
import time

from selenium import webdriver

browser = webdriver.Chrome()
print("Opening the browser...")
browser.get("https://shorturl.at/OELXJ")
time.sleep(149)  # Let the user actually see something!
browser.quit()
