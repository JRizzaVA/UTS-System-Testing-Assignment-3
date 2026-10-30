
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Open Microsoft Edge and set the waiting time for page elements
driver = webdriver.Edge()
driver.maximize_window()
wait = WebDriverWait(driver, 20)

try:
    # Open the Contact Us page
    driver.get(
        "https://opencart.abstracta.us/index.php?route=information/contact"
    )

    # Wait for the main page content to appear
    wait.until(
        EC.visibility_of_element_located((By.ID, "content"))
    )

    # Make sure the correct page was opened
    assert "Contact Us" in driver.title, (
        "Contact Us page was not opened"
    )

    print("PASS: Contact Us page opened successfully")

    # Find the three required fields on the contact form
    name_field = wait.until(
        EC.visibility_of_element_located((By.ID, "input-name"))
    )

    email_field = wait.until(
        EC.visibility_of_element_located((By.ID, "input-email"))
    )

    enquiry_field = wait.until(
        EC.visibility_of_element_located((By.ID, "input-enquiry"))
    )

    # Check that all three fields are visible
    assert name_field.is_displayed()
    assert email_field.is_displayed()
    assert enquiry_field.is_displayed()

    print("PASS: Required contact form fields displayed")

    # Leave all fields empty to test the required field validation
    assert name_field.get_attribute("value") == ""
    assert email_field.get_attribute("value") == ""
    assert enquiry_field.get_attribute("value") == ""

    print("PASS: Name, email and enquiry fields left empty")

    # Save the empty form before attempting submission
    driver.save_screenshot(
        "T012_Scenario2_EmptyForm.png"
    )

    # Find the Submit button
    submit_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#content input[type='submit']")
        )
    )

    # Scroll to the button before clicking it
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        submit_button
    )

    # Try submitting the form without entering any details
    submit_button.click()

    # Wait for either validation messages or a successful submission
    wait.until(
        lambda d: (
            "route=information/contact/success" in d.current_url
            or len(d.find_elements(
                By.CSS_SELECTOR, "#content .text-danger"
            )) > 0
        )
    )

    print("Current URL:", driver.current_url)

    # Make sure the empty form was not accepted
    assert "route=information/contact/success" not in driver.current_url, (
        "Empty enquiry was incorrectly submitted"
    )

    print("PASS: Empty enquiry submission was prevented")

    # Collect the validation messages displayed on the form
    errors = driver.find_elements(
        By.CSS_SELECTOR, "#content .text-danger"
    )

    error_messages = [
        error.text.strip()
        for error in errors
        if error.is_displayed() and error.text.strip()
    ]

    # Print the messages in the terminal to see which fields have errors
    print("Validation Messages:")

    for message in error_messages:
        print("-", message)

    # Check that there are validation messages for the three required fields
    assert len(error_messages) >= 3, (
        "Expected validation messages for all three required fields"
    )

    print("PASS: Validation messages displayed for required fields")

    # Make sure the form is still available after the failed submission
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

    # Save the validation messages as evidence
    driver.save_screenshot(
        "T012_Scenario2_Validation.png"
    )

    print("TEST RESULT: PASS - T012 Scenario 2")

except AssertionError as error:
    # Report a failed test if the expected validation does not happen
    print("TEST RESULT: FAIL - T012 Scenario 2")
    print("FAILED CHECK:", str(error))

    # Save a screenshot showing the failed test
    try:
        driver.save_screenshot(
            "T012_Scenario2_Error.png"
        )
    except Exception:
        print("Screenshot unavailable")

except Exception as error:
    # Report any other error that stops Selenium from completing the test
    print("TEST RESULT: ERROR - T012 Scenario 2")
    print("ERROR:", type(error).__name__, str(error))

    # Try to capture the page where the error occurred
    try:
        driver.save_screenshot(
            "T012_Scenario2_Error.png"
        )
    except Exception:
        print("Screenshot unavailable")

finally:
    # Close Edge after the test finishes
    try:
        driver.quit()
    except Exception:
        pass
