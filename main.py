#!/usr/bin/env python

from util.init_driver import init_driver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

import time
from ConfigParser import RawConfigParser
from random import randint

TIMER_READY = 'Ready!'
TIMER_FORMAT = '%M:%S'

# LOGIN INTO MOUSEHUNT
def login(driver):
    global config
    driver.get(config.get("Crawler","START_URL"))

    # Find out if we are already logged in
    # If we are logged in, do nothing
    if find_main_header(driver) != None:
        pass
    # Else, find username, password field and log-in
    else:
        try:
            username_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@name='accountName']")))
            password_field = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//input[@name='password']")))
            username_field.send_keys(config.get("Credential","USERNAME"))
            password_field.send_keys(config.get("Credential","PASSWORD"))
        except TimeoutException:
            print "Timeout while loading LOGIN page"
            return False

        try:
            rmbLogin = driver.find_element_by_xpath("//input[@name='remember']")
            if rmbLogin.is_selected() == False:
                rmbLogin.click()
        except NoSuchElementException:
            print "Failed finding remember checkbox. Skip"

        try:
            driver.find_element_by_xpath("//input[@name='doLogin']").click()
        except NoSuchElementException:
            print "Failed clicking on Login button"
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
    try:
        while True:
            # Check the status (envHeaderImg class)
            main_header = find_main_header(driver)
            if main_header == None:
                print "Cannot find main header to horn"
                return False
            else:
                main_header_class = main_header.get_attribute("class")

            hunt_timer = WebDriverWait(driver, 10).until(EC.visibility_of_element_located((By.XPATH, "//span[@id='huntTimer']")))
            if 'hornError' in main_header_class.lower():
                print 'HORN ERROR: ' + hunt_timer.text
                return False
            elif 'hornResult' in main_header_class.lower():
                print 'Got captcha!'
                #solve_captcha(driver)
                return False
            else:
                if 'ready' in hunt_timer.text.lower():
                    print 'Horn now!'
                    actual_horn(driver)
                else:
                    print "Timer=" + hunt_timer.text
                    time_left = seconds_left(hunt_timer.text)
                    print "Seconds left = " + str(time_left)
                    if time_left < 0:
                        return False
                    else:
                        # Wait time_left + random number of seconds
                        time.sleep(time_left + randint(config.getint("Crawler","TIME_SLEEP_RANDOM_MIN"),config.getint("Crawler","TIME_SLEEP_RANDOM_MAX")))

    except TimeoutException:
        print "Failed finding Hunt Timer"
        return False
    except KeyboardInterrupt:
        print "STOP NOW."
        return True

def actual_horn(driver):
    driver.find_element_by_xpath("//div[@class='mousehuntHud-huntersHorn-container']/a").click()
    time.sleep(5)

def seconds_left(time_string):
    try:
        t = time.strptime(time_string.strip(), TIMER_FORMAT)
        return (t.tm_min * 60 + t.tm_sec)
    except ValueError:
        print "Failed reading time left"
        return -1
    
def solve_captcha(driver):
    captcha_img = driver.find_element_by_xpath("//div[@class='mousehuntPage-puzzle-form-captcha-image']")
    print captcha_img.get_attribute("style")

def main(config_file="config.cfg"):
    global config

    # GET CONFIG
    config = RawConfigParser()
    config.read(config_file)

    #prefered_time_slots = [parse_time_slot(tss) for tss in config.get("Personal","TIME_SLOTS").split(',')]

    # START BROWSER
    driver = init_driver(browser=config.get("Crawler","BROWSER"))
    driver.maximize_window()

    # Login in
    if login(driver) == False:
        return False
    if check_and_horn(driver) == False:
        return False

    driver.quit()


if __name__ == "__main__":
    import getopt, sys

    config_file = "config.cfg"
    try:
        opts, args = getopt.getopt(sys.argv[1:], "c:", ["config-file="])
    except getopt.GetoptError as err:
        print str(err)
        sys.exit(2)

    for o, a in opts:
        if o in ("-c","--config-file"):
            config_file = a
        else:
            assert False, "Unhandled option: " + o

    main(config_file)
                                              