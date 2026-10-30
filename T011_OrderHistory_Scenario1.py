
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from getpass import getpass

# Ask for the registered account details before starting the test
email = input("Enter registered test account email: ")
password = getpass("Enter test account password: ")

# Open Microsoft Edge and allow time for the pages to load
driver = webdriver.Edge()
driver.maximize_window()
wait = WebDriverWait(driver, 20)

try:
    # Open the customer login page
    driver.get(
        "https://opencart.abstracta.us/index.php?route=account/login"
    )

    # Enter the registered customer's email address
    email_field = wait.until(
        EC.visibility_of_element_located((By.ID, "input-email"))
    )
    email_field.send_keys(email)

    # Enter the account password
    password_field = driver.find_element(By.ID, "input-password")
    password_field.send_keys(password)

    # Click Login to access the customer account
    login_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[type='submit'][value='Login']")
        )
    )
    login_button.click()

    # Check that the customer was successfully logged in
    wait.until(EC.url_contains("route=account/account"))

    print("PASS: Registered customer logged in successfully")

    # Open Order History while still logged into the account
    driver.get(
        "https://opencart.abstracta.us/index.php?route=account/order"
    )

    content = wait.until(
        EC.visibility_of_element_located((By.ID, "content"))
    )

    # Check that the browser opened the Order History URL
    assert "route=account/order" in driver.current_url, (
        "Order History URL was not opened"
    )

    # Make sure the customer was not redirected back to Login
    assert "route=account/login" not in driver.current_url, (
        "Customer was redirected to the Login page"
    )

    print("PASS: Customer accessed Order History")
    print("PASS: Customer remained logged in")

    # Verify that the browser title identifies the Order History page
    assert "Order History" in driver.title, (
        "Browser title does not identify Order History"
    )

    # Check that Order History also appears in the page breadcrumb
    breadcrumb = driver.find_element(
        By.CSS_SELECTOR, ".breadcrumb"
    )

    assert "Order History" in breadcrumb.text, (
        "Order History breadcrumb was not displayed"
    )

    print("PASS: Order History title and breadcrumb displayed")

    # Look for any previous orders listed in the account
    order_rows = driver.find_elements(
        By.CSS_SELECTOR,
        "#content .table-responsive tbody tr"
    )

    # Confirm that no order records are displayed
    assert len(order_rows) == 0, (
        "Previous order records were unexpectedly displayed"
    )

    print("PASS: No previous order records displayed")

    # Print the page content to see what the website actually displays
    page_text = content.text

    print("Order History Page Content:")
    print(page_text)

    # Save a screenshot of the Order History page
    driver.save_screenshot(
        "T011_Scenario1_EmptyOrderHistory.png"
    )

    print("TEST RESULT: PASS - T011 Scenario 1")

except Exception as error:
    # Show the error if the test does not complete successfully
    print("TEST RESULT: FAIL - T011 Scenario 1")
    print("ERROR:", type(error).__name__, str(error))

    # Try to save a screenshot of the page where the test failed
    try:
        driver.save_screenshot(
            "T011_Scenario1_Error.png"
        )
    except Exception:
        print("Screenshot unavailable")

finally:
    # Close the browser after completing the test
    try:
        driver.quit()
    except Exception:
        pass
