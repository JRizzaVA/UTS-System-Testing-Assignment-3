
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC

# Allow the test to place the order after checking the details
CONFIRM_ORDER = True

# Open Microsoft Edge and set a waiting time for page elements
driver = webdriver.Edge()
wait = WebDriverWait(driver, 15)

try:
     # Open the iPhone product page
    driver.get("https://opencart.abstracta.us/index.php?route=product/product&product_id=40")

    print("Page Title:", driver.title)

    # Set the product quantity to one
    quantity = wait.until(
        EC.visibility_of_element_located((By.ID, "input-quantity"))
    )
    quantity.clear()
    quantity.send_keys("1")

    # Add the iPhone to the shopping cart
    add_to_cart = wait.until(
        EC.element_to_be_clickable((By.ID, "button-cart"))
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

    # Open the shopping cart to check the selected product
    driver.get("https://opencart.abstracta.us/index.php?route=checkout/cart")

    cart = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, ".table-responsive")
        )
    )

    # Make sure the iPhone appears in the cart
    assert "iPhone" in cart.text, "iPhone was not found in the shopping cart"

    print("PASS: iPhone successfully added to the shopping cart")

    # Go to checkout without logging into an account
    driver.get("https://opencart.abstracta.us/index.php?route=checkout/checkout")

    print("Checkout Page Title:", driver.title)

    # Select Guest Checkout instead of registering an account
    guest_checkout = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[value='guest']")
        )
    )
    guest_checkout.click()

    # Check that Guest Checkout is selected
    assert guest_checkout.is_selected(), "Guest Checkout was not selected"

    print("PASS: Guest Checkout selected")

    # Continue to the billing details section
    wait.until(
        EC.element_to_be_clickable((By.ID, "button-account"))
    ).click()

    wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-payment-firstname")
        )
    )

    print("PASS: Billing Details form displayed")

    # Use sample customer details to complete the checkout form
    billing_details = {
        "input-payment-firstname": "Jane",
        "input-payment-lastname": "Doe",
        "input-payment-email": "jane.doe@gmail.com",
        "input-payment-telephone": "0491771888",
        "input-payment-company": "UTS",
        "input-payment-address-1": "Leichhardt",
        "input-payment-city": "Sydney",
        "input-payment-postcode": "2040"
    }

    # Enter each value into its matching billing field
    for field_id, value in billing_details.items():
        field = driver.find_element(By.ID, field_id)
        field.clear()
        field.send_keys(value)

    country = Select(driver.find_element(By.ID, "input-payment-country"))
    country.select_by_visible_text("Australia")

    # Wait for the state options to load after selecting Australia
    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "input-payment-zone"),
            "New South Wales"
        )
    )

    # Select New South Wales as the billing region
    region = Select(driver.find_element(By.ID, "input-payment-zone"))
    region.select_by_visible_text("New South Wales")

    # Check that the correct region was selected
    selected_region = Select(
        driver.find_element(By.ID, "input-payment-zone")
    ).first_selected_option.text

    assert selected_region == "New South Wales"

    print("PASS: Country and Region selected successfully")
    print("PASS: Billing information entered")

    # Use the same address for billing and delivery
    same_address = driver.find_elements(
        By.CSS_SELECTOR, "input[name='shipping_address']"
    )

    if same_address and not same_address[0].is_selected():
        same_address[0].click()

    # Submit the completed billing details
    continue_button = wait.until(
        EC.element_to_be_clickable((By.ID, "button-guest"))
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        continue_button
    )

    continue_button.click()

    print("PASS: Billing details submitted")

    # Find the Continue button for the delivery method
    delivery_button = wait.until(
        EC.element_to_be_clickable((By.ID, "button-shipping-method"))
    )

    delivery_options = driver.find_elements(
        By.CSS_SELECTOR, "input[name='shipping_method']"
    )
    # Select an available delivery method if none is selected
    if delivery_options and not any(
        option.is_selected() for option in delivery_options
    ):
        delivery_options[0].click()

    delivery_button.click()

    print("PASS: Delivery method completed")

    # Continue to the payment method section
    payment_button = wait.until(
        EC.element_to_be_clickable((By.ID, "button-payment-method"))
    )

     # Select Bank Transfer as the payment method
    bank_transfer = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "input[name='payment_method'][value='bank_transfer']")
        )
    )
    bank_transfer.click()

    # Accept the Terms and Conditions if required
    agreement = driver.find_elements(
        By.CSS_SELECTOR, "input[name='agree']"
    )

    if agreement and not agreement[0].is_selected():
        agreement[0].click()

    # Continue to the final order confirmation
    payment_button.click()

    print("PASS: Bank Transfer payment method selected")

     # Wait until the Confirm Order button is available
    confirm_button = wait.until(
        EC.element_to_be_clickable((By.ID, "button-confirm"))
    )

    # Check that the order summary still contains the iPhone
    confirmation = driver.find_element(
        By.ID, "collapse-checkout-confirm"
    ).text

    assert "iPhone" in confirmation, "iPhone missing from order summary"

    print("PASS: Order summary displayed")
    print("PASS: iPhone found in order confirmation")

    # Save a screenshot of the order details before submission
    driver.save_screenshot("T010_Scenario1_Confirmation.png")

    # Place the test order when final confirmation is enabled
    if CONFIRM_ORDER:
        confirm_button = wait.until(
            EC.element_to_be_clickable((By.ID, "button-confirm"))
        )
        # Keep the button in view before clicking it
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            confirm_button
        )

        confirm_button.click()

         # Check for the successful order confirmation message
        wait.until(
            EC.text_to_be_present_in_element(
                (By.TAG_NAME, "body"),
                "Your order has been placed!"
            )
        )

        print("PASS: Guest checkout completed successfully")

        # Save the success page as evidence
        driver.save_screenshot("T010_Scenario1_Success.png")
    else:
        print("READY: Order confirmation verified; final submission disabled")

except Exception as error:
    # Display the error and save a screenshot if the test fails
    print("ERROR:", type(error).__name__, str(error))
    driver.save_screenshot("T010_Scenario1_Error.png")
    raise

finally:
    # Close Edge after the test, whether it passes or fails
    driver.quit()
