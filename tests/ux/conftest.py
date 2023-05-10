"""Allow configuration for python and selenium parameters"""

import pytest
from selenium import webdriver  # pylint: disable=import-error
from selenium.webdriver.firefox.options import Options as FirefoxOptions  # pylint: disable=import-error # noqa: E501
from selenium.webdriver.chrome.options import Options as ChromeOptions  # pylint: disable=import-error # noqa: E501


def pytest_addoption(parser):
    """Add options for Selenium"""
    parser.addoption("--browser", action="store", default="Chrome")
    parser.addoption("--headless", action="store", default="No")
    parser.addoption("--url", action="store")


@pytest.fixture
def url(request):
    """Get the target URL"""
    return request.config.getoption("--url")


@pytest.fixture(scope="class")
def setup(request):
    """Setup the required browser with the command line options"""
    requested_browser = request.config.getoption("--browser")
    requested_headless = request.config.getoption("--headless")
    if requested_browser.lower() == "firefox":
        options = FirefoxOptions()
        if requested_headless.lower() == "yes":
            options.add_argument("--headless")
        driver = webdriver.Firefox(options=options)
    else:
        options = ChromeOptions()
        if requested_headless.lower() == "yes":
            options.add_argument("--headless")
        options.add_argument('--hide-scrollbars')
        options.add_argument('--ignore-certificate-errors')
        options.add_argument('--window-size=1920,1080')
        options.add_argument("--disable-popup-blocking")
        options.add_experimental_option('excludeSwitches', ['enable-logging'])

        driver = webdriver.Chrome(options=options)

    driver.implicitly_wait(10)
    request.cls.driver = driver
    # Start function
    yield driver

    # Teardown code
    driver.close()
    driver.quit()
