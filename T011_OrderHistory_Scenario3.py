
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Open a new Edge browser session without logging into an account
driver = webdriver.Edge()
driver.maximize_window()
wait = WebDriverWait(driver, 20)

try:
    # Try to open Order History directly without logging in
    driver.get(
        "https://opencart.abstracta.us/index.php?route=account/order"
    )

    print("Requested URL: https://opencart.abstracta.us/index.php?route=account/order")

    # Wait to see if the website redirects the visitor to Login
    wait.until(
        EC.url_contains("route=account/login")
    )

    print("PASS: Unauthenticated visitor redirected to Login")

    # Print the actual page details after the redirect
    print("Actual URL:", driver.current_url)
    print("Page Title:", driver.title)

    # Check that the visitor was redirected to the login page
    assert "route=account/login" in driver.current_url, (
        "Order History did not redirect to Login"
    )

    # Make sure the browser title shows Account Login
    assert "Account Login" in driver.title, (
        "Login page title was not displayed"
    )

    print("PASS: Account Login page displayed")

    # Find the email and password fields on the login page
    email_field = wait.until(
        EC.visibility_of_element_located((By.ID, "input-email"))
    )

    password_field = wait.until(
        EC.visibility_of_element_located((By.ID, "input-password"))
    )

    # Check that both login fields are visible
    assert email_field.is_displayed()
    assert password_field.is_displayed()

    print("PASS: Email and password fields displayed")

    # Check the page content for any customer order information
    content = driver.find_element(By.ID, "content")

    # Make sure order numbers are not displayed without logging in
    assert "Order ID" not in content.text, (
        "Order History records are visible without login"
    )

    # Make sure the order date details are also hidden
    assert "Date Added" not in content.text, (
        "Customer order details are visible without login"
    )

    print("PASS: No customer order records displayed")
    print("PASS: Order History requires authentication")

    # Save a screenshot showing the redirected login page
    driver.save_screenshot(
        "T011_Scenario3_LoginRedirect.png"
    )

    print("TEST RESULT: PASS - T011 Scenario 3")

except Exception as error:
    # Display any error if the test does not complete successfully
    print("TEST RESULT: FAIL/ERROR - T011 Scenario 3")
    print("ERROR:", type(error).__name__, str(error))

    # Try to capture the page if the test fails
    try:
        driver.save_screenshot(
            "T011_Scenario3_Error.png"
        )
    except Exception:
        print("Screenshot unavailable")

finally:
    # Close the browser after the test
    try:
        driver.quit()
    except Exception:
        pass
