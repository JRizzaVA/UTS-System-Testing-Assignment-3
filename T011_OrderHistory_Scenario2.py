
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException
from getpass import getpass

# Ask for the registered account details without saving the password in the script
email = input("Enter registered test account email: ")
password = getpass("Enter test account password: ")

# Keep the website address in one place so it is easier to reuse
base_url = "https://opencart.abstracta.us/index.php?route="

# Open Edge and set how long Selenium should wait for pages
driver = webdriver.Edge()
driver.maximize_window()
wait = WebDriverWait(driver, 25)

# Scroll the button into view before clicking it
def click_button(button_id):
    button = wait.until(
        EC.element_to_be_clickable((By.ID, button_id))
    )
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        button
    )
    button.click()

# Collect any warning messages shown by the website
def visible_warnings():
    elements = driver.find_elements(
        By.CSS_SELECTOR,
        ".alert-danger, .alert-warning, .text-danger"
    )
    return [
        element.text.strip()
        for element in elements
        if element.is_displayed() and element.text.strip()
    ]

# If checkout gets stuck, show the page details and save a screenshot
def show_diagnostics(stage):
    print("FAILED STAGE:", stage)

    try:
        print("Current URL:", driver.current_url)
        print("Page Title:", driver.title)

        for warning in visible_warnings():
            print("WEBSITE WARNING:", warning)

        content = driver.find_elements(By.ID, "content")
        if content:
            print("PAGE CONTENT:", content[0].text[:1200])

        driver.save_screenshot(
            "T011_Scenario2_Diagnostic.png"
        )
    except Exception:
        print("Browser diagnostics unavailable")

# Wait for each checkout section to open before moving to the next one
def wait_for_stage(stage_id, stage_name):
    try:
        wait.until(
            EC.visibility_of_element_located(
                (By.ID, stage_id)
            )
        )
        print("PASS:", stage_name)
    except TimeoutException:
        show_diagnostics(stage_name)
        raise AssertionError(
            stage_name + " did not open successfully"
        )

# Use the customer saved address rather than entering it again
def select_existing_address(name):
    option = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR,
             f"input[name='{name}'][value='existing']")
        )
    )

    if not option.is_selected():
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            option
        )
        option.click()

    assert option.is_selected(), (
        "Existing address selection failed"
    )

