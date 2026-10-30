
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Open Microsoft Edge and wait for elements to load when needed
driver = webdriver.Edge()
wait = WebDriverWait(driver, 15)

try:
    # Open the iPhone product page
    driver.get("https://opencart.abstracta.us/index.php?route=product/product&product_id=40")

    print("Page Title:", driver.title)

    quantity = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-quantity")
        )
    )
    # Set the quantity to one
    quantity.clear()
    quantity.send_keys("1")

    # Add the iPhone to the shopping cart
    add_to_cart = wait.until(
        EC.element_to_be_clickable(
            (By.ID, "button-cart")
        )
    )

    add_to_cart.click()

    # Check if the cart updates to show one item
    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "cart-total"),
            "1 item(s)"
        )
    )

    print("PASS: Shopping cart updated successfully")

    # Open the shopping cart and check that the iPhone was added
    driver.get("https://opencart.abstracta.us/index.php?route=checkout/cart")

    cart = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".table-responsive")
        )
    )

    assert "iPhone" in cart.text, "iPhone was not found in the cart"

    print("PASS: iPhone added to shopping cart")

    # Proceed to checkout without logging in
    driver.get("https://opencart.abstracta.us/index.php?route=checkout/checkout")

    print("Checkout Page Title:", driver.title)

    # Select Guest Checkout
    guest_checkout = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[value='guest']")
        )
    )

    guest_checkout.click()

    # Make sure Guest Checkout is selected
    assert guest_checkout.is_selected()

    print("PASS: Guest Checkout selected")

    # Continue to the billing details form
    continue_button = wait.until(
        EC.element_to_be_clickable(
            (By.ID, "button-account")
        )
    )

    continue_button.click()

    billing_form = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-payment-firstname")
        )
    )

    print("PASS: Billing Details form displayed")

    # These are the required billing fields we want to leave empty
    required_fields = [
        "input-payment-firstname",
        "input-payment-lastname",
        "input-payment-email",
        "input-payment-telephone",
        "input-payment-address-1",
        "input-payment-city",
        "input-payment-postcode"
    ]

    # Clear each field and check that no information was entered
    for field_id in required_fields:
        field = driver.find_element(By.ID, field_id)
        field.clear()
        assert field.get_attribute("value") == "", (
            field_id + " was not empty"
        )

    print("PASS: Required billing fields left empty")

    # Try to continue checkout without completing the billing form
    billing_continue = wait.until(
        EC.element_to_be_clickable(
            (By.ID, "button-guest")
        )
    )

    # Move the button into view before clicking
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        billing_continue
    )

    billing_continue.click()

    # Wait for the website to display billing validation errors
    wait.until(
        lambda d: len([
            element for element in d.find_elements(
                By.CSS_SELECTOR,
                "#collapse-payment-address .text-danger"
            )
            if element.is_displayed() and element.text.strip()
        ]) > 0
    )

    # Collect the validation messages shown under the billing fields
    errors = driver.find_elements(
        By.CSS_SELECTOR,
        "#collapse-payment-address .text-danger"
    )

    error_messages = [
        element.text.strip()
        for element in errors
        if element.is_displayed() and element.text.strip()
    ]

    # Display the validation messages in the terminal
    print("Validation messages:")

    for message in error_messages:
        print("-", message)

    # Check that the website displayed at least one validation message
    assert len(error_messages) > 0, (
        "No billing validation messages appeared"
    )

    # Verify that the First Name field has a validation message
    assert any(
        "first name" in message.lower()
        for message in error_messages
    ), "First Name validation message was not found"

    # Verify that the Last Name field has a validation message
    assert any(
        "last name" in message.lower()
        for message in error_messages
    ), "Last Name validation message was not found"

    # Check that the billing form is still displayed after the failed submission
    assert driver.find_element(
        By.ID, "input-payment-firstname"
    ).is_displayed(), "Billing Details form was no longer displayed"

    print("PASS: Required field validation displayed")
    print("PASS: Incomplete guest checkout was blocked")
    print("TEST RESULT: PASS - Scenario 2")

     # Save the validation messages as screenshot evidence
    driver.save_screenshot("T010_Scenario2_Validation.png")

except Exception as error:
    # Display the error and save evidence if the test cannot finish
    print("TEST RESULT: ERROR")
    print("ERROR:", type(error).__name__, str(error))

    driver.save_screenshot("T010_Scenario2_Error.png")
    raise

finally:
    # Close the browser after the test
    driver.quit()
