
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Open Microsoft Edge and allow time for the page to load
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
        EC.visibility_of_element_located(
            (By.ID, "content")
        )
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

    print("PASS: Name, email and enquiry fields displayed")

    # Enter sample customer details into the contact form
    name_field.send_keys("Jane Doe")

    email_field.send_keys("jane.doe@gmail.com")

    enquiry_field.send_keys(
        "Hello, I would like to enquire about the "
        "availability of the iPhone product. Thank you."
    )

    # Check that the details were entered correctly
    assert name_field.get_attribute("value") == "Jane Doe"

    assert email_field.get_attribute("value") == "jane.doe@gmail.com"

    assert "iPhone product" in enquiry_field.get_attribute("value")

    print("PASS: Valid contact form details entered")

    # Save a screenshot of the completed form before submitting
    driver.save_screenshot(
        "T012_Scenario1_CompletedForm.png"
    )

    # Find the Submit button
    submit_button = wait.until(
        EC.element_to_be_clickable(
            (By.CSS_SELECTOR, "#content input[type='submit']")
        )
    )

    # Scroll to the button so it can be clicked properly
    driver.execute_script(
        "arguments[0].scrollIntoView({block: 'center'});",
        submit_button
    )

    # Submit the contact form with the entered details
    submit_button.click()

    # Check whether the website goes to the contact success page
    wait.until(
        EC.url_contains("route=information/contact/success")
    )

    print("PASS: Contact form submitted successfully")

    # Get the content displayed after submitting the form
    content = wait.until(
        EC.visibility_of_element_located(
            (By.ID, "content")
        )
    )

    # Print the actual URL and page content to check the result
    print("Contact Success URL:", driver.current_url)
    print("Contact Success Page Content:")
    print(content.text)

    # Save a screenshot of the page after submission
    driver.save_screenshot(
        "T012_Scenario1_Success.png"
    )

    # Check if the website displays the expected confirmation message
    assert "Your enquiry has been successfully sent" in content.text, (
        "Expected enquiry confirmation was not displayed"
    )

    print("PASS: Enquiry confirmation message displayed")
    print("TEST RESULT: PASS - T012 Scenario 1")

except Exception as error:
    # Report the error if the actual result does not match what was expected
    print("TEST RESULT: FAIL/ERROR - T012 Scenario 1")
    print("ERROR:", type(error).__name__, str(error))

    # Try to save a screenshot showing where the test failed
    try:
        driver.save_screenshot(
            "T012_Scenario1_Error.png"
        )
    except Exception:
        print("Screenshot unavailable")

finally:
    # Close the browser after completing the test
    try:
        driver.quit()
    except Exception:
        pass