try:
    # Start by logging into the registered customer account
    driver.get(base_url + "account/login")

    wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-email")
        )
    ).send_keys(email)

    driver.find_element(
        By.ID, "input-password"
    ).send_keys(password)

    driver.find_element(
        By.CSS_SELECTOR,
        "input[type='submit'][value='Login']"
    ).click()

    # Make sure login takes us to the account page
    wait.until(
        EC.url_contains("route=account/account")
    )

    print("PASS: Registered customer logged in")

    # Open the shopping cart before removing leftover products
    driver.get(base_url + "checkout/cart")

    # Remove existing products one at a time until the cart is empty
    for attempt in range(10):
        remove_buttons = driver.find_elements(
            By.CSS_SELECTOR,
            "button[onclick*='cart.remove']"
        )

        if not remove_buttons:
            break

        remove_button = remove_buttons[0]

        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            remove_button
        )

        remove_button.click()

        wait.until(
            EC.staleness_of(remove_button)
        )

    cart_content = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "content")
        )
    )

    # Check that the cart really is empty before adding our test product
    assert "Your shopping cart is empty!" in cart_content.text, (
        "Shopping cart was not cleared successfully"
    )

    print("PASS: Previous cart items cleared")

    driver.get(
        base_url + "product/product&product_id=40"
    )

    quantity = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-quantity")
        )
    )

    # Add just one iPhone for this order
    quantity.clear()
    quantity.send_keys("1")

    click_button("button-cart")

    wait.until(
        EC.text_to_be_present_in_element(
            (By.ID, "cart-total"), "1 item(s)"
        )
    )

    driver.get(base_url + "checkout/cart")

    # Open the cart again to check the product and quantity
    cart_table = wait.until(
        EC.visibility_of_element_located(
            (By.CSS_SELECTOR, "#content .table-responsive")
        )
    )

    assert "iPhone" in cart_table.text

    cart_rows = cart_table.find_elements(
        By.CSS_SELECTOR, "tbody tr"
    )

    # Make sure we did not accidentally add extra products
    assert len(cart_rows) == 1, (
        "Shopping cart contains unexpected products"
    )

    print("PASS: Shopping cart contains one iPhone")

    # Begin checkout using the registered account
    driver.get(base_url + "checkout/checkout")

    wait_for_stage(
        "collapse-payment-address",
        "Billing address section opened"
    )

    # Select the address already saved for billing
    select_existing_address("payment_address")
    print("PASS: Existing billing address selected")

    # Save the billing selection and continue to delivery address
    click_button("button-payment-address")

    wait_for_stage(
        "collapse-shipping-address",
        "Delivery address section opened"
    )

    # Choose the saved address for delivery as well
    select_existing_address("shipping_address")

    print("PASS: Existing delivery address selected")

    click_button("button-shipping-address")

    # Continue to the available shipping options
    wait_for_stage(
        "collapse-shipping-method",
        "Shipping method section opened"
    )

    # Find the shipping methods offered by the website
    shipping_methods = wait.until(
        EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR,
             "#collapse-shipping-method input[name='shipping_method']")
        )
    )

    selected_shipping = next(
        (method for method in shipping_methods
         if method.is_selected()),
        shipping_methods[0]
    )

    # Select a shipping option only if none is chosen yet
    if not selected_shipping.is_selected():
        selected_shipping.click()

    assert selected_shipping.is_selected()

    # Continue to the payment method section
    click_button("button-shipping-method")

    wait_for_stage(
        "collapse-payment-method",
        "Payment method section opened"
    )

    # Select Bank Transfer for this test order
    bank_transfer = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR,
             "#collapse-payment-method "
             "input[name='payment_method'][value='bank_transfer']")
        )
    )

    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        bank_transfer
    )

    if not bank_transfer.is_selected():
        bank_transfer.click()

    assert bank_transfer.is_selected(), (
        "Bank Transfer was not selected"
    )

    # Accept the Terms and Conditions before continuing
    agreement = wait.until(
        EC.presence_of_element_located(
            (By.CSS_SELECTOR,
             "#collapse-payment-method input[name='agree']")
        )
    )

    if not agreement.is_selected():
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            agreement
        )
        agreement.click()

    assert agreement.is_selected(), (
        "Terms and Conditions not accepted"
    )

    print("PASS: Bank Transfer and Terms selected")

    # Save the selected payment method as test evidence
    driver.save_screenshot(
        "T011_Scenario2_PaymentMethod.png"
    )

    # Move to the final order confirmation page
    click_button("button-payment-method")

    try:
        wait.until(
            EC.visibility_of_element_located(
                (By.ID, "button-confirm")
            )
        )
    except TimeoutException:
        show_diagnostics("Order confirmation")
        raise AssertionError(
            "Checkout did not reach order confirmation"
        )

    # Check the order summary still includes the iPhone
    confirmation = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "collapse-checkout-confirm")
        )
    )

    assert "iPhone" in confirmation.text, (
        "iPhone missing from order summary"
    )

    print("PASS: Order confirmation contains iPhone")

    # Save the order summary before placing the order
    driver.save_screenshot(
        "T011_Scenario2_OrderConfirmation.png"
    )

    # Submit the test order
    click_button("button-confirm")

    wait.until(
        EC.text_to_be_present_in_element(
            (By.TAG_NAME, "body"),
            "Your order has been placed!"
        )
    )

    print("PASS: Registered customer order placed")

    driver.save_screenshot(
        "T011_Scenario2_OrderSuccess.png"
    )

    driver.get(base_url + "account/order")

    # Open Order History to look for the new order
    history_content = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "content")
        )
    )

    assert "Order History" in driver.title, (
        "Order History page was not opened"
    )

    # Find the order records displayed in the table
    rows = driver.find_elements(
        By.CSS_SELECTOR,
        "#content .table-responsive tbody tr"
    )

    assert len(rows) > 0, (
        "Newly placed order was not displayed"
    )

    # Read the first order shown in the history list
    order_row = rows[0]
    order_text = order_row.text

    print("Order History Record:")
    print(order_text)

    assert order_text.strip(), (
        "Order History record is empty"
    )

    print("PASS: Order record displayed")

    # Save a screenshot of the order record
    driver.save_screenshot(
        "T011_Scenario2_OrderHistory.png"
    )

    # Open the order record to check its product details
    view_link = order_row.find_element(
        By.CSS_SELECTOR,
        "a[href*='route=account/order/info']"
    )

    view_link.click()

    wait.until(
        EC.url_contains("route=account/order/info")
    )

    details = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "content")
        )
    )

    # Make sure the order details show the iPhone
    assert "iPhone" in details.text, (
        "iPhone missing from order details"
    )

    product_rows = details.find_elements(
        By.CSS_SELECTOR, ".table-responsive tbody tr"
    )

    # Find the product row containing the iPhone
    iphone_rows = [
        row for row in product_rows
        if "iPhone" in row.text
    ]

    assert iphone_rows, (
        "iPhone product row was not found"
    )

    print("PASS: iPhone found in order details")
    print("Order Product Details:")
    print(iphone_rows[0].text)

    # Save the order details as the final website evidence
    driver.save_screenshot(
        "T011_Scenario2_OrderDetails.png"
    )

    print("TEST RESULT: PASS - T011 Scenario 2")
#Report the error and save useful details if the test stops
except Exception as error:
    print("TEST RESULT: FAIL/ERROR - T011 Scenario 2")
    print("ERROR:", type(error).__name__, str(error))
    show_diagnostics("Test execution")

# Close Edge after the test finishes
finally:
    try:
        driver.quit()
    except Exception:
        pass
