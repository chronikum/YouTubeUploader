import logging
import re
from datetime import datetime
from time import sleep

from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException
from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.remote.file_detector import LocalFileDetector


def upload_file(
        driver: WebDriver,
        video_path: str,
        title: str,
        description: str,
        game: str,
        kids: bool,
        upload_time: datetime,
        thumbnail_path: str = None,
):
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.CSS_SELECTOR, "ytcp-button#create-icon"))).click()
    WebDriverWait(driver, 20).until(
        EC.element_to_be_clickable((By.XPATH, '//tp-yt-paper-item[@test-id="upload-beta"]'))
    ).click()
    video_input = driver.find_element_by_xpath('//input[@type="file"]')
    video_input.send_keys(video_path)
    
    logging.info("Uploading video...")
    _set_basic_settings(driver, title, description, thumbnail_path)
    sleep(1)
    logging.info("Now going to visibiity...")
    for i in range(3):
        WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "next-button"))).click()
    # logging.info("Arrived at visibility page. Setting visibility to public...")
    # _set_visibility_public(driver)
    # logging.info("Visibility set to public. Now going to done button")
    # Click on DONE
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.ID, "done-button"))).click()

    # Wait for the dialog to disappear
    sleep(5)
    logging.info("Upload is complete")


def _wait_for_processing(driver):
    # Wait for processing to complete
    progress_label: WebElement = driver.find_element_by_css_selector("span.progress-label")
    pattern = re.compile(r"(finished processing)|(processing hd.*)|(check.*)")
    current_progress = progress_label.get_attribute("textContent")
    last_progress = None
    while not pattern.match(current_progress.lower()):
        if last_progress != current_progress:
            logging.info(f'Current progress: {current_progress}')
        last_progress = current_progress
        sleep(5)
        current_progress = progress_label.get_attribute("textContent")

# skips the currently selected element
def skip_current_element(driver: WebDriver):
    currentObject = driver.switch_to.active_element
    currentObject.send_keys(Keys.TAB)
    
def go_key_down_in_element(driver: WebDriver):
    currentObject = driver.switch_to.active_element
    currentObject.send_keys(Keys.DOWN)
    
# sets visibility of the video to public
def _set_visibility_public(driver: WebDriver):
    try:
        WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, '//*[@id="onRadio"]'))
        ).click()
        sleep(5)
        logging.info("Clicking on visibility!")
        sleep(5)
        skip_current_element(driver)
        sleep(3)
        go_key_down_in_element(driver)
        sleep(3)
        go_key_down_in_element(driver)
        sleep(5)
        logging.info("Waiting to make sure upload is complete.")
        sleep(60)
    except NoSuchElementException:
        logging.info("No visibility element found")

def _set_basic_settings(driver: WebDriver, title: str, description: str, thumbnail_path: str = None):
    try:
        sleep(10)
        title_object = driver.switch_to.active_element
        title_object.send_keys(title + " " + "#shorts")
        logging.info("Setting title now!")
        sleep(1)
        title_object.send_keys(Keys.ENTER)
        title_object = driver.switch_to.active_element
        sleep(1)
        skip_current_element(driver)
        sleep(1)
        skip_current_element(driver)
        logging.info("Setting description now!")
        description_input = driver.switch_to.active_element
        description_input.send_keys(description)
    except any:
        logging.info("nono")

def _set_time(driver: WebDriver, upload_time: datetime):
    # Start time scheduling
    WebDriverWait(driver, 20).until(EC.element_to_be_clickable((By.NAME, "SCHEDULE"))).click()

    # Open date_picker
    driver.find_element_by_css_selector("#datepicker-trigger > ytcp-dropdown-trigger:nth-child(1)").click()

    date_input: WebElement = driver.find_element_by_css_selector("input.tp-yt-paper-input")
    date_input.clear()
    # Transform date into required format: Mar 19, 2021
    date_input.send_keys(upload_time.strftime("%b %d, %Y"))
    date_input.send_keys(Keys.RETURN)

    # Open time_picker
    driver.find_element_by_css_selector(
        "#time-of-day-trigger > ytcp-dropdown-trigger:nth-child(1) > div:nth-child(2)"
    ).click()

    time_list = driver.find_elements_by_css_selector("tp-yt-paper-item.tp-yt-paper-item")
    # Transform time into required format: 8:15 PM
    time_str = upload_time.strftime("%I:%M %p").strip("0")
    time = [time for time in time_list[2:] if time.text == time_str][0]
    time.click()
