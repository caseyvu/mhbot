#!/usr/bin/env python3
# encoding: utf-8

from __future__ import absolute_import
from __future__ import division
from __future__ import print_function

from selenium import webdriver
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities


def init_driver(browser='Firefox'):
    # Create the Driver instance
    if browser == 'PhantomJS':
        #--------------------------------------------------------------------------------------------#
        # user_agent = 'User-agent header sent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/49.0.2623.87 Safari/537.36'
        # dcap = dict(DesiredCapabilities.PHANTOMJS)
        # dcap["phantomjs.page.settings.userAgent"] = user_agent
        # dcap["phantomjs.page.settings.javascriptEnabled"] = True
        # dcap["phantomjs.page.settings.cookiesEnabled"] = True
        # driver = webdriver.PhantomJS(desired_capabilities=dcap)
        # driver.cleanSession = True
        # driver.ensureCleanSession = True
        # driver.delete_all_cookies()
        #--------------------------------------------------------------------------------------------#
        # driver = webdriver.PhantomJS()
        #--------------------------------------------------------------------------------------------#
        dcap = dict(DesiredCapabilities.PHANTOMJS)
        user_agent = (
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_4) " +
            "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/29.0.1547.57 Safari/537.36"
        )
        dcap["phantomjs.page.settings.userAgent"] = user_agent
        driver = webdriver.PhantomJS(desired_capabilities=dcap)
    else:
        driver = webdriver.Firefox()
    # End of if/else statements.

    # An implicit wait is to tell WebDriver to poll the DOM for a certain amount of time when trying
    # to find an element or elements if they are not immediately available. The default setting is 0.
    # Once set, the implicit wait is set for the life of the WebDriver object instance.
    # Source: http://selenium-python.readthedocs.org/waits.html#implicit-waits
    driver.implicitly_wait(0.1)  # seconds

    return driver
