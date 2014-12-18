#!/usr/bin/env python


from __future__ import print_function
import os
import sys
sys.stdout = os.fdopen(sys.stdout.fileno(), 'w', 0)

# core
from   datetime import datetime, timedelta
from   functools import wraps
import logging
import pprint
import random
import re
import sys
import time


# pypi
import argh
from clint.textui import progress
from splinter import Browser
from selenium.common.exceptions import TimeoutException, UnexpectedAlertPresentException, WebDriverException
from selenium.webdriver.common.by import By
import selenium.webdriver.support.expected_conditions as EC
import selenium.webdriver.support.ui as ui

# local
import conf  # it is used. Even though flymake cant figure that out.

logging.basicConfig(
    format='%(lineno)s %(message)s',
    level=logging.WARN
)


random.seed()

pp = pprint.PrettyPrinter(indent=4)

base_url = 'http://www.myadvertisingpays.com/'

action_path = dict(
    login = "Dot_memberlogin.asp?referURL=Dot_MembersPage.asp",
    viewads = 'viewAds.asp',
    dashboard = 'Dot_MembersPage.asp'
)

one_minute    = 60
three_minutes = 3 * one_minute
ten_minutes   = 10 * one_minute
one_hour      = 3600


def url_for_action(action):
    return "{0}/{1}".format(base_url, action_path[action])

def loop_forever():
    while True: pass

def wait_visible(driver, locator, by=By.XPATH, timeout=30):
    try:
        return ui.WebDriverWait(driver, timeout).until(
            EC.visibility_of_element_located((by, locator)))
    except TimeoutException:
        return False

def trap_unexpected_alert(func):
    @wraps(func)
    def wrapper(self):
        try:
            return func(self)
        except UnexpectedAlertPresentException:
            print("Caught unexpected alert.")
            return 254
        except WebDriverException:
            print("Caught webdriver exception.")
            return 254

    return wrapper

def trap_any(func):
    @wraps(func)
    def wrapper(self):
        try:
            return func(self)
        except:
            print("Caught exception.")
            return 254

    return wrapper

def trap_alert(func):
    @wraps(func)
    def wrapper(self):
        try:
            return func(self)
        except UnexpectedAlertPresentException:
            print("Caught UnexpectedAlertPresentException.")
            return 254
        except WebDriverException:
            print("Caught webdriver exception.")
            return 253


    return wrapper


class Entry(object):

    def __init__(
            self, loginas, browser, action, surf
    ):

        modobj = sys.modules['conf']
        print(modobj)
        d = getattr(modobj, loginas)

        self._username = d['username']
        self._password = d['password']
        self._second_password = d['password2']
        self.browser = browser
        self.action = action
        self.surf = surf

    def login(self):
        print("Logging in...")

        self.browser_visit('login')

        self.browser.find_by_name('username').type(self._username)
        self.browser.find_by_name('password').type(self._password)
        self.browser.find_by_value('Login').first.click()

        time.sleep(1)

        self.browser.find_by_name('password2').type(self._second_password)

        self.browser.find_by_value('Login').first.click()

    def browser_visit(self, action_label):
        try:
            logging.warn("Visiting URL for {0}".format(action_label))
            self.browser.visit(url_for_action(action_label))
            return 0
        except UnexpectedAlertPresentException:
            print("Caught UnexpectedAlertPresentException.")
            logging.warn("Attempting to dismiss alert")
            alert = self.driver.switch_to_alert()
            alert.dismiss()
            return 254
        except WebDriverException:
            print("Caught webdriver exception.")
            return 253


    def view_ads(self):
        for i in xrange(1, self.surf+1):
            while True:
                print("Viewing ad {0}".format(i))
                result = self.view_ad()
                if result == 0:
                    break

        self.calc_account_balance()
        self.calc_time(stay=False)

    @trap_alert
    def view_ad(self):

        logging.warn("Visiting viewads")
        self.browser_visit('viewads')
        time.sleep(random.randrange(2,5))

        logging.warn("Finding text_button")
        buttons = self.browser.find_by_css('.text_button')

        logging.warn("Clicking button")
        buttons[0].click()

        logging.warn("Solving captcha")
        self.solve_captcha()

        #self.wait_on_ad()
        logging.warn("wait_on_ad2")
        self.wait_on_ad2()

        return 0

    def wait_on_ad(self):
        time_to_wait_on_ad = random.randrange(40,50)
        for i in progress.bar(range(time_to_wait_on_ad)):
            time.sleep(1)

    def wait_on_ad2(self):
        wait_visible(self.browser.driver,
                     '//img[@src="images/moreadstop.gif"]',
                     By.XPATH,
                     60)

    def time_macro(self):
        self.calc_account_balance()
        self.calc_time()

    def calc_account_balance(self):

        time.sleep(3)

        logging.warn("visiting dashboard")
        self.browser_visit('dashboard')

        logging.warn("finding element by xpath")
        elem = self.browser.find_by_xpath(
            '/html/body/table[2]/tbody/tr/td[2]/table/tbody/tr/td[2]/table[6]/tbody/tr/td/table/tbody/tr[2]/td/h2[2]/font/font'
        )

        print("Available Account Balance: {}".format(elem.text))


    def calc_time(self, stay=True):

        time.sleep(3)

        self.browser_visit('dashboard')

        elem = self.browser.find_by_xpath(
            '//table[@width="80%"]/tbody/tr/td[1]'
        )

        remaining = elem.text.split()
        for i, v in enumerate(remaining):
            print(i,v)

        indices = dict(
            hours=17,
            minutes=19
        )

        hours = int(remaining[indices['hours']])
        minutes = int(remaining[indices['minutes']])

        next_time  = datetime.now() + timedelta(
            hours=hours, minutes=minutes)

        print("Next time to click is {0}".format(
            next_time.strftime("%Y-%m-%d %H:%M")))

        if stay:
            loop_forever()

    def solve_captcha(self):
        time.sleep(3)
        elem = self.browser.find_by_xpath(
            "/html/body/form[@id='form1']/table/tbody/tr/td/table/tbody/tr[1]/td/font"
        )
        time.sleep(3)

        (x, y, captcha) = elem.text.split()

        print("CAPTCHA = {0}".format(captcha))

        self.browser.find_by_name('codeSb').fill(captcha)

        time.sleep(6)
        button = self.browser.find_by_name('Submit')
        button.click()

def main(loginas, random_delay=False, action='click', stayup=False, surf=10):

    if random_delay:
        random_delay = random.randint(1,15)
        print("Random delay = {0}".format(random_delay))
        time.sleep(one_minute * random_delay)


    with Browser() as browser:

        browser.driver.set_window_size(1200,1100)

        e = Entry(loginas, browser, action, surf)

        e.login()

        if action == 'click':
            e.view_ads()
        if action == 'time':
            e.time_macro()

        if stayup:
            e.time_macro()
            loop_forever()


def conda_main():
    argh.dispatch_command(main)

if __name__ == '__main__':
    argh.dispatch_command(main)
