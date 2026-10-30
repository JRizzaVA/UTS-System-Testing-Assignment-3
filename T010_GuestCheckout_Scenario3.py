
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Open Microsoft Edge and set a waiting time for the page elements
driver = webdriver.Edge()
wait = WebDriverWait(driver, 15)

try:
    # Clear the browser cookies to start with a fresh session
    driver.delete_all_cookies()

    # Open the store homepage
    driver.get("https://opencart.abstracta.us/index.php?route=common/home")

    print("Page Title:", driver.title)

    # Go directly to the shopping cart without adding any products
    driver.get("https://opencart.abstracta.us/index.php?route=checkout/cart")

    cart_message = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "content")
        )
    )

    # Check that the website displays the empty cart message
    assert "Your shopping cart is empty!" in cart_message.text, (
        "Empty cart message was not displayed"
    )

    print("PASS: Empty shopping cart message displayed")

    # Make sure there are no product quantity fields in the cart
    assert len(
        driver.find_elements(By.CSS_SELECTOR, "#content input[name^='quantity']")
    ) == 0, "Cart contains product quantity fields"

    print("PASS: No products found in the shopping cart")

    # Save a screenshot showing the empty shopping cart
    driver.save_screenshot("T010_Scenario3_EmptyCart.png")

    # Try to access checkout even though the cart is empty
    driver.get("https://opencart.abstracta.us/index.php?route=checkout/checkout")

    # Wait for the website to redirect back to the shopping cart
    wait.until(
        EC.url_contains("route=checkout/cart")
    )

    print("Redirected Page Title:", driver.title)

    # Check that checkout was redirected to the shopping cart page
    assert "route=checkout/cart" in driver.current_url, (
        "Checkout did not redirect to Shopping Cart"
    )

    print("PASS: Empty cart checkout redirected to Shopping Cart")

    # Check that the empty cart message is still displayed after redirecting
    cart_content = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "content")
        )
    )

    assert "Your shopping cart is empty!" in cart_content.text, (
        "Empty cart message missing after redirect"
    )

    # Make sure the Guest Checkout option is not available
    assert len(
        driver.find_elements(By.ID, "button-account")
    ) == 0, "Guest Checkout form was unexpectedly available"

    # Make sure the customer cannot enter billing information
    assert len(
        driver.find_elements(By.ID, "input-payment-firstname")
    ) == 0, "Billing Details form was unexpectedly available"

    print("PASS: Guest Checkout and Billing Details were not available")
    print("PASS: Checkout prevented with an empty shopping cart")
    print("TEST RESULT: PASS - Scenario 3")

    # Save a screenshot showing the page after checkout was blocked
    driver.save_screenshot("T010_Scenario3_Redirect.png")

except Exception as error:
    # Display the error and save a screenshot if the test fails
    print("TEST RESULT: ERROR")
    print("ERROR:", type(error).__name__, str(error))
    driver.save_screenshot("T010_Scenario3_Error.png")
    raise

finally:
    # Close the browser after finishing the test
    driver.quit()
