import requests
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")  # Run in headless mode (no browser window)
driver = webdriver.Chrome(options=chrome_options)
import time

def scrape_UC(url: str) -> None:
    driver.get(url)
    time.sleep(3)
    soup  = BeautifulSoup(driver.page_source, "html.parser")



    return


if __name__ == "__main__":
    all_events = []
    scrape_UC("https://www.uc.utoronto.ca/about-uc-connect-us-events")