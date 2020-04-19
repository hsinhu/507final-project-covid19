from selenium import webdriver
import time
from webdriver_manager.chrome import ChromeDriverManager
from bs4 import BeautifulSoup
from selenium.webdriver.chrome.options import Options
import datetime
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement



def fetch_nyt(url, source):
    # today=str(datetime.date.today())
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    driver=webdriver.Chrome(ChromeDriverManager().install(), chrome_options=chrome_options)
    # driver=webdriver.Chrome(ChromeDriverManager().install())

    driver.get(url)
    driver.implicitly_wait(10)
    # time.sleep(20)

    if source == "nyt":
        element = driver.find_element_by_xpath("//div[@id='states']/div/button")
        driver.execute_script("arguments[0].click();", element)
        # driver.find_element_by_xpath("//div[@id='states']/div/button").click()
    else:
        try:
            element = driver.find_element_by_xpath("//div[@id='county']/div/button")
            driver.execute_script("arguments[0].click();", element)
        except:
            print("no click button")
        # element.click()
    driver.implicitly_wait(10)
    # time.sleep(5)
    html = driver.page_source
    driver.close()
    return html
    # soup = BeautifulSoup(html, 'html.parser')


    # print(len(elements))

    # element = elements[1]
    # element.click()



if __name__ == "__main__":
    get_state_cases()