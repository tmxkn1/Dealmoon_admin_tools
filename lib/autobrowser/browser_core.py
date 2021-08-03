import logging
import os
import platform
import time
import zipfile

import requests
from selenium import webdriver
from selenium.common.exceptions import WebDriverException, TimeoutException, UnexpectedAlertPresentException
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait


def update_driver():
    '''
    Auto deletes Chrome driver to ensure no errors - this forces an autoupdate of chrome drivers. There is probably a more efficient way of doing this.
    '''
    os.remove("drivers/chromedriver.exe")


def download_driver(driver_path, system):
    # determine latest chromedriver version
    url = "https://chromedriver.storage.googleapis.com/LATEST_RELEASE"
    r = requests.get(url)
    latest_version = r.text
    if system == "Windows":
        url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_win32.zip".format(
            latest_version)
    elif system == "Darwin":
        url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_mac64.zip".format(
            latest_version)
    elif system == "Linux":
        url = "https://chromedriver.storage.googleapis.com/{}/chromedriver_linux64.zip".format(
            latest_version)

    response = requests.get(url, stream=True)
    zip_file_path = os.path.join(os.path.dirname(
        driver_path), os.path.basename(url))
    with open(zip_file_path, "wb") as handle:
        for chunk in response.iter_content(chunk_size=512):
            if chunk:  # filter out keep alive chunks
                handle.write(chunk)
    extracted_dir = os.path.splitext(zip_file_path)[0]
    with zipfile.ZipFile(zip_file_path, "r") as zip_file:
        zip_file.extractall(extracted_dir)
    os.remove(zip_file_path)

    driver = os.listdir(extracted_dir)[0]
    os.rename(os.path.join(extracted_dir, driver), driver_path)
    os.rmdir(extracted_dir)

    os.chmod(driver_path, 0o755)
    # way to note which chromedriver version is installed
    open(os.path.join(os.path.dirname(driver_path),
                      "{}.txt".format(latest_version)), "w").close()


def browser_setup(headless_mode):
    """
    Inits the chrome browser with headless setting and user agent
    :param headless_mode: Boolean
    :param user_agent: String
    :return: webdriver obj
    """
    os.makedirs('drivers', exist_ok=True)
    path = os.path.join('drivers', 'chromedriver')
    system = platform.system()
    if system == "Windows":
        if not path.endswith(".exe"):
            path += ".exe"
    if not os.path.exists(path):
        download_driver(path, system)

    options = Options()
    options.add_argument('--disable-webgl')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--log-level=3')
    options.add_experimental_option('w3c', False)

    prefs = {
        "profile.default_content_setting_values.geolocation": 2, "profile.default_content_setting_values.notifications": 2
    }

    options.add_experimental_option("prefs", prefs)

    if headless_mode:
        options.add_argument('--headless')

    chrome_obj = webdriver.Chrome(path, options=options)

    return chrome_obj


def wait_until_visible(browser, by_, selector, time_to_wait=10):
    start_time = time.time()
    while (time.time() - start_time) < time_to_wait:
        if browser.find_elements(by=by_, value=selector):
            return True
        time.sleep(0.1)
    return False


def wait_until_disappear(browser, by_, selector, time_to_wait=10):
    start_time = time.time()
    while (time.time() - start_time) < time_to_wait:
        if not browser.find_elements(by=by_, value=selector):
            return True
        time.sleep(0.5)
    return False


def wait_until_clickable(browser, by_, selector, time_to_wait=10):
    try:
        WebDriverWait(browser, time_to_wait).until(
            ec.element_to_be_clickable((by_, selector)))
    except TimeoutException:
        logging.exception(
            msg=f'{selector} element Not clickable - Timeout Exception', exc_info=False)
    except UnexpectedAlertPresentException:
        # FIXME
        browser.switch_to.alert.dismiss()
        # logging.exception(msg=f'{selector} element Not Visible - Unexpected Alert Exception', exc_info=False)
        # screenshot(selector)
        # browser.refresh()
    except WebDriverException:
        logging.exception(msg=f'Webdriver Error for {selector} object')