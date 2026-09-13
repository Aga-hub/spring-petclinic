from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

PROD_URL = "http://192.168.56.30:8080"

options = webdriver.ChromeOptions()
options.add_argument("--headless=new")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")

driver = webdriver.Chrome(options=options)

try:
    print(f"Opening {PROD_URL}")
    driver.get(PROD_URL)

    wait = WebDriverWait(driver, 10)

    find_owners = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a[href="/owners/find"]')
        )
    )

    print("Clicking Find Owners")
    find_owners.click()

    last_name_input = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "lastName")
        )
    )

    assert last_name_input.is_displayed()

    print("Selenium PROD test PASSED")

finally:
    driver.quit()
