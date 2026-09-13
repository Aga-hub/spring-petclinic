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
            (By.CSS_SELECTOR, 'a[href$="/owners/find"]')
        )
    )

    print("Found link:", find_owners.text)
    print("Link target:", find_owners.get_attribute("href"))

    find_owners.click()

    wait.until(
        EC.url_contains("/owners/find")
    )

    last_name = wait.until(
        EC.visibility_of_element_located(
            (By.NAME, "lastName")
        )
    )

    assert last_name.is_displayed()

    print("Current URL:", driver.current_url)
    print("Selenium PROD test PASSED")

except Exception:
    print("FAILED on URL:", driver.current_url)
    print("Page title:", driver.title)

    driver.save_screenshot("selenium-failure.png")

    with open("selenium-page.html", "w", encoding="utf-8") as f:
        f.write(driver.page_source)

    raise

finally:
    driver.quit()
