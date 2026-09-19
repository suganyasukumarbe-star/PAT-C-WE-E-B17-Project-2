import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BaseOrangeHRMTest(unittest.TestCase):
    """Base test class to handle browser lifecycle setup and teardown."""

    @classmethod
    def setUpClass(cls):
        # Initializing the Chrome browser instance
        cls.driver = webdriver.Chrome()
        cls.driver.maximize_window()
        cls.base_url = "https://orangehrmlive.com"
        cls.wait = WebDriverWait(cls.driver, 10)

    @classmethod
    def tearDownClass(cls):
        # Clean up: Ensure browser closes properly after tests run
        if cls.driver:
            cls.driver.quit()


class TestOrangeHRMAutomation(BaseOrangeHRMTest):

    def test_02_verify_home_url_accessible(self):
        """Test-Case-2: Verify that the home URL is accessible."""
        try:
            self.driver.get(self.base_url)
            # Verify the page title to ensure it loaded without error
            self.assertIn("OrangeHRM", self.driver.title)
            print("TC-2 Passed: Home URL is accessible.")
        except Exception as e:
            self.fail(f"TC-2 Failed: Home URL loading encountered an error: {e}")

    def test_03_validate_presence_of_login_fields(self):
        """Test-Case-3: Validate presence and visibility of login fields."""
        try:
            self.driver.get(self.base_url)

            # Explicitly wait for username and password elements to be visible
            username_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "username")))
            password_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "password")))

            self.assertTrue(username_field.is_enabled())
            self.assertTrue(password_field.is_enabled())
            print("TC-3 Passed: Login fields are visible and enabled.")
        except TimeoutException:
            self.fail("TC-3 Failed: Login fields were not visible within the timeout period.")

    def test_01_data_driven_login(self):
        """Test-Case-1: Validate login functionality using multiple sets of credentials."""
        # Structured test dataset acting as the external data source simulation
        test_data = [
            {"username": "Admin", "password": "admin123", "expected": "success"},
            {"username": "manager@guvi.in", "password": "password@123", "expected": "fail"},
            {"username": "suman@guvi.in", "password": "password@123", "expected": "fail"}
        ]

        for data in test_data:
            with self.subTest(data=data):
                try:
                    self.driver.get(self.base_url)

                    username_field = self.wait.until(EC.visibility_of_element_located((By.NAME, "username")))
                    password_field = self.driver.find_element(By.NAME, "password")
                    login_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")

                    # Perform login action
                    username_field.send_keys(data["username"])
                    password_field.send_keys(data["password"])
                    login_button.click()

                    if data["expected"] == "success":
                        # Validate successful redirection to the dashboard
                        self.wait.until(EC.url_contains("/dashboard/index"))
                        self.assertIn("/dashboard/index", self.driver.current_url)

                        # Perform logout to clean up state for the next dataset step
                        profile_dropdown = self.wait.until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "oxd-userdropdown-tab")))
                        profile_dropdown.click()
                        logout_link = self.wait.until(EC.element_to_be_clickable((By.XPATH, "//a[text()='Logout']")))
                        logout_link.click()

                        # Verify redirection back to the login frame
                        self.wait.until(EC.visibility_of_element_located((By.NAME, "username")))
                        print(f"TC-1 Passed: Successful login validated for user {data['username']}.")

                    else:
                        # Validate error alert presence for invalid credentials
                        error_alert = self.wait.until(
                            EC.visibility_of_element_located((By.CLASS_NAME, "oxd-alert-content-text")))
                        self.assertEqual(error_alert.text, "Invalid credentials")
                        print(f"TC-1 Passed: Invalid login properly rejected for user {data['username']}.")

                except (TimeoutException, NoSuchElementException) as e:
                    self.fail(f"TC-1 Failed during execution for credentials {data['username']}: {e}")

    def test_07_verify_forgot_password_link(self):
        """Test-Case-7: Verify 'Forgot Password' link functionality."""
        try:
            self.driver.get(self.base_url)

            # Click the forgot password locator link
            forgot_pass_link = self.wait.until(
                EC.element_to_be_clickable((By.CLASS_NAME, "orangehrm-login-forgot-header")))
            forgot_pass_link.click()

            # Validate redirection to request password reset layout
            self.wait.until(EC.url_contains("/requestPasswordResetCode"))

            # Input username and submit request
            username_input = self.wait.until(EC.visibility_of_element_located((By.NAME, "username")))
            username_input.send_keys("Admin")

            reset_button = self.driver.find_element(By.XPATH, "//button[@type='submit']")
            reset_button.click()

            # Validate standard success verification header message
            success_header = self.wait.until(
                EC.visibility_of_element_located((By.CLASS_NAME, "orangehrm-forgot-password-title")))
            self.assertEqual(success_header.text, "Reset Password Link Sent")
            print("TC-7 Passed: Forgot Password confirmation flow validated successfully.")
        except Exception as e:
            self.fail(f"TC-7 Failed: {e}")


if __name__ == "__main__":
    unittest.main()

