#!/usr/bin/env python3

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function 

import gzip
import io
import logging 
import re
import requests
import shutil
import time
import traceback

from configparser import ConfigParser
from random import randint

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from util.email_utils import send_captcha_alert_mail
from util.init_driver import init_driver


TIMER_READY = 'Ready!'
TIMER_FORMAT = '%M:%S'

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s\t%(levelname)s\t%(message)s',
)

# LOGIN INTO MOUSEHUNT
def login(driver):
    global config
    driver.get(config.get("Crawler","start_url"))

    # Find out if we are already logged in
    # If we are logged in, do nothing
    if find_main_header(driver) != None:
        pass
    # Else, find username, password field and log-in
    else:
        try:
            username_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@name='accountName']")))
            password_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@name='password']")))
            username_field.send_keys(config.get("Credential","username"))
            password_field.send_keys(config.get("Credential","password"))
        except TimeoutException:
            logging.error("Timeout while loading LOGIN page")
            return False

        try:
            rmbLogin = driver.find_element_by_xpath("//input[@name='remember']")
            if rmbLogin.is_selected() == False:
                rmbLogin.click()
        except NoSuchElementException:
            logging.error("Failed finding remember checkbox. Skip")

        try:
            driver.find_element_by_xpath("//button[@name='doLogin']").click()
        except NoSuchElementException:
            logging.error("Failed clicking on Login button")
            return False

    return True

def find_main_header(driver):
    try:
        main_header = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@id='envHeaderImg']")))
        return main_header
    except TimeoutException:
        return None

def check_and_horn(driver):
    global config
    time.sleep(5)
    try:
        while True:
            # Check if captcha is shown
            try:
                captcha_img_div = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='mousehuntPage-puzzle-form-captcha-image']")))
                captcha_code = handle_captcha(captcha_img_div.get_attribute("style")) 
                if captcha_code != None:
                    driver.find_element_by_xpath("//input[@class='mousehuntPage-puzzle-form-code']").send_keys(captcha_code)
                    driver.find_element_by_xpath("//input[@class='mousehuntPage-puzzle-form-code-button']").click()
                    time.sleep(10)
                    continue
                logging.info("ERROR handling captcha!")
                return False
            except TimeoutException:
                pass

            # Check if link to KR is shown
            try:
                kr_link = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='mousehuntHud-huntersHorn-responseMessage']/a")))
                kr_link.click()
                continue
            except TimeoutException:
                pass

            # Check Hunt Timer
            hunt_timer = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[@id='huntTimer']")))
            if 'ready' in hunt_timer.text.lower():
                logging.info('Horn now!')
                actual_horn(driver)
            else:
                time_left = seconds_left(hunt_timer.text)
                # Wait for horn to be ready
                if time_left >= 0:
                    logging.info("Seconds left = {0}".format(time_left))
                    # Wait time_left + random number of seconds
                    time_wait = time_left + randint(config.getint("Crawler","time_sleep_random_min"),config.getint("Crawler","time_sleep_random_max"))
                    logging.info("Wait for {0} seconds...".format(time_wait))
                    time.sleep(time_wait)
                # Error, i.e. Out of cheese,...
                else:
                    logging.info('HORN ERROR: {0}'.format(hunt_timer.text))
                    return False

    except TimeoutException:
        logging.error("Failed finding Hunt Timer")
        return False
    except KeyboardInterrupt:
        logging.info("STOP NOW.")
        return True

def actual_horn(driver):
    try:
        horn_btn = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//div[@class='mousehuntHud-huntersHorn-container']/a")))
        horn_btn.click()
        logging.info("Horn succeed!")
        time.sleep(5)
    except TimeoutException:
        pass

def seconds_left(time_string):
    try:
        t = time.strptime(time_string.strip(), TIMER_FORMAT)
        return (t.tm_min * 60 + t.tm_sec)
    except ValueError:
        logging.error("Failed reading time left: {0}".format(time_string))
        return -1

def handle_captcha(style_string):
    logging.info("Style string=[{0}]".format(style_string))
    captcha_dir = 'captcha/'
    m2 = re.search('url\((.+)\)',style_string)
    if m2 is not None:
        logging.info("Found match in style_string")
        try:
            img_url = m2.group(1)
            logging.info("CAPTCHA URL = [{0}]".format(img_url))
            r = requests.get(img_url, stream=True)
            compressedFile = io.BytesIO(r.raw.read())
            decompressedFile = gzip.GzipFile(fileobj=compressedFile)
            final_file = captcha_dir + str(int(time.time())) + ".jpeg"
            with open(final_file, 'wb') as outfile:
                outfile.write(decompressedFile.read())
            del r

            # Send email
            send_captcha_alert_mail([config.get("Email","email_to")],config.get("Email","email_from"),final_file)

            # Wait for input
            captcha_code = input('Enter captcha code:')
            return captcha_code
        except Exception as e:
            logging.error("ERROR while handling captcha img file:")
            traceback.print_exc()
            return None
    return None

def main(config_file="config.cfg"):
    global config

    # GET CONFIG
    config = ConfigParser()
    config.read(config_file)

    try:
        # START BROWSER
        driver = init_driver(browser=config.get("Crawler","browser"))
        #driver.maximize_window()

        # Login in
        if login(driver) == False:
            return False
        if check_and_horn(driver) == False:
            return False
    finally:
        if driver is not None:
            driver.quit()


if __name__ == "__main__":
    import getopt, sys

    config_file = "config.cfg"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:", ["config-file="])
    except getopt.GetoptError as err:
        logging.error(str(err))
        sys.exit(2)

    for o, a in opts:
        if o in ("-c","--config-file"):
            config_file = a
        else:
            assert False, "Unhandled option: {0}".format(o)

    main(config_file)
                                              
