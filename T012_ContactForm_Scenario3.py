
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

# Open Microsoft Edge and set the waiting time for page elements
driver = webdriver.Edge()
driver.maximize_window()
wait = WebDriverWait(driver, 20)

try:
    # Open the Contact Us page
    driver.get(
        "https://opencart.abstracta.us/index.php?route=information/contact"
    )

    # Check that the correct page was opened
    assert "Contact Us" in driver.title, (
        "Contact Us page was not opened"
    )

    print("PASS: Contact Us page opened successfully")

    # Find the name, email and enquiry fields
    name_field = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-name")
        )
    )

    email_field = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-email")
        )
    )

    enquiry_field = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "input-enquiry")
        )
    )

    print("PASS: Contact form fields displayed")

    # Enter a valid customer name
    name_field.send_keys("Jane Doe")

    # Enter an invalid email address without the @ symbol
    email_field.send_keys("janedoe.com")

    # Enter a valid enquiry so we can focus on testing the email field
    enquiry_field.send_keys(
        "Hello, I would like to enquire about the "
        "availability of the iPhone product. Thank you."
    )

    # Check that the sample name was entered correctly
    assert name_field.get_attribute("value") == "Jane Doe"

    # Make sure the invalid email was entered as intended
    assert email_field.get_attribute("value") == "janedoe.com"

    # Check that the enquiry contains the correct information
    assert "iPhone product" in enquiry_field.get_attribute("value")

    print("PASS: Valid name and enquiry entered")
    print("PASS: Invalid email format entered")

    # Save a screenshot of the completed form before submission
    driver.save_screenshot(
        "T012_Scenario3_InvalidEmail.png"
    )

    # Find the Submit button
    submit_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#content input[type='submit']")
        )
    )

    # Scroll to the Submit button before clicking it
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        submit_button
    )

    # Try submitting the form with the invalid email
    submit_button.click()

    # Wait for either a validation message or a successful submission
    try:
        wait.until(
            lambda d: (
                "route=information/contact/success" in d.current_url
                or len(d.find_elements(
                    By.CSS_SELECTOR, "#content .text-danger"
                )) > 0
            )
        )
    except TimeoutException:
        # Report a failed check if the website gives no response
        raise AssertionError(
            "No validation response appeared after submission"
        )

    print("Current URL:", driver.current_url)

    # Make sure the invalid email was not accepted
    assert "route=information/contact/success" not in driver.current_url, (
        "Invalid email was incorrectly accepted"
    )

    print("PASS: Invalid email submission prevented")

    # Collect the validation messages displayed on the page
    errors = driver.find_elements(
        By.CSS_SELECTOR, "#content .text-danger"
    )

    error_messages = [
        error.text.strip()
        for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    # Print the validation messages in the terminal
    print("Validation Messages:")

    for message in error_messages:
        print("-", message)

    # Check that the website displays an invalid email message
    assert any(
        "E-Mail Address" in message
        and "valid" in message.lower()
        for message in error_messages
    ), "Expected invalid email validation message was not displayed"

    print("PASS: Invalid email validation message displayed")

    # Make sure there are no errors for the valid name and enquiry
    assert len(error_messages) == 1, (
        "Unexpected validation errors were displayed"
    )

    print("PASS: No other field validation errors displayed")

    # Confirm that the contact form is still available after submission
    assert driver.find_element(
        By.ID, "input-name"
    ).is_displayed()

    assert driver.find_element(
        By.ID, "input-email"
    ).is_displayed()

    assert driver.find_element(
        By.ID, "input-enquiry"
    ).is_displayed()

    print("PASS: Contact form remains accessible")

    # Save a screenshot showing the email validation message
    driver.save_screenshot(
        "T012_Scenario3_Validation.png"
    )

    print("TEST RESULT: PASS - T012 Scenario 3")

except AssertionError as error:
    # Report FAIL if the actual result does not match the expected result
    print("TEST RESULT: FAIL - T012 Scenario 3")
    print("FAILED CHECK:", str(error))

    # Save a screenshot showing the failed test
    try:
        driver.save_screenshot(
            "T012_Scenario3_Error.png"
        )
    except Exception:
        print("Screenshot unavailable")

except Exception as error:
    # Report any other error that interrupts the test
    print("TEST RESULT: ERROR - T012 Scenario 3")
    print("ERROR:", type(error).__name__, str(error))

    # Try to save a screenshot of the error
    try:
        driver.save_screenshot(
            "T012_Scenario3_Error.png"
        )
    except Exception:
        print("Screenshot unavailable")

finally:
    # Close the browser after the test
    try:
        driver.quit()
    except Exception:
        pass
