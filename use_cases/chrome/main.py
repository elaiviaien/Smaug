# Improved example from https://www.selenium.dev/selenium/docs/api/py/
import time

from selenium import webdriver

browser = webdriver.Chrome()

browser.get("https://shorturl.at/OELXJ")
time.sleep(100)  # Let the user actually see something!
browser.quit()
